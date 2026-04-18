# chat/routes.py
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from datetime import datetime, timedelta, date
import time

from chat import chat_bp
from models import db, User, Message, Booking, Post

# ============ 自动回复关键词字典 ============
AUTO_REPLY_KEYWORDS = {
    '租金': '这套房子的租金是{price}，包含物业费，押一付三。如果长租可以优惠哦~',
    '价格': '租金是{price}，性价比很高！周边配套齐全。',
    '多少钱': '房租是{price}，欢迎来看房详谈~',
    '面积': '这套房子面积是{area}，三室一厅，空间很宽敞！',
    '大小': '房子{area}，户型方正，采光好。',
    '位置': '房子在{location}，交通便利，地铁5分钟。',
    '地址': '具体地址是{location}，附近有商场和学校。',
    '哪里': '房源位置：{location}，周边生活设施完善。',
    '看房': '欢迎随时来看房！我的空闲时间是工作日晚上和周末全天。您方便什么时候呢？',
    '预约': '好的！您可以点击右上角"预约看房"按钮选择时间，或者直接告诉我您方便的时间~',
    '家具': '房子配有全套家具：床、沙发、冰箱、洗衣机、空调等，拎包入住！',
    '家电': '家电齐全：冰箱、洗衣机、空调、热水器、电视，都是近两年新买的。',
    '宠物': '可以养宠物，但需要保持房屋清洁哦。',
    '合租': '这套房子适合整租，也可以合租，具体可以面谈。',
    '水电': '水电燃气费用按实际使用量缴纳，一般每月200元左右。',
    '物业费': '物业费包含在租金里，不需要另外交。',
    '押金': '押金是一个月租金，退租时没有损坏会全额退还。',
    '合同': '签订正规租赁合同，保障双方权益。',
    '你好': '您好！很高兴为您服务，请问有什么可以帮您的吗？',
    '在吗': '在的！有什么问题尽管问我~',
    '您好': '您好呀！欢迎咨询~',
}

DEFAULT_AUTO_REPLY = '您好，我暂时不在，稍后会尽快回复您！您也可以点击右上角预约看房哦~'


def _current_user_id():
    """获取当前登录用户ID"""
    return session.get('user_id')


def _require_login():
    """检查登录"""
    if not _current_user_id():
        flash('请先登录')
        return redirect(url_for('auth.login'))
    return None


def generate_auto_reply(user_message, contact_user, post=None):
    """
    智能自动回复
    user_message: 用户发送的消息内容
    contact_user: 联系人User对象
    """
    message_lower = user_message.lower()

    # 优先使用传入的 post，没有则取对方最新帖子
    if not post:
        post = Post.query.filter_by(user_id=contact_user.id).order_by(Post.created_at.desc()).first()

    # 如果有帖子，使用帖子信息；否则使用默认信息
    if post:
        price = f"{post.rent}元/月"
        area = f"{post.area}㎡" if post.area else "80㎡"
        location = post.location
    else:
        price = "8000元/月"
        area = "60㎡"
        location = "香港"

    # 匹配关键词
    for keyword, reply_template in AUTO_REPLY_KEYWORDS.items():
        if keyword in message_lower:
            reply = reply_template.format(
                price=price,
                area=area,
                location=location
            )
            return reply

    return DEFAULT_AUTO_REPLY


@chat_bp.route('/')
def chat_home():
    """聊天主页"""
    login_redirect = _require_login()
    if login_redirect:
        return login_redirect

    current_user_id = _current_user_id()

    # 获取所有与当前用户有聊天记录的联系人
    # 方法：查询所有消息，提取对方ID，去重
    sent_to = db.session.query(Message.receiver_id).filter(Message.sender_id == current_user_id).distinct()
    received_from = db.session.query(Message.sender_id).filter(Message.receiver_id == current_user_id).distinct()

    contact_ids = set()
    for row in sent_to:
        contact_ids.add(row[0])
    for row in received_from:
        contact_ids.add(row[0])

    # 获取联系人信息
    contacts = []
    if contact_ids:
        contacts = User.query.filter(User.id.in_(contact_ids)).all()

    # 为每个联系人添加最后一条消息
    for contact in contacts:
        last_msg = Message.query.filter(
            ((Message.sender_id == current_user_id) & (Message.receiver_id == contact.id)) |
            ((Message.sender_id == contact.id) & (Message.receiver_id == current_user_id))
        ).order_by(Message.sent_at.desc()).first()

        if last_msg:
            contact.last_message = last_msg.content[:30]
            contact.last_message_time = last_msg.sent_at
        else:
            contact.last_message = ""
            contact.last_message_time = datetime.now()

    # 按时间排序
    contacts.sort(key=lambda x: x.last_message_time, reverse=True)

    return render_template('chat.html', contacts=contacts,
                           current_contact=None,
                           messages=[],
                           current_user_id=current_user_id)


