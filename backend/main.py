from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from sqlalchemy import func

from jose import jwt, JWTError
from dotenv import load_dotenv

import hashlib
import json
import os
import requests
import uuid

from database import engine, get_db
from models import Base, User, TravelPlan, ScenicSpot, AiLog
from schemas import (
    UserRegister,
    UserLogin,
    TravelPlanCreate,
    TravelPlanUpdate,
    AiPlanRequest,
    ScenicCreate,
    ScenicUpdate,
    ExtractSpotRequest,
)
from agent_service import analyze_user_need, search_spots, build_spot_text, build_plan_prompt


app = FastAPI(title="AI智能旅游规划平台")

os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# CORS：本地开发 + ECS 公网访问都允许
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://121.40.139.220",
        "http://121.40.139.220:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


security = HTTPBearer()

Base.metadata.create_all(bind=engine)

# 后端Token生成代码
SECRET_KEY = "ai-travel-secret-key"
ALGORITHM = "HS256"

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL")


# =========================
# 工具函数
# =========================

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


# 后端Token生成代码
def create_token(username: str):
    data = {"sub": username}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


# 后端解析当前用户代码
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="token无效")

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user


# 后端管理员校验代码
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="没有管理员权限")
    return current_user


# =========================
# 基础测试接口
# =========================

@app.get("/")
def root():
    return {"message": "AI旅游规划平台后端启动成功"}


@app.get("/test")
def test():
    return {"code": 200, "data": "测试接口正常"}


@app.get("/db-test")
def db_test():
    return {"message": "数据库连接测试接口正常"}


# =========================
# 用户注册 / 登录
# =========================

@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    old_user = db.query(User).filter(User.username == user.username).first()

    if old_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    new_user = User(
        username=user.username,
        password=hash_password(user.password),
        role="user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "id": new_user.id,
            "username": new_user.username,
            "role": new_user.role,
        },
    }


# 登录成功后返回 token 和用户角色，前端根据角色展示不同界面
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="用户名不存在")

    if db_user.password != hash_password(user.password):
        raise HTTPException(status_code=401, detail="密码错误")

    token = create_token(db_user.username)

    return {
        "code": 200,
        "message": "登录成功",
        "token": token,
        "role": db_user.role,
    }


# =========================
# 旅游规划 CRUD
# =========================

@app.post("/travel-plans")
def create_travel_plan(
    plan: TravelPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_plan = TravelPlan(
        user_id=current_user.id,
        destination=plan.destination,
        days=plan.days,
        preference=plan.preference,
        plan_content=plan.plan_content,
    )

    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return {"code": 200, "message": "新增旅游规划成功", "data": new_plan}


@app.get("/travel-plans")
def get_travel_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        plans = db.query(TravelPlan).all()
    else:
        plans = db.query(TravelPlan).filter(TravelPlan.user_id == current_user.id).all()

    return {"code": 200, "message": "查询成功", "data": plans}


@app.get("/travel-plans/{plan_id}")
def get_travel_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(TravelPlan).filter(TravelPlan.id == plan_id).first()

    if not plan:
        raise HTTPException(status_code=404, detail="旅游规划不存在")

    if current_user.role != "admin" and plan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="不能访问别人的行程")

    return {"code": 200, "message": "查询成功", "data": plan}


@app.put("/travel-plans/{plan_id}")
def update_travel_plan(
    plan_id: int,
    update_data: TravelPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(TravelPlan).filter(TravelPlan.id == plan_id).first()

    if not plan:
        raise HTTPException(status_code=404, detail="旅游规划不存在")

    if current_user.role != "admin" and plan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="不能修改别人的行程")

    if update_data.destination is not None:
        plan.destination = update_data.destination

    if update_data.days is not None:
        plan.days = update_data.days

    if update_data.preference is not None:
        plan.preference = update_data.preference

    if update_data.plan_content is not None:
        plan.plan_content = update_data.plan_content

    db.commit()
    db.refresh(plan)

    return {"code": 200, "message": "修改成功", "data": plan}


@app.delete("/travel-plans/{plan_id}")
def delete_travel_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(TravelPlan).filter(TravelPlan.id == plan_id).first()

    if not plan:
        raise HTTPException(status_code=404, detail="旅游规划不存在")

    if current_user.role != "admin" and plan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="不能删除别人的行程")

    db.delete(plan)
    db.commit()

    return {"code": 200, "message": "删除成功"}


# =========================
# AI 旅游规划
# =========================

@app.post("/ai/plan-stream")
def ai_plan_stream(
    req: AiPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="没有配置 DEEPSEEK_API_KEY")

    # Agent Service：分析用户需求、检索本地景点数据、整理景点资料、生成最终 prompt
    user_need = analyze_user_need(req)
    spots = search_spots(db, user_need["destination"])
    spot_text = build_spot_text(spots)
    prompt = build_plan_prompt(req, spot_text)

    def generate():
        full_response = ""

        try:
            response = requests.post(
                DEEPSEEK_BASE_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的旅游规划助手。",
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    "stream": True,
                },
                stream=True,
                timeout=60,
            )

            # 后端接收 DeepSeek 的流式内容
            response.raise_for_status()

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                if line.startswith("data: "):
                    data = line.replace("data: ", "")

                    if data == "[DONE]":
                        break

                    try:
                        json_data = json.loads(data)
                        content = json_data["choices"][0]["delta"].get("content", "")

                        if content:
                            full_response += content
                            yield content

                    except Exception:
                        continue

            ai_log = AiLog(
                user_id=current_user.id,
                prompt=prompt,
                response=full_response,
            )

            db.add(ai_log)
            db.commit()

        except Exception as e:
            yield f"\nAI接口调用失败：{str(e)}"

    # 返回给前端一个流式响应，前端会一边收到一边显示
    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")


