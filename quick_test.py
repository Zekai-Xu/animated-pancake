#!/usr/bin/env python3
"""
快速测试脚本 - 验证系统基本功能
Quick test script - Verify basic system functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from datetime import datetime

# 配置简单的日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def test_basic_functionality():
    """测试基本功能"""
    print("🚀 AI学术论文监控系统 - 快速测试")
    print("=" * 50)
    
    # 1. 测试导入
    print("\n1. 测试模块导入...")
    try:
        from main import PaperMonitoringSystem
        print("✅ 主系统导入成功")
        
        from src.core.database import DatabaseManager
        print("✅ 数据库模块导入成功")
        
        from src.scoring.investment_scorer import InvestmentScorer
        print("✅ 评分模块导入成功")
        
        from src.export.excel_exporter import ExcelExporter
        print("✅ 导出模块导入成功")
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    
    # 2. 测试配置文件
    print("\n2. 测试配置文件...")
    try:
        import yaml
        with open('config/config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print("✅ 配置文件加载成功")
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False
    
    # 3. 测试数据库连接
    print("\n3. 测试数据库连接...")
    try:
        db = DatabaseManager("data/test_papers.db")
        
        # 测试添加示例数据
        sample_paper = {
            'title': 'Test Paper',
            'authors': '["Test Author"]',
            'conference': 'Test Conference',
            'year': 2024,
            'investment_score': 7.5,
            'investment_recommendation': '推荐关注'
        }
        
        paper_id = db.add_paper(sample_paper)
        print(f"✅ 数据库连接成功，测试论文ID: {paper_id}")
        
        # 测试搜索
        papers = db.search_papers(limit=1)
        print(f"✅ 数据库搜索成功，找到 {len(papers)} 篇论文")
        
        db.close()
        
        # 清理测试数据库
        if os.path.exists("data/test_papers.db"):
            os.remove("data/test_papers.db")
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False
    
    # 4. 测试评分系统
    print("\n4. 测试评分系统...")
    try:
        scorer = InvestmentScorer(config)
        
        test_paper = {
            'title': 'Attention Is All You Need',
            'abstract': 'The dominant sequence transduction models are based on complex recurrent neural networks.',
            'authors': '["Ashish Vaswani", "Noam Shazeer"]',
            'keywords': '["transformer", "attention"]',
            'conference': 'NeurIPS',
            'year': 2017
        }
        
        result = scorer.score_paper(test_paper)
        print(f"✅ 评分系统正常，测试论文评分: {result['investment_score']}")
        
    except Exception as e:
        print(f"❌ 评分系统测试失败: {e}")
        return False
    
    # 5. 测试Excel导出
    print("\n5. 测试Excel导出...")
    try:
        exporter = ExcelExporter(config)
        
        # 创建测试数据
        test_papers = [{
            'id': 1,
            'title': 'Test Paper for Export',
            'authors': '["Test Author"]',
            'conference': 'Test Conference',
            'year': 2024,
            'investment_score': 8.0,
            'investment_recommendation': '强烈推荐',
            'technical_depth_score': 7.5,
            'novelty_score': 8.5,
            'commercial_potential_score': 7.0,
            'keywords': '["test", "export"]',
            'created_at': datetime.now()
        }]
        
        # 测试数据准备
        overview_df = exporter.prepare_overview_data(test_papers)
        print(f"✅ Excel数据准备成功，数据行数: {len(overview_df)}")
        
    except Exception as e:
        print(f"❌ Excel导出测试失败: {e}")
        return False
    
    print("\n🎉 所有基本功能测试通过！")
    return True

def test_recommended_config():
    """测试推荐配置"""
    print("\n" + "=" * 50)
    print("📋 推荐的测试配置")
    print("=" * 50)
    
    configs = [
        {
            "name": "🔥 推荐配置 1: ICLR 2024 热门关键词",
            "conferences": ["ICLR"],
            "years": [2024],
            "keywords": ["transformer", "diffusion model"],
            "reason": "ICLR 2024数据稳定，热门关键词确保有结果"
        },
        {
            "name": "🌟 推荐配置 2: 多会议 2023年",
            "conferences": ["ICLR", "CVPR"],
            "years": [2023],
            "keywords": ["deep learning"],
            "reason": "2023年数据完整，多会议增加数据量"
        },
        {
            "name": "🎯 推荐配置 3: 计算机视觉专题",
            "conferences": ["CVPR"],
            "years": [2024],
            "keywords": ["object detection", "image segmentation"],
            "reason": "CVPR是CV顶会，相关论文质量高"
        }
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n{config['name']}")
        print(f"   会议: {', '.join(config['conferences'])}")
        print(f"   年份: {', '.join(map(str, config['years']))}")
        print(f"   关键词: {', '.join(config['keywords'])}")
        print(f"   原因: {config['reason']}")

def main():
    """主函数"""
    try:
        # 确保必要目录存在
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        
        # 运行基本功能测试
        if test_basic_functionality():
            test_recommended_config()
            
            print("\n" + "=" * 50)
            print("🚀 系统就绪！")
            print("=" * 50)
            print("\n启动方式:")
            print("1. Web界面: streamlit run gui.py")
            print("2. 命令行: python main.py --help")
            print("3. 一键启动: ./run.sh gui")
            
            print("\n💡 解决0篇论文问题的建议:")
            print("1. 使用上述推荐配置之一")
            print("2. 避免选择2025年（论文可能未发布）")
            print("3. 添加关键词过滤提高成功率")
            print("4. 检查网络连接和代理设置")
        else:
            print("\n❌ 基本功能测试失败，请检查安装")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)