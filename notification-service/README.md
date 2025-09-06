# Notification Service

This service handles real-time notifications using Kafka and WebSockets.

## Features
- Kafka consumer for event processing
- WebSocket connections for real-time notifications
- REST API for notification management
- Integration with other microservices

## Events Consumed
- User registration
- Booking creation/updates
- Service creation/updates
- Payment processing

## API Endpoints
- `GET /api/v1/notifications` - Get user notifications
- `POST /api/v1/notifications` - Create notification
- `WebSocket /ws/{user_id}` - Real-time notifications
