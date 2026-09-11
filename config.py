# 配置文件
import os

# ===== 平台配置 =====
PLATFORMS = {
    'taobao': {
        'name': '淘宝',
        'enabled': True,
        'search_url': 'https://s.taobao.com/search',
        'timeout': 10,
    },
    'jd': {
        'name': '京东',
        'enabled': True,
        'search_url': 'https://search.jd.com/Search',
        'timeout': 10,
    },
    'pdd': {
        'name': '拼多多',
        'enabled': True,
        'search_url': 'https://mobile.pinduoduo.com/search',
        'timeout': 10,
    },
}

# ===== 请求配置 =====
TIMEOUT = 10  # 请求超时时间（秒）
RETRIES = 3   # 重试次数
DELAY = 1     # 请求间隔（秒）

# ===== 代理配置（可选）=====
PROXY = None  # 如需代理，设置为 {'http': 'http://...', 'https': 'http://...'}

# ===== 数据库配置 =====
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DATA_DIR, 'history.db')

# ===== 日志配置 =====
LOG_LEVEL = 'INFO'
LOG_FILE = os.path.join(DATA_DIR, 'app.log')

# ===== Web 应用配置 =====
FLASK_DEBUG = True
FLASK_PORT = 5000
FLASK_HOST = 'localhost'

# ===== User Agent =====
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# ===== 创建数据目录 =====
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
