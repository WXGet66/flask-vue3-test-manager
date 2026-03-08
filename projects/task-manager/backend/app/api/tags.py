from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Tag
from app import db

bp = Blueprint('tags', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_tags():
    """获取当前用户的所有标签"""
    user_id = get_jwt_identity()
    tags = Tag.query.filter_by(user_id=user_id).all()
    return jsonify({
        'code': 200,
        'data': [tag.to_dict() for tag in tags]
    })


@bp.route('/', methods=['POST'])
@jwt_required()
def create_tag():
    """创建新标签"""
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'code': 400, 'msg': '标签名称不能为空'}), 400

    # 检查同一用户下是否已存在同名标签
    existing = Tag.query.filter_by(user_id=user_id, name=name).first()
    if existing:
        return jsonify({'code': 409, 'msg': '标签已存在'}), 409

    tag = Tag(name=name, user_id=user_id)
    db.session.add(tag)
    db.session.commit()
    return jsonify({'code': 201, 'msg': '创建成功', 'data': tag.to_dict()}), 201


@bp.route('/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    """修改标签名称"""
    user_id = get_jwt_identity()
    tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
    if not tag:
        return jsonify({'code': 404, 'msg': '标签不存在'}), 404

    data = request.get_json()
    new_name = data.get('name')
    if not new_name:
        return jsonify({'code': 400, 'msg': '标签名称不能为空'}), 400

    # 检查新名称是否与其他标签冲突（排除自身）
    existing = Tag.query.filter_by(user_id=user_id, name=new_name).first()
    if existing and existing.id != tag_id:
        return jsonify({'code': 409, 'msg': '标签名称已存在'}), 409

    tag.name = new_name
    db.session.commit()
    return jsonify({'code': 200, 'msg': '更新成功', 'data': tag.to_dict()})


@bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """删除标签（同时会从所有任务的关联中自动移除）"""
    user_id = get_jwt_identity()
    tag = Tag.query.filter_by(id=tag_id, user_id=user_id).first()
    if not tag:
        return jsonify({'code': 404, 'msg': '标签不存在'}), 404

    db.session.delete(tag)  # 由于 relationship 设置了 cascade，关联表中的记录会自动删除
    db.session.commit()
    return jsonify({'code': 200, 'msg': '删除成功'})