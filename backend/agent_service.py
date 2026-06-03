from models import ScenicSpot


# 1. 分析用户需求
def analyze_user_need(req):
    return {
        "destination": req.destination,
        "days": req.days,
        "budget": req.budget,
        "preference": req.preference,
        "language": req.language
    }


# 2. 检索本地景点数据
def search_spots(db, destination: str):
    return db.query(ScenicSpot).filter(ScenicSpot.city == destination).all()


# 3. 整理景点资料
def build_spot_text(spots):
    if not spots:
        return "数据库中暂时没有该城市的景点资料。"

    return "\n".join([
        f"景点名称：{spot.name}；地址：{spot.address}；标签：{spot.tags}；门票：{spot.price}；介绍：{spot.description}"
        for spot in spots
    ])


# 4. 生成最终 prompt
def build_plan_prompt(req, spot_text: str):
    output_language = "英文" if req.language == "en" else "中文"

    prompt = f"""
你是一个智能旅游规划助手，只能回答旅游规划相关问题。

用户需求：
目的地：{req.destination}
天数：{req.days}
预算：{req.budget}
偏好：{req.preference}

下面是系统从本地景点数据库中检索到的资料：
{spot_text}

请优先参考上面的本地景点资料来生成旅行计划。
如果本地资料不足，可以适当补充常识性旅游建议，但不要胡编不存在的景点。

请使用{output_language}输出完整旅行计划。

请按以下格式输出：
1. 总体建议
2. 每日行程安排
3. 交通建议
4. 美食推荐
5. 预算估算
6. 注意事项

如果用户需求和旅游无关，请拒绝回答。
"""
    return prompt