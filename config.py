import os
from dotenv import load_dotenv

load_dotenv()

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 项目配置
REPORT_TITLE = "孟加拉商业情报日报"
UPDATE_TIME = "北京时间 07:00"

INDUSTRIES = [
    "成衣纺织", "基建", "能源", "太阳能", "电动两轮车", "电动汽车",
    "制药", "ICT电商", "黄麻", "皮革", "船舶拆解", "渔业",
    "农产品加工", "陶瓷", "家具", "轻工制造", "造船", "医疗器械",
    "塑料", "家电", "数字经济", "其他"
]

# 采集设置
DAYS_BACK = 1.5
MAX_NEWS = 120