# 高德地图 POI 提取接口：从用户输入的行程文本中提取景点名称，供地图展示和 RAG 检索使用
@app.post("/ai/extract-spots")
def extract_spots(
    req: ExtractSpotRequest,
    current_user: User = Depends(get_current_user),
):
    if not DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="没有配置 DEEPSEEK_API_KEY")

    prompt = f"""
你是一个旅游行程景点提取助手。

请从下面的旅游行程文本中，提取真正的景点、地标、公园、博物馆、街区名称。
不要提取餐厅、酒店、交通方式、预算、时间。

目的地：{req.destination}

行程文本：
{req.content}

请只返回 JSON 数组，不要解释，不要 markdown。
例如：
["故宫博物院", "天安门广场", "颐和园"]
"""

    try:
        response = requests.post(
            DEEPSEEK_BASE_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "你只负责从旅游文本中提取景点名称。",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "stream": False,
            },
            timeout=60,
        )

        response.raise_for_status()

        text = response.json()["choices"][0]["message"]["content"].strip()
        text = text.replace("```json", "").replace("```", "").strip()

        names = json.loads(text)

        if not isinstance(names, list):
            names = []

        return {
            "code": 200,
            "message": "景点提取成功",
            "data": names,
        }

    except Exception as e:
        return {
            "code": 500,
            "message": f"景点提取失败：{str(e)}",
            "data": [],
        }


# =========================
# 景点管理
# =========================

# 查询景点列表：公开访问，不需要登录
# 这样地图展示、景点展示、RAG 检索都不会因为 token 丢失而 401
@app.get("/scenic-spots")
def get_scenic_spots(
    city: str = "",
    db: Session = Depends(get_db),
):
    query = db.query(ScenicSpot)

    if city:
        query = query.filter(ScenicSpot.city == city)

    spots = query.all()

    return {
        "code": 200,
        "message": "查询成功",
        "data": spots,
    }


# 新增景点：管理员权限
@app.post("/scenic-spots")
def create_scenic_spot(
    data: ScenicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    spot = ScenicSpot(
        city=data.city,
        name=data.name,
        address=data.address,
        lng=data.lng,
        lat=data.lat,
        tags=data.tags,
        description=data.description,
        price=data.price,
        cover_url=data.cover_url,
    )

    db.add(spot)
    db.commit()
    db.refresh(spot)

    return {
        "code": 200,
        "message": "新增景点成功",
        "data": spot,
    }


# 修改景点：管理员权限
@app.put("/scenic-spots/{spot_id}")
def update_scenic_spot(
    spot_id: int,
    data: ScenicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == spot_id).first()

    if not spot:
        raise HTTPException(status_code=404, detail="景点不存在")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(spot, key, value)

    db.commit()
    db.refresh(spot)

    return {
        "code": 200,
        "message": "修改景点成功",
        "data": spot,
    }


# 删除景点：管理员权限
@app.delete("/scenic-spots/{spot_id}")
def delete_scenic_spot(
    spot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    spot = db.query(ScenicSpot).filter(ScenicSpot.id == spot_id).first()

    if not spot:
        raise HTTPException(status_code=404, detail="景点不存在")

    db.delete(spot)
    db.commit()

    return {
        "code": 200,
        "message": "删除景点成功",
    }


# =========================
# 管理员数据大屏
# =========================

@app.get("/admin/statistics")
def admin_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user_count = db.query(User).count()                  # 用户总数
    trip_count = db.query(TravelPlan).count()            # 行程总数
    scenic_count = db.query(ScenicSpot).count()          # 景点总数
    ai_count = db.query(AiLog).count()                   # AI调用次数

    top_destinations_query = (
        db.query(TravelPlan.destination, func.count(TravelPlan.id).label("count"))
        .group_by(TravelPlan.destination)
        .order_by(func.count(TravelPlan.id).desc())
        .limit(10)
        .all()
    )

    top_destinations = [
        {
            "destination": item.destination,
            "count": item.count,
        }
        for item in top_destinations_query
    ]

    return {
        "code": 200,
        "message": "统计成功",
        "data": {
            "user_count": user_count,
            "trip_count": trip_count,
            "scenic_count": scenic_count,
            "ai_count": ai_count,
            "top_destinations": top_destinations,
        },
    }


# =========================
# 文件上传
# =========================

@app.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
):
    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"static/uploads/{file_name}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # 用相对路径，避免部署到 ECS 后还返回 127.0.0.1
    file_url = f"/static/uploads/{file_name}"

    return {
        "code": 200,
        "message": "上传成功",
        "url": file_url,
    }