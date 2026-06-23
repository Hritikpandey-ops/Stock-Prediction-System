from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.data_ingestion.scheduler import DataIngestionScheduler
from config.settings import get_settings

app = FastAPI(title="Stock Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

settings = get_settings()

@app.on_event("startup")
def startup_event():
    """Run complete data ingestion when API starts"""
    scheduler = DataIngestionScheduler()
    symbols = settings.nifty50_symbols
    
    # Run full data ingestion pipeline
    scheduler.full_ingestion(symbols, include_news=True)
    
    # Also fetch today's price data for up-to-date market data
    scheduler.fetch_and_store_prices_for_today(symbols)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "stock-prediction-api"}