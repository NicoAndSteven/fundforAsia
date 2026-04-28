"""Constants and utilities related to analysts configuration."""

from src.agents import portfolio_manager
from src.agents.aswath_damodaran import aswath_damodaran_agent
from src.agents.ben_graham import ben_graham_agent
from src.agents.bill_ackman import bill_ackman_agent
from src.agents.cathie_wood import cathie_wood_agent
from src.agents.charlie_munger import charlie_munger_agent
from src.agents.fundamentals import fundamentals_analyst_agent
from src.agents.michael_burry import michael_burry_agent
from src.agents.phil_fisher import phil_fisher_agent
from src.agents.peter_lynch import peter_lynch_agent
from src.agents.sentiment import sentiment_analyst_agent
from src.agents.stanley_druckenmiller import stanley_druckenmiller_agent
from src.agents.technicals import technical_analyst_agent
from src.agents.valuation import valuation_analyst_agent
from src.agents.warren_buffett import warren_buffett_agent
from src.agents.rakesh_jhunjhunwala import rakesh_jhunjhunwala_agent
from src.agents.mohnish_pabrai import mohnish_pabrai_agent
from src.agents.nassim_taleb import nassim_taleb_agent
from src.agents.news_sentiment import news_sentiment_agent
from src.agents.growth_agent import growth_analyst_agent

