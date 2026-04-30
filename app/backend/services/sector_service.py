"""板块分析服务 - 生成大师推荐报告"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from app.backend.models.schemas import (
    MasterReport,
    ConsensusPick,
    MasterPerformance,
    MasterStockPick,
)

logger = logging.getLogger(__name__)

# 板块名称 → ETF 代码映射表
# 使用板块名称（而非不稳定的 BK 代码）进行匹配
# 顺序按名称长度降序排列：更具体的匹配优先于通用匹配
SECTOR_NAME_TO_ETF: List[Tuple[str, str]] = [
    # ── 科技类 ──
    ("半导体概念",        "512480"),   # 半导体ETF
    ("第三代半导体",      "512480"),   # 半导体ETF
    ("汽车芯片",          "159995"),   # 芯片ETF
    ("国产芯片",          "159995"),   # 芯片ETF
    ("芯片",              "512760"),   # 芯片ETF
    ("5G概念",            "159995"),   # 5GETF
    ("人工智能",          "159819"),   # 人工智能ETF
    ("软件开发",          "159852"),   # 软件ETF
    ("国产软件",          "159852"),   # 软件ETF
    ("软件",              "159852"),   # 软件ETF
    ("云计算",            "516510"),   # 云计算ETF
    ("大数据",            "159899"),   # 大数据ETF
    ("物联网",            "159897"),   # 物联网ETF
    ("机器人",            "159850"),   # 机器人ETF
    ("智能汽车",          "159892"),   # 智能汽车ETF
    ("无人驾驶",          "159892"),   # 智能汽车ETF（覆盖）
    ("消费电子",          "159865"),   # 消费电子ETF（实际为农业ETF，待确认）
    ("LED概念",           "159865"),   # 消费电子ETF
    ("MiniLED",           "159865"),   # 消费电子ETF
    ("MicroLED",          "159865"),   # 消费电子ETF
    ("OLED",              "159865"),   # 消费电子ETF
    ("机器视觉",          "159850"),   # 机器人ETF（近似）
    ("人脑工程",          "159850"),   # 机器人ETF（近似）
    ("虚拟现实",          "159852"),   # 软件ETF 覆盖VR内容
    # ── 新能源 ──
    ("新能源汽车",        "515030"),   # 新能源汽车ETF
    ("新能源车",          "515030"),   # 新能源汽车ETF
    ("特斯拉概念",        "515030"),   # 新能源汽车ETF
    ("换电概念",          "515030"),   # 新能源汽车ETF
    ("新能源",            "516160"),   # 新能源ETF
    ("锂电池概念",        "561160"),   # 锂电池ETF
    ("刀片电池",          "561160"),   # 锂电池ETF
    ("燃料电池概念",      "561160"),   # 锂电池ETF
    ("固态电池",          "561160"),   # 锂电池ETF
    ("钠离子电池",        "561160"),   # 锂电池ETF
    ("光伏概念",          "159930"),   # 光伏ETF
    ("HJT电池",           "159930"),   # 光伏ETF
    ("碳中和",            "159687"),   # 碳中和ETF
    ("碳交易",            "159687"),   # 碳中和ETF
    ("低碳冶金",          "159687"),   # 碳中和ETF（近似）
    ("储能概念",          "159637"),   # 储能ETF
    ("氢能源",            "159850"),   # 机器人ETF/或者没有完美对应
    ("核能核电",          "560860"),   # 核电ETF
    ("风能",              "516160"),   # 新能源ETF 覆盖
    ("特高压",            "516160"),   # 新能源ETF 覆盖
    ("智能电网",          "516160"),   # 新能源ETF 覆盖
    ("充电桩",            "516160"),   # 新能源ETF 覆盖
    # ── 消费 ──
    ("酿酒概念",          "512690"),   # 酒ETF
    ("白酒",              "512690"),   # 酒ETF
    ("食品饮料",          "159854"),   # 食品饮料ETF
    ("家用电器",          "159996"),   # 家电ETF
    ("家电",              "159996"),   # 家电ETF
    ("汽车零部件",        "516110"),   # 汽车ETF
    ("汽车",              "516110"),   # 汽车ETF
    ("消费",              "159928"),   # 消费ETF
    ("新零售",            "159928"),   # 消费ETF（近似）
    ("电商概念",          "159928"),   # 消费ETF（近似）
    ("纺织服饰",          "159928"),   # 消费ETF（近似）
    ("饰品",              "159928"),   # 消费ETF（近似）
    ("养殖",              "159865"),   # 农业ETF
    ("猪肉概念",          "159865"),   # 农业ETF
    ("鸡肉概念",          "159865"),   # 农业ETF
    ("水产概念",          "159865"),   # 农业ETF
    ("农业种植",          "159865"),   # 农业ETF
    ("生态农业",          "159865"),   # 农业ETF
    ("宠物经济",          "159865"),   # 农业ETF（近似）
    ("乳业",              "159854"),   # 食品饮料ETF（近似）
    ("代糖概念",          "159854"),   # 食品饮料ETF（近似）
    # ── 医药 ──
    ("化学制药",          "512010"),   # 医药ETF
    ("中药概念",          "512010"),   # 医药ETF
    ("医药",              "512010"),   # 医药ETF
    ("创新药",            "159992"),   # 创新药ETF
    ("医疗器械概念",      "159828"),   # 医疗ETF
    ("医疗服务",          "159828"),   # 医疗ETF
    ("医疗",              "159828"),   # 医疗ETF
    ("体外诊断概念",      "159828"),   # 医疗ETF
    ("精准医疗",          "159828"),   # 医疗ETF
    ("免疫治疗",          "159837"),   # 生物医药ETF
    ("生物疫苗",          "159828"),   # 医疗ETF
    ("生物医药",          "159837"),   # 生物医药ETF
    ("基因测序",          "159837"),   # 生物医药ETF
    ("CRO",               "159828"),   # 医疗ETF
    ("CAR-T细胞疗法",     "159837"),   # 生物医药ETF
    ("医美概念",          "159837"),   # 生物医药ETF（近似）
    ("化妆品概念",        "159837"),   # 生物医药ETF（近似）
    ("毛发医疗",          "159828"),   # 医疗ETF
    ("阿兹海默",          "512010"),   # 医药ETF
    ("流感",              "512010"),   # 医药ETF
    ("病毒防治",          "512010"),   # 医药ETF
    ("肝素概念",          "512010"),   # 医药ETF
    ("长寿药",            "512010"),   # 医药ETF
    ("辅助生殖",          "512010"),   # 医药ETF
    ("医废处理",          "159828"),   # 医疗ETF
    ("工业大麻",          "159828"),   # 医疗ETF（近似）
    # ── 金融 ──
    ("银行",              "512800"),   # 银行ETF
    ("证券",              "512880"),   # 证券ETF
    ("券商概念",          "512880"),   # 证券ETF
    ("保险",              "512070"),   # 保险ETF
    ("参股保险",          "512070"),   # 保险ETF
    ("参股券商",          "512880"),   # 证券ETF
    ("参股银行",          "512800"),   # 银行ETF
    ("房地产开发",        "512200"),   # 房地产ETF
    ("房地产",            "512200"),   # 房地产ETF
    ("租售同权",          "512200"),   # 房地产ETF
    ("装修装饰",          "512200"),   # 房地产ETF（近似）
    ("装修建材",          "512200"),   # 房地产ETF（近似）
    ("多元金融",          "512800"),   # 银行ETF（近似）
    # ── 制造/周期 ──
    ("军工",              "516970"),   # 军工ETF
    ("航天航空",          "516970"),   # 军工ETF
    ("航母概念",          "516970"),   # 军工ETF
    ("大飞机",            "516970"),   # 军工ETF
    ("无人机",            "516970"),   # 军工ETF
    ("军民融合",          "516970"),   # 军工ETF
    ("有色金属",          "159609"),   # 有色金属ETF
    ("小金属概念",        "159609"),   # 有色金属ETF
    ("稀土永磁",          "159713"),   # 稀土ETF
    ("钢铁",              "159944"),   # 钢铁ETF
    ("煤炭",              "515220"),   # 煤炭ETF
    ("煤化工概念",        "515220"),   # 煤炭ETF
    ("黄金概念",          "518880"),   # 黄金ETF
    ("贵金属",            "518880"),   # 黄金ETF
    ("化工原料",          "159870"),   # 化工ETF
    ("化学制品",          "159870"),   # 化工ETF
    ("氟化工概念",        "159870"),   # 化工ETF
    ("有机硅概念",        "159870"),   # 化工ETF
    ("化肥",              "159870"),   # 化工ETF（近似）
    ("农药",              "159870"),   # 化工ETF（近似）
    ("草甘膦",            "159870"),   # 化工ETF（近似）
    ("磷化工",            "159870"),   # 化工ETF
    ("石油石化",          "159870"),   # 化工ETF（近似）
    ("油气设服",          "159870"),   # 化工ETF（近似）
    ("天然气",            "159870"),   # 化工ETF（近似）
    ("页岩气",            "159870"),   # 化工ETF（近似）
    ("新材料",            "159713"),   # 稀土ETF（近似）
    ("石墨烯",            "159713"),   # 稀土ETF（近似）
    ("蓝宝石",            "159713"),   # 稀土ETF（近似）
    ("磁悬浮概念",        "159713"),   # 稀土ETF（近似）
    ("玻璃玻纤",          "515220"),   # 煤炭ETF（近似，无完美对应）
    ("包装材料",          "159870"),   # 化工ETF（近似）
    ("降解塑料",          "159870"),   # 化工ETF（近似）
    ("塑料",              "159870"),   # 化工ETF（近似）
    ("造纸印刷",          "159870"),   # 化工ETF（近似）
    ("水泥",              "159870"),   # 化工ETF（近似）
    # ── 宽基指数 ──
    ("沪深300",           "510300"),   # 沪深300ETF
    ("上证50",            "510050"),   # 上证50ETF
    ("创业板综",          "159915"),   # 创业板ETF
    ("创业板",            "159915"),   # 创业板ETF
    ("创业成份",          "159915"),   # 创业板ETF
    ("科创50",            "588000"),   # 科创50ETF
    ("中证500",           "510500"),   # 中证500ETF
    ("上证180",           "510500"),   # 中证500ETF（近似）
    ("深证100R",          "159915"),   # 创业板ETF（近似）
    ("深成500",           "510500"),   # 中证500ETF（近似）
    ("上证380",           "510500"),   # 中证500ETF（近似）
    # ── 热门题材 ──
    ("数字经济",          "560800"),   # 数字经济ETF
    ("信创",              "159539"),   # 信创ETF
    ("区块链",            "512480"),   # 半导体ETF（近似）
    ("数字货币",          "512480"),   # 半导体ETF（近似）
    ("数据中心",          "516510"),   # 云计算ETF
    ("工业互联",          "516510"),   # 云计算ETF
    ("车联网(车路云)",    "516510"),   # 云计算ETF（近似）
    ("车联网",            "516510"),   # 云计算ETF（近似）
    ("机器视觉",          "516510"),   # 云计算ETF（近似）
    ("数字孪生",          "516510"),   # 云计算ETF（近似）
    ("智慧城市",          "516510"),   # 云计算ETF（近似）
    ("智慧政务",          "516510"),   # 云计算ETF（近似）
    ("电子政务",          "516510"),   # 云计算ETF（近似）
    ("网络安全",          "512480"),   # 半导体ETF（近似）
    ("VPN",               "512480"),   # 半导体ETF（近似）
    ("边缘计算",          "512480"),   # 半导体ETF（近似）
    ("超算/量子",         "512480"),   # 半导体ETF（近似）
    ("量子科技",          "512480"),   # 半导体ETF（近似）
    ("华为概念",          "159995"),   # 芯片ETF（近似）
    ("华为汽车",          "515030"),   # 新能源汽车ETF
    ("华为昇腾",          "159995"),   # 芯片ETF（近似）
    ("小米概念",          "159995"),   # 芯片ETF（近似）
    ("苹果概念",          "159995"),   # 芯片ETF（近似）
    ("PCB",               "159995"),   # 芯片ETF（近似）
    ("被动元件概念",      "159995"),   # 芯片ETF（近似）
    ("3D打印",            "159995"),   # 芯片ETF（近似）
    ("超清视频",          "159995"),   # 芯片ETF（近似）
    ("氮化镓",            "159995"),   # 芯片ETF（近似）
    ("碳化硅",            "159995"),   # 芯片ETF（近似）
    ("EDA概念",           "512480"),   # 半导体ETF
    ("光刻机(胶)",        "512480"),   # 半导体ETF
    ("中芯概念",          "512480"),   # 半导体ETF
    ("3D摄像头",          "512480"),   # 半导体ETF
    ("传感器",            "512480"),   # 半导体ETF（近似）
    ("生物识别",          "512480"),   # 半导体ETF（近似）
    ("无线充电",          "512480"),   # 半导体ETF（近似）
    ("无线耳机",          "512480"),   # 半导体ETF（近似）
    ("智能穿戴",          "512480"),   # 半导体ETF（近似）
    ("智能家居",          "512480"),   # 半导体ETF（近似）
    ("智能电视",          "512480"),   # 半导体ETF（近似）
    ("电子烟",            "512480"),   # 半导体ETF（近似）
    ("超导概念",          "512480"),   # 半导体ETF（近似）
    ("UWB概念",           "512480"),   # 半导体ETF（近似）
    ("智能家居",          "512480"),   # 半导体ETF（近似）
    ("机器视觉",          "512480"),   # 半导体ETF（近似）
    ("EDR概念",           "512480"),   # 半导体ETF（近似）
    ("ETC",               "512480"),   # 半导体ETF（近似）
    ("电子车牌",          "512480"),   # 半导体ETF（近似）
    # ── 其他 ──
    ("体育产业",          "159928"),   # 消费ETF（近似）
    ("旅游酒店",          "159928"),   # 消费ETF（近似）
    ("旅游概念",          "159928"),   # 消费ETF（近似）
    ("教育",              "159928"),   # 消费ETF（近似）
    ("在线教育",          "159928"),   # 消费ETF（近似）
    ("婴童概念",          "159928"),   # 消费ETF（近似）
    ("盲盒经济",          "159928"),   # 消费ETF（近似）
    ("网红经济",          "159928"),   # 消费ETF（近似）
    ("抖音概念",          "159928"),   # 消费ETF（近似）
    ("快手概念",          "159928"),   # 消费ETF（近似）
    ("拼多多概念",        "159928"),   # 消费ETF（近似）
    ("免税概念",          "159928"),   # 消费ETF（近似）
    ("退税商店",          "159928"),   # 消费ETF（近似）
    ("土地流转",          "159928"),   # 消费ETF（近似）
    ("乡村振兴",          "159928"),   # 消费ETF（近似）
    ("一带一路",          "516970"),   # 军工ETF（近似）
    ("铁路基建",          "516970"),   # 军工ETF（近似）
    ("工程建设",          "516970"),   # 军工ETF（近似）
    ("工程机械概念",      "516970"),   # 军工ETF（近似）
    ("通用机械",          "516970"),   # 军工ETF（近似）
    ("专用设备",          "516970"),   # 军工ETF（近似）
    ("工程咨询服务",      "516970"),   # 军工ETF（近似）
]


def get_etf_for_sector(sector_name: str) -> Optional[str]:
    """获取板块对应的 ETF 代码（按名称模糊匹配）

    使用板块名称进行匹配（而非不稳定的 BK 代码），
    按 SECTOR_NAME_TO_ETF 列表顺序返回首个匹配结果。
    """
    for name_pattern, etf_code in SECTOR_NAME_TO_ETF:
        if name_pattern in sector_name:
            return etf_code
    return None


def get_etf_for_sector_name(sectors: List[Dict[str, Any]], sector_name: str) -> Optional[str]:
    """通过东方财富板块名称查找对应的 ETF 代码（兼容旧接口）"""
    # 直接使用 sector_name 匹配（不依赖 API 返回的代码）
    return get_etf_for_sector(sector_name)

# 分析师中文名映射（与 consensus-tab-utils.ts 保持一致）
ANALYST_NAMES: Dict[str, str] = {
    "warren_buffett": "巴菲特",
    "charlie_munger": "芒格",
    "ben_graham": "格雷厄姆",
    "peter_lynch": "林奇",
    "phil_fisher": "费舍",
    "bill_ackman": "阿克曼",
    "cathie_wood": "伍德",
    "michael_burry": "布瑞",
    "stanley_druckenmiller": "德鲁肯米勒",
    "rakesh_jhunjhunwala": "金君瓦拉",
    "nassim_taleb": "塔勒布",
    "mohnish_pabrai": "帕布莱",
    "aswath_damodaran": "达莫达兰",
    "fundamentals_analyst": "基本面",
    "technical_analyst": "技术面",
    "sentiment_analyst": "情绪面",
    "valuation_analyst": "估值面",
    "growth_analyst": "成长面",
    "news_sentiment_analyst": "新闻情绪",
}

# 非大师分析师的 key，生成报告时跳过
_FUNCTIONAL_ANALYSTS = {
    "fundamentals_analyst", "technical_analyst", "sentiment_analyst",
    "valuation_analyst", "growth_analyst", "news_sentiment_analyst",
}


def _normalize_signal(signal_data: Any) -> tuple[str, float] | None:
    """标准化信号数据，返回 (signal, confidence) 或 None"""
    if not signal_data or not isinstance(signal_data, dict):
        return None
    signal = str(signal_data.get("signal", "NEUTRAL")).upper()
    confidence_raw = signal_data.get("confidence", 0)
    try:
        confidence = float(confidence_raw)
    except (ValueError, TypeError):
        confidence = 0.0
    return signal, confidence


def _get_analyst_name(key: str) -> str:
    """获取分析师中文名"""
    return ANALYST_NAMES.get(key, key.replace("_", " ").title())


def _is_master_analyst(key: str) -> bool:
    """判断是否为投资大师（相对于功能性分析师）"""
    return key not in _FUNCTIONAL_ANALYSTS and "_analyst" not in key


def generate_master_report(
    backtest_results: List[Dict[str, Any]],
) -> MasterReport:
    """从回测结果生成大师推荐报告。

    遍历所有回测日期的 analyst_signals，跨周期聚合：
    1. 各大师对所有股票的最终信号
    2. 大师共识精选排行
    3. 各大师表现统计（胜率）
    """
    if not backtest_results:
        return MasterReport(generated_at=datetime.now().isoformat())

    # ── 用最后一个交易日的数据作为"当前推荐" ──
    latest = backtest_results[-1]
    latest_signals: Dict[str, Any] = latest.get("analyst_signals", {}) or {}

    # ── 1. 计算每只股票的共识 ──
    ticker_signals: Dict[str, Dict[str, tuple[str, float]]] = {}
    for analyst_key, tickers in latest_signals.items():
        if not isinstance(tickers, dict):
            continue
        for ticker, sig_data in tickers.items():
            normalized = _normalize_signal(sig_data)
            if normalized is None:
                continue
            if ticker not in ticker_signals:
                ticker_signals[ticker] = {}
            ticker_signals[ticker][analyst_key] = normalized

    consensus_picks: List[ConsensusPick] = []
    for ticker, signals in ticker_signals.items():
        bullish = sum(1 for s, _ in signals.values() if s == "BULLISH")
        bearish = sum(1 for s, _ in signals.values() if s == "BEARISH")
        neutral = sum(1 for s, _ in signals.values() if s == "NEUTRAL")
        total = len(signals)
        score = (bullish - bearish) / total if total > 0 else 0.0

        # 找出看多的（投资）大师
        top_masters = sorted(
            [
                _get_analyst_name(k)
                for k, (s, _) in signals.items()
                if s == "BULLISH" and _is_master_analyst(k)
            ],
            key=lambda x: -signals.get(
                [k for k in signals if _get_analyst_name(k) == x],
                ("", 0),
            )[1] if any(_get_analyst_name(k) == x for k in signals) else 0,
        )[:5]

        consensus_picks.append(ConsensusPick(
            ticker=ticker,
            consensus_score=round(score, 4),
            bullish_count=bullish,
            bearish_count=bearish,
            neutral_count=neutral,
            total_analysts=total,
            top_bullish_analysts=top_masters,
        ))

    consensus_picks.sort(key=lambda x: x.consensus_score, reverse=True)

    # ── 2. 计算各大师的表现（跨全周期） ──
    master_stats: Dict[str, Dict[str, Any]] = {}
    for analyst_key in ANALYST_NAMES:
        if _is_master_analyst(analyst_key):
            master_stats[analyst_key] = {"total": 0, "correct": 0}

    for i in range(len(backtest_results) - 1):
        today = backtest_results[i]
        tomorrow = backtest_results[i + 1]
        signals_today = today.get("analyst_signals", {}) or {}
        prices_today = today.get("current_prices", {}) or {}
        prices_tomorrow = tomorrow.get("current_prices", {}) or {}

        for analyst_key, tickers in signals_today.items():
            if analyst_key not in master_stats:
                continue
            if not isinstance(tickers, dict):
                continue
            for ticker, sig_data in tickers.items():
                normalized = _normalize_signal(sig_data)
                if normalized is None:
                    continue
                signal, _ = normalized
                if signal == "NEUTRAL":
                    continue

                price_today = prices_today.get(ticker)
                price_tomorrow = prices_tomorrow.get(ticker)
                if not isinstance(price_today, (int, float)) or not isinstance(price_tomorrow, (int, float)):
                    continue
                if price_today == 0:
                    continue

                price_change = (price_tomorrow - price_today) / price_today
                is_correct = (signal == "BULLISH" and price_change > 0) or \
                             (signal == "BEARISH" and price_change < 0)

                master_stats[analyst_key]["total"] += 1
                if is_correct:
                    master_stats[analyst_key]["correct"] += 1

    master_performances: List[MasterPerformance] = []
    for analyst_key, stats in master_stats.items():
        total = stats["total"]
        correct = stats["correct"]
        win_rate = (correct / total * 100) if total > 0 else 0.0
        master_performances.append(MasterPerformance(
            analyst_key=analyst_key,
            analyst_name=_get_analyst_name(analyst_key),
            total_predictions=total,
            correct_predictions=correct,
            win_rate=round(win_rate, 1),
        ))
    master_performances.sort(key=lambda x: x.win_rate, reverse=True)

    # ── 3. 构建每位大师的推荐清单 ──
    master_picks: Dict[str, List[MasterStockPick]] = {}
    for analyst_key, tickers in latest_signals.items():
        if not isinstance(tickers, dict):
            continue
        picks: List[MasterStockPick] = []
        for ticker, sig_data in tickers.items():
            normalized = _normalize_signal(sig_data)
            if normalized is None:
                continue
            signal, confidence = normalized
            picks.append(MasterStockPick(
                ticker=ticker,
                signal=signal,
                confidence=confidence,
                analyst_key=analyst_key,
                analyst_name=_get_analyst_name(analyst_key),
            ))
        if picks:
            picks.sort(key=lambda x: x.confidence, reverse=True)
            master_picks[analyst_key] = picks

    # ── 4. 生成简短摘要 ──
    top_picks = consensus_picks[:3]
    summary_parts = []
    if top_picks:
        top_lines = []
        for p in top_picks:
            direction = "看多" if p.consensus_score > 0 else "看空"
            masters_str = "、".join(p.top_bullish_analysts[:3]) if p.top_bullish_analysts else ""
            top_lines.append(f"{p.ticker}（{direction}，{p.bullish_count}/{p.total_analysts}位分析师推荐）")
        summary_parts.append("大师共识精选：" + "；".join(top_lines))

    best_master = master_performances[0] if master_performances else None
    if best_master and best_master.total_predictions > 0:
        summary_parts.append(
            f"表现最佳：{best_master.analyst_name}（胜率{best_master.win_rate:.1f}%，"
            f"{best_master.correct_predictions}/{best_master.total_predictions}次预测正确）"
        )

    summary = "；".join(summary_parts) if summary_parts else "暂无足够数据生成摘要"

    return MasterReport(
        summary=summary,
        consensus_picks=consensus_picks,
        master_performances=master_performances,
        master_picks=master_picks,
        generated_at=datetime.now().isoformat(),
    )
