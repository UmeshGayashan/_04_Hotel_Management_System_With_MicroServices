import json
import asyncio
from kafka import KafkaConsumer
from typing import Dict, Any
from app.core.config import settings
from app.services.notification_service import NotificationService
from app.services.websocket_manager import WebSocketManager

class KafkaService:
    def __init__(self):
        self.consumer = None
        self.notification_service = NotificationService()
        self.websocket_manager = WebSocketManager()
        
    async def start_consumer(self):
        """Start Kafka consumer in a separate thread"""
        try:
            self.consumer = KafkaConsumer(
                *settings.KAFKA_TOPICS.values(),
                bootstrap_servers=[settings.KAFKA_BOOTSTRAP_SERVERS],
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                group_id='notification_service'
            )
            
            # Run consumer in background task
            asyncio.create_task(self._consume_messages())
            
        except Exception as e:
            print(f"Error starting Kafka consumer: {e}")
    
    async def _consume_messages(self):
        """Consume messages from Kafka"""
        try:
            for message in self.consumer:
                await self._process_message(message.topic, message.value)
        except Exception as e:
            print(f"Error consuming messages: {e}")
    
    async def _process_message(self, topic: str, data: Dict[str, Any]):
        """Process incoming Kafka message"""
        try:
            notification_data = await self._create_notification_from_event(topic, data)
            
            if notification_data:
                # Save notification to database
                notification = await self.notification_service.create_notification(notification_data)
                
                # Send real-time notification via WebSocket
                await self.websocket_manager.send_notification(
                    notification.user_id, 
                    notification
                )
                
        except Exception as e:
            print(f"Error processing message from topic {topic}: {e}")
    
    async def _create_notification_from_event(self, topic: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create notification data based on event type"""
        
        if topic == settings.KAFKA_TOPICS["user_events"]:
            return {
                "user_id": data.get("user_id"),
                "title": "Welcome!",
                "message": f"Welcome {data.get('full_name', 'User')}! Your account has been created successfully.",
                "type": "user"
            }
            
        elif topic == settings.KAFKA_TOPICS["booking_events"]:
            action = data.get("action", "created")
            if action == "created":
                return {
                    "user_id": data.get("user_id"),
                    "title": "Booking Confirmed",
                    "message": f"Your booking for {data.get('service_name', 'service')} has been confirmed.",
                    "type": "booking"
                }
            elif action == "updated":
                return {
                    "user_id": data.get("user_id"),
                    "title": "Booking Updated",
                    "message": f"Your booking has been updated.",
                    "type": "booking"
                }
                
        elif topic == settings.KAFKA_TOPICS["service_events"]:
            action = data.get("action", "created")
            if action == "created":
                return {
                    "user_id": data.get("user_id", 1),  # Broadcast to admin or all users
                    "title": "New Service Available",
                    "message": f"New service '{data.get('name', 'Service')}' is now available!",
                    "type": "service"
                }
                
        elif topic == settings.KAFKA_TOPICS["payment_events"]:
            return {
                "user_id": data.get("user_id"),
                "title": "Payment Processed",
                "message": f"Your payment of ${data.get('amount', '0.00')} has been processed successfully.",
                "type": "payment"
            }
        
        return None

kafka_service = KafkaService()
