import uuid


class Session:
    def __init__(self, user1, user2):
        # Generate a unique room ID for the session
        self.room_id = str(uuid.uuid4())

        # Store the user IDs of the participants
        self.sender_id = user1
        self.receiver_id = user2

        # You can add more attributes to the session as needed
        # For example, you might want to store the creation timestamp or other session-related data.

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            # Include other session attributes here
        }
