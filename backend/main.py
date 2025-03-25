from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.stock import router as stock_router

app = FastAPI(title="Stock Trader API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stock_router, prefix="/api", tags=["stock"])

# 添加根路由用于测试
@app.get("/")
async def root():
    return {"message": "Stock Trader API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)