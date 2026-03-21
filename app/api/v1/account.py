from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# ===== 持仓数据模型 =====
class Position(BaseModel):
    ts_code: str          # 股票代码，如 "000001.SZ"
    symbol: str           # 股票名称
    shares: int           # 持仓数量
    avg_cost: float       # 平均成本
    current_price: Optional[float] = None  # 当前价格
    market_value: Optional[float] = None   # 市值
    profit_loss: Optional[float] = None    # 盈亏金额
    profit_rate: Optional[float] = None      # 盈亏比例
    update_time: Optional[str] = None        # 更新时间


class PositionCreate(BaseModel):
    ts_code: str
    symbol: str
    shares: int
    avg_cost: float


class PositionUpdate(BaseModel):
    shares: Optional[int] = None
    avg_cost: Optional[float] = None
    current_price: Optional[float] = None


# ===== MOCK 内存存储 =====
MOCK_HOLDINGS: List[dict] = [
    {
        "ts_code": "000001.SZ",
        "symbol": "平安银行",
        "shares": 1000,
        "avg_cost": 12.50,
        "current_price": 13.20,
        "market_value": 13200.00,
        "profit_loss": 700.00,
        "profit_rate": 5.60,
        "update_time": "2026-03-21 10:00:00"
    },
    {
        "ts_code": "600519.SH",
        "symbol": "贵州茅台",
        "shares": 100,
        "avg_cost": 1650.00,
        "current_price": 1720.00,
        "market_value": 172000.00,
        "profit_loss": 7000.00,
        "profit_rate": 4.24,
        "update_time": "2026-03-21 10:00:00"
    }
]


# ===== 辅助函数 =====
def calculate_profit_loss(shares: int, avg_cost: float, current_price: float) -> dict:
    """计算盈亏"""
    market_value = shares * current_price
    cost = shares * avg_cost
    profit_loss = market_value - cost
    profit_rate = (profit_loss / cost * 100) if cost > 0 else 0
    return {
        "market_value": round(market_value, 2),
        "profit_loss": round(profit_loss, 2),
        "profit_rate": round(profit_rate, 2)
    }


def find_position(ts_code: str) -> Optional[dict]:
    """根据股票代码查找持仓"""
    for pos in MOCK_HOLDINGS:
        if pos["ts_code"] == ts_code:
            return pos
    return None


def find_position_index(ts_code: str) -> Optional[int]:
    """根据股票代码查找持仓索引"""
    for i, pos in enumerate(MOCK_HOLDINGS):
        if pos["ts_code"] == ts_code:
            return i
    return None


# ===== API 端点 =====

@router.get("/positions", response_model=List[dict])
async def get_positions():
    """查询所有持仓"""
    return MOCK_HOLDINGS


@router.post("/positions", response_model=dict)
async def create_position(position: PositionCreate):
    """新增持仓"""
    # 检查是否已存在
    if find_position(position.ts_code):
        raise HTTPException(
            status_code=400,
            detail=f"股票 {position.ts_code} 已存在，请使用 PUT 更新"
        )
    
    # 计算市值和盈亏
    current_price = position.avg_cost  # 初始默认成本价
    pl = calculate_profit_loss(position.shares, position.avg_cost, current_price)
    
    new_position = {
        "ts_code": position.ts_code,
        "symbol": position.symbol,
        "shares": position.shares,
        "avg_cost": position.avg_cost,
        "current_price": current_price,
        **pl,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    MOCK_HOLDINGS.append(new_position)
    return {
        "status": "success",
        "message": "持仓添加成功",
        "data": new_position
    }


@router.put("/positions/{ts_code}", response_model=dict)
async def update_position(ts_code: str, position: PositionUpdate):
    """修改持仓"""
    index = find_position_index(ts_code)
    if index is None:
        raise HTTPException(status_code=404, detail=f"股票 {ts_code} 不存在")
    
    pos = MOCK_HOLDINGS[index]
    
    # 更新字段
    if position.shares is not None:
        pos["shares"] = position.shares
    if position.avg_cost is not None:
        pos["avg_cost"] = position.avg_cost
    if position.current_price is not None:
        pos["current_price"] = position.current_price
    
    # 重新计算盈亏
    current_price = pos.get("current_price", pos["avg_cost"])
    pl = calculate_profit_loss(pos["shares"], pos["avg_cost"], current_price)
    pos.update(pl)
    pos["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "status": "success",
        "message": "持仓更新成功",
        "data": pos
    }


@router.delete("/positions/{ts_code}", response_model=dict)
async def delete_position(ts_code: str):
    """删除持仓"""
    index = find_position_index(ts_code)
    if index is None:
        raise HTTPException(status_code=404, detail=f"股票 {ts_code} 不存在")
    
    deleted = MOCK_HOLDINGS.pop(index)
    return {
        "status": "success",
        "message": f"股票 {ts_code} 已删除",
        "data": deleted
    }
