from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Task, Tag, User
from app import db, mail  # 导入 mail 扩展
from datetime import datetime, timedelta
from flask_mail import Message

bp = Blueprint('tasks', __name__)

# ------------------- 任务 CRUD -------------------

@bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """获取当前用户的所有任务（可筛选完成状态）"""
    user_id = get_jwt_identity()
    completed = request.args.get('completed')  # 可选：true/false
    query = Task.query.filter_by(user_id=user_id)
    if completed is not None:
        query = query.filter_by(completed=completed.lower() == 'true')
    tasks = query.all()
    return jsonify({'code': 200, 'data': [t.to_dict() for t in tasks]})


@bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    """创建新任务（支持标签）"""
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data.get('title'):
        return jsonify({'code': 400, 'msg': '标题不能为空'}), 400

    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        completed=data.get('completed', False),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
        user_id=user_id
    )

    # 处理标签
    tag_ids = data.get('tag_ids', [])
    if tag_ids:
        tags = Tag.query.filter(Tag.id.in_(tag_ids), Tag.user_id == user_id).all()
        task.tags = tags

    db.session.add(task)
    db.session.commit()
    return jsonify({'code': 201, 'msg': '创建成功', 'data': task.to_dict()}), 201


@bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """更新任务（支持标签更新）"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'code': 404, 'msg': '任务不存在'}), 404

    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None

    # 更新标签
    if 'tag_ids' in data:
        tag_ids = data['tag_ids']
        tags = Tag.query.filter(Tag.id.in_(tag_ids), Tag.user_id == user_id).all()
        task.tags = tags

    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功', 'data': task.to_dict()})


@bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """删除任务"""
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'code': 404, 'msg': '任务不存在'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})


# ------------------- 邮件提醒功能 -------------------

def send_email(subject, recipients, html_body):
    """发送邮件的辅助函数（直接使用 flask-mail）"""
    msg = Message(subject, recipients=recipients, html=html_body)
    mail.send(msg)


@bp.route('/remind', methods=['POST'])
@jwt_required()
def remind_tasks():
    """向当前用户发送今天到期的任务提醒邮件"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.email:
        return jsonify({'code': 400, 'msg': '用户邮箱未设置'}), 400

    # 查询今天到期的未完成任务
    today = datetime.utcnow().date()
    tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.completed == False,
        Task.due_date >= today,
        Task.due_date < today + timedelta(days=1)
    ).all()

    if not tasks:
        return jsonify({'code': 200, 'msg': '今天没有待办任务'})

    # 构建邮件内容
    task_list = ''.join([f'<li>{t.title} (截止: {t.due_date.strftime("%Y-%m-%d %H:%M")})</li>' for t in tasks])
    html = f"""
    <h3>您有以下待办任务：</h3>
    <ul>{task_list}</ul>
    <p>请及时处理。</p>
    """

    try:
        send_email('任务提醒', [user.email], html)
        return jsonify({'code': 200, 'msg': '提醒邮件已发送'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'邮件发送失败: {str(e)}'}), 500


@bp.route('/test-email', methods=['GET'])
@jwt_required()
def test_email():
    """测试邮件配置是否正常"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.email:
        return jsonify({'code': 400, 'msg': '用户邮箱未设置'}), 400

    try:
        send_email('测试邮件', [user.email], '<h1>邮件服务配置正确</h1><p>恭喜，你可以正常发送邮件了。</p>')
        return jsonify({'code': 200, 'msg': '测试邮件发送成功'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)}), 500