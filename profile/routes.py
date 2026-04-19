# profile/routes.py
from flask import render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
import uuid

from profile import profile_bp
from models import db, User, Post, Favorite, Appointment, Booking


def _current_user_id():
    """获取当前用户ID"""
    return session.get('user_id')


def _require_login():
    """检查登录"""
    if not _current_user_id():
        flash('请先登录')
        return redirect(url_for('auth.login'))
    return None


def _get_current_user():
    """获取当前用户对象"""
    user_id = _current_user_id()
    if user_id:
        return User.query.get(user_id)
    return None


def allowed_file(filename):
    """检查文件格式"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@profile_bp.before_request
def require_login():
    """全局登录检查"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))


@profile_bp.route('/')
def profile():
    """个人资料主页"""
    user = _get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    # 获取用户的帖子
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()

    # 获取收藏
    favorites_query = Favorite.query.filter_by(user_id=user.id).all()
    favorites = []
    for fav in favorites_query:
        post = Post.query.get(fav.post_id)
        if post:
            # 获取封面图
            cover_image = post.images.first()
            favorites.append({
                'id': post.id,
                'title': post.title,
                'location': post.location,
                'rent': post.rent,
                'image': cover_image.image_url if cover_image else 'https://picsum.photos/300/200'
            })

    # 获取预约（合并Appointment和Booking）
    appointments = []
    # Appointment表的预约
    appts = Appointment.query.filter_by(user_id=user.id).all()
    for appt in appts:
        post = Post.query.get(appt.post_id) if appt.post_id else None
        appointments.append({
            'id': appt.id,
            'post_title': post.title if post else '房源',
            'date': appt.appointment_date.strftime('%Y-%m-%d'),
            'time_slot': appt.appointment_time_slot,
            'status': appt.status,
            'type': 'appointment'
        })

    # Booking表的预约
    bookings = Booking.query.filter_by(user_id=user.id).all()
    for booking in bookings:
        appointments.append({
            'id': booking.id,
            'post_title': booking.house_title,
            'date': booking.visit_date.strftime('%Y-%m-%d'),
            'time_slot': booking.visit_time,
            'status': booking.status,
            'type': 'booking'
        })

    # 按日期排序
    appointments.sort(key=lambda x: x['date'], reverse=True)

    return render_template('profile.html',
                           user=user,
                           posts=posts,
                           favorites=favorites,
                           appointments=appointments)


@profile_bp.route('/update_profile', methods=['POST'])
def update_profile():
    """更新个人资料"""
    user = _get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    # 更新基本信息
    user.nickname = request.form.get('nickname', '').strip() or user.username
    user.school = request.form.get('school', '').strip()
    user.identity_type = request.form.get('identity', 'student')
    user.gender = request.form.get('gender', 'male')
    user.bio = request.form.get('bio', '').strip()
    user.phone = request.form.get('phone', '').strip()

    # 处理头像上传
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = str(uuid.uuid4()) + '.' + filename.rsplit('.', 1)[1].lower()
            from flask import current_app
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)

            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)

            user.avatar = f'/static/uploads/{unique_filename}'

        elif file and file.filename and not allowed_file(file.filename):
            flash('不支持的文件格式，请上传 PNG、JPG、JPEG 或 GIF 格式的图片')
            return redirect(url_for('profile.profile'))

    db.session.commit()

    # 更新session
    session['nickname'] = user.nickname
    session['avatar'] = user.avatar

    flash('个人信息更新成功')
    return redirect(url_for('profile.profile'))


@profile_bp.route('/auth_verification')
def auth_verification():
    """身份认证页面"""
    user = _get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    return render_template('auth_verification.html', user=user)


@profile_bp.route('/upload_auth', methods=['POST'])
def upload_auth():
    """上传认证文件"""
    user = _get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    if 'auth_file' not in request.files:
        flash('没有选择文件')
        return redirect(url_for('profile.auth_verification'))

    file = request.files['auth_file']
    if file.filename == '':
        flash('没有选择文件')
        return redirect(url_for('profile.auth_verification'))

    school = request.form.get('school', '').strip()
    if not school:
        flash('请选择学校')
        return redirect(url_for('profile.auth_verification'))

    # 保存认证文件
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + '.' + filename.rsplit('.', 1)[1].lower()

        from flask import current_app
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        user.auth_photo = f'/static/uploads/{unique_filename}'
        user.school = school
        user.auth_status = 'pending'

        db.session.commit()

        flash('身份认证文件上传成功，等待审核')
    else:
        flash('不支持的文件格式')

    return redirect(url_for('profile.auth_verification'))


@profile_bp.route('/cancel_auth', methods=['POST'])
def cancel_auth():
    """取消认证"""
    user = _get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    user.auth_status = 'none'
    user.auth_photo = None

    db.session.commit()
    flash('认证已取消')

    return redirect(url_for('profile.auth_verification'))


@profile_bp.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    """取消预约"""
    user = _get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    # 先查Appointment表
    appt = Appointment.query.filter_by(id=appointment_id, user_id=user.id).first()
    if appt:
        appt.status = 'cancelled'
        db.session.commit()
        flash('预约已取消')
        return redirect(url_for('profile.profile'))

    # 再查Booking表
    booking = Booking.query.filter_by(id=appointment_id, user_id=user.id).first()
    if booking:
        booking.status = 'cancelled'
        db.session.commit()
        flash('预约已取消')
        return redirect(url_for('profile.profile'))

    flash('预约不存在')
    return redirect(url_for('profile.profile'))


@profile_bp.route('/posts_list')
def posts_list():
    """我的帖子列表"""
    user = _get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()

    posts_with_cover = []
    for post in posts:
        # 获取第一张图片作为封面
        cover_image = post.images.first()
        posts_with_cover.append({
            'post': post,  # 保留完整的post对象
            'cover_url': cover_image.image_url if cover_image else 'https://picsum.photos/seed/default/400/300'
        })
    return render_template('profile/posts_list.html', user=user,
                           posts=posts_with_cover)

@profile_bp.route('/favorites_list')
def favorites_list():
    """我的收藏列表"""
    user = _get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    favorites_query = Favorite.query.filter_by(user_id=user.id).all()
    favorites = []

    for fav in favorites_query:
        post = Post.query.get(fav.post_id)
        if post:
            cover_image = post.images.first()
            favorites.append({
                'id': post.id,
                'title': post.title,
                'location': post.location,
                'rent': post.rent,
                'image': cover_image.image_url if cover_image else 'https://picsum.photos/300/200'
            })

    return render_template('favorites_list.html', user=user, favorites=favorites)


@profile_bp.route('/appointments_list')
def appointments_list():
    """我的预约列表"""
    user = _get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    #直接查询 Booking 对象列表（保持完整对象，供模板使用）
    from datetime import date
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.visit_date.desc()).all()
    today = date.today()

    #渲染 my_dashboard.html 模板
    return redirect(url_for('chat.dashboard'))