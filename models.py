# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """用户表- 合并所有用户相关字段"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 基础信息（统一字段名）
    username = db.Column(db.String(50), unique=True, nullable=False)  # 统一用username
    password_hash = db.Column(db.String(128), nullable=False)
    nickname = db.Column(db.String(50), nullable=True)  # 昵称/显示名称
    # 联系方式
    phone = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)

    # 个人资料
    avatar = db.Column(db.String(255), default='https://picsum.photos/seed/avatar/200/200')
    gender = db.Column(db.String(10), default='male')  # male, female, other
    bio = db.Column(db.Text, nullable=True)

    # 身份信息
    identity_type = db.Column(db.String(20), default='student')  # student, landlord
    school = db.Column(db.String(100), nullable=True)  # 学校名称
    # 认证状态
    auth_photo = db.Column(db.String(255), nullable=True)
    auth_status = db.Column(db.String(20), default='none')  # none, pending, approved, rejected

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver',
                                        lazy='dynamic')
    appointments = db.relationship('Appointment', backref='user', lazy='dynamic')
    bookings = db.relationship('Booking', backref='user', lazy='dynamic')  # 新增
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')
    view_histories = db.relationship('ViewHistory', backref='user', lazy='dynamic')

    def set_password(self, password):
        """设置密码（加密）"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典（用于API返回）"""
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname or self.username,
            'avatar': self.avatar,
            'gender': self.gender,
            'bio': self.bio,
            'identity_type': self.identity_type,
            'school': self.school,
            'auth_status': self.auth_status, }


class Post(db.Model):
    """帖子表"""
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 基本信息
    title = db.Column(db.String(100), nullable=False)
    rent = db.Column(db.Numeric(10, 2), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    nearby_school = db.Column(db.String(100), nullable=True)
    community_name = db.Column(db.String(100), nullable=True)
    layout = db.Column(db.String(50), nullable=True)
    area = db.Column(db.Numeric(10, 2), nullable=True)

    # 发帖人信息
    poster_gender = db.Column(db.String(10), nullable=True)
    poster_age = db.Column(db.Integer, nullable=True)
    poster_occupation_or_school = db.Column(db.String(100), nullable=True)
    poster_intro = db.Column(db.Text, nullable=True)
    hobbies = db.Column(db.Text, nullable=True)  # JSON格式

    # 室友期望
    expected_schedule = db.Column(db.String(100), nullable=True)
    cleaning_frequency = db.Column(db.String(50), nullable=True)
    custom_requirements = db.Column(db.Text, nullable=True)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    images = db.relationship('PostImage', backref='post', lazy='dynamic', cascade="all, delete-orphan")
    appointments = db.relationship('Appointment', backref='post', lazy='dynamic', cascade="all, delete-orphan")
    favorites = db.relationship('Favorite', backref='post', lazy='dynamic', cascade="all, delete-orphan")
    view_histories = db.relationship('ViewHistory', backref='post', lazy='dynamic', cascade="all, delete-orphan")


class PostImage(db.Model):
    """帖子图片表"""
    __tablename__ = 'post_images'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0)


class Message(db.Model):
    """消息表 - 统一字段名"""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 统一用receiver
    content = db.Column(db.Text, nullable=False)
    is_auto_reply = db.Column(db.Boolean, default=False)  # 新增：是否自动回复
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)  # 统一用sent_at

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'is_auto_reply': self.is_auto_reply,
            'is_read': self.is_read,
            'sent_at': self.sent_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Appointment(db.Model):
    """预约表（原有的）"""
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time_slot = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Booking(db.Model):
    """预约看房表（第二个人的功能）"""
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)  # 可选关联帖子

    user_name = db.Column(db.String(50), default="访客")
    house_title = db.Column(db.String(200), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    visit_time = db.Column(db.String(10), nullable=False)

    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Favorite(db.Model):
    """收藏表"""
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ViewHistory(db.Model):
    """浏览历史表"""
    __tablename__ = 'view_histories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

