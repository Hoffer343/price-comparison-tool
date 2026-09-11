# 🛒 电商比价工具

批量对商品在**淘宝、京东、拼多多**三大平台进行实时比价。

## ✨ 功能

- ✅ 支持淘宝、天猫、京东、拼多多
- ✅ 批量输入商品名称或链接
- ✅ 实时获取最新价格、销量、评分
- ✅ 生成对比报告（CSV/Excel）
- ✅ 历史价格记录
- ✅ Web 界面 + CLI 两种使用方式

## 🚀 快速开始

### 前置要求
- Python 3.8+
- pip

### 安装

```bash
# 克隆仓库
git clone https://github.com/Hoffer343/price-comparison-tool.git
cd price-comparison-tool

# 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 📖 使用方式

### 方式 1：CLI 命令行（最简单）

```bash
# 单个商品比价
python cli.py "iPhone 15"

# 批量比价（从 CSV）
python cli.py --batch products.csv

# 保存结果
python cli.py "iPhone 15" --output result.csv
```

### 方式 2：Web 界面

```bash
python app.py
# 打开浏览器访问 http://localhost:5000
```

### 方式 3：Python 脚本

```python
from scraper import PriceComparison

# 创建比较器
comparer = PriceComparison()

# 搜索商品
results = comparer.search("iPhone 15")

# 查看结果
for platform, products in results.items():
    print(f"{platform}: {products}")
```

## 📁 项目结构

```
.
├── README.md                 # 项目说明
├── requirements.txt          # Python 依赖
├── config.py                 # 配置文件
├── scraper.py               # 核心爬虫模块
├── cli.py                   # 命令行工具
├── app.py                   # Flask Web 应用
├── data/
│   ├── history.db           # 历史记录数据库
│   └── templates/
│       ├── index.html       # 首页
│       └── result.html      # 结果页
└── tests/
    └── test_scraper.py      # 单元测试
```

## ⚙️ 配置

编辑 `config.py` 调整设置：

```python
# 平台配置
PLATFORMS = ['taobao', 'jd', 'pdd']  # 要比价的平台
TIMEOUT = 10  # 请求超时时间（秒）
RETRIES = 3   # 重试次数
DELAY = 1     # 请求间隔（秒）
```

## 📊 输出示例

```
搜索商品：iPhone 15

┌─────────┬──────────┬─────┬─────┬────────┐
│ 平台    │ 商品名   │ 价格 │ 销量 │ 评分   │
├─────────┼──────────┼─────┼─────┼────────┤
│ 淘宝    │ iPhone15 │ 5999│ 1.2w│ 4.8 ★  │
│ 京东    │ iPhone15 │ 5899│ 8.5k│ 4.9 ★  │
│ 拼多多  │ iPhone15 │ 5699│ 3.2k│ 4.7 ★  │
└─────────┴──────────┴─────┴─────┴────────┘

💡 推荐：拼多多 - 最便宜（便宜 300 元）
```

## ⚠️ 注意事项

1. **遵守服务条款**：本工具仅用于学习和个人使用
2. **请求频率**：避免高频请求，建议间隔 ≥1 秒
3. **Cookie 管理**：部分平台需要登录态���见下方说明
4. **更新维护**：平台反爬虫规则会变化，代码可能需要定期更新

## 🔐 处理平台登录

### 京东（推荐方式）

```bash
# 首次使用会自动打开浏览器登录
python cli.py "iPhone 15" --platform jd
# 登录后自动保存 Cookie 到 ~/.price_tool/jd_cookies.json
```

### 淘宝

本工具已集成无需登录的搜索（基于 MTOP API），但如需获取完整信息可手动登录。

### 拼多多

拼多多限制严格，首次搜索需要登录验证。

## 📝 批量比价示例

创建 `products.csv`：

```csv
商品名
iPhone 15
AirPods Pro
小米 13
```

运行：

```bash
python cli.py --batch products.csv --output result.csv
```

生成 `result.csv`：

```csv
商品名,淘宝价格,京东价格,拼多多价格,最便宜平台,节省金额
iPhone 15,5999,5899,5699,拼多多,300
AirPods Pro,1299,1199,1099,拼多多,200
小米 13,2999,2899,2799,拼多多,200
```

## 🔧 常见问题

### Q: 为什么搜不到商品？
A: 检查商品名是否准确，尝试更简洁的关键词。部分商品可能需要登录才能获取。

### Q: 如何设置代理？
A: 编辑 `config.py` 的 `PROXY` 配置：
```python
PROXY = {
    'http': 'http://proxy.example.com:8080',
    'https': 'http://proxy.example.com:8080',
}
```

### Q: 能否自动定时检查价格？
A: 可以，使用 `schedule` 库：
```python
import schedule
import time

schedule.every(1).hours.do(job)
while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📄 许可证

MIT License - 仅供学习交流使用

## 🤝 贡献

欢迎 PR 和 Issue！

---

**⚠️ 免责声明**：本工具仅供学习研究使用。用户需遵守各平台服务条款，不承担商业使用责任。
