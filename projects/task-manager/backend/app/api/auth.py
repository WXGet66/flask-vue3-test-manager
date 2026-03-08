from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'code': 409, 'msg': '用户名已存在'}), 409

    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'code': 201, 'msg': '注册成功', 'data': user.to_dict()}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not user.check_password(data.get('password')):
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401

    # 关键修改：将 user.id 转为字符串，避免 JWT subject 类型错误
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'code': 200, 'msg': '登录成功', 'data': {'token': access_token, 'user': user.to_dict()}}), 200

@bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    # 如果后续需要整数 ID，可以转换：current_user_id = int(current_user_id)
    user = User.query.get(current_user_id)
    return jsonify({'code': 200, 'data': user.to_dict()})