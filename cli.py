#!/usr/bin/env python3
"""
命令行工具 - 直接在终端使用
"""

import argparse
import csv
import sys
import logging
from pathlib import Path
from tabulate import tabulate
from scraper import PriceComparison
from config import PLATFORMS

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class PriceCLI:
    """命令行接口"""
    
    def __init__(self):
        self.comparator = PriceComparison()
    
    def search_single(self, keyword: str, output_file: str = None) -> None:
        """搜索单个商品"""
        logger.info(f"🔍 搜索商品: {keyword}\n")
        
        results = self.comparator.search(keyword)
        
        # 组织数据用于表格显示
        table_data = []
        for platform_key, products in results.items():
            if products and 'error' not in products[0]:
                product = products[0]
                table_data.append([
                    PLATFORMS[platform_key]['name'],
                    product.get('title', '').split()[0][:20],  # 简化标题
                    product.get('price', '暂无'),
                    product.get('sales', '暂无'),
                    product.get('rating', '暂无'),
                ])
            else:
                table_data.append([
                    PLATFORMS[platform_key]['name'],
                    '❌ 获取失败',
                    '-', '-', '-',
                ])
        
        # 显示表格
        headers = ['平台', '商品名', '价格', '销量', '评分']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # 显示比价结果
        comparison = self.comparator.compare(keyword)
        if 'cheapest' in comparison:
            logger.info(f"\n💡 推荐购买: {comparison['cheapest']['platform']} "
                       f"({comparison['cheapest']['product']['price']})")
        
        # 保存到文件
        if output_file:
            self._save_to_csv(keyword, results, output_file)
            logger.info(f"\n✅ 结果已保存到: {output_file}")
    
    def batch_search(self, csv_file: str, output_file: str = None) -> None:
        """批量搜索"""
        if not Path(csv_file).exists():
            logger.error(f"❌ 文件不存在: {csv_file}")
            sys.exit(1)
        
        logger.info(f"📁 批量处理: {csv_file}\n")
        
        results_all = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # 跳过表头
            next(reader, None)
            
            for row in reader:
                if not row or not row[0].strip():
                    continue
                
                keyword = row[0].strip()
                logger.info(f"🔍 处理: {keyword}")
                
                comparison = self.comparator.compare(keyword)
                results_all.append(comparison)
        
        # 保存批量结果
        if output_file:
            self._save_batch_to_csv(results_all, output_file)
            logger.info(f"\n✅ 批量结果已保存到: {output_file}")
        else:
            # 打印摘要
            self._print_summary(results_all)
    
    def _save_to_csv(self, keyword: str, results: dict, filename: str) -> None:
        """保存单个搜索结果到 CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['商品名', '平台', '价格', '销量', '评分', '链接'])
            
            for platform_key, products in results.items():
                if products and 'error' not in products[0]:
                    for product in products[:1]:  # 仅保存第一个
                        writer.writerow([
                            keyword,
                            PLATFORMS[platform_key]['name'],
                            product.get('price', '-'),
                            product.get('sales', '-'),
                            product.get('rating', '-'),
                            product.get('link', '-'),
                        ])
    
    def _save_batch_to_csv(self, comparisons: list, filename: str) -> None:
        """保存批量结果到 CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['商品名', '淘宝价格', '京东价格', '拼多多价格', '最便宜平台', '省钱金额'])
            
            for comparison in comparisons:
                keyword = comparison['keyword']
                platforms = comparison.get('platforms', {})
                cheapest = comparison.get('cheapest', {})
                
                taobao_price = platforms.get('淘宝', {}).get('price', '-')
                jd_price = platforms.get('京东', {}).get('price', '-')
                pdd_price = platforms.get('拼多多', {}).get('price', '-')
                
                writer.writerow([
                    keyword,
                    taobao_price,
                    jd_price,
                    pdd_price,
                    cheapest.get('platform', '-'),
                    '计算中...',  # 可扩展
                ])
    
    def _print_summary(self, comparisons: list) -> None:
        """打印摘要"""
        logger.info("\n" + "="*50)
        logger.info("批量搜索摘要")
        logger.info("="*50)
        
        for comparison in comparisons:
            logger.info(f"\n商品: {comparison['keyword']}")
            if 'cheapest' in comparison:
                logger.info(f"  最便宜: {comparison['cheapest']['platform']} "
                           f"({comparison['cheapest']['product']['price']})")


def main():
    parser = argparse.ArgumentParser(
        description='🛒 电商比价工具 - 淘宝、京东、拼多多',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  单个搜索:  python cli.py "iPhone 15"
  批量搜索:  python cli.py --batch products.csv
  保存结果:  python cli.py "iPhone 15" --output result.csv
        """
    )
    
    parser.add_argument('keyword', nargs='?', help='搜索关键词')
    parser.add_argument('--batch', help='批量搜索文件 (CSV格式)')
    parser.add_argument('--output', '-o', help='输出文件名 (CSV格式)')
    parser.add_argument('--platform', '-p', choices=['taobao', 'jd', 'pdd'], 
                       help='指定单个平台搜索')
    
    args = parser.parse_args()
    
    cli = PriceCLI()
    
    try:
        if args.batch:
            cli.batch_search(args.batch, args.output)
        elif args.keyword:
            cli.search_single(args.keyword, args.output)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        logger.info("\n⏹️  已中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
