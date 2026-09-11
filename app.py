from flask import Flask, render_template, request, jsonify
import json
import logging
from scraper import PriceComparison
from config import FLASK_DEBUG, FLASK_PORT, FLASK_HOST

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['DEBUG'] = FLASK_DEBUG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

comparator = PriceComparison()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search():
    """搜索API"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({'error': '请输入商品名称'}), 400
        
        logger.info(f"搜索: {keyword}")
        results = comparator.search(keyword)
        comparison = comparator.compare(keyword)
        
        return jsonify({
            'success': True,
            'keyword': keyword,
            'results': results,
            'comparison': comparison
        })
    
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch', methods=['POST'])
def batch_search():
    """批量搜索API"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        
        if not keywords:
            return jsonify({'error': '请输入商品列表'}), 400
        
        results = []
        for keyword in keywords:
            keyword = keyword.strip()
            if keyword:
                logger.info(f"处理: {keyword}")
                comparison = comparator.compare(keyword)
                results.append(comparison)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
    
    except Exception as e:
        logger.error(f"批量搜索失败: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
