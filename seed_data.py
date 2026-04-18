from decimal import Decimal

from app import create_app
from models import db, User, Post


def seed_users():
    """Create seed users if they do not already exist."""
    users_seed = [
        {"username": "小王", "nickname": "小王", "gender": "male", "identity_type": "student", "school": "香港大学"},
        {"username": "小李", "nickname": "小李", "gender": "female", "identity_type": "student", "school": "香港中文大学"},
        {"username": "小张", "nickname": "小张", "gender": "male", "identity_type": "student", "school": "香港科技大学"},
    ]

    user_map = {}
    created = 0

    for item in users_seed:
        user = User.query.filter_by(username=item["username"]).first()
        if user is None:
            user = User(
                username=item["username"],
                nickname=item["nickname"],
                gender=item["gender"],
                identity_type=item["identity_type"],
                school=item["school"],
                auth_status="approved",
                bio="港漂学生，认真找作息合拍、爱干净的室友。",
            )
            user.set_password("123456")
            db.session.add(user)
            db.session.flush()
            created += 1
        user_map[item["username"]] = user

    return user_map, created


def seed_posts(user_map):
    """Create two posts per seed user (idempotent by user_id + title)."""
    posts_seed = [
        {
            "username": "小王",
            "title": "港大附近两房次卧招室友，步行到地铁站",
            "rent": Decimal("7800"),
            "location": "港岛",
            "nearby_school": "香港大学",
            "community_name": "坚尼地城海景苑",
            "layout": "两房",
            "area": Decimal("62.0"),
            "poster_intro": "房子采光很好，客厅有落地窗，家电齐全，拎包即可入住。",
            "expected_schedule": "希望工作日23:30前休息，周末可灵活。",
            "cleaning_frequency": "每周轮流打扫公共区域一次，垃圾当天清理。",
            "custom_requirements": "不抽烟、可小酌、带朋友来提前说一声。",
            "hobbies": "健身, 徒步, 咖啡探店",
        },
        {
            "username": "小王",
            "title": "港岛安静小区一房分租，适合港大同学",
            "rent": Decimal("8300"),
            "location": "港岛",
            "nearby_school": "香港大学",
            "community_name": "西营盘雅居",
            "layout": "一房",
            "area": Decimal("45.5"),
            "poster_intro": "近巴士站和超市，厨房可明火，房东响应快。",
            "expected_schedule": "偏早睡早起，尽量避免深夜外放声音。",
            "cleaning_frequency": "公共区域每周至少深度清洁一次。",
            "custom_requirements": "希望室友守时守约，保持公共区域整洁。",
            "hobbies": "摄影, 羽毛球, 看展",
        },
        {
            "username": "小李",
            "title": "沙田近港中文三房合租，主卧带独立卫浴",
            "rent": Decimal("9200"),
            "location": "新界",
            "nearby_school": "香港中文大学",
            "community_name": "沙田第一城",
            "layout": "三房",
            "area": Decimal("78.0"),
            "poster_intro": "离港铁近，通勤方便，客厅空间大，适合一起做饭。",
            "expected_schedule": "平日11点前休息，考试周可互相体谅。",
            "cleaning_frequency": "按值日表轮流打扫，厨房用后即清。",
            "custom_requirements": "女生优先，爱干净，不在室内抽烟。",
            "hobbies": "烘焙, 瑜伽, 追剧",
        },
        {
            "username": "小李",
            "title": "九龙塘两房次卧，近城大理工交通方便",
            "rent": Decimal("7600"),
            "location": "九龙",
            "nearby_school": "香港城市大学",
            "community_name": "又一居",
            "layout": "两房",
            "area": Decimal("58.0"),
            "poster_intro": "家具齐全，周边生活配套成熟，晚上环境安静。",
            "expected_schedule": "希望作息规律，晚上尽量减少噪音。",
            "cleaning_frequency": "每人每周负责一次公共区卫生。",
            "custom_requirements": "可接受短期实习生，爱护家具。",
            "hobbies": "跑步, 桌游, 美食",
        },
        {
            "username": "小张",
            "title": "将军澳两房招室友，去科大巴士直达",
            "rent": Decimal("7000"),
            "location": "新界",
            "nearby_school": "香港科技大学",
            "community_name": "日出康城",
            "layout": "两房",
            "area": Decimal("60.0"),
            "poster_intro": "小区会所设施齐全，安保好，适合长期稳定居住。",
            "expected_schedule": "希望互不打扰，工作日23点后保持安静。",
            "cleaning_frequency": "公共区域一周两次基础清洁。",
            "custom_requirements": "不养大型宠物，保持厨房卫生。",
            "hobbies": "篮球, 游戏, 电影",
        },
        {
            "username": "小张",
            "title": "离岛区海景开放式，适合想要安静环境的同学",
            "rent": Decimal("6800"),
            "location": "离岛",
            "nearby_school": "香港教育大学",
            "community_name": "东涌映湾园",
            "layout": "开放式",
            "area": Decimal("39.0"),
            "poster_intro": "窗外景观好，通风强，附近有商场和运动场。",
            "expected_schedule": "作息可协商，尊重彼此学习和休息时间。",
            "cleaning_frequency": "每周固定周末大扫除。",
            "custom_requirements": "希望室友沟通顺畅，有问题及时说。",
            "hobbies": "徒步, 摄影, 烹饪",
        },
    ]

    created = 0

    for item in posts_seed:
        user = user_map[item["username"]]
        exists = Post.query.filter_by(user_id=user.id, title=item["title"]).first()
        if exists is not None:
            continue

        post = Post(
            user_id=user.id,
            title=item["title"],
            rent=item["rent"],
            location=item["location"],
            nearby_school=item["nearby_school"],
            community_name=item["community_name"],
            layout=item["layout"],
            area=item["area"],
            poster_intro=item["poster_intro"],
            expected_schedule=item["expected_schedule"],
            cleaning_frequency=item["cleaning_frequency"],
            custom_requirements=item["custom_requirements"],
            hobbies=item["hobbies"],
        )
        db.session.add(post)
        created += 1

    return created


def main():
    app = create_app()
    with app.app_context():
        try:
            user_map, users_created = seed_users()
            posts_created = seed_posts(user_map)
            db.session.commit()
            print(f"Seed complete: users_created={users_created}, posts_created={posts_created}")
        except Exception as exc:
            db.session.rollback()
            print(f"Seed failed: {exc}")
            raise


if __name__ == "__main__":
    main()

