from fastapi import APIRouter, HTTPException
from typing import List
import jqdatasdk as jq
from datetime import datetime
import pandas as pd
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 初始化 JQData
jq.auth(
    os.getenv('JQDATA_USERNAME'),
    os.getenv('JQDATA_PASSWORD')
)

class StockData(BaseModel):
    date: str
    code: str
    open: float
    close: float
    high: float
    low: float
    volume: float
    money: float

@router.get("/daily")  # 修改路由路径
async def get_stock_daily(code: str, startDate: str, endDate: str):
    try:
        logger.info(f"开始获取股票数据: code={code}, startDate={startDate}, endDate={endDate}")
        
        # 验证 JQData 认证状态
        if not jq.is_auth():
            logger.error("JQData 未认证")
            raise HTTPException(status_code=500, detail="JQData 认证失败")
            
        try:
            df = jq.get_price(
                code,
                start_date=startDate,
                end_date=endDate,
                frequency='daily',
                fields=['open', 'close', 'high', 'low', 'volume', 'money']
            )
        except Exception as jq_error:
            logger.error(f"JQData API 调用失败: {str(jq_error)}")
            raise HTTPException(status_code=500, detail=f"获取数据失败: {str(jq_error)}")
        
        logger.info("数据获取成功，开始处理数据格式")
        
        # 确保数据不为空
        if df.empty:
            return []
            
        # 处理数据格式
        df.reset_index(inplace=True)
        df['date'] = df['index'].dt.strftime('%Y-%m-%d')
        df['code'] = code
        
        # 转换为列表并确保数值类型正确
        result = []
        for _, row in df.iterrows():
            result.append({
                'date': row['date'],
                'code': row['code'],
                'open': float(row['open']),
                'close': float(row['close']),
                'high': float(row['high']),
                'low': float(row['low']),
                'volume': float(row['volume']),
                'money': float(row['money'])
            })
        
        logger.info(f"数据处理完成，返回 {len(result)} 条记录")
        return result
        
    except HTTPException as he:
        logger.error(f"HTTP错误: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@router.get("/minute")
async def get_stock_minute(code: str, startDate: str, endDate: str):
    try:
        logger.info(f"开始获取股票分钟数据: code={code}, startDate={startDate}, endDate={endDate}")
        
        if not jq.is_auth():
            logger.error("JQData 未认证")
            raise HTTPException(status_code=500, detail="JQData 认证失败")
            
        try:
            df = jq.get_price(
                code,
                start_date=startDate,
                end_date=endDate,
                frequency='1m',
                fields=['open', 'close', 'high', 'low', 'volume', 'money']
            )
        except Exception as jq_error:
            logger.error(f"JQData API 调用失败: {str(jq_error)}")
            raise HTTPException(status_code=500, detail=f"获取数据失败: {str(jq_error)}")
        
        if df.empty:
            return []
            
        df.reset_index(inplace=True)
        df['datetime'] = df['index'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df['code'] = code
        
        result = []
        for _, row in df.iterrows():
            result.append({
                'datetime': row['datetime'],
                'code': row['code'],
                'open': float(row['open']),
                'close': float(row['close']),
                'high': float(row['high']),
                'low': float(row['low']),
                'volume': float(row['volume']),
                'money': float(row['money'])
            })
        
        logger.info(f"分钟数据处理完成，返回 {len(result)} 条记录")
        return result
        
    except HTTPException as he:
        logger.error(f"HTTP错误: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

# 添加测试路由
@router.get("/test")
async def test():
    return {"message": "Stock API is working"}