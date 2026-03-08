import csv
import io
import json
from flask import Blueprint, make_response, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Task

bp = Blueprint('export', __name__)

@bp.route('/csv', methods=['GET'])
@jwt_required()
def export_csv():
    """将当前用户的任务导出为 CSV 文件"""
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()

    # 创建内存中的 CSV 文件
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', '标题', '描述', '完成状态', '创建时间', '截止日期', '标签'])

    for task in tasks:
        writer.writerow([
            task.id,
            task.title,
            task.description or '',
            '是' if task.completed else '否',
            task.created_at.strftime('%Y-%m-%d %H:%M') if task.created_at else '',
            task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
            ', '.join([tag.name for tag in task.tags])
        ])

    # 生成响应
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=tasks.csv'
    response.headers['Content-type'] = 'text/csv'
    return response


@bp.route('/json', methods=['GET'])
@jwt_required()
def export_json():
    """将当前用户的任务导出为 JSON 文件"""
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()
    task_list = [task.to_dict() for task in tasks]  # to_dict 已包含标签信息

    response = make_response(json.dumps(task_list, ensure_ascii=False, indent=2))
    response.headers['Content-Disposition'] = 'attachment; filename=tasks.json'
    response.headers['Content-type'] = 'application/json'
    return response