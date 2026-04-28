import math
from langchain_core.messages import HumanMessage
from src.graph.state import AgentState, show_agent_reasoning
from src.utils.api_key import get_api_key_from_state
import json
import pandas as pd
import numpy as np
from src.tools.api_unified import get_prices, prices_to_df
from src.utils.progress import progress


def safe_float(value, default=0.0):
    """安全转换为float类型"""
    try:
        if pd.isna(value) or np.isnan(value):
            return default
        return float(value)
    except (ValueError, TypeError, OverflowError):
        return default


def calculate_limit_price(close: float, pct_limit: float) -> tuple:
    """
    计算涨跌停价格（A股特有）
    
    Args:
        close: 前一日收盘价
        pct_limit: 涨跌停幅度（0.10表示10%，0.20表示20%）
        
    Returns:
        (涨停价, 跌停价)
    """
    limit_up = round(close * (1 + pct_limit), 2)
    limit_down = round(close * (1 - pct_limit), 2)
    return limit_up, limit_down


def get_limit_pct(ticker: str) -> float:
    """
    根据股票代码获取涨跌停幅度
    
    Args:
        ticker: 股票代码
        
    Returns:
        涨跌停幅度（0.05, 0.10, 0.20）
    """
    ticker = ticker.upper()
    
    if 'ST' in ticker or 'st' in ticker:
        return 0.05
    elif ticker.startswith('68') or ticker.startswith('300'):
        return 0.20
    else:
        return 0.10


def check_limit_status(prices_df: pd.DataFrame, ticker: str) -> dict:
    """
    检查涨跌停状态（A股特有）
    
    Args:
        prices_df: 价格数据DataFrame
        ticker: 股票代码
        
    Returns:
        涨跌停状态字典
    """
    if len(prices_df) < 2:
        return {"is_limit_up": False, "is_limit_down": False}
    
    last_close = prices_df['close'].iloc[-1]
    prev_close = prices_df['close'].iloc[-2]
    
    pct_limit = get_limit_pct(ticker)
    limit_up, limit_down = calculate_limit_price(prev_close, pct_limit)
    
    is_limit_up = abs(last_close - limit_up) < 0.01
    is_limit_down = abs(last_close - limit_down) < 0.01
    
    return {
        "is_limit_up": is_limit_up,
        "is_limit_down": is_limit_down,
        "limit_up_price": limit_up,
        "limit_down_price": limit_down,
        "pct_limit": pct_limit
    }


