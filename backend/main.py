from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.stock import router as stock_router
from api.strategy import router as strategy_router  # 添加这行
import uvicorn  # 添加这行导入

app = FastAPI(title="Stock Trader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.0.89:3000",
        "http://localhost:3000",
        "*"  # 开发阶段可以允许所有源
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 修改回原来的前缀
app.include_router(stock_router, prefix="/api/stock")
app.include_router(strategy_router, prefix="/api/strategy")  # 添加这行


# 修改 uvicorn 启动配置
if __name__ == "__main__":
    uvicorn.run(
        app,            # 直接使用 app 实例
        host="0.0.0.0", # 修改这里，使用 0.0.0.0 允许所有网络接口访问
        port=8000,
        reload=True
    )