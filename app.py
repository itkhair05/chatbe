from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép mọi nguồn truy cập

rooms = {}  # Lưu thông tin phòng và người dùng trong phòng

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    for room_id, users in rooms.items():
        if request.sid in users.values():
            username = [k for k, v in users.items() if v == request.sid][0]
            leave_room(room_id)
            del rooms[room_id][username]
            if not rooms[room_id]:
                del rooms[room_id]
            else:
                emit('user_left', {'username': username}, room=room_id)
            break

@socketio.on('join_room')
def handle_join_room(data):
    username = data['username']
    room_id = data['room_id']
    
    if room_id not in rooms:
        rooms[room_id] = {}
    
    join_room(room_id)
    rooms[room_id][username] = request.sid
    emit('user_joined', {'username': username}, room=room_id)
    # Gửi danh sách người dùng trong phòng
    emit('user_list', {'users': list(rooms[room_id].keys())}, room=room_id)

@socketio.on('message')
def handle_message(data):
    room_id = data['room_id']
    message = {
        'text': data['text'],
        'sender': data['sender'],
        'timestamp': datetime.datetime.now().strftime('%H:%M')
    }
    emit('new_message', message, room=room_id)

@socketio.on('get_rooms')
def handle_get_rooms():
    emit('room_list', {'rooms': list(rooms.keys())})

if __name__ == '__main__':
    # Chạy trên 0.0.0.0 để cho phép truy cập từ mọi IP
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)