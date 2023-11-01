import socketIO_client
import aiortc
import asyncio
from app import app


class VideoChatClient:
    def __init__(self, server_url):
        self.socket = socketIO_client.SocketIO(server_url)

        # Create a WebRTC PeerConnection object
        self.peer_connection = aiortc.RTCPeerConnection()

        # Create a WebRTC DataChannel object
        self.data_channel = self.peer_connection.createDataChannel()

        # Create a WebRTC VideoStream object
        self.video_stream = aiortc.VideoStream(self.peer_connection)

        # Create a asyncio task to handle video chat events
        self.video_chat_task = asyncio.create_task(self._handle_video_chat_events())

    async def _handle_video_chat_events(self):
        # Listen for video chat events
        while True:
            event_type, data = await self.socket.recv_async()

            if event_type == 'video_chat_request':
                # Handle a video chat request
                await self.on_video_chat_request(data)

            elif event_type == 'video_chat_offer':
                # Handle a video chat offer
                await self.on_video_chat_offer(data)

            elif event_type == 'video_chat_answer':
                # Handle a video chat answer
                await self.on_video_chat_answer(data)

            elif event_type == 'video_chat_ice_candidate':
                # Handle a video chat ICE candidate
                await self.on_video_chat_ice_candidate(data)

            elif event_type == 'video_chat_ended':
                # Handle the end of a video chat session
                await self.on_video_chat_ended()

    async def on_video_chat_request(self, data):
        # Accept the video chat request
        answer = await self.peer_connection.createAnswer()

        # Send the answer to the sender
        await self.socket.emit('video_chat_answer', answer, room=data['sender_id'])

    async def on_video_chat_offer(self, data):
        # Set the remote description of the PeerConnection
        await self.peer_connection.setRemoteDescription(data['offer'])

        # Create an answer to the offer
        answer = await self.peer_connection.createAnswer()

        # Send the answer to the sender
        await self.socket.emit('video_chat_answer', answer, room=data['sender_id'])

    async def on_video_chat_answer(self, data):
        # Set the remote description of the PeerConnection
        await self.peer_connection.setRemoteDescription(data['answer'])

    async def on_video_chat_ice_candidate(self, data):
        # Add the ICE candidate to the PeerConnection
        await self.peer_connection.addIceCandidate(data['candidate'])

    async def on_video_chat_ended(self):
        # Close the PeerConnection
        await self.peer_connection.close()

        # Cancel the video chat task
        self.video_chat_task.cancel()

    async def start(self, server_url):
        try:
            # Connect to the Socket.IO server
            await self.socket.connect()

            if not self.socket.connected:
                print('Failed to connect to Socket.IO server.')
                return

            # Start the video chat task
            await self.video_chat_task

            # Start receiving video frames
            await self.video_stream.start()

            # Keep receiving video frames until the video chat session is ended
            while True:
                video_frame = await self.video_stream.read_frame()

                # Send the video frame to the other user
                await self.data_channel.send(video_frame)

        finally:
            # Close the video stream
            await self.video_stream.stop()

            # Wait for the video chat task to complete
            await self.video_chat_task

            # Disconnect from the Socket.IO server
            await self.socket.disconnect()


if __name__ == '__main__':
    server_url = 'http://localhost:5000'

    client = VideoChatClient
    await client.start(server_url)