def technical_analyst_agent_china(state: AgentState, agent_id: str = "technical_analyst_agent"):
    """
    A股技术分析Agent，考虑涨跌停板影响
    
    分析系统结合多种交易策略：
    1. 趋势跟踪
    2. 均值回归
    3. 动量分析
    4. 波动率分析
    5. 涨跌停板分析（A股特有）
    """
    data = state["data"]
    start_date = data["start_date"]
    end_date = data["end_date"]
    tickers = data["tickers"]
    api_key = get_api_key_from_state(state, "FINANCIAL_DATASETS_API_KEY")
    
    technical_analysis = {}
    
    for ticker in tickers:
        progress.update_status(agent_id, ticker, "分析价格数据")
        
        prices = get_prices(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            api_key=api_key,
        )
        
        if not prices:
            progress.update_status(agent_id, ticker, "失败: 未找到价格数据")
            continue
        
        prices_df = prices_to_df(prices)
        
        progress.update_status(agent_id, ticker, "检查涨跌停状态")
        limit_status = check_limit_status(prices_df, ticker)
        
        progress.update_status(agent_id, ticker, "计算趋势信号")
        trend_signals = calculate_trend_signals(prices_df)
        
        progress.update_status(agent_id, ticker, "计算均值回归")
        mean_reversion_signals = calculate_mean_reversion_signals(prices_df)
        
        progress.update_status(agent_id, ticker, "计算动量")
        momentum_signals = calculate_momentum_signals(prices_df)
        
        progress.update_status(agent_id, ticker, "分析波动率")
        volatility_signals = calculate_volatility_signals(prices_df)
        
        progress.update_status(agent_id, ticker, "分析涨跌停板")
        limit_signals = calculate_limit_signals(prices_df, ticker, limit_status)
        
        strategy_weights = {
            "trend": 0.25,
            "mean_reversion": 0.20,
            "momentum": 0.25,
            "volatility": 0.15,
            "limit_analysis": 0.15,
        }
        
        progress.update_status(agent_id, ticker, "组合信号")
        combined_signal = weighted_signal_combination(
            {
                "trend": trend_signals,
                "mean_reversion": mean_reversion_signals,
                "momentum": momentum_signals,
                "volatility": volatility_signals,
                "limit_analysis": limit_signals,
            },
            strategy_weights,
        )
        
        technical_analysis[ticker] = {
            "signal": combined_signal["signal"],
            "confidence": round(combined_signal["confidence"] * 100),
            "reasoning": {
                "trend_following": {
                    "signal": trend_signals["signal"],
                    "confidence": round(trend_signals["confidence"] * 100),
                    "metrics": normalize_pandas(trend_signals["metrics"]),
                },
                "mean_reversion": {
                    "signal": mean_reversion_signals["signal"],
                    "confidence": round(mean_reversion_signals["confidence"] * 100),
                    "metrics": normalize_pandas(mean_reversion_signals["metrics"]),
                },
                "momentum": {
                    "signal": momentum_signals["signal"],
                    "confidence": round(momentum_signals["confidence"] * 100),
                    "metrics": normalize_pandas(momentum_signals["metrics"]),
                },
                "volatility": {
                    "signal": volatility_signals["signal"],
                    "confidence": round(volatility_signals["confidence"] * 100),
                    "metrics": normalize_pandas(volatility_signals["metrics"]),
                },
                "limit_analysis": {
                    "signal": limit_signals["signal"],
                    "confidence": round(limit_signals["confidence"] * 100),
                    "metrics": normalize_pandas(limit_signals["metrics"]),
                },
            },
        }
        progress.update_status(agent_id, ticker, "完成", analysis=json.dumps(technical_analysis, indent=4))
    
    message = HumanMessage(
        content=json.dumps(technical_analysis),
        name=agent_id,
    )
    
    if state["metadata"]["show_reasoning"]:
        show_agent_reasoning(technical_analysis, "技术分析Agent (A股)")
    
    state["data"]["analyst_signals"][agent_id] = technical_analysis
    
    progress.update_status(agent_id, None, "完成")
    
    return {
        "messages": state["messages"] + [message],
        "data": data,
    }


def calculate_limit_signals(prices_df: pd.DataFrame, ticker: str, limit_status: dict) -> dict:
    """
    涨跌停板分析策略（A股特有）
    
    Args:
        prices_df: 价格数据
        ticker: 股票代码
        limit_status: 涨跌停状态
        
    Returns:
        信号字典
    """
    if limit_status["is_limit_up"]:
        return {
            "signal": "bullish",
            "confidence": 0.8,
            "metrics": {
                "status": "涨停",
                "limit_price": limit_status["limit_up_price"],
                "pct_limit": limit_status["pct_limit"],
                "note": "涨停板，强势特征"
            }
        }
    elif limit_status["is_limit_down"]:
        return {
            "signal": "bearish",
            "confidence": 0.8,
            "metrics": {
                "status": "跌停",
                "limit_price": limit_status["limit_down_price"],
                "pct_limit": limit_status["pct_limit"],
                "note": "跌停板，弱势特征"
            }
        }
    
    recent_limits = 0
    if len(prices_df) >= 5:
        for i in range(-5, 0):
            if i >= -len(prices_df) and i < -1:
                close = prices_df['close'].iloc[i]
                prev_close = prices_df['close'].iloc[i-1]
                pct_chg = abs((close - prev_close) / prev_close)
                if pct_chg >= limit_status["pct_limit"] * 0.95:
                    recent_limits += 1
    
    if recent_limits >= 2:
        signal = "bullish"
        confidence = 0.7
    elif recent_limits == 1:
        signal = "neutral"
        confidence = 0.5
    else:
        signal = "neutral"
        confidence = 0.5
    
    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "status": "正常交易",
            "recent_limit_days": recent_limits,
            "pct_limit": limit_status["pct_limit"],
            "note": f"近5日有{recent_limits}日接近涨跌停"
        }
    }


