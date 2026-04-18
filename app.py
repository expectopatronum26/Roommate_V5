# app.py
import sys
from flask import Flask, redirect, url_for, session
from config import Config
from models import db


def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 确保上传文件夹存在
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # UTF-8配置（Windows兼容）
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    from auth import auth_bp
    from posts import posts_bp
    from chat import chat_bp
    from profile import profile_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(posts_bp, url_prefix='/posts')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(profile_bp, url_prefix='/profile')

    # 创建数据库表
    with app.app_context():
        db.create_all()
        init_test_data()  # 初始化测试数据

    # 主页路由
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('posts.list_posts'))
        return redirect(url_for('auth.login'))

    return app


def init_test_data():
    """初始化测试数据"""
    from models import User, Post

    # 创建测试用户（如果不存在）
    if User.query.count() == 0:
        # 测试用户1 - 学生
        user1 = User(
            username='student1',
            nickname='张同学',
            phone='13800138000',
            email='student@example.com',
            gender='male',
            identity_type='student',
            school='香港中文大学',
            bio='我是港中文的学生，想找个安静的室友',
            auth_status='approved'
        )
        user1.set_password('123456')

        # 测试用户2 - 房东
        user2 = User(
            username='landlord1',
            nickname='陈小姐',
            phone='13900139000',
            email='landlord@example.com',
            gender='female',
            identity_type='landlord',
            bio='有多套房源出租',
            auth_status='approved'
        )
        user2.set_password('123456')

        db.session.add_all([user1, user2])
        db.session.commit()
        print("✅ 测试用户创建成功")
        print("用户名: student1, 密码: 123456")
        print("   用户名: landlord1, 密码: 123456")


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

