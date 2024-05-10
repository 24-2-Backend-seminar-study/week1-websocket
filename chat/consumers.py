import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
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

    async def connect(self):
        # 현재 WebSocket이 연결된 채팅방의 이름을 가져옴
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # 채팅방의 그룹 이름을 생성
        self.room_group_name = f"chat_{self.room_name}"

        # 채팅방 그룹에 소비자를 추가하여 연결
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # WebSocket 연결을 수락
        await self.accept()

    async def disconnect(self, close_code):
        # 채팅방 그룹에서 나가기
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # WebSocket으로부터 메시지 받기
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # 채팅방 그룹에 메시지 보내기
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # 채팅방 그룹으로부터 메시지 받기
    async def chat_message(self, event):
        message = event["message"]

        # WebSocket으로 메시지 보내기
        await self.send(text_data=json.dumps({"message": message}))