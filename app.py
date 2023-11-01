import aiortc
from flask import Flask, render_template
from socketIO_client import SocketIO
import logging

logging.basicConfig(level=logging.DEBUG)

# Create the Flask app object
app = Flask(__name__)

# Connect to the SocketIO server
socket = SocketIO('http://localhost:5000')

# Create the peer connection
peer_connection = aiortc.RTCPeerConnection()

# Create the data channel with a label
data_channel = peer_connection.createDataChannel(label='chat')

# Create the video stream
video_stream = aiortc.VideoStreamTrack(peer_connection)


# Handle video chat events
async def _handle_video_chat_events():
    # ...

    # Render the HTML template
    @app.route('/')
    def index():
        return render_template('index.html', socket=socket, peer_connection=peer_connection, data_channel=data_channel,
                               video_stream=video_stream)


if __name__ == '__main__':
    # Start the Flask app
    app.run(debug=True)
