import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    """
    Represents a WebSocket consumer for handling chat functionality.

    This consumer is responsible for connecting to a specific chat room,
    receiving and sending messages within the room.

    Attributes:
        room_name (str): The name of the chat room.
        room_group_name (str): The group name for the chat room.

    Methods:
        connect(): Connects to the chat room and adds the consumer to the room group.
        disconnect(close_code): Disconnects from the chat room and removes the consumer from the room group.
        receive(text_data): Receives a message from the WebSocket and sends it to the room group.
        chat_message(event): Receives a message from the room group and sends it to the WebSocket.
    """

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))