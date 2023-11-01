import flask
from flask_socketio import SocketIO
import datetime
from session import Session
from app import app

app = flask.Flask(__name__)
socketio = SocketIO(app)

# Create a list to store active video chat sessions
sessions = []


# Define a function to validate an invite link
def validate_invite_link(link):
    # Check if the link is expired
    if link.created_at + datetime.timedelta(minutes=10) < datetime.datetime.now():
        return False

    # Check if the link is already in use
    for session in sessions:
        if session.invite_link == link:
            return False

    return True


# Define a function to start a new video chat session
def start_video_chat_session(user1, user2):
    # Create a new session object
    session = Session(user1, user2)

    # Add the session to the list of active sessions
    sessions.append(session)

    # Return the session object to the client
    return session


# Define a function to end a video chat session
def end_video_chat_session(session):
    # Remove the session from the list of active sessions
    sessions.remove(session)

    # Send a message to both users notifying them that the session has ended
    socketio.emit('video_chat_ended', None, room=session.room_id)


# Define a function to handle video chat events
def handle_video_chat_event(event_type, data, session):
    # Check the event type
    if event_type == 'video_chat_request':
        # Validate the invite link
        if not validate_invite_link(data['invite_link']):
            return

        # Start a new video chat session
        session = start_video_chat_session(data['sender_id'], data['receiver_id'])

        # Send a message to both users notifying them that the session has started
        socketio.emit('video_chat_started', session.room_id, room=[session.sender_id, session.receiver_id])

    elif event_type == 'video_chat_offer':
        # Send the offer to the other user
        socketio.emit('video_chat_offer', data['offer'], room=session.receiver_id)

    elif event_type == 'video_chat_answer':
        # Send the answer to the other user
        socketio.emit('video_chat_answer', data['answer'], room=session.sender_id)

    elif event_type == 'video_chat_ice_candidate':
        # Send the ICE candidate to the other user
        socketio.emit('video_chat_ice_candidate', data['candidate'], room=session.receiver_id)

    elif event_type == 'video_chat_ended':
        # End the video chat session
        end_video_chat_session(session)


# @app.route('/')
# def index():
#    return "Welcome to the video conferencing app"  # Customize the message as needed


# Start the Socket.IO server
@socketio.on('video_chat_event')
def on_video_chat_event(data):
    # Get the video chat session object
    session = None
    for s in sessions:
        if s.room_id == data['room_id']:
            session = s
            break

    # Handle the video chat event
    handle_video_chat_event(data['event_type'], data, session)


if __name__ == '__main__':
    app.run(debug=True)