@chat_bp.route('/<int:contact_id>')
def chat_with_contact(contact_id):
    """与指定联系人聊天"""
    login_redirect = _require_login()
    if login_redirect:
        return login_redirect

    current_user_id = _current_user_id()
    current_contact = User.query.get_or_404(contact_id)

    from models import Post
    post_id = request.args.get('post_id', type=int)
    if not post_id:
        # 从历史消息中找最近一条带 post_id 的消息
        recent_msg = Message.query.filter(
            db.or_(
                db.and_(Message.sender_id == current_user_id, Message.receiver_id == contact_id),
                db.and_(Message.sender_id == contact_id, Message.receiver_id == current_user_id)
            ),
            Message.post_id.isnot(None)
        ).order_by(Message.sent_at.desc()).first()
        if recent_msg:
            post_id = recent_msg.post_id
    house_info = Post.query.get(post_id) if post_id else None

    # 获取所有联系人（同上）
    sent_to = db.session.query(Message.receiver_id).filter(Message.sender_id == current_user_id).distinct()
    received_from = db.session.query(Message.sender_id).filter(Message.receiver_id == current_user_id).distinct()

    contact_ids = set()
    for row in sent_to:
        contact_ids.add(row[0])
    for row in received_from:
        contact_ids.add(row[0])

    contacts = []
    if contact_ids:
        contacts = User.query.filter(User.id.in_(contact_ids)).all()

    # 确保当前聊天对象也在联系人列表里（首次私信时没有历史消息）
    if contact_id not in contact_ids:
        contacts.insert(0, current_contact)

    for contact in contacts:
        last_msg = Message.query.filter(
            ((Message.sender_id == current_user_id) & (Message.receiver_id == contact.id)) |
            ((Message.sender_id == contact.id) & (Message.receiver_id == current_user_id))
        ).order_by(Message.sent_at.desc()).first()

        if last_msg:
            contact.last_message = last_msg.content[:30]
            contact.last_message_time = last_msg.sent_at
        else:
            contact.last_message = ""
            contact.last_message_time = datetime.now()

    contacts.sort(key=lambda x: x.last_message_time, reverse=True)

    # 获取聊天记录
    messages = Message.query.filter(
        ((Message.sender_id == current_user_id) & (Message.receiver_id == contact_id)) |
        ((Message.sender_id == contact_id) & (Message.receiver_id == current_user_id))
    ).order_by(Message.sent_at.asc()).all()

    messages_dict = [msg.to_dict() for msg in messages]

    return render_template('chat.html',
                           contacts=contacts,
                           current_contact=current_contact,
                           messages=messages_dict,
                           current_user_id=current_user_id,
                           house_info=house_info)


@chat_bp.route('/api/messages/<int:contact_id>', methods=['GET'])
def get_messages(contact_id):
    """获取聊天记录API"""
    login_redirect = _require_login()
    if login_redirect:
        return jsonify({'error': '未登录'}), 401

    current_user_id = _current_user_id()
    messages = Message.query.filter(
        ((Message.sender_id == current_user_id) & (Message.receiver_id == contact_id)) |
        ((Message.sender_id == contact_id) & (Message.receiver_id == current_user_id))
    ).order_by(Message.sent_at.asc()).all()

    return jsonify([msg.to_dict() for msg in messages])


