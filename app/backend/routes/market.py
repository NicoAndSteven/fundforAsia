"""Market dashboard API - 市场全景看板数据接口"""
import logging
from datetime import datetime
from fastapi import APIRouter
from src.tools import api_unified

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
