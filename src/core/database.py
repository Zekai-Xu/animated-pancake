"""
数据库模块 - AI学术论文监控系统
Database Module - AI Academic Paper Monitoring System

该模块负责管理论文数据的存储、检索和更新
This module handles storage, retrieval, and updates of paper data
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class Paper(Base):
    """
    论文数据模型
    Paper data model for storing academic paper information
    """
    __tablename__ = 'papers'
    
    # 基本信息 Basic Information
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    abstract = Column(Text)
    authors = Column(Text)  # JSON格式存储作者列表
    authors_affiliations = Column(Text)  # JSON格式存储作者机构
    authors_countries = Column(Text)  # JSON格式存储作者国籍
    authors_emails = Column(Text)  # JSON格式存储联系方式
    
    # 发表信息 Publication Information
    conference = Column(String(50), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    publication_date = Column(DateTime)
    paper_url = Column(String(500))
    pdf_url = Column(String(500))
    
    # 引用和影响力指标 Citation and Impact Metrics
    citation_count = Column(Integer, default=0)
    citation_growth_rate = Column(Float, default=0.0)  # 月增长率
    h_index_max = Column(Float, default=0.0)  # 作者中最高H指数
    venue_impact_factor = Column(Float, default=0.0)
    
    # 内容分析指标 Content Analysis Metrics
    keywords = Column(Text)  # JSON格式存储关键词
    technical_depth_score = Column(Float, default=0.0)  # 技术深度评分(1-10)
    novelty_score = Column(Float, default=0.0)  # 新颖性评分(1-10)
    commercial_potential_score = Column(Float, default=0.0)  # 商业潜力评分(1-10)
    
    # 投资相关指标 Investment-Related Metrics
    investment_score = Column(Float, default=0.0)  # 综合投资价值评分(1-10)
    investment_recommendation = Column(String(50))  # 投资建议: High/Medium/Low
    market_size_estimate = Column(String(100))  # 市场规模估计
    technology_maturity = Column(String(50))  # 技术成熟度: Research/Development/Commercial
    
    # 公司和团队信息 Company and Team Information
    company_affiliations = Column(Text)  # JSON格式存储相关公司
    startup_indicators = Column(Boolean, default=False)  # 是否涉及创业公司
    industry_partnerships = Column(Text)  # 产业合作信息
    
    # 系统信息 System Information
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_citation_update = Column(DateTime)
    data_source = Column(String(100))  # 数据来源


class DatabaseManager:
    """
    数据库管理器
    Database manager for handling all database operations
    """
    
    def __init__(self, db_path: str = "data/papers.db"):
        """
        初始化数据库管理器
        Initialize database manager
        
        Args:
            db_path: 数据库文件路径 Database file path
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # 创建表
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"数据库初始化完成: {db_path}")
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    def add_paper(self, paper_data: Dict) -> int:
        """
        添加新论文到数据库
        Add new paper to database
        
        Args:
            paper_data: 论文数据字典 Paper data dictionary
            
        Returns:
            int: 新添加论文的ID New paper ID
        """
        session = self.get_session()
        try:
            # 检查是否已存在
            existing = session.query(Paper).filter_by(
                title=paper_data.get('title'),
                conference=paper_data.get('conference'),
                year=paper_data.get('year')
            ).first()
            
            if existing:
                logger.info(f"论文已存在: {paper_data.get('title')}")
                return existing.id
            
            # 创建新论文记录
            paper = Paper(**paper_data)
            session.add(paper)
            session.commit()
            
            logger.info(f"新论文添加成功: {paper.title} (ID: {paper.id})")
            return paper.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"添加论文失败: {e}")
            raise
        finally:
            session.close()
    
    def update_paper_metrics(self, paper_id: int, metrics: Dict) -> bool:
        """
        更新论文指标
        Update paper metrics
        
        Args:
            paper_id: 论文ID Paper ID
            metrics: 指标数据字典 Metrics dictionary
            
        Returns:
            bool: 更新是否成功 Whether update was successful
        """
        session = self.get_session()
        try:
            paper = session.query(Paper).filter_by(id=paper_id).first()
            if not paper:
                logger.warning(f"论文不存在: ID {paper_id}")
                return False
            
            # 更新指标
            for key, value in metrics.items():
                if hasattr(paper, key):
                    setattr(paper, key, value)
            
            paper.updated_at = datetime.utcnow()
            session.commit()
            
            logger.info(f"论文指标更新成功: {paper.title}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"更新论文指标失败: {e}")
            return False
        finally:
            session.close()
    
    def search_papers(self, 
                     keywords: Optional[List[str]] = None,
                     conferences: Optional[List[str]] = None,
                     years: Optional[List[int]] = None,
                     min_investment_score: Optional[float] = None,
                     min_citation_count: Optional[int] = None,
                     date_from: Optional[datetime] = None,
                     date_to: Optional[datetime] = None,
                     limit: int = 1000) -> List[Paper]:
        """
        搜索论文
        Search papers with filters
        
        Args:
            keywords: 关键词列表 Keywords list
            conferences: 会议列表 Conferences list  
            years: 年份列表 Years list
            min_investment_score: 最小投资评分 Minimum investment score
            min_citation_count: 最小引用数 Minimum citation count
            date_from: 开始日期 Start date
            date_to: 结束日期 End date
            limit: 结果限制 Result limit
            
        Returns:
            List[Paper]: 论文列表 Paper list
        """
        session = self.get_session()
        try:
            query = session.query(Paper)
            
            # 应用过滤条件
            if keywords:
                keyword_conditions = []
                for keyword in keywords:
                    keyword_conditions.append(Paper.title.contains(keyword))
                    keyword_conditions.append(Paper.abstract.contains(keyword))
                    keyword_conditions.append(Paper.keywords.contains(keyword))
                
                # 使用OR连接关键词条件
                from sqlalchemy import or_
                query = query.filter(or_(*keyword_conditions))
            
            if conferences:
                query = query.filter(Paper.conference.in_(conferences))
            
            if years:
                query = query.filter(Paper.year.in_(years))
            
            if min_investment_score is not None:
                query = query.filter(Paper.investment_score >= min_investment_score)
            
            if min_citation_count is not None:
                query = query.filter(Paper.citation_count >= min_citation_count)
            
            if date_from:
                query = query.filter(Paper.publication_date >= date_from)
            
            if date_to:
                query = query.filter(Paper.publication_date <= date_to)
            
            # 按投资评分降序排列
            query = query.order_by(Paper.investment_score.desc())
            
            if limit:
                query = query.limit(limit)
            
            papers = query.all()
            logger.info(f"搜索完成，找到 {len(papers)} 篇论文")
            
            return papers
            
        except Exception as e:
            logger.error(f"搜索论文失败: {e}")
            return []
        finally:
            session.close()
    
    def get_papers_dataframe(self, 
                           search_params: Optional[Dict] = None) -> pd.DataFrame:
        """
        获取论文数据的DataFrame格式
        Get papers data as DataFrame
        
        Args:
            search_params: 搜索参数 Search parameters
            
        Returns:
            pd.DataFrame: 论文数据DataFrame Papers DataFrame
        """
        if search_params:
            papers = self.search_papers(**search_params)
        else:
            session = self.get_session()
            papers = session.query(Paper).all()
            session.close()
        
        # 转换为DataFrame
        data = []
        for paper in papers:
            data.append({
                'ID': paper.id,
                '标题': paper.title,
                '作者': paper.authors,
                '机构': paper.authors_affiliations,
                '国籍': paper.authors_countries,
                '联系方式': paper.authors_emails,
                '会议': paper.conference,
                '年份': paper.year,
                '发表日期': paper.publication_date,
                '论文链接': paper.paper_url,
                'PDF链接': paper.pdf_url,
                '引用次数': paper.citation_count,
                '引用增长率': paper.citation_growth_rate,
                '最高H指数': paper.h_index_max,
                '会议影响因子': paper.venue_impact_factor,
                '关键词': paper.keywords,
                '技术深度': paper.technical_depth_score,
                '新颖性': paper.novelty_score,
                '商业潜力': paper.commercial_potential_score,
                '投资评分': paper.investment_score,
                '投资建议': paper.investment_recommendation,
                '市场规模': paper.market_size_estimate,
                '技术成熟度': paper.technology_maturity,
                '相关公司': paper.company_affiliations,
                '创业指标': paper.startup_indicators,
                '产业合作': paper.industry_partnerships,
                '创建时间': paper.created_at,
                '更新时间': paper.updated_at
            })
        
        return pd.DataFrame(data)
    
    def get_statistics(self) -> Dict:
        """
        获取数据库统计信息
        Get database statistics
        
        Returns:
            Dict: 统计信息字典 Statistics dictionary
        """
        session = self.get_session()
        try:
            stats = {
                'total_papers': session.query(Paper).count(),
                'papers_by_year': {},
                'papers_by_conference': {},
                'avg_investment_score': 0.0,
                'high_potential_papers': 0,
                'recent_papers': 0
            }
            
            # 按年份统计
            years_data = session.query(Paper.year, 
                                     session.query(Paper).filter_by(year=Paper.year).count()
                                     ).group_by(Paper.year).all()
            for year, count in years_data:
                stats['papers_by_year'][year] = count
            
            # 按会议统计  
            conf_data = session.query(Paper.conference,
                                    session.query(Paper).filter_by(conference=Paper.conference).count()
                                    ).group_by(Paper.conference).all()
            for conf, count in conf_data:
                stats['papers_by_conference'][conf] = count
            
            # 平均投资评分
            avg_score = session.query(Paper.investment_score).filter(
                Paper.investment_score > 0).all()
            if avg_score:
                stats['avg_investment_score'] = sum([s[0] for s in avg_score]) / len(avg_score)
            
            # 高潜力论文数量 (评分 >= 7.0)
            stats['high_potential_papers'] = session.query(Paper).filter(
                Paper.investment_score >= 7.0).count()
            
            # 最近30天的论文
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            stats['recent_papers'] = session.query(Paper).filter(
                Paper.created_at >= thirty_days_ago).count()
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
        finally:
            session.close()
    
    def backup_database(self, backup_path: str) -> bool:
        """
        备份数据库
        Backup database
        
        Args:
            backup_path: 备份路径 Backup path
            
        Returns:
            bool: 备份是否成功 Whether backup was successful
        """
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"数据库备份成功: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        self.engine.dispose()
        logger.info("数据库连接已关闭")


# 使用示例
if __name__ == "__main__":
    # 创建数据库管理器
    db = DatabaseManager()
    
    # 示例数据
    sample_paper = {
        'title': 'Attention Is All You Need',
        'abstract': 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...',
        'authors': json.dumps(['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar']),
        'authors_affiliations': json.dumps(['Google Brain', 'Google Research', 'Google Research']),
        'authors_countries': json.dumps(['USA', 'USA', 'USA']),
        'conference': 'NeurIPS',
        'year': 2017,
        'citation_count': 50000,
        'investment_score': 9.5,
        'investment_recommendation': 'High',
        'keywords': json.dumps(['transformer', 'attention', 'neural machine translation'])
    }
    
    # 添加论文
    paper_id = db.add_paper(sample_paper)
    print(f"添加论文ID: {paper_id}")
    
    # 搜索论文
    papers = db.search_papers(keywords=['transformer'], min_investment_score=8.0)
    print(f"搜索到 {len(papers)} 篇高投资价值论文")
    
    # 获取统计信息
    stats = db.get_statistics()
    print(f"数据库统计: {stats}")
    
    # 关闭数据库
    db.close()