def calculate_trend_signals(prices_df):
    """趋势跟踪策略"""
    ema_8 = calculate_ema(prices_df, 8)
    ema_21 = calculate_ema(prices_df, 21)
    ema_55 = calculate_ema(prices_df, 55)
    
    adx = calculate_adx(prices_df, 14)
    
    short_trend = ema_8 > ema_21
    medium_trend = ema_21 > ema_55
    
    trend_strength = adx["adx"].iloc[-1] / 100.0
    
    if short_trend.iloc[-1] and medium_trend.iloc[-1]:
        signal = "bullish"
        confidence = trend_strength
    elif not short_trend.iloc[-1] and not medium_trend.iloc[-1]:
        signal = "bearish"
        confidence = trend_strength
    else:
        signal = "neutral"
        confidence = 0.5
    
    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "adx": safe_float(adx["adx"].iloc[-1]),
            "trend_strength": safe_float(trend_strength),
        },
    }


def calculate_mean_reversion_signals(prices_df):
    """均值回归策略"""
    ma_50 = prices_df["close"].rolling(window=50).mean()
    std_50 = prices_df["close"].rolling(window=50).std()
    z_score = (prices_df["close"] - ma_50) / std_50
    
    bb_upper, bb_lower = calculate_bollinger_bands(prices_df)
    
    rsi_14 = calculate_rsi(prices_df, 14)
    rsi_28 = calculate_rsi(prices_df, 28)
    
    price_vs_bb = (prices_df["close"].iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
    
    if z_score.iloc[-1] < -2 and price_vs_bb < 0.2:
        signal = "bullish"
        confidence = min(abs(z_score.iloc[-1]) / 4, 1.0)
    elif z_score.iloc[-1] > 2 and price_vs_bb > 0.8:
        signal = "bearish"
        confidence = min(abs(z_score.iloc[-1]) / 4, 1.0)
    else:
        signal = "neutral"
        confidence = 0.5
    
    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "z_score": safe_float(z_score.iloc[-1]),
            "price_vs_bb": safe_float(price_vs_bb),
            "rsi_14": safe_float(rsi_14.iloc[-1]),
            "rsi_28": safe_float(rsi_28.iloc[-1]),
        },
    }


def calculate_momentum_signals(prices_df):
    """多因子动量策略"""
    returns = prices_df["close"].pct_change()
    mom_1m = returns.rolling(21).sum()
    mom_3m = returns.rolling(63).sum()
    mom_6m = returns.rolling(126).sum()
    
    volume_ma = prices_df["volume"].rolling(21).mean()
    volume_momentum = prices_df["volume"] / volume_ma
    
    momentum_score = (0.4 * mom_1m + 0.3 * mom_3m + 0.3 * mom_6m).iloc[-1]
    
    volume_confirmation = volume_momentum.iloc[-1] > 1.0
    
    if momentum_score > 0.05 and volume_confirmation:
        signal = "bullish"
        confidence = min(abs(momentum_score) * 5, 1.0)
    elif momentum_score < -0.05 and volume_confirmation:
        signal = "bearish"
        confidence = min(abs(momentum_score) * 5, 1.0)
    else:
        signal = "neutral"
        confidence = 0.5
    
    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "momentum_1m": safe_float(mom_1m.iloc[-1]),
            "momentum_3m": safe_float(mom_3m.iloc[-1]),
            "momentum_6m": safe_float(mom_6m.iloc[-1]),
            "volume_momentum": safe_float(volume_momentum.iloc[-1]),
        },
    }


