"""
AI学术论文监控系统 - 主程序
AI Academic Paper Monitoring System - Main Program

专为AI投资人设计的学术论文监控和分析系统
Academic paper monitoring and analysis system designed for AI investors

作者: AI Assistant
版本: 1.0.0
"""

import os
import sys
import logging
import argparse
import yaml
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.database import DatabaseManager
from src.crawlers.openreview_crawler import OpenReviewCrawler
from src.crawlers.cvf_crawler import CVFCrawler, ECCVCrawler
from src.scoring.investment_scorer import InvestmentScorer
from src.export.excel_exporter import ExcelExporter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/paper_monitor.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PaperMonitoringSystem:
    """
    AI学术论文监控系统主类
    Main class for AI Academic Paper Monitoring System
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化监控系统
        Initialize monitoring system
        
        Args:
            config_path: 配置文件路径 Configuration file path
        """
        self.config = self.load_config(config_path)
        self.db = DatabaseManager(self.config['database']['path'])
        self.scorer = InvestmentScorer(self.config)
        self.exporter = ExcelExporter(self.config)
        
        # 初始化爬虫
        self.crawlers = {
            'openreview': OpenReviewCrawler(self.config['crawler']),
            'cvf': CVFCrawler(self.config['crawler']),
            'eccv': ECCVCrawler(self.config['crawler'])
        }
        
        logger.info("AI学术论文监控系统初始化完成")
    
    def load_config(self, config_path: str) -> Dict:
        """
        加载配置文件
        Load configuration file
        
        Args:
            config_path: 配置文件路径 Configuration file path
            
        Returns:
            Dict: 配置字典 Configuration dictionary
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {config_path}")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def crawl_papers(self, 
                    conferences: Optional[List[str]] = None,
                    years: Optional[List[int]] = None,
                    keywords: Optional[List[str]] = None,
                    date_from: Optional[datetime] = None,
                    date_to: Optional[datetime] = None) -> List[Dict]:
        """
        爬取论文数据
        Crawl paper data
        
        Args:
            conferences: 会议列表 Conference list
            years: 年份列表 Year list
            keywords: 关键词列表 Keywords list
            date_from: 开始日期 Start date
            date_to: 结束日期 End date
            
        Returns:
            List[Dict]: 爬取的论文数据 Crawled paper data
        """
        logger.info("开始爬取论文数据")
        
        all_papers = []
        
        # 如果未指定会议，使用配置中的所有会议
        if not conferences:
            conferences = []
            for category in self.config['conferences'].values():
                conferences.extend([conf['name'] for conf in category])
        
        # 如果未指定年份，使用最近3年
        if not years:
            current_year = datetime.now().year
            years = [current_year - i for i in range(3)]
        
        # 遍历每个会议和年份
        for conference in conferences:
            for year in years:
                try:
                    logger.info(f"爬取 {conference} {year}")
                    
                    # 选择合适的爬虫
                    if conference.upper() in ['ICLR', 'ICML', 'NEURIPS']:
                        crawler = self.crawlers['openreview']
                    elif conference.upper() == 'ECCV':
                        crawler = self.crawlers['eccv']
                    elif conference.upper() in ['CVPR', 'ICCV', 'WACV']:
                        crawler = self.crawlers['cvf']
                    else:
                        logger.warning(f"不支持的会议: {conference}")
                        continue
                    
                    # 爬取论文
                    papers = crawler.crawl_papers(
                        conference=conference.upper(),
                        year=year,
                        keywords=keywords,
                        date_from=date_from,
                        date_to=date_to
                    )
                    
                    logger.info(f"{conference} {year} 爬取完成: {len(papers)} 篇论文")
                    all_papers.extend(papers)
                    
                except Exception as e:
                    logger.error(f"爬取 {conference} {year} 失败: {e}")
                    continue
        
        logger.info(f"论文爬取完成，共获得 {len(all_papers)} 篇论文")
        return all_papers
    
    def process_and_score_papers(self, papers_data: List[Dict]) -> List[Dict]:
        """
        处理和评分论文
        Process and score papers
        
        Args:
            papers_data: 论文数据列表 Paper data list
            
        Returns:
            List[Dict]: 评分后的论文数据 Scored paper data
        """
        logger.info(f"开始处理和评分 {len(papers_data)} 篇论文")
        
        # 批量评分
        scored_papers = self.scorer.batch_score_papers(papers_data)
        
        # 存储到数据库
        for paper in scored_papers:
            try:
                paper_id = self.db.add_paper(paper)
                paper['id'] = paper_id
            except Exception as e:
                logger.warning(f"存储论文失败: {e}")
                continue
        
        logger.info(f"论文处理完成，成功处理 {len(scored_papers)} 篇论文")
        return scored_papers
    
    def generate_report(self, papers_data: List[Dict], output_path: Optional[str] = None) -> str:
        """
        生成Excel报告
        Generate Excel report
        
        Args:
            papers_data: 论文数据列表 Paper data list
            output_path: 输出路径 Output path
            
        Returns:
            str: 报告文件路径 Report file path
        """
        logger.info("开始生成Excel报告")
        
        try:
            report_path = self.exporter.create_excel_report(papers_data, output_path)
            logger.info(f"Excel报告生成成功: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"生成Excel报告失败: {e}")
            raise
    
    def run_monitoring(self, 
                      conferences: Optional[List[str]] = None,
                      years: Optional[List[int]] = None,
                      keywords: Optional[List[str]] = None,
                      date_from: Optional[datetime] = None,
                      date_to: Optional[datetime] = None,
                      output_path: Optional[str] = None) -> str:
        """
        运行完整的监控流程
        Run complete monitoring workflow
        
        Args:
            conferences: 会议列表 Conference list
            years: 年份列表 Year list
            keywords: 关键词列表 Keywords list
            date_from: 开始日期 Start date
            date_to: 结束日期 End date
            output_path: 输出路径 Output path
            
        Returns:
            str: 生成的报告路径 Generated report path
        """
        try:
            logger.info("=" * 60)
            logger.info("AI学术论文监控系统 - 开始运行")
            logger.info("=" * 60)
            
            # 1. 爬取论文数据
            papers_data = self.crawl_papers(
                conferences=conferences,
                years=years,
                keywords=keywords,
                date_from=date_from,
                date_to=date_to
            )
            
            if not papers_data:
                logger.warning("未获得任何论文数据")
                return ""
            
            # 2. 处理和评分论文
            scored_papers = self.process_and_score_papers(papers_data)
            
            # 3. 生成Excel报告
            report_path = self.generate_report(scored_papers, output_path)
            
            # 4. 输出统计信息
            self.print_statistics(scored_papers)
            
            logger.info("=" * 60)
            logger.info("AI学术论文监控系统 - 运行完成")
            logger.info(f"报告文件: {report_path}")
            logger.info("=" * 60)
            
            return report_path
            
        except Exception as e:
            logger.error(f"监控系统运行失败: {e}")
            raise
    
    def print_statistics(self, papers_data: List[Dict]):
        """
        打印统计信息
        Print statistics
        
        Args:
            papers_data: 论文数据列表 Paper data list
        """
        try:
            total_papers = len(papers_data)
            high_value_papers = len([p for p in papers_data if p.get('investment_score', 0) >= 8.0])
            avg_score = sum([p.get('investment_score', 0) for p in papers_data]) / total_papers if total_papers > 0 else 0
            
            # 按会议统计
            conference_stats = {}
            for paper in papers_data:
                conf = paper.get('conference', 'Unknown')
                if conf not in conference_stats:
                    conference_stats[conf] = 0
                conference_stats[conf] += 1
            
            logger.info("\n" + "=" * 40)
            logger.info("统计信息汇总")
            logger.info("=" * 40)
            logger.info(f"论文总数: {total_papers}")
            logger.info(f"高价值论文数 (评分≥8.0): {high_value_papers}")
            logger.info(f"平均投资评分: {avg_score:.2f}")
            logger.info(f"高价值比例: {high_value_papers/total_papers*100:.1f}%" if total_papers > 0 else "0%")
            
            logger.info("\n按会议分布:")
            for conf, count in sorted(conference_stats.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {conf}: {count} 篇")
            
            # 显示投资价值最高的论文
            top_papers = sorted(papers_data, key=lambda x: x.get('investment_score', 0), reverse=True)[:5]
            logger.info("\n投资价值最高的5篇论文:")
            for i, paper in enumerate(top_papers, 1):
                title = paper.get('title', 'Unknown')[:50]
                score = paper.get('investment_score', 0)
                conf = paper.get('conference', 'Unknown')
                year = paper.get('year', 'Unknown')
                logger.info(f"  {i}. [{conf} {year}] {title}... (评分: {score:.2f})")
            
        except Exception as e:
            logger.error(f"打印统计信息失败: {e}")
    
    def close(self):
        """
        关闭系统资源
        Close system resources
        """
        try:
            self.db.close()
            for crawler in self.crawlers.values():
                crawler.close()
            logger.info("系统资源已关闭")
        except Exception as e:
            logger.error(f"关闭系统资源失败: {e}")


def parse_arguments():
    """
    解析命令行参数
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description="AI学术论文监控系统 - 专为投资人设计的论文分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 爬取所有支持的会议最近3年的论文
  python main.py
  
  # 指定会议和年份
  python main.py --conferences ICLR CVPR --years 2023 2024
  
  # 使用关键词过滤
  python main.py --keywords "transformer" "diffusion model"
  
  # 指定输出文件
  python main.py --output reports/ai_papers_2024.xlsx
  
  # 指定日期范围 (格式: YYYY-MM-DD)
  python main.py --date-from 2024-01-01 --date-to 2024-12-31
        """
    )
    
    parser.add_argument(
        '--conferences', '-c',
        nargs='+',
        help='指定要爬取的会议 (如: ICLR CVPR ICCV)',
        default=None
    )
    
    parser.add_argument(
        '--years', '-y',
        nargs='+',
        type=int,
        help='指定要爬取的年份 (如: 2023 2024)',
        default=None
    )
    
    parser.add_argument(
        '--keywords', '-k',
        nargs='+',
        help='指定关键词过滤 (如: "transformer" "diffusion")',
        default=None
    )
    
    parser.add_argument(
        '--date-from',
        type=str,
        help='开始日期 (格式: YYYY-MM-DD)',
        default=None
    )
    
    parser.add_argument(
        '--date-to',
        type=str,
        help='结束日期 (格式: YYYY-MM-DD)',
        default=None
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='输出文件路径',
        default=None
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='配置文件路径',
        default='config/config.yaml'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出'
    )
    
    return parser.parse_args()


def main():
    """
    主函数
    Main function
    """
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 设置日志级别
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # 确保必要的目录存在
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        
        # 解析日期参数
        date_from = None
        date_to = None
        if args.date_from:
            date_from = datetime.strptime(args.date_from, '%Y-%m-%d')
        if args.date_to:
            date_to = datetime.strptime(args.date_to, '%Y-%m-%d')
        
        # 初始化监控系统
        monitor = PaperMonitoringSystem(args.config)
        
        try:
            # 运行监控
            report_path = monitor.run_monitoring(
                conferences=args.conferences,
                years=args.years,
                keywords=args.keywords,
                date_from=date_from,
                date_to=date_to,
                output_path=args.output
            )
            
            if report_path:
                print(f"\n✅ 监控完成！Excel报告已生成: {report_path}")
                print(f"📊 请查看报告了解详细的投资分析结果")
            else:
                print("\n⚠️  未生成报告，请检查日志了解详情")
                
        finally:
            # 清理资源
            monitor.close()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        print(f"\n❌ 程序运行失败: {e}")
        print("📋 请查看日志文件了解详细错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()