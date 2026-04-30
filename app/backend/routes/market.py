"""Market dashboard API - 市场全景看板数据接口"""
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query
from src.tools import api_unified
from app.backend.services.sector_service import get_etf_for_sector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["market"])

_cache = {}
_cache_time = {}


def _is_cache_valid(key: str, ttl_seconds: int = 300) -> bool:
    if key not in _cache or key not in _cache_time:
        return False
    return (datetime.now() - _cache_time[key]).total_seconds() < ttl_seconds


def _get_cached(key: str):
    return _cache.get(key)


def _set_cache(key: str, data):
    _cache[key] = data
    _cache_time[key] = datetime.now()


@router.get("/dashboard")
async def get_market_dashboard():
    """
    获取A股市场全景看板数据。
    数据源：efinance（东方财富），缓存5分钟。
    """
    cache_key = "dashboard"

    if _is_cache_valid(cache_key):
        return _get_cached(cache_key)

    try:
        data = api_unified.get_market_overview()
        data["note"] = "数据来源于东方财富，每5分钟刷新"
        _set_cache(cache_key, data)
        return data
    except Exception as e:
        logger.error(f"获取市场全景数据失败: {e}", exc_info=True)
        return {
            "indices": [],
            "market_breadth": {},
            "sectors": [],
            "top_gainers": [],
            "top_losers": [],
            "top_volume": [],
            "market_summary": {},
            "limit_up_count": 0,
            "limit_down_count": 0,
            "updated_at": datetime.now().isoformat(),
            "error": str(e),
        }


@router.get("/sectors")
async def get_sectors():
    """获取所有行业/概念板块列表（含代码、名称、涨跌幅）"""
    cache_key = "sectors_list"

    if _is_cache_valid(cache_key, ttl_seconds=300):
        return _get_cached(cache_key)

    try:
        data = api_unified.get_market_overview()
        sectors = data.get("sectors", [])
        # 确保有必要的字段
        result = []
        for s in sectors:
            name = s.get("板块名称", "")
            code = s.get("板块代码", "")
            etf_code = get_etf_for_sector(name)  # 按名称匹配（更稳定）
            result.append({
                "code": code,
                "name": name,
                "change_pct": s.get("涨跌幅"),
                "current": s.get("最新价"),
                "etf_code": etf_code or "",
                "has_etf": etf_code is not None,
            })
        # 按涨跌幅排序（涨幅榜靠前）
        result.sort(key=lambda x: abs(x.get("change_pct") or 0), reverse=True)
        _set_cache(cache_key, result)
        return result
    except Exception as e:
        logger.error(f"获取板块列表失败: {e}", exc_info=True)
        return []


@router.get("/sector/{sector_code}/etf")
async def get_sector_etf(sector_code: str, name: Optional[str] = Query(None)):
    """获取板块对应的ETF代码（按名称匹配优先）。

    Args:
        sector_code: 板块代码，如 BK0420
        name: 板块名称（推荐），如 "半导体概念"，匹配更稳定
    """
    etf_code = get_etf_for_sector(name) if name else None
    if not etf_code:
        # 兜底：从缓存列表按代码查找
        sectors = _get_cached("sectors_list")
        if sectors:
            for s in sectors:
                if s.get("code") == sector_code:
                    etf_code = s.get("etf_code", "")
                    break
    return {
        "sector_code": sector_code,
        "etf_code": etf_code or "",
        "has_etf": bool(etf_code),
    }
