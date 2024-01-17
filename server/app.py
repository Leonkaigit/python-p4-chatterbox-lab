from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([message.serialize() for message in messages])

    elif request.method == 'POST':
        
        data = request.get_json()
        body = data.get('body')
        username = data.get('username')

        if body and username:
            new_message = Message(body=body, username=username)
            db.session.add(new_message)
            db.session.commit()

            response = make_response(jsonify(new_message.serialize()), 201)
            response.headers['Location'] = f'/messages/{new_message.id}'
            return response
        else:
            return make_response(jsonify({'error': 'Invalid data provided'}), 400)

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def update_message(id):
    message = Message.query.get(id)

    if message is None:
        return make_response(jsonify({'error': 'Message not found'}), 404)

    if request.method == 'PATCH':
        
        data = request.get_json()
        new_body = data.get('body')

        if new_body is not None:
            message.body = new_body
            db.session.commit()

            return jsonify(message.serialize())
        else:
            return make_response(jsonify({'error': 'Invalid data provided'}), 400)

    elif request.method == 'DELETE':
        
        db.session.delete(message)
        db.session.commit()

        return make_response(jsonify({'message': 'Message deleted successfully'}), 200)

if __name__ == '__main__':
    app.run(port=5555)
