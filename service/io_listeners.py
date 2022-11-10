from flask_socketio import join_room, leave_room
from main import io

@io.on('addUser')
def add_user(data):
    user_id = data['_id']
    print(f"socket connected from client {user_id}")
    join_room(user_id)