def calculate_volatility_signals(prices_df):
    """波动率交易策略"""
    returns = prices_df["close"].pct_change()
    
    hist_vol = returns.rolling(21).std() * math.sqrt(252)
    
    vol_ma = hist_vol.rolling(63).mean()
    vol_regime = hist_vol / vol_ma
    
    vol_z_score = (hist_vol - vol_ma) / hist_vol.rolling(63).std()
    
    atr = calculate_atr(prices_df)
    atr_ratio = atr / prices_df["close"]
    
    current_vol_regime = vol_regime.iloc[-1]
    vol_z = vol_z_score.iloc[-1]
    
    if current_vol_regime < 0.8 and vol_z < -1:
        signal = "bullish"
        confidence = min(abs(vol_z) / 3, 1.0)
    elif current_vol_regime > 1.2 and vol_z > 1:
        signal = "bearish"
        confidence = min(abs(vol_z) / 3, 1.0)
    else:
        signal = "neutral"
        confidence = 0.5
    
    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "historical_volatility": safe_float(hist_vol.iloc[-1]),
            "volatility_regime": safe_float(current_vol_regime),
            "volatility_z_score": safe_float(vol_z),
            "atr_ratio": safe_float(atr_ratio.iloc[-1]),
        },
    }


def weighted_signal_combination(signals, weights):
    """加权信号组合"""
    signal_values = {"bullish": 1, "neutral": 0, "bearish": -1}
    
    weighted_sum = 0
    total_confidence = 0
    
    for strategy, signal in signals.items():
        numeric_signal = signal_values[signal["signal"]]
        weight = weights[strategy]
        confidence = signal["confidence"]
        
        weighted_sum += numeric_signal * weight * confidence
        total_confidence += weight * confidence
    
    if total_confidence > 0:
        final_score = weighted_sum / total_confidence
    else:
        final_score = 0
    
    if final_score > 0.2:
        signal = "bullish"
    elif final_score < -0.2:
        signal = "bearish"
    else:
        signal = "neutral"
    
    return {"signal": signal, "confidence": abs(final_score)}


def normalize_pandas(obj):
    """转换pandas对象为Python原生类型"""
    if isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict("records")
    elif isinstance(obj, dict):
        return {k: normalize_pandas(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [normalize_pandas(item) for item in obj]
    return obj


def calculate_rsi(prices_df: pd.DataFrame, period: int = 14) -> pd.Series:
    """计算RSI"""
    delta = prices_df["close"].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_bollinger_bands(prices_df: pd.DataFrame, window: int = 20) -> tuple:
    """计算布林带"""
    sma = prices_df["close"].rolling(window).mean()
    std_dev = prices_df["close"].rolling(window).std()
    upper_band = sma + (std_dev * 2)
    lower_band = sma - (std_dev * 2)
    return upper_band, lower_band


def calculate_ema(df: pd.DataFrame, window: int) -> pd.Series:
    """计算EMA"""
    return df["close"].ewm(span=window, adjust=False).mean()


def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """计算ADX"""
    df["high_low"] = df["high"] - df["low"]
    df["high_close"] = abs(df["high"] - df["close"].shift())
    df["low_close"] = abs(df["low"] - df["close"].shift())
    df["tr"] = df[["high_low", "high_close", "low_close"]].max(axis=1)
    
    df["up_move"] = df["high"] - df["high"].shift()
    df["down_move"] = df["low"].shift() - df["low"]
    
    df["plus_dm"] = np.where((df["up_move"] > df["down_move"]) & (df["up_move"] > 0), df["up_move"], 0)
    df["minus_dm"] = np.where((df["down_move"] > df["up_move"]) & (df["down_move"] > 0), df["down_move"], 0)
    
    df["+di"] = 100 * (df["plus_dm"].ewm(span=period).mean() / df["tr"].ewm(span=period).mean())
    df["-di"] = 100 * (df["minus_dm"].ewm(span=period).mean() / df["tr"].ewm(span=period).mean())
    df["dx"] = 100 * abs(df["+di"] - df["-di"]) / (df["+di"] + df["-di"])
    df["adx"] = df["dx"].ewm(span=period).mean()
    
    return df[["adx", "+di", "-di"]]


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """计算ATR"""
    high_low = df["high"] - df["low"]
    high_close = abs(df["high"] - df["close"].shift())
    low_close = abs(df["low"] - df["close"].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    
    return true_range.rolling(period).mean()