ANALYST_CONFIG = {
    "aswath_damodaran": {
        "display_name": "阿斯沃斯·达莫达兰",
        "display_name_en": "Aswath Damodaran",
        "description": "估值之父",
        "description_en": "The Dean of Valuation",
        "investing_style": "专注于内在价值和财务指标，通过严谨的估值分析评估投资机会。",
        "agent_func": aswath_damodaran_agent,
        "type": "analyst",
        "order": 0,
    },
    "ben_graham": {
        "display_name": "本杰明·格雷厄姆",
        "display_name_en": "Ben Graham",
        "description": "价值投资之父",
        "description_en": "The Father of Value Investing",
        "investing_style": "强调安全边际，通过系统性的价值分析投资于被低估的优质公司。",
        "agent_func": ben_graham_agent,
        "type": "analyst",
        "order": 1,
    },
    "bill_ackman": {
        "display_name": "比尔·阿克曼",
        "display_name_en": "Bill Ackman",
        "description": "激进投资者",
        "description_en": "The Activist Investor",
        "investing_style": "通过战略性的激进投资和逆向投资立场，寻求影响管理层并释放价值。",
        "agent_func": bill_ackman_agent,
        "type": "analyst",
        "order": 2,
    },
    "cathie_wood": {
        "display_name": "凯瑟琳·伍德",
        "display_name_en": "Cathie Wood",
        "description": "成长投资女王",
        "description_en": "The Queen of Growth Investing",
        "investing_style": "专注于颠覆性创新和成长，投资于引领技术进步和市场变革的公司。",
        "agent_func": cathie_wood_agent,
        "type": "analyst",
        "order": 3,
    },
    "charlie_munger": {
        "display_name": "查理·芒格",
        "display_name_en": "Charlie Munger",
        "description": "理性思考者",
        "description_en": "The Rational Thinker",
        "investing_style": "倡导价值投资，通过理性决策专注于优质企业和长期增长。",
        "agent_func": charlie_munger_agent,
        "type": "analyst",
        "order": 4,
    },
    "michael_burry": {
        "display_name": "迈克尔·布瑞",
        "display_name_en": "Michael Burry",
        "description": "大空头逆向投资者",
        "description_en": "The Big Short Contrarian",
        "investing_style": "进行逆向押注，通过深度基本面分析做空高估市场并投资被低估资产。",
        "agent_func": michael_burry_agent,
        "type": "analyst",
        "order": 5,
    },
    "mohnish_pabrai": {
        "display_name": "莫尼什·帕布莱",
        "display_name_en": "Mohnish Pabrai",
        "description": "丹道投资者",
        "description_en": "The Dhandho Investor",
        "investing_style": "通过基本面分析和安全边际专注于价值投资和长期增长。",
        "agent_func": mohnish_pabrai_agent,
        "type": "analyst",
        "order": 6,
    },
    "nassim_taleb": {
        "display_name": "纳西姆·塔勒布",
        "display_name_en": "Nassim Taleb",
        "description": "黑天鹅风险分析师",
        "description_en": "The Black Swan Risk Analyst",
        "investing_style": "专注于尾部风险、反脆弱性和非对称收益。使用杠铃策略，通过否定法避开脆弱企业，寻求有限下行和无限上行的凸性仓位。",
        "agent_func": nassim_taleb_agent,
        "type": "analyst",
        "order": 7,
    },
    "peter_lynch": {
        "display_name": "彼得·林奇",
        "display_name_en": "Peter Lynch",
        "description": "十倍股投资者",
        "description_en": "The 10-Bagger Investor",
        "investing_style": "投资于商业模式清晰、增长潜力强的公司，采用'买你所知'策略。",
        "agent_func": peter_lynch_agent,
        "type": "analyst",
        "order": 8,
    },
    "phil_fisher": {
        "display_name": "菲利普·费舍尔",
        "display_name_en": "Phil Fisher",
        "description": "闲聊投资者",
        "description_en": "The Scuttlebutt Investor",
        "investing_style": "强调投资于管理优秀、产品创新的公司，通过闲聊研究关注长期增长。",
        "agent_func": phil_fisher_agent,
        "type": "analyst",
        "order": 9,
    },
    "rakesh_jhunjhunwala": {
        "display_name": "拉凯什·金君瓦拉",
        "display_name_en": "Rakesh Jhunjhunwala",
        "description": "印度大牛",
        "description_en": "The Big Bull Of India",
        "investing_style": "利用宏观经济洞察投资于高增长行业，特别是新兴市场和国内机会。",
        "agent_func": rakesh_jhunjhunwala_agent,
        "type": "analyst",
        "order": 10,
    },
    "stanley_druckenmiller": {
        "display_name": "斯坦利·德鲁肯米勒",
        "display_name_en": "Stanley Druckenmiller",
        "description": "宏观投资者",
        "description_en": "The Macro Investor",
        "investing_style": "专注于宏观经济趋势，通过自上而下的分析对货币、商品和利率进行大额押注。",
        "agent_func": stanley_druckenmiller_agent,
        "type": "analyst",
        "order": 11,
    },
    "warren_buffett": {
        "display_name": "沃伦·巴菲特",
        "display_name_en": "Warren Buffett",
        "description": "奥马哈先知",
        "description_en": "The Oracle of Omaha",
        "investing_style": "通过价值投资和长期持有，寻求具有强大基本面和竞争优势的公司。",
        "agent_func": warren_buffett_agent,
        "type": "analyst",
        "order": 12,
    },
    "technical_analyst": {
        "display_name": "技术分析师",
        "display_name_en": "Technical Analyst",
        "description": "图表形态专家",
        "description_en": "Chart Pattern Specialist",
        "investing_style": "专注于图表形态和市场趋势进行投资决策，常使用技术指标和价格行为分析。",
        "agent_func": technical_analyst_agent,
        "type": "analyst",
        "order": 13,
    },
    "fundamentals_analyst": {
        "display_name": "基本面分析师",
        "display_name_en": "Fundamentals Analyst",
        "description": "财务报表专家",
        "description_en": "Financial Statement Specialist",
        "investing_style": "深入研究财务报表和经济指标，通过基本面分析评估公司内在价值。",
        "agent_func": fundamentals_analyst_agent,
        "type": "analyst",
        "order": 14,
    },
    "growth_analyst": {
        "display_name": "成长分析师",
        "display_name_en": "Growth Analyst",
        "description": "成长专家",
        "description_en": "Growth Specialist",
        "investing_style": "分析成长趋势和估值，通过成长分析识别成长机会。",
        "agent_func": growth_analyst_agent,
        "type": "analyst",
        "order": 15,
    },
    "news_sentiment_analyst": {
        "display_name": "新闻情绪分析师",
        "display_name_en": "News Sentiment Analyst",
        "description": "新闻情绪专家",
        "description_en": "News Sentiment Specialist",
        "investing_style": "分析新闻情绪预测市场走势，通过新闻分析识别投资机会。",
        "agent_func": news_sentiment_agent,
        "type": "analyst",
        "order": 16,
    },
    "sentiment_analyst": {
        "display_name": "情绪分析师",
        "display_name_en": "Sentiment Analyst",
        "description": "市场情绪专家",
        "description_en": "Market Sentiment Specialist",
        "investing_style": "通过行为分析衡量市场情绪和投资者行为，预测市场走势并识别机会。",
        "agent_func": sentiment_analyst_agent,
        "type": "analyst",
        "order": 17,
    },
    "valuation_analyst": {
        "display_name": "估值分析师",
        "display_name_en": "Valuation Analyst",
        "description": "公司估值专家",
        "description_en": "Company Valuation Specialist",
        "investing_style": "专注于确定公司公允价值，使用各种估值模型和财务指标进行投资决策。",
        "agent_func": valuation_analyst_agent,
        "type": "analyst",
        "order": 18,
    },
}

ANALYST_ORDER = [(config["display_name"], key) for key, config in sorted(ANALYST_CONFIG.items(), key=lambda x: x[1]["order"])]


def get_analyst_nodes():
    """Get the mapping of analyst keys to their (node_name, agent_func) tuples."""
    return {key: (f"{key}_agent", config["agent_func"]) for key, config in ANALYST_CONFIG.items()}


def get_agents_list():
    """Get the list of agents for API responses."""
    return [
        {
            "key": key,
            "display_name": config["display_name"],
            "display_name_en": config.get("display_name_en", config["display_name"]),
            "description": config["description"],
            "description_en": config.get("description_en", config["description"]),
            "investing_style": config["investing_style"],
            "order": config["order"]
        }
        for key, config in sorted(ANALYST_CONFIG.items(), key=lambda x: x[1]["order"])
    ]
