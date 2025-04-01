from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
import jqdatasdk as jq
from datetime import datetime
import pandas as pd

router = APIRouter()

class StrategyParams(BaseModel):
    code: str
    startDate: str
    endDate: str
    strategy: str
    params: Dict[str, Any]

@router.post("/simulate")
async def simulate_strategy(params: StrategyParams):
    try:
        # 验证必要参数
        required_params = {
            'xue_strategy': ['initialQuantity', 'minHolding', 'maxHolding', 'tradeQuantity', 'downThreshold', 'upThreshold'],
            'yu_strategy_1': ['tradeQuantity', 'maxHolding', 'minHoldingForSell', 'downThreshold', 'upThreshold']
        }
        
        if params.strategy not in required_params:
            raise HTTPException(status_code=400, detail="不支持的策略类型")
            
        # 检查必要参数是否都存在
        missing_params = [p for p in required_params[params.strategy] if p not in params.params]
        if missing_params:
            raise HTTPException(status_code=400, detail=f"缺少必要参数: {', '.join(missing_params)}")
        
        # 获取股票数据
        # 获取分钟级股票数据
        df = jq.get_price(
            params.code,
            start_date=params.startDate,
            end_date=params.endDate,
            frequency='1m',  # 改为1分钟级数据
            fields=['open', 'close', 'high', 'low', 'volume', 'money'],
            skip_paused=True
        )
        
        if df.empty:
            raise HTTPException(status_code=400, detail="未获取到股票数据")
        
        # 根据策略类型执行不同的模拟逻辑
        if params.strategy == 'xue_strategy':
            return simulate_xue_strategy(df, params.params)
        elif params.strategy == 'yu_strategy_1':
            return simulate_yu_strategy(df, params.params)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def aggregate_daily_results(results: List[Dict], df: pd.DataFrame, initial_quantity: int) -> List[Dict]:
    """
    将分钟级的交易结果聚合为日级别数据
    
    Args:
        results: 分钟级交易记录列表
        df: 原始股票数据
        initial_quantity: 初始建仓数量
    
    Returns:
        List[Dict]: 按天聚合后的交易记录
    """
    daily_aggregated = {}
    
    # 添加初始建仓日的信息（前一天）
    initial_date = (pd.to_datetime(results[0]['date']) - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    initial_price = df.iloc[0]['open']
    daily_aggregated[initial_date] = {
        'date': initial_date,
        'holdingQuantity': initial_quantity,
        'holdingAvgPrice': initial_price,
        'buyQuantity': initial_quantity,
        'buyPrice': initial_price,
        'sellQuantity': 0,
        'sellPrice': 0,
        'totalCost': initial_quantity * initial_price,
        'totalValue': initial_quantity * initial_price,
        'closePrice': initial_price
    }
    
    # 获取每日收盘价数据
    daily_close_prices = {}
    for index, row in df.iterrows():
        day = index.strftime('%Y-%m-%d')
        daily_close_prices[day] = float(row['close'])
    
    # 处理其他交易日数据
    for record in results:
        day = record['date'][:10]
        
        if day not in daily_aggregated:
            daily_aggregated[day] = {
                'date': day,
                'holdingQuantity': record['holdingQuantity'],
                'holdingAvgPrice': record['holdingAvgPrice'],
                'buyQuantity': 0,
                'buyPrice': 0,
                'sellQuantity': 0,
                'sellPrice': 0,
                'totalCost': record['totalCost'],
                'totalValue': record['totalValue'],
                'closePrice': daily_close_prices.get(day, 0)
            }
        
        # 更新当天的最后状态
        daily_aggregated[day].update({
            'holdingQuantity': record['holdingQuantity'],
            'holdingAvgPrice': record['holdingAvgPrice'],
            'totalCost': record['totalCost'],
            'totalValue': record['totalValue'],
            'closePrice': daily_close_prices.get(day, 0)
        })
        
        # 累计当天的买入卖出记录
        if record['buyQuantity'] > 0:
            daily_aggregated[day]['buyQuantity'] = record['buyQuantity']
            daily_aggregated[day]['buyPrice'] = record['buyPrice']
        if record['sellQuantity'] > 0:
            daily_aggregated[day]['sellQuantity'] = record['sellQuantity']
            daily_aggregated[day]['sellPrice'] = record['sellPrice']
    
    # 转换为列表并按日期排序
    aggregated_results = list(daily_aggregated.values())
    aggregated_results.sort(key=lambda x: x['date'])
    
    return aggregated_results

def simulate_xue_strategy(df: pd.DataFrame, params: Dict[str, Any]) -> List[Dict]:
    results = []
    holding_quantity = params.get('initialQuantity', 100000)
    holding_cost = holding_quantity * df.iloc[0]['open']
    today_bought_quantity = 0  # 记录当天买入的数量
    current_day = None  # 记录当前交易日
    
    min_holding = params.get('minHolding', 100000)
    max_holding = params.get('maxHolding', 120000)
    trade_quantity = params.get('tradeQuantity', 20000)
    down_threshold = params.get('downThreshold', 0.95)
    up_threshold = params.get('upThreshold', 1.05)
    
    for index, row in df.iterrows():
        date = index.strftime('%Y-%m-%d %H:%M')
        day = index.strftime('%Y-%m-%d')
        
        # 新的交易日，重置当天买入数量
        if day != current_day:
            current_day = day
            today_bought_quantity = 0
            
        current_price = float(row['close'])
        volume = float(row['volume'])
        
        daily_result = {
            'date': date,
            'holdingQuantity': holding_quantity,
            'holdingAvgPrice': holding_cost / holding_quantity if holding_quantity > 0 else 0,
            'buyQuantity': 0,
            'buyPrice': 0,
            'sellQuantity': 0,
            'sellPrice': 0,
            'totalCost': holding_cost,
            'totalValue': holding_quantity * current_price
        }
        
        # 先判断卖出条件（可卖出数量 = 总持仓 - 当天买入数量 - 最小持仓）
        sellable_quantity = holding_quantity - today_bought_quantity - min_holding
        if sellable_quantity > 0:
            avg_price = holding_cost / holding_quantity
            if current_price >= avg_price * up_threshold:
                sell_quantity = min(trade_quantity, sellable_quantity, volume)
                if sell_quantity > 0:
                    daily_result['sellQuantity'] = sell_quantity
                    daily_result['sellPrice'] = current_price
                    holding_quantity -= sell_quantity
                    holding_cost = holding_cost * (holding_quantity / (holding_quantity + sell_quantity))
        
        # 判断买入条件
        if holding_quantity < max_holding:
            avg_price = holding_cost / holding_quantity if holding_quantity > 0 else current_price
            if current_price <= avg_price * down_threshold:
                buy_quantity = min(trade_quantity, max_holding - holding_quantity, volume)
                if buy_quantity > 0:
                    daily_result['buyQuantity'] = buy_quantity
                    daily_result['buyPrice'] = current_price
                    holding_cost += buy_quantity * current_price
                    holding_quantity += buy_quantity
                    today_bought_quantity += buy_quantity  # 记录当天买入数量
        
        # 更新结果
        daily_result['holdingQuantity'] = holding_quantity
        daily_result['holdingAvgPrice'] = holding_cost / holding_quantity if holding_quantity > 0 else 0
        daily_result['totalCost'] = holding_cost
        daily_result['totalValue'] = holding_quantity * current_price
        
        results.append(daily_result)
    
    # 使用通用的聚合函数
    return aggregate_daily_results(results, df, params.get('initialQuantity', 100000))

def simulate_yu_strategy(df: pd.DataFrame, params: Dict[str, Any]) -> List[Dict]:
    results = []
    holding_quantity = 0
    holding_cost = 0
    last_buy_date = None
    
    trade_quantity = params.get('tradeQuantity', 20000)
    max_holding = params.get('maxHolding', 120000)
    min_holding_for_sell = params.get('minHoldingForSell', 20000)
    down_threshold = params.get('downThreshold', 0.95)
    up_threshold = params.get('upThreshold', 1.05)
    
    for index, row in df.iterrows():
        date = index.strftime('%Y-%m-%d')
        open_price = float(row['open'])
        high_price = float(row['high'])
        low_price = float(row['low'])
        close_price = float(row['close'])
        
        daily_result = {
            'date': date,
            'holdingQuantity': holding_quantity,
            'holdingAvgPrice': holding_cost / holding_quantity if holding_quantity > 0 else 0,
            'buyQuantity': 0,
            'buyPrice': 0,
            'sellQuantity': 0,
            'sellPrice': 0,
            'totalCost': holding_cost,
            'totalValue': holding_quantity * close_price
        }
        
        # 买入条件：当日最低价低于开盘价指定百分比
        if holding_quantity < max_holding and low_price <= open_price * down_threshold:
            buy_quantity = min(trade_quantity, max_holding - holding_quantity)
            daily_result['buyQuantity'] = buy_quantity
            daily_result['buyPrice'] = low_price
            holding_cost += buy_quantity * low_price
            holding_quantity += buy_quantity
            last_buy_date = date
        
        # 卖出条件：当日最高价高于持仓均价指定百分比，且不是买入当天
        if (holding_quantity >= min_holding_for_sell and 
            high_price >= (holding_cost / holding_quantity) * up_threshold and
            date != last_buy_date):
            sell_quantity = min(trade_quantity, holding_quantity)
            daily_result['sellQuantity'] = sell_quantity
            daily_result['sellPrice'] = high_price
            holding_quantity -= sell_quantity
            holding_cost = holding_cost * (holding_quantity / (holding_quantity + sell_quantity))
        
        # 更新每日结果
        daily_result['holdingQuantity'] = holding_quantity
        daily_result['holdingAvgPrice'] = holding_cost / holding_quantity if holding_quantity > 0 else 0
        daily_result['totalCost'] = holding_cost
        daily_result['totalValue'] = holding_quantity * close_price
        
        results.append(daily_result)
    
    # 使用通用的聚合函数
    return aggregate_daily_results(results, df, 0)  # yu策略初始持仓为0