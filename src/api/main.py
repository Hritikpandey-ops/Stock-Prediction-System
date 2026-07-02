import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.data_ingestion.scheduler import DataIngestionScheduler
from config.settings import get_settings
from config.database import test_connection


def _run_background_ingestion(symbols):
    """Run data ingestion in background thread (non-blocking)."""
    try:
        scheduler = DataIngestionScheduler()
        scheduler.full_ingestion(symbols, include_news=True)
        scheduler.fetch_and_store_prices_for_today(symbols)
    except Exception as e:
        from loguru import logger
        logger.error(f"Background ingestion failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    settings = get_settings()
    
    # Test database connection on startup
    if not test_connection():
        from loguru import logger
        logger.warning("Database connection failed on startup - API will serve cached data only")
    
    # Run data ingestion in background thread (non-blocking)
    symbols = settings.nifty50_symbols
    ingestion_thread = threading.Thread(
        target=_run_background_ingestion,
        args=(symbols,),
        daemon=True
    )
    ingestion_thread.start()
    
    yield


app = FastAPI(
    title="Stock Prediction API",
    version="1.0.0",
    description="Nifty 50 stock analysis with technical indicators, fundamentals, and news sentiment",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/api/health")
def health():
    """Basic health check endpoint."""
    db_ok = test_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "stock-prediction-api",
        "database": "connected" if db_ok else "disconnected",
    }
