##--step 1
cd /Users/innovitegrasolutions/Desktop/personal\ project\ document/Stock-Prediction-System
docker compose up -d db

##--step 2
# Create virtual environment (first time only)
python3 -m venv venv
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the API server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

##--step 3
cd frontend
npm install   # first time only
npm run dev

###--step 4
tail -f logs/api.log