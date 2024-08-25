from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
api = Api(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'mysql://root:root@db/task_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'super-secret-key'

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(50), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

# Resources
class TaskResource(Resource):
    @jwt_required()
    def get(self, task_id):
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if task:
            return jsonify({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date,
                'created_at': task.created_at,
                'updated_at': task.updated_at
            })
        else:
            return {'message': 'Task not found'}, 404

    @jwt_required()
    def put(self, task_id):
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if task:
            data = request.get_json()
            task.title = data.get('title', task.title)
            task.description = data.get('description', task.description)
            task.status = data.get('status', task.status)
            task.priority = data.get('priority', task.priority)
            task.due_date = data.get('due_date', task.due_date)
            db.session.commit()
            return jsonify({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date,
                'created_at': task.created_at,
                'updated_at': task.updated_at
            })
        else:
            return {'message': 'Task not found'}, 404

    @jwt_required()
    def delete(self, task_id):
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            return {'message': 'Task deleted successfully'}, 200
        else:
            return {'message': 'Task not found'}, 404

class TaskListResource(Resource):
    @jwt_required()
    def get(self):
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
        } for task in tasks])

    @jwt_required()
    def post(self):
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
        return jsonify({
            'id': new_task.id,
            'title': new_task.title,
            'description': new_task.description,
            'status': new_task.status,
            'priority': new_task.priority,
            'due_date': new_task.due_date,
            'created_at': new_task.created_at,
            'updated_at': new_task.updated_at
        }), 201

# Add resources to API
api.add_resource(TaskResource, '/api/tasks/<int:task_id>')
api.add_resource(TaskListResource, '/api/tasks')

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
