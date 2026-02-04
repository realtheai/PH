"""
FastAPI Backend Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import analyze, stats

app = FastAPI(
    title="Phishingapp API",
    description="피싱 메시지 분석 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(analyze.router, prefix="/api/v1", tags=["analyze"])
app.include_router(stats.router, prefix="/api/v1", tags=["stats"])

@app.get("/")
async def root():
    return {
        "message": "Phishingapp API", 
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "analyze": "/api/v1/analyze",
            "stats": "/api/v1/stats"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
