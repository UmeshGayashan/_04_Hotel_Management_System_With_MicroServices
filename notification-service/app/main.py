from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import notifications
from app.services.kafka_service import kafka_service

app = FastAPI(title="Notification Service", version="1.0.0")

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()] if settings.CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "notification"}

@app.on_event("startup")
async def startup_event():
    """Start Kafka consumer on startup"""
    await kafka_service.start_consumer()

@app.on_event("shutdown")  
async def shutdown_event():
    """Cleanup on shutdown"""
    if kafka_service.consumer:
        kafka_service.consumer.close()
