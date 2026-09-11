import requests
import json
import time
import logging
from typing import Dict, List, Optional
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
from config import PLATFORMS, TIMEOUT, RETRIES, DELAY, PROXY, USER_AGENT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper:
    """基础爬虫类"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.platform_config = PLATFORMS.get(platform_name, {})
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        if PROXY:
            self.session.proxies.update(PROXY)
    
    def _request(self, url: str, params: dict = None, **kwargs) -> Optional[requests.Response]:
        """带重试机制的请求"""
        for attempt in range(RETRIES):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=TIMEOUT,
                    **kwargs
                )
                response.raise_for_status()
                return response
            except Exception as e:
                logger.warning(f"[{self.platform_name}] 第 {attempt + 1} 次请求失败: {e}")
                if attempt < RETRIES - 1:
                    time.sleep(DELAY)
        return None
    
    def search(self, keyword: str) -> List[Dict]:
        """搜索商品（子类实现）"""
        raise NotImplementedError


class TaobaoScraper(BaseScraper):
    """淘宝爬虫"""
    
    def __init__(self):
        super().__init__('taobao')
    
    def search(self, keyword: str) -> List[Dict]:
        """搜索淘宝商品"""
        try:
            url = self.platform_config['search_url']
            params = {
                'q': keyword,
                'sort': 'default',
                'refine': 'off'
            }
            
            response = self._request(url, params=params)
            if not response:
                return []
            
            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            products = []
            
            # 查找商品列表
            items = soup.find_all('div', class_='s-item-pic')
            for item in items[:5]:  # 仅取前 5 个
                try:
                    title_elem = item.find('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get('title', '').strip()
                    link = title_elem.get('href', '')
                    
                    # 从父容器获取价格
                    price_container = item.parent.find('span', class_='s-price')
                    price = price_container.get_text(strip=True) if price_container else '信息不全'
                    
                    # 获取销量
                    sales_elem = item.parent.find('span', class_='s-sales')
                    sales = sales_elem.get_text(strip=True) if sales_elem else '0'
                    
                    products.append({
                        'title': title[:50],  # 截取前 50 个字符
                        'price': price,
                        'sales': sales,
                        'link': link,
                        'rating': '暂无'
                    })
                except Exception as e:
                    logger.error(f"解析淘宝商品失败: {e}")
                    continue
            
            return products if products else [{'error': '未找到商品'}]
        
        except Exception as e:
            logger.error(f"[淘宝] 搜索失败: {e}")
            return [{'error': str(e)}]


class JDScraper(BaseScraper):
    """京东爬虫"""
    
    def __init__(self):
        super().__init__('jd')
    
    def search(self, keyword: str) -> List[Dict]:
        """搜索京东商品"""
        try:
            url = self.platform_config['search_url']
            params = {
                'keyword': keyword,
                'page': '1'
            }
            
            response = self._request(url, params=params)
            if not response:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            products = []
            
            # 查找商品列表
            items = soup.find_all('li', class_='gl-item')
            for item in items[:5]:
                try:
                    # 标题
                    title_elem = item.find('em')
                    title = title_elem.get_text(strip=True) if title_elem else '无标题'
                    
                    # 价格
                    price_elem = item.find('i', class_='J-p-')
                    price = price_elem.get_text(strip=True) if price_elem else '暂无价格'
                    
                    # 评分
                    rating_elem = item.find('strong', class_='J-p-comment-count')
                    rating = rating_elem.get_text(strip=True) if rating_elem else '暂无'
                    
                    # 链接
                    link_elem = item.find('a', class_='productTitle')
                    link = link_elem.get('href', '') if link_elem else ''
                    
                    products.append({
                        'title': title[:50],
                        'price': price,
                        'sales': '暂无',
                        'link': link,
                        'rating': rating
                    })
                except Exception as e:
                    logger.error(f"解析京东商品失败: {e}")
                    continue
            
            return products if products else [{'error': '未找到商品'}]
        
        except Exception as e:
            logger.error(f"[京东] 搜索失败: {e}")
            return [{'error': str(e)}]


class PDDScraper(BaseScraper):
    """拼多多爬虫"""
    
    def __init__(self):
        super().__init__('pdd')
    
    def search(self, keyword: str) -> List[Dict]:
        """搜索拼多多商品"""
        try:
            url = self.platform_config['search_url']
            params = {
                'keyword': keyword,
                'search_range': '',
            }
            
            response = self._request(url, params=params)
            if not response:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            products = []
            
            # 查找商品列表
            items = soup.find_all('div', class_='goods-item')
            for item in items[:5]:
                try:
                    # 标题
                    title_elem = item.find('a', class_='title')
                    title = title_elem.get_text(strip=True) if title_elem else '无标题'
                    
                    # 价格
                    price_elem = item.find('span', class_='price')
                    price = price_elem.get_text(strip=True) if price_elem else '暂无价格'
                    
                    # 销量
                    sales_elem = item.find('span', class_='sales')
                    sales = sales_elem.get_text(strip=True) if sales_elem else '0'
                    
                    # 链接
                    link_elem = item.find('a')
                    link = link_elem.get('href', '') if link_elem else ''
                    
                    products.append({
                        'title': title[:50],
                        'price': price,
                        'sales': sales,
                        'link': link,
                        'rating': '暂无'
                    })
                except Exception as e:
                    logger.error(f"解析拼多多商品失败: {e}")
                    continue
            
            return products if products else [{'error': '未找到商品'}]
        
        except Exception as e:
            logger.error(f"[拼多多] 搜索失败: {e}")
            return [{'error': str(e)}]


class PriceComparison:
    """价格比较器 - 聚合所有爬虫"""
    
    def __init__(self):
        self.scrapers = {
            'taobao': TaobaoScraper(),
            'jd': JDScraper(),
            'pdd': PDDScraper(),
        }
    
    def search(self, keyword: str) -> Dict[str, List[Dict]]:
        """在所有平台搜索商品"""
        logger.info(f"开始搜索: {keyword}")
        results = {}
        
        for platform_key, scraper in self.scrapers.items():
            if not PLATFORMS.get(platform_key, {}).get('enabled', False):
                continue
            
            logger.info(f"[{PLATFORMS[platform_key]['name']}] 正在搜索...")
            try:
                results[platform_key] = scraper.search(keyword)
            except Exception as e:
                logger.error(f"[{PLATFORMS[platform_key]['name']}] 搜索异常: {e}")
                results[platform_key] = [{'error': str(e)}]
            
            time.sleep(DELAY)
        
        return results
    
    def compare(self, keyword: str) -> Dict:
        """比较价格并生成报告"""
        results = self.search(keyword)
        comparison = {'keyword': keyword, 'platforms': {}}
        
        for platform, products in results.items():
            if products and 'error' not in products[0]:
                # 取第一个商品作为比较对象
                product = products[0]
                comparison['platforms'][PLATFORMS[platform]['name']] = product
        
        # 找出最便宜的
        if comparison['platforms']:
            cheapest = min(
                comparison['platforms'].items(),
                key=lambda x: float(x[1]['price'].replace('¥', '').replace(',', '') or 0)
            )
            comparison['cheapest'] = {'platform': cheapest[0], 'product': cheapest[1]}
        
        return comparison
