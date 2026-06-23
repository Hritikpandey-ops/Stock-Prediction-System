docker compose up -d db
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
cd Frontend && npm run dev