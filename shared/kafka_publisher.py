import json
from kafka import KafkaProducer
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(self, bootstrap_servers: str = "kafka:9092"):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[bootstrap_servers],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Failed to create Kafka producer: {e}")
            self.producer = None
    
    def publish_user_event(self, user_data: Dict[str, Any]):
        """Publish user registration event"""
        if self.producer:
            try:
                event = {
                    "user_id": user_data.get("id"),
                    "email": user_data.get("email"),
                    "full_name": user_data.get("full_name"),
                    "action": "registered",
                    "timestamp": user_data.get("created_at")
                }
                self.producer.send("user_events", event)
                logger.info(f"Published user event: {event}")
            except Exception as e:
                logger.error(f"Failed to publish user event: {e}")
    
    def publish_booking_event(self, booking_data: Dict[str, Any], action: str = "created"):
        """Publish booking event"""
        if self.producer:
            try:
                event = {
                    "user_id": booking_data.get("user_id"),
                    "booking_id": booking_data.get("id"),
                    "service_id": booking_data.get("service_id"),
                    "service_name": booking_data.get("service_name"),
                    "action": action,
                    "timestamp": booking_data.get("created_at")
                }
                self.producer.send("booking_events", event)
                logger.info(f"Published booking event: {event}")
            except Exception as e:
                logger.error(f"Failed to publish booking event: {e}")
    
    def publish_service_event(self, service_data: Dict[str, Any], action: str = "created"):
        """Publish service event"""
        if self.producer:
            try:
                event = {
                    "service_id": service_data.get("id"),
                    "name": service_data.get("name"),
                    "description": service_data.get("description"),
                    "price": service_data.get("price"),
                    "action": action,
                    "timestamp": service_data.get("created_at")
                }
                self.producer.send("service_events", event)
                logger.info(f"Published service event: {event}")
            except Exception as e:
                logger.error(f"Failed to publish service event: {e}")
    
    def publish_payment_event(self, payment_data: Dict[str, Any]):
        """Publish payment event"""
        if self.producer:
            try:
                event = {
                    "user_id": payment_data.get("user_id"),
                    "payment_id": payment_data.get("id"),
                    "booking_id": payment_data.get("booking_id"),
                    "amount": payment_data.get("amount"),
                    "status": payment_data.get("status"),
                    "action": "processed",
                    "timestamp": payment_data.get("created_at")
                }
                self.producer.send("payment_events", event)
                logger.info(f"Published payment event: {event}")
            except Exception as e:
                logger.error(f"Failed to publish payment event: {e}")
    
    def close(self):
        """Close the producer"""
        if self.producer:
            self.producer.close()

# Global instance
event_publisher = EventPublisher()
