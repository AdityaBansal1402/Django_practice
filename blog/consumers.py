import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist

class BlogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            print(self)
            self.blog_id = self.scope['url_route']['kwargs']['blog_id']
            self.room_group_name = f'blog_{self.blog_id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            
            await self.send_initial_state()
            
        except Exception as e:
            print(f"WebSocket connection error: {str(e)}")
            raise DenyConnection()

    @database_sync_to_async
    def get_blog_data(self):
        try:
            from .models import Blog 
            blog = Blog.objects.get(pk=self.blog_id)
            return {
                'type': 'blog_update',
                'title': blog.title,
                'content': blog.content,
                'likes': blog.likes
            }
        except ObjectDoesNotExist:
            return None

    async def send_initial_state(self):
        try:
            blog_data = await self.get_blog_data()
            if blog_data:
                await self.send(text_data=json.dumps(blog_data))
        except Exception as e:
            print(f"Error sending initial state: {str(e)}")

    async def disconnect(self, close_code):
        try:
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Error during disconnect: {str(e)}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'blog_update',
                    'title': text_data_json.get('title', ''),
                    'content': text_data_json.get('content', ''),
                    'likes': text_data_json.get('likes', 0)
                }
            )
        except Exception as e:
            print(f"Error receiving message: {str(e)}")

    async def blog_update(self, event):
        try:
            await self.send(text_data=json.dumps({
                'title': event['title'],
                'content': event['content'],
                'likes': event['likes']
            }))
        except Exception as e:
            print(f"Error sending update: {str(e)}")