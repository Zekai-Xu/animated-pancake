"""
投资评分模块 - AI学术论文监控系统
Investment Scoring Module - AI Academic Paper Monitoring System

该模块负责对学术论文进行投资价值评分和分析
This module handles investment value scoring and analysis of academic papers
"""

import logging
import re
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import requests
from dataclasses import dataclass
import numpy as np

# 第三方库用于学术数据获取
try:
    from scholarly import scholarly
    SCHOLARLY_AVAILABLE = True
except ImportError:
    SCHOLARLY_AVAILABLE = False
    logging.warning("scholarly库未安装，将跳过作者H指数查询")

try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False
    logging.warning("arxiv库未安装，将跳过arXiv数据查询")

logger = logging.getLogger(__name__)


@dataclass
class InvestmentMetrics:
    """
    投资指标数据类
    Investment metrics data class
    """
    citation_count: int = 0
    citation_growth_rate: float = 0.0
    author_max_h_index: float = 0.0
    venue_impact_factor: float = 0.0
    novelty_score: float = 0.0
    technical_depth_score: float = 0.0
    commercial_potential_score: float = 0.0
    market_size_estimate: str = "未知"
    technology_maturity: str = "研究阶段"
    startup_indicators: bool = False
    industry_partnerships: List[str] = None
    
    def __post_init__(self):
        if self.industry_partnerships is None:
            self.industry_partnerships = []


