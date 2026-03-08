from app import db
from datetime import datetime

# 任务-标签多对多关联表
task_tag = db.Table('task_tag',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)

    # 外键：关联到用户
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 与标签的多对多关系
    tags = db.relationship('Tag', secondary=task_tag, lazy='subquery',
                           backref=db.backref('tasks', lazy=True))

    def to_dict(self):
        """将任务对象转换为字典，方便返回 JSON"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'tags': [{'id': t.id, 'name': t.name} for t in self.tags]
        }


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    # 外键：关联到用户（标签属于特定用户）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 确保同一个用户下标签名称唯一
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='unique_user_tag'),)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }