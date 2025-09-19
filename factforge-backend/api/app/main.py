"""
FactForge Backend API
"""
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

from .core.db import init_db, get_redis
from .core.audit import create_audit_entry
from .routes import check, posts, review, admin
from .websocket import websocket_service

# Global variables for services
redis_client = None
milvus_client = None
ollama_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global redis_client, milvus_client, ollama_client
    
    # Startup
    print("🚀 Starting FactForge Backend...")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Initialize Redis
    redis_client = get_redis()
    print("✅ Redis connected")
    
    # Initialize Milvus (vector database)
    try:
        from pymilvus import connections, Collection
        connections.connect(
            host=os.getenv("MILVUS_HOST", "localhost"),
            port=os.getenv("MILVUS_PORT", "19530")
        )
        milvus_client = Collection("factforge_vectors")
        print("✅ Milvus connected")
    except Exception as e:
        print(f"⚠️ Milvus connection failed: {e}")
        milvus_client = None
    
    # Initialize Ollama
    try:
        import requests
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            ollama_client = ollama_url
            print("✅ Ollama connected")
        else:
            print("⚠️ Ollama not available")
            ollama_client = None
    except Exception as e:
        print(f"⚠️ Ollama connection failed: {e}")
        ollama_client = None
    
    print("🎉 FactForge Backend started successfully!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down FactForge Backend...")

# Create FastAPI app
app = FastAPI(
    title="FactForge API",
    description="Multilingual fact-checking and misinformation detection API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Add Prometheus metrics
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Include routers
app.include_router(check.router, prefix="/api", tags=["check"])
app.include_router(posts.router, prefix="/api", tags=["posts"])
app.include_router(review.router, prefix="/api", tags=["review"])
app.include_router(admin.router, prefix="/api", tags=["admin"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FactForge API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": time.time()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "database": "unknown",
            "redis": "unknown",
            "milvus": "unknown",
            "ollama": "unknown"
        }
    }
    
    # Check database
    try:
        from .core.db import get_db_session
        with get_db_session() as db:
            db.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
    
    # Check Milvus
    try:
        if milvus_client:
            milvus_client.query(expr="id > 0", limit=1)
            health_status["services"]["milvus"] = "healthy"
        else:
            health_status["services"]["milvus"] = "not_configured"
    except Exception as e:
        health_status["services"]["milvus"] = f"unhealthy: {str(e)}"
    
    # Check Ollama
    try:
        if ollama_client:
            import requests
            response = requests.get(f"{ollama_client}/api/tags", timeout=5)
            if response.status_code == 200:
                health_status["services"]["ollama"] = "healthy"
            else:
                health_status["services"]["ollama"] = "unhealthy"
        else:
            health_status["services"]["ollama"] = "not_configured"
    except Exception as e:
        health_status["services"]["ollama"] = f"unhealthy: {str(e)}"
    
    # Overall status
    unhealthy_services = [k for k, v in health_status["services"].items() 
                         if not v.startswith("healthy") and v != "not_configured"]
    
    if unhealthy_services:
        health_status["status"] = "degraded"
        health_status["unhealthy_services"] = unhealthy_services
    
    return health_status

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket, user_id: str = None, role: str = "user"):
    """WebSocket endpoint for real-time events"""
    await websocket_service.handle_connection(websocket, user_id, role)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    # Log the error
    print(f"Unhandled exception: {exc}")
    
    # Create audit entry
    try:
        create_audit_entry("error", {
            "error": str(exc),
            "path": str(request.url),
            "method": request.method
        })
    except Exception:
        pass  # Don't fail if audit logging fails
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": time.time()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
