"""
修复爬虫问题的临时解决方案
Temporary solution to fix crawler issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.crawlers.openreview_crawler import OpenReviewCrawler
import logging
import yaml

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_iclr_2025():
    """测试ICLR 2025爬取"""
    
    # 加载配置
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 创建爬虫
    crawler = OpenReviewCrawler(config['crawler'])
    
    try:
        print("=" * 60)
        print("测试ICLR 2025论文爬取")
        print("=" * 60)
        
        # 测试不同年份
        test_years = [2024, 2023]  # 先测试已知有数据的年份
        
        for year in test_years:
            print(f"\n测试 ICLR {year}...")
            try:
                papers = crawler.crawl_papers(
                    conference='ICLR',
                    year=year,
                    keywords=None  # 不过滤关键词
                )
                
                print(f"ICLR {year}: 找到 {len(papers)} 篇论文")
                
                if papers:
                    print("前3篇论文:")
                    for i, paper in enumerate(papers[:3], 1):
                        print(f"  {i}. {paper.get('title', 'Unknown Title')}")
                    break  # 如果找到数据就停止测试
                
            except Exception as e:
                print(f"ICLR {year} 测试失败: {e}")
        
        # 现在测试2025年
        print(f"\n测试 ICLR 2025...")
        try:
            papers_2025 = crawler.crawl_papers(
                conference='ICLR',
                year=2025,
                keywords=None
            )
            
            print(f"ICLR 2025: 找到 {len(papers_2025)} 篇论文")
            
            if papers_2025:
                print("前3篇论文:")
                for i, paper in enumerate(papers_2025[:3], 1):
                    print(f"  {i}. {paper.get('title', 'Unknown Title')}")
            else:
                print("ICLR 2025 可能的原因:")
                print("1. 论文还未发布（通常在4-5月发布）")
                print("2. 还在审核阶段（submissions under review）")
                print("3. 网站结构发生变化")
                print("4. 需要特殊的访问权限")
                
                # 建议替代方案
                print("\n建议替代方案:")
                print("- 尝试爬取ICLR 2024的论文")
                print("- 或者等待ICLR 2025正式发布")
                
        except Exception as e:
            print(f"ICLR 2025 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    finally:
        crawler.close()

def suggest_alternatives():
    """建议替代方案"""
    print("\n" + "=" * 60)
    print("推荐的替代配置")
    print("=" * 60)
    
    alternatives = [
        {
            "name": "ICLR 2024 + 关键词过滤",
            "conferences": ["ICLR"],
            "years": [2024],
            "keywords": ["transformer", "diffusion", "large language model"]
        },
        {
            "name": "多会议 2023-2024",
            "conferences": ["ICLR", "CVPR", "NeurIPS"],
            "years": [2023, 2024],
            "keywords": ["AI", "machine learning"]
        },
        {
            "name": "计算机视觉专题",
            "conferences": ["CVPR", "ICCV"],
            "years": [2023, 2024],
            "keywords": ["computer vision", "image", "detection"]
        }
    ]
    
    for i, alt in enumerate(alternatives, 1):
        print(f"\n{i}. {alt['name']}")
        print(f"   会议: {', '.join(alt['conferences'])}")
        print(f"   年份: {', '.join(map(str, alt['years']))}")
        print(f"   关键词: {', '.join(alt['keywords'])}")

if __name__ == "__main__":
    test_iclr_2025()
    suggest_alternatives()