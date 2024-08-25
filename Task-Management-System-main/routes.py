from flask import Blueprint, request, jsonify
from app import db
from app.models import Task
from app.auth import register_user, login_user
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('api', __name__)

@bp.route('/api/register', methods=['POST'])
def register():
    return register_user()

@bp.route('/api/login', methods=['POST'])
def login():
    return login_user()

@bp.route('/api/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data['status'],
        priority=data.get('priority', 'Medium'),
        due_date=data.get('due_date'),
        user_id=user_id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"msg": "Task created successfully"}), 201

@bp.route('/api/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'due_date': task.due_date,
        'created_at': task.created_at,
        'updated_at': task.updated_at
    } for task in tasks]), 200

@bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"msg": "Task not found"}), 404

    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    task.priority = data.get('priority', task.priority)
    task.due_date = data.get('due_date', task.due_date)

    db.session.commit()
    return jsonify({"msg": "Task updated successfully"}), 200

@bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"msg": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"msg": "Task deleted successfully"}), 200
