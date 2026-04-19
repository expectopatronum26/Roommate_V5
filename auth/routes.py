# auth/routes.py
from flask import render_template, request, redirect, url_for, flash, session
from auth import auth_bp
from models import db, User
from datetime import datetime


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('请输入用户名和密码')
            return render_template('login.html')

        # 从数据库查询用户
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # 登录成功，保存到session
            session['user_id'] = user.id
            session['username'] = user.username
            session['nickname'] = user.nickname or user.username
            session['avatar'] = user.avatar
            session['identity_type'] = user.identity_type
            session['auth_status'] = user.auth_status

            # 更新最后登录时间
            user.last_login = datetime.utcnow()
            db.session.commit()

            flash('登录成功！')
            return redirect(url_for('posts.list_posts'))
        else:
            flash('用户名或密码错误')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """注册"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        phone = request.form.get('phone', '').strip()
        identity_type = request.form.get('identity_type', 'student')

        # 验证
        if not username or not password:
            flash('用户名和密码不能为空')
            return render_template('register.html')

        if password != confirm_password:
            flash('两次密码不一致')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return render_template('register.html')

        if phone and User.query.filter_by(phone=phone).first():
            flash('手机号已被注册')
            return render_template('register.html')

        # 创建新用户
        new_user = User(
            username=username,
            nickname=username,
            phone=phone,
            identity_type=identity_type,
            auth_status='none'
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('注册成功！请登录')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """登出"""
    session.clear()
    flash('已退出登录')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码（简化版）"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        phone = request.form.get('phone', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if new_password != confirm_password:
            flash('两次密码不一致')
            return render_template('forgot_password.html')

        # 通过用户名和手机号验证身份
        user = User.query.filter_by(username=username, phone=phone).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            flash('密码重置成功！请登录')
            return redirect(url_for('auth.login'))
        else:
            flash('用户名或手机号不正确')

    return render_template('forgot_password.html')


@auth_bp.route('/quick_login')
def quick_login():
    """测试期快捷登录（自动用student1登录）"""
    user = User.query.filter_by(username='student1').first()
    if not user:
        flash('测试用户不存在，请先注册')
        return redirect(url_for('auth.register'))

    # 自动登录
    session['user_id'] = user.id
    session['username'] = user.username
    session['nickname'] = user.nickname or user.username
    session['avatar'] = user.avatar
    session['identity_type'] = user.identity_type
    session['auth_status'] = user.auth_status

    user.last_login = datetime.utcnow()
    db.session.commit()

    return redirect(url_for('posts.list_posts'))