class InvestmentScorer:
    """
    投资评分器
    Investment scorer for academic papers
    """
    
    def __init__(self, config: Dict):
        """
        初始化投资评分器
        Initialize investment scorer
        
        Args:
            config: 配置字典 Configuration dictionary
        """
        self.config = config
        self.scoring_weights = config.get('scoring', {}).get('weights', {
            'citation_count': 0.25,
            'citation_growth': 0.20,
            'author_h_index': 0.15,
            'venue_impact': 0.15,
            'novelty_score': 0.10,
            'technical_depth': 0.10,
            'commercial_potential': 0.05
        })
        
        self.thresholds = config.get('scoring', {}).get('thresholds', {
            'min_citation_count': 5,
            'min_h_index': 10,
            'min_venue_rank': 0.7,
            'investment_score_threshold': 7.0
        })
        
        # 会议影响因子 (基于经验数据)
        self.venue_impact_factors = {
            'CVPR': 9.5, 'ICCV': 9.0, 'ECCV': 8.5, 'WACV': 6.5,
            'ICLR': 9.8, 'ICML': 9.5, 'NeurIPS': 9.8,
            'AAAI': 8.0, 'IJCAI': 8.5, 'KDD': 8.0,
            'SIGIR': 7.5, 'WWW': 7.0, 'EMNLP': 8.0, 'ACL': 8.5
        }
        
        # 热门技术领域和商业化潜力映射
        self.tech_commercial_mapping = {
            'large language model': {'maturity': '发展阶段', 'market': '千亿级', 'potential': 9.5},
            'llm': {'maturity': '发展阶段', 'market': '千亿级', 'potential': 9.5},
            'diffusion model': {'maturity': '发展阶段', 'market': '百亿级', 'potential': 9.0},
            'transformer': {'maturity': '商业化', 'market': '千亿级', 'potential': 9.0},
            'computer vision': {'maturity': '商业化', 'market': '千亿级', 'potential': 8.5},
            'autonomous driving': {'maturity': '发展阶段', 'market': '万亿级', 'potential': 9.5},
            'robotics': {'maturity': '发展阶段', 'market': '千亿级', 'potential': 8.5},
            'multimodal': {'maturity': '研究阶段', 'market': '百亿级', 'potential': 8.0},
            'federated learning': {'maturity': '研究阶段', 'market': '百亿级', 'potential': 7.5},
            'edge computing': {'maturity': '发展阶段', 'market': '千亿级', 'potential': 8.0},
            'quantum machine learning': {'maturity': '研究阶段', 'market': '千亿级', 'potential': 7.0}
        }
        
        # 知名科技公司和机构
        self.top_institutions = {
            'google', 'microsoft', 'openai', 'anthropic', 'meta', 'apple', 'nvidia',
            'stanford', 'mit', 'berkeley', 'cmu', 'harvard', 'oxford', 'cambridge',
            'deepmind', 'tesla', 'uber', 'amazon', 'alibaba', 'tencent', 'baidu'
        }
        
        logger.info("投资评分器初始化完成")
    
    def get_citation_count(self, title: str, authors: List[str]) -> Tuple[int, float]:
        """
        获取论文引用数和增长率
        Get paper citation count and growth rate
        
        Args:
            title: 论文标题 Paper title
            authors: 作者列表 Authors list
            
        Returns:
            Tuple[int, float]: (引用数, 增长率) (citation count, growth rate)
        """
        try:
            if not SCHOLARLY_AVAILABLE:
                return 0, 0.0
            
            # 搜索论文
            search_query = f'"{title}"'
            if authors:
                search_query += f' author:"{authors[0]}"'
            
            search_results = scholarly.search_pubs(search_query)
            
            for result in search_results:
                # 检查标题相似度
                if self._calculate_title_similarity(title, result.get('title', '')) > 0.8:
                    citation_count = result.get('num_citations', 0)
                    
                    # 估算增长率 (基于发表年份)
                    pub_year = result.get('pub_year')
                    growth_rate = 0.0
                    if pub_year and citation_count > 0:
                        years_since_pub = datetime.now().year - pub_year
                        if years_since_pub > 0:
                            growth_rate = citation_count / years_since_pub / 12  # 月增长率
                    
                    return citation_count, growth_rate
            
            return 0, 0.0
            
        except Exception as e:
            logger.warning(f"获取引用数失败: {e}")
            return 0, 0.0
    
    def get_author_h_index(self, authors: List[str]) -> float:
        """
        获取作者最高H指数
        Get maximum H-index among authors
        
        Args:
            authors: 作者列表 Authors list
            
        Returns:
            float: 最高H指数 Maximum H-index
        """
        try:
            if not SCHOLARLY_AVAILABLE or not authors:
                return 0.0
            
            max_h_index = 0.0
            
            for author in authors[:3]:  # 只查询前3个作者以节省时间
                try:
                    search_results = scholarly.search_author(author)
                    author_info = next(search_results, None)
                    
                    if author_info:
                        # 获取详细信息
                        author_detail = scholarly.fill(author_info)
                        h_index = author_detail.get('hindex', 0)
                        max_h_index = max(max_h_index, h_index)
                
                except Exception as e:
                    logger.debug(f"查询作者 {author} H指数失败: {e}")
                    continue
            
            return float(max_h_index)
            
        except Exception as e:
            logger.warning(f"获取作者H指数失败: {e}")
            return 0.0
    
    def calculate_novelty_score(self, title: str, abstract: str, keywords: List[str]) -> float:
        """
        计算新颖性评分
        Calculate novelty score based on content analysis
        
        Args:
            title: 论文标题 Paper title
            abstract: 论文摘要 Paper abstract
            keywords: 关键词列表 Keywords list
            
        Returns:
            float: 新颖性评分 (1-10) Novelty score (1-10)
        """
        try:
            text = f"{title} {abstract}".lower()
            score = 5.0  # 基础分数
            
            # 新颖性指标词汇
            novelty_indicators = {
                'high': ['novel', 'new', 'first', 'unprecedented', 'breakthrough', 'revolutionary', 
                        'innovative', 'pioneering', 'groundbreaking', 'cutting-edge'],
                'medium': ['improved', 'enhanced', 'advanced', 'superior', 'better', 'efficient',
                          'effective', 'optimized', 'refined'],
                'technical': ['algorithm', 'method', 'approach', 'technique', 'framework', 
                             'architecture', 'model', 'system']
            }
            
            # 计算新颖性指标
            for indicator_type, words in novelty_indicators.items():
                count = sum(1 for word in words if word in text)
                if indicator_type == 'high':
                    score += count * 0.5  # 高新颖性词汇权重更高
                elif indicator_type == 'medium':
                    score += count * 0.3
                elif indicator_type == 'technical':
                    score += count * 0.1
            
            # 基于关键词的新颖性评估
            emerging_keywords = [
                'large language model', 'diffusion', 'transformer', 'attention',
                'multimodal', 'foundation model', 'few-shot', 'zero-shot',
                'self-supervised', 'contrastive learning', 'meta-learning'
            ]
            
            for keyword in keywords:
                if keyword.lower() in emerging_keywords:
                    score += 0.3
            
            # 限制分数范围
            score = min(max(score, 1.0), 10.0)
            
            return round(score, 2)
            
        except Exception as e:
            logger.warning(f"计算新颖性评分失败: {e}")
            return 5.0
    
    def calculate_technical_depth_score(self, title: str, abstract: str) -> float:
        """
        计算技术深度评分
        Calculate technical depth score
        
        Args:
            title: 论文标题 Paper title
            abstract: 论文摘要 Paper abstract
            
        Returns:
            float: 技术深度评分 (1-10) Technical depth score (1-10)
        """
        try:
            text = f"{title} {abstract}".lower()
            score = 5.0
            
            # 技术深度指标
            depth_indicators = {
                'mathematical': ['theorem', 'proof', 'optimization', 'convergence', 'complexity',
                               'analysis', 'bounds', 'guarantee', 'theoretical'],
                'experimental': ['experiment', 'evaluation', 'benchmark', 'dataset', 'baseline',
                               'comparison', 'ablation', 'results', 'performance'],
                'implementation': ['implementation', 'system', 'architecture', 'design',
                                 'scalable', 'efficient', 'practical']
            }
            
            for indicator_type, words in depth_indicators.items():
                count = sum(1 for word in words if word in text)
                score += count * 0.2
            
            # 数学公式和技术术语的存在
            math_indicators = ['equation', 'formula', 'matrix', 'vector', 'gradient',
                             'loss function', 'objective', 'constraint']
            math_count = sum(1 for word in math_indicators if word in text)
            score += math_count * 0.3
            
            # 限制分数范围
            score = min(max(score, 1.0), 10.0)
            
            return round(score, 2)
            
        except Exception as e:
            logger.warning(f"计算技术深度评分失败: {e}")
            return 5.0
    
    def calculate_commercial_potential_score(self, title: str, abstract: str, 
                                           keywords: List[str], authors: List[str]) -> Dict:
        """
        计算商业化潜力评分
        Calculate commercial potential score
        
        Args:
            title: 论文标题 Paper title
            abstract: 论文摘要 Paper abstract
            keywords: 关键词列表 Keywords list
            authors: 作者列表 Authors list
            
        Returns:
            Dict: 商业化潜力信息 Commercial potential information
        """
        try:
            text = f"{title} {abstract}".lower()
            score = 3.0  # 基础分数
            market_size = "未知"
            maturity = "研究阶段"
            startup_indicators = False
            industry_partnerships = []
            
            # 检查热门技术领域
            for tech, info in self.tech_commercial_mapping.items():
                if tech in text:
                    score = max(score, info['potential'])
                    market_size = info['market']
                    maturity = info['maturity']
                    break
            
            # 商业化指标词汇
            commercial_indicators = [
                'industry', 'production', 'deployment', 'real-world', 'practical',
                'commercial', 'application', 'market', 'business', 'scalable',
                'cost-effective', 'efficient', 'user-friendly'
            ]
            
            commercial_count = sum(1 for word in commercial_indicators if word in text)
            score += commercial_count * 0.3
            
            # 检查知名机构/公司
            author_text = ' '.join(authors).lower()
            for institution in self.top_institutions:
                if institution in author_text:
                    score += 0.5
                    industry_partnerships.append(institution.title())
                    if institution in ['google', 'microsoft', 'openai', 'meta', 'nvidia']:
                        startup_indicators = True
            
            # 创业公司指标
            startup_keywords = ['startup', 'founding', 'ceo', 'cto', 'entrepreneur']
            if any(keyword in text for keyword in startup_keywords):
                startup_indicators = True
                score += 0.5
            
            # 限制分数范围
            score = min(max(score, 1.0), 10.0)
            
            return {
                'score': round(score, 2),
                'market_size': market_size,
                'maturity': maturity,
                'startup_indicators': startup_indicators,
                'industry_partnerships': industry_partnerships
            }
            
        except Exception as e:
            logger.warning(f"计算商业化潜力失败: {e}")
            return {
                'score': 3.0,
                'market_size': "未知",
                'maturity': "研究阶段",
                'startup_indicators': False,
                'industry_partnerships': []
            }
    
    def get_venue_impact_factor(self, conference: str) -> float:
        """
        获取会议影响因子
        Get venue impact factor
        
        Args:
            conference: 会议名称 Conference name
            
        Returns:
            float: 影响因子 Impact factor
        """
        return self.venue_impact_factors.get(conference.upper(), 5.0)
    
    def calculate_investment_score(self, metrics: InvestmentMetrics) -> Tuple[float, str]:
        """
        计算综合投资评分
        Calculate comprehensive investment score
        
        Args:
            metrics: 投资指标 Investment metrics
            
        Returns:
            Tuple[float, str]: (投资评分, 投资建议) (investment score, recommendation)
        """
        try:
            # 归一化各项指标到0-10分
            normalized_scores = {}
            
            # 引用数评分 (对数缩放)
            if metrics.citation_count > 0:
                normalized_scores['citation'] = min(math.log10(metrics.citation_count + 1) * 2, 10)
            else:
                normalized_scores['citation'] = 0
            
            # 引用增长率评分
            normalized_scores['growth'] = min(metrics.citation_growth_rate * 2, 10)
            
            # H指数评分
            normalized_scores['h_index'] = min(metrics.author_max_h_index / 10, 10)
            
            # 会议影响因子评分
            normalized_scores['venue'] = min(metrics.venue_impact_factor, 10)
            
            # 新颖性和技术深度评分
            normalized_scores['novelty'] = metrics.novelty_score
            normalized_scores['technical'] = metrics.technical_depth_score
            
            # 商业化潜力评分
            normalized_scores['commercial'] = metrics.commercial_potential_score
            
            # 加权计算综合评分
            total_score = (
                normalized_scores['citation'] * self.scoring_weights.get('citation_count', 0.25) +
                normalized_scores['growth'] * self.scoring_weights.get('citation_growth', 0.20) +
                normalized_scores['h_index'] * self.scoring_weights.get('author_h_index', 0.15) +
                normalized_scores['venue'] * self.scoring_weights.get('venue_impact', 0.15) +
                normalized_scores['novelty'] * self.scoring_weights.get('novelty_score', 0.10) +
                normalized_scores['technical'] * self.scoring_weights.get('technical_depth', 0.10) +
                normalized_scores['commercial'] * self.scoring_weights.get('commercial_potential', 0.05)
            )
            
            # 额外加分项
            if metrics.startup_indicators:
                total_score += 0.5
            
            if len(metrics.industry_partnerships) > 0:
                total_score += 0.3
            
            # 限制分数范围
            total_score = min(max(total_score, 0.0), 10.0)
            
            # 投资建议
            if total_score >= 8.0:
                recommendation = "强烈推荐"
            elif total_score >= 6.5:
                recommendation = "推荐关注"
            elif total_score >= 5.0:
                recommendation = "一般关注"
            else:
                recommendation = "暂不关注"
            
            return round(total_score, 2), recommendation
            
        except Exception as e:
            logger.error(f"计算投资评分失败: {e}")
            return 5.0, "评分失败"
    
    def score_paper(self, paper_data: Dict) -> Dict:
        """
        对单篇论文进行完整的投资评分
        Complete investment scoring for a single paper
        
        Args:
            paper_data: 论文数据 Paper data
            
        Returns:
            Dict: 评分结果 Scoring results
        """
        try:
            logger.info(f"开始评分论文: {paper_data.get('title', 'Unknown')}")
            
            # 提取基本信息
            title = paper_data.get('title', '')
            abstract = paper_data.get('abstract', '')
            authors_json = paper_data.get('authors', '[]')
            keywords_json = paper_data.get('keywords', '[]')
            conference = paper_data.get('conference', '')
            
            # 解析JSON字符串
            try:
                authors = json.loads(authors_json) if isinstance(authors_json, str) else authors_json
                keywords = json.loads(keywords_json) if isinstance(keywords_json, str) else keywords_json
            except json.JSONDecodeError:
                authors = []
                keywords = []
            
            # 获取引用数据 (可选，耗时较长)
            citation_count, citation_growth = 0, 0.0
            # citation_count, citation_growth = self.get_citation_count(title, authors)
            
            # 获取作者H指数 (可选，耗时较长)
            author_h_index = 0.0
            # author_h_index = self.get_author_h_index(authors)
            
            # 计算各项评分
            novelty_score = self.calculate_novelty_score(title, abstract, keywords)
            technical_depth = self.calculate_technical_depth_score(title, abstract)
            commercial_info = self.calculate_commercial_potential_score(title, abstract, keywords, authors)
            venue_impact = self.get_venue_impact_factor(conference)
            
            # 创建指标对象
            metrics = InvestmentMetrics(
                citation_count=citation_count,
                citation_growth_rate=citation_growth,
                author_max_h_index=author_h_index,
                venue_impact_factor=venue_impact,
                novelty_score=novelty_score,
                technical_depth_score=technical_depth,
                commercial_potential_score=commercial_info['score'],
                market_size_estimate=commercial_info['market_size'],
                technology_maturity=commercial_info['maturity'],
                startup_indicators=commercial_info['startup_indicators'],
                industry_partnerships=commercial_info['industry_partnerships']
            )
            
            # 计算综合投资评分
            investment_score, recommendation = self.calculate_investment_score(metrics)
            
            # 返回评分结果
            result = {
                'investment_score': investment_score,
                'investment_recommendation': recommendation,
                'citation_count': citation_count,
                'citation_growth_rate': citation_growth,
                'h_index_max': author_h_index,
                'venue_impact_factor': venue_impact,
                'technical_depth_score': technical_depth,
                'novelty_score': novelty_score,
                'commercial_potential_score': commercial_info['score'],
                'market_size_estimate': commercial_info['market_size'],
                'technology_maturity': commercial_info['maturity'],
                'startup_indicators': commercial_info['startup_indicators'],
                'industry_partnerships': json.dumps(commercial_info['industry_partnerships'], ensure_ascii=False),
                'scoring_details': {
                    'citation_normalized': min(math.log10(citation_count + 1) * 2, 10) if citation_count > 0 else 0,
                    'growth_normalized': min(citation_growth * 2, 10),
                    'h_index_normalized': min(author_h_index / 10, 10),
                    'venue_normalized': min(venue_impact, 10),
                    'weights_used': self.scoring_weights
                }
            }
            
            logger.info(f"论文评分完成: {title[:50]}... -> 投资评分: {investment_score}")
            return result
            
        except Exception as e:
            logger.error(f"论文评分失败: {e}")
            return {
                'investment_score': 5.0,
                'investment_recommendation': '评分失败',
                'error': str(e)
            }
    
    def batch_score_papers(self, papers_data: List[Dict]) -> List[Dict]:
        """
        批量评分论文
        Batch scoring of papers
        
        Args:
            papers_data: 论文数据列表 List of paper data
            
        Returns:
            List[Dict]: 评分结果列表 List of scoring results
        """
        logger.info(f"开始批量评分 {len(papers_data)} 篇论文")
        
        scored_papers = []
        for i, paper in enumerate(papers_data):
            try:
                score_result = self.score_paper(paper)
                
                # 合并原始数据和评分结果
                scored_paper = {**paper, **score_result}
                scored_papers.append(scored_paper)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"已完成评分: {i + 1}/{len(papers_data)}")
                    
            except Exception as e:
                logger.error(f"评分论文 {i+1} 失败: {e}")
                continue
        
        logger.info(f"批量评分完成，成功评分 {len(scored_papers)} 篇论文")
        return scored_papers
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        计算标题相似度
        Calculate title similarity
        
        Args:
            title1: 标题1 Title 1
            title2: 标题2 Title 2
            
        Returns:
            float: 相似度 (0-1) Similarity (0-1)
        """
        try:
            # 简单的基于词汇重叠的相似度计算
            words1 = set(title1.lower().split())
            words2 = set(title2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0


# 使用示例
if __name__ == "__main__":
    # 示例配置
    config = {
        'scoring': {
            'weights': {
                'citation_count': 0.25,
                'citation_growth': 0.20,
                'author_h_index': 0.15,
                'venue_impact': 0.15,
                'novelty_score': 0.10,
                'technical_depth': 0.10,
                'commercial_potential': 0.05
            },
            'thresholds': {
                'investment_score_threshold': 7.0
            }
        }
    }
    
    # 创建评分器
    scorer = InvestmentScorer(config)
    
    # 示例论文数据
    sample_paper = {
        'title': 'Attention Is All You Need',
        'abstract': 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.',
        'authors': '["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"]',
        'keywords': '["transformer", "attention", "neural machine translation"]',
        'conference': 'NeurIPS',
        'year': 2017
    }
    
    # 评分
    result = scorer.score_paper(sample_paper)
    print(f"投资评分结果: {result['investment_score']}")
    print(f"投资建议: {result['investment_recommendation']}")
    print(f"技术深度: {result['technical_depth_score']}")
    print(f"新颖性: {result['novelty_score']}")
    print(f"商业潜力: {result['commercial_potential_score']}")