from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Vercel Cron CSV Export API",
    description="15分間隔で来店客数データをCSV形式でFTP送信するAPI",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Vercel Cron CSV Export API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "csv-export-api"}