@chat_bp.route('/api/send_message', methods=['POST'])
def send_message():
    """发送消息API"""
    login_redirect = _require_login()
    if login_redirect:
        return jsonify({'error': '未登录'}), 401

    data = request.get_json()
    current_user_id = _current_user_id()
    receiver_id = data.get('receiver_id')  # 统一用receiver_id
    content = data.get('content')
    post_id = data.get('post_id')

    if not receiver_id or not content:
        return jsonify({'error': '参数错误'}), 400

    # 保存用户消息
    print(f"DEBUG: current_user_id={current_user_id}, receiver_id={receiver_id}")
    new_message = Message(
        sender_id=current_user_id,
        receiver_id=receiver_id,
        content=content,
        post_id=post_id,
        is_auto_reply=False
    )
    db.session.add(new_message)
    db.session.commit()

    # 生成自动回复
    receiver = User.query.get(receiver_id)
    auto_reply_message = None
    if receiver:
        time.sleep(0.5)  # 模拟输入延迟

        post = Post.query.get(post_id) if post_id else None
        auto_reply_content = generate_auto_reply(content, receiver, post=post)

        print(f"DEBUG auto_reply: sender_id={receiver_id}, receiver_id={current_user_id}")
        auto_reply_message = Message(
            sender_id=receiver_id,
            receiver_id=current_user_id,
            content=auto_reply_content,
            post_id=post_id,
            is_auto_reply=True
        )
        db.session.add(auto_reply_message)
        db.session.commit()

    result = {
        'success': True,
        'message': new_message.to_dict()
    }

    if auto_reply_message:
        result['auto_reply'] = auto_reply_message.to_dict()

    return jsonify(result)


# ============ 预约看房功能 ============

@chat_bp.route('/booking')
def booking():
    """预约看房页面"""
    login_redirect = _require_login()
    if login_redirect:
        return login_redirect

    # 生成未来7天日期
    available_dates = []
    for i in range(7):
        day = date.today() + timedelta(days=i)
        available_dates.append({
            'date': day.strftime('%Y-%m-%d'),
            'weekday': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][day.weekday()]
        })

    # 时间段（9:00-18:00）
    available_times = [f"{h:02d}:00" for h in range(9, 19)]

    # 获取当前用户的预约记录
    current_user_id = _current_user_id()
    my_bookings = Booking.query.filter_by(user_id=current_user_id).order_by(Booking.visit_date.desc()).all()

    # 今天已被预约的时间
    today = date.today()
    booked_times_today = [b.visit_time for b in Booking.query.filter_by(visit_date=today).all()]

    from models import Post
    post_id = request.args.get('post_id', type=int)
    post = Post.query.get(post_id) if post_id else None
    return render_template('/chat/booking.html',
                           dates=available_dates,
                           times=available_times,
                           bookings=my_bookings,
                           booked_times=booked_times_today,
                           today=today,
                           post=post)


@chat_bp.route('/make_booking', methods=['POST'])
def make_booking():
    """提交预约"""
    login_redirect = _require_login()
    if login_redirect:
        return login_redirect

    current_user_id = _current_user_id()
    current_user = User.query.get(current_user_id)

    visit_date_str = request.form.get('date')
    visit_time = request.form.get('time')
    house_title = request.form.get('house_title', '待看房源')

    visit_date = datetime.strptime(visit_date_str, '%Y-%m-%d').date()
    # 检查时间冲突
    existing = Booking.query.filter_by(
        user_id=current_user_id,
        visit_date=visit_date,
        visit_time=visit_time
    ).first()

    if existing:
        flash('您在这个时间已有预约')
        return redirect(url_for('chat.booking'))

    # 创建预约
    new_booking = Booking(
        user_id=current_user_id,
        user_name=current_user.nickname or current_user.username,
        house_title=house_title,
        visit_date=visit_date,
        visit_time=visit_time,
        status='pending'
    )
    db.session.add(new_booking)
    db.session.commit()

    return render_template('chat/booking_success.html',
                           date=visit_date_str,
                           time=visit_time,
                           house_title=house_title)


@chat_bp.route('/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    """取消预约"""
    login_redirect = _require_login()
    if login_redirect:
        return login_redirect

    current_user_id = _current_user_id()
    source = request.args.get('source', 'booking')

    booking = Booking.query.get_or_404(booking_id)

    # 验证是否是本人的预约
    if booking.user_id != current_user_id:
        flash('无权取消此预约')
        return redirect(url_for('chat.booking'))

    booking_date = str(booking.visit_date)
    booking_time = booking.visit_time
    house_title = booking.house_title

    db.session.delete(booking)
    db.session.commit()

    return render_template('cancel_success.html',
                           date=booking_date,
                           time=booking_time,
                           house_title=house_title,
                           source=source)


@chat_bp.route('/dashboard')
def dashboard():
    """个人预约日程"""
    login_redirect = _require_login()
    if login_redirect:
        return login_redirect

    current_user_id = _current_user_id()
    all_bookings = Booking.query.filter_by(user_id=current_user_id).order_by(Booking.visit_date.desc()).all()
    today = date.today()

    return render_template('my_dashboard.html',
                           bookings=all_bookings,
                           today=today)

