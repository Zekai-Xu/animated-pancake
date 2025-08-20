"""
Excel导出模块 - AI学术论文监控系统
Excel Export Module - AI Academic Paper Monitoring System

该模块负责将论文数据导出为专业的Excel报告
This module handles exporting paper data to professional Excel reports
"""

import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import json
import os
from pathlib import Path
import xlsxwriter
from xlsxwriter.utility import xl_range
import numpy as np

logger = logging.getLogger(__name__)


class ExcelExporter:
    """
    Excel导出器
    Excel exporter for academic paper data
    """
    
    def __init__(self, config: Dict):
        """
        初始化Excel导出器
        Initialize Excel exporter
        
        Args:
            config: 配置字典 Configuration dictionary
        """
        self.config = config
        self.export_config = config.get('export', {}).get('excel', {})
        
        # 默认样式配置
        self.styles = {
            'header': {
                'bg_color': self.export_config.get('formatting', {}).get('header_color', '366092'),
                'font_color': 'white',
                'bold': True,
                'font_size': 12,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            },
            'highlight': {
                'bg_color': self.export_config.get('formatting', {}).get('highlight_color', 'FFE699'),
                'border': 1
            },
            'normal': {
                'font_name': self.export_config.get('formatting', {}).get('font_name', 'Calibri'),
                'font_size': self.export_config.get('formatting', {}).get('font_size', 11),
                'border': 1,
                'text_wrap': True,
                'valign': 'top'
            },
            'number': {
                'num_format': '0.00',
                'align': 'center'
            },
            'percentage': {
                'num_format': '0.00%',
                'align': 'center'
            },
            'date': {
                'num_format': 'yyyy-mm-dd',
                'align': 'center'
            }
        }
        
        logger.info("Excel导出器初始化完成")
    
    def prepare_overview_data(self, papers_data: List[Dict]) -> pd.DataFrame:
        """
        准备论文概览数据
        Prepare paper overview data
        
        Args:
            papers_data: 论文数据列表 List of paper data
            
        Returns:
            pd.DataFrame: 概览数据DataFrame Overview data DataFrame
        """
        overview_data = []
        
        for paper in papers_data:
            try:
                # 解析JSON字段
                authors = json.loads(paper.get('authors', '[]')) if isinstance(paper.get('authors'), str) else paper.get('authors', [])
                keywords = json.loads(paper.get('keywords', '[]')) if isinstance(paper.get('keywords'), str) else paper.get('keywords', [])
                
                # 格式化作者 (最多显示前3个)
                author_str = ', '.join(authors[:3])
                if len(authors) > 3:
                    author_str += f' 等{len(authors)}人'
                
                # 格式化关键词
                keyword_str = ', '.join(keywords[:5])
                
                overview_data.append({
                    '论文ID': paper.get('id', ''),
                    '标题': paper.get('title', ''),
                    '作者': author_str,
                    '会议': paper.get('conference', ''),
                    '年份': paper.get('year', ''),
                    '发表日期': paper.get('publication_date', ''),
                    '投资评分': paper.get('investment_score', 0),
                    '投资建议': paper.get('investment_recommendation', ''),
                    '引用次数': paper.get('citation_count', 0),
                    '引用增长率(月)': paper.get('citation_growth_rate', 0),
                    '最高H指数': paper.get('h_index_max', 0),
                    '会议影响因子': paper.get('venue_impact_factor', 0),
                    '技术深度': paper.get('technical_depth_score', 0),
                    '新颖性评分': paper.get('novelty_score', 0),
                    '商业潜力': paper.get('commercial_potential_score', 0),
                    '技术成熟度': paper.get('technology_maturity', ''),
                    '市场规模': paper.get('market_size_estimate', ''),
                    '关键词': keyword_str,
                    '论文链接': paper.get('paper_url', ''),
                    'PDF链接': paper.get('pdf_url', ''),
                    '创建时间': paper.get('created_at', ''),
                    '更新时间': paper.get('updated_at', '')
                })
                
            except Exception as e:
                logger.warning(f"处理论文数据失败: {e}")
                continue
        
        return pd.DataFrame(overview_data)
    
    def prepare_investment_data(self, papers_data: List[Dict]) -> pd.DataFrame:
        """
        准备投资机会数据
        Prepare investment opportunity data
        
        Args:
            papers_data: 论文数据列表 List of paper data
            
        Returns:
            pd.DataFrame: 投资机会数据DataFrame Investment opportunity DataFrame
        """
        # 过滤高投资价值论文 (评分 >= 6.5)
        high_value_papers = [p for p in papers_data if p.get('investment_score', 0) >= 6.5]
        
        investment_data = []
        
        for paper in high_value_papers:
            try:
                # 解析JSON字段
                authors = json.loads(paper.get('authors', '[]')) if isinstance(paper.get('authors'), str) else paper.get('authors', [])
                affiliations = json.loads(paper.get('authors_affiliations', '[]')) if isinstance(paper.get('authors_affiliations'), str) else paper.get('authors_affiliations', [])
                emails = json.loads(paper.get('authors_emails', '[]')) if isinstance(paper.get('authors_emails'), str) else paper.get('authors_emails', [])
                partnerships = json.loads(paper.get('industry_partnerships', '[]')) if isinstance(paper.get('industry_partnerships'), str) else paper.get('industry_partnerships', [])
                
                # 构建作者信息
                author_info = []
                for i, author in enumerate(authors[:3]):  # 最多显示前3个作者
                    info = f"{author}"
                    if i < len(affiliations) and affiliations[i]:
                        info += f" ({affiliations[i]})"
                    author_info.append(info)
                
                # 构建联系方式
                contact_info = []
                for email in emails[:3]:  # 最多显示前3个邮箱
                    if email and '@' in email:
                        contact_info.append(email)
                
                # 生成投资建议
                investment_advice = self._generate_investment_advice(paper)
                
                investment_data.append({
                    '论文标题': paper.get('title', ''),
                    '投资评分': paper.get('investment_score', 0),
                    '投资建议': paper.get('investment_recommendation', ''),
                    '主要作者': '; '.join(author_info),
                    '机构信息': '; '.join(affiliations[:3]),
                    '联系方式': '; '.join(contact_info),
                    '技术成熟度': paper.get('technology_maturity', ''),
                    '市场规模估计': paper.get('market_size_estimate', ''),
                    '商业潜力评分': paper.get('commercial_potential_score', 0),
                    '创业指标': '是' if paper.get('startup_indicators', False) else '否',
                    '产业合作': '; '.join(partnerships),
                    '会议年份': f"{paper.get('conference', '')} {paper.get('year', '')}",
                    '引用表现': f"{paper.get('citation_count', 0)} 次引用 (月增长 {paper.get('citation_growth_rate', 0):.2f})",
                    '技术亮点': self._extract_technical_highlights(paper),
                    '投资建议详情': investment_advice,
                    '论文链接': paper.get('paper_url', ''),
                    'PDF下载': paper.get('pdf_url', '')
                })
                
            except Exception as e:
                logger.warning(f"处理投资数据失败: {e}")
                continue
        
        return pd.DataFrame(investment_data)
    
    def prepare_trend_analysis_data(self, papers_data: List[Dict]) -> pd.DataFrame:
        """
        准备趋势分析数据
        Prepare trend analysis data
        
        Args:
            papers_data: 论文数据列表 List of paper data
            
        Returns:
            pd.DataFrame: 趋势分析数据DataFrame Trend analysis DataFrame
        """
        # 按技术领域分组分析
        tech_trends = {}
        
        for paper in papers_data:
            try:
                keywords = json.loads(paper.get('keywords', '[]')) if isinstance(paper.get('keywords'), str) else paper.get('keywords', [])
                investment_score = paper.get('investment_score', 0)
                year = paper.get('year', 0)
                
                # 确定主要技术领域
                main_tech = self._categorize_technology(keywords, paper.get('title', ''))
                
                if main_tech not in tech_trends:
                    tech_trends[main_tech] = {
                        'papers': [],
                        'scores': [],
                        'years': []
                    }
                
                tech_trends[main_tech]['papers'].append(paper)
                tech_trends[main_tech]['scores'].append(investment_score)
                tech_trends[main_tech]['years'].append(year)
                
            except Exception as e:
                logger.warning(f"处理趋势数据失败: {e}")
                continue
        
        # 生成趋势分析结果
        trend_data = []
        
        for tech, data in tech_trends.items():
            if len(data['papers']) < 2:  # 至少需要2篇论文才能分析趋势
                continue
            
            try:
                avg_score = np.mean(data['scores'])
                paper_count = len(data['papers'])
                
                # 计算年度增长趋势
                recent_years = [year for year in data['years'] if year >= 2022]
                growth_trend = "增长" if len(recent_years) > len(data['years']) * 0.6 else "稳定"
                
                # 投资热度评估
                high_score_count = len([s for s in data['scores'] if s >= 7.0])
                investment_heat = "高" if high_score_count > paper_count * 0.3 else ("中" if high_score_count > 0 else "低")
                
                # 代表性论文
                top_papers = sorted(data['papers'], key=lambda x: x.get('investment_score', 0), reverse=True)[:3]
                representative_papers = [p.get('title', '')[:50] + '...' for p in top_papers]
                
                trend_data.append({
                    '技术领域': tech,
                    '论文数量': paper_count,
                    '平均投资评分': round(avg_score, 2),
                    '高价值论文数': high_score_count,
                    '增长趋势': growth_trend,
                    '投资热度': investment_heat,
                    '近年论文占比': f"{len(recent_years)/paper_count*100:.1f}%",
                    '代表性论文': '; '.join(representative_papers),
                    '技术特点': self._get_technology_characteristics(tech),
                    '市场前景': self._assess_market_prospect(tech, avg_score),
                    '投资建议': self._get_trend_investment_advice(tech, avg_score, growth_trend)
                })
                
            except Exception as e:
                logger.warning(f"计算趋势统计失败: {e}")
                continue
        
        # 按平均评分排序
        trend_data.sort(key=lambda x: x['平均投资评分'], reverse=True)
        
        return pd.DataFrame(trend_data)
    
    def create_excel_report(self, papers_data: List[Dict], output_path: Optional[str] = None) -> str:
        """
        创建完整的Excel报告
        Create complete Excel report
        
        Args:
            papers_data: 论文数据列表 List of paper data
            output_path: 输出路径 Output path
            
        Returns:
            str: 生成的文件路径 Generated file path
        """
        try:
            # 生成输出路径
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = self.export_config.get('filename_template', 'AI_Papers_Analysis_{date}.xlsx').format(date=timestamp)
                output_path = f"output/{filename}"
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            logger.info(f"开始创建Excel报告: {output_path}")
            
            # 准备数据
            overview_df = self.prepare_overview_data(papers_data)
            investment_df = self.prepare_investment_data(papers_data)
            trend_df = self.prepare_trend_analysis_data(papers_data)
            
            # 创建Excel文件
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                # 获取工作簿和样式
                workbook = writer.book
                
                # 定义样式
                header_format = workbook.add_format(self.styles['header'])
                highlight_format = workbook.add_format(self.styles['highlight'])
                normal_format = workbook.add_format(self.styles['normal'])
                number_format = workbook.add_format({**self.styles['normal'], **self.styles['number']})
                percentage_format = workbook.add_format({**self.styles['normal'], **self.styles['percentage']})
                date_format = workbook.add_format({**self.styles['normal'], **self.styles['date']})
                
                # 写入各个工作表
                self._write_overview_sheet(overview_df, writer, workbook, header_format, normal_format, number_format, date_format)
                self._write_investment_sheet(investment_df, writer, workbook, header_format, normal_format, number_format, highlight_format)
                self._write_trend_sheet(trend_df, writer, workbook, header_format, normal_format, number_format)
                self._write_summary_sheet(papers_data, writer, workbook, header_format, normal_format, number_format)
            
            logger.info(f"Excel报告创建完成: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"创建Excel报告失败: {e}")
            raise
    
    def _write_overview_sheet(self, df: pd.DataFrame, writer, workbook, header_format, normal_format, number_format, date_format):
        """写入论文概览工作表"""
        sheet_name = '论文概览'
        df.to_excel(writer, sheet_name=sheet_name, index=False, freeze_panes=(1, 0))
        
        worksheet = writer.sheets[sheet_name]
        
        # 设置列宽和格式
        column_widths = {
            '论文ID': 8, '标题': 40, '作者': 25, '会议': 10, '年份': 8,
            '投资评分': 12, '投资建议': 12, '引用次数': 10, '引用增长率(月)': 15,
            '最高H指数': 12, '会议影响因子': 15, '技术深度': 10, '新颖性评分': 12,
            '商业潜力': 12, '技术成熟度': 15, '市场规模': 12, '关键词': 30,
            '论文链接': 20, 'PDF链接': 20, '创建时间': 15, '更新时间': 15
        }
        
        for col_num, (column, width) in enumerate(column_widths.items()):
            worksheet.set_column(col_num, col_num, width)
            
            # 应用格式
            if column in ['投资评分', '引用增长率(月)', '最高H指数', '会议影响因子', '技术深度', '新颖性评分', '商业潜力']:
                worksheet.set_column(col_num, col_num, width, number_format)
            elif column in ['创建时间', '更新时间', '发表日期']:
                worksheet.set_column(col_num, col_num, width, date_format)
            else:
                worksheet.set_column(col_num, col_num, width, normal_format)
        
        # 设置表头格式
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # 条件格式 - 高投资评分论文
        worksheet.conditional_format(1, 6, len(df), 6, {
            'type': 'cell',
            'criteria': '>=',
            'value': 8.0,
            'format': workbook.add_format({'bg_color': '#90EE90'})  # 浅绿色
        })
    
    def _write_investment_sheet(self, df: pd.DataFrame, writer, workbook, header_format, normal_format, number_format, highlight_format):
        """写入投资机会工作表"""
        sheet_name = '投资机会分析'
        df.to_excel(writer, sheet_name=sheet_name, index=False, freeze_panes=(1, 0))
        
        worksheet = writer.sheets[sheet_name]
        
        # 设置列宽
        column_widths = {
            '论文标题': 35, '投资评分': 12, '投资建议': 12, '主要作者': 30,
            '机构信息': 25, '联系方式': 25, '技术成熟度': 15, '市场规模估计': 15,
            '商业潜力评分': 15, '创业指标': 10, '产业合作': 20, '会议年份': 15,
            '引用表现': 20, '技术亮点': 40, '投资建议详情': 50, '论文链接': 20, 'PDF下载': 20
        }
        
        for col_num, (column, width) in enumerate(column_widths.items()):
            if column in ['投资评分', '商业潜力评分']:
                worksheet.set_column(col_num, col_num, width, number_format)
            else:
                worksheet.set_column(col_num, col_num, width, normal_format)
        
        # 设置表头格式
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # 突出显示强烈推荐的论文
        for row_num, row_data in df.iterrows():
            if row_data.get('投资建议') == '强烈推荐':
                for col_num in range(len(df.columns)):
                    worksheet.write(row_num + 1, col_num, row_data.iloc[col_num], highlight_format)
    
    def _write_trend_sheet(self, df: pd.DataFrame, writer, workbook, header_format, normal_format, number_format):
        """写入趋势分析工作表"""
        sheet_name = '技术趋势分析'
        df.to_excel(writer, sheet_name=sheet_name, index=False, freeze_panes=(1, 0))
        
        worksheet = writer.sheets[sheet_name]
        
        # 设置列宽
        column_widths = {
            '技术领域': 20, '论文数量': 12, '平均投资评分': 15, '高价值论文数': 15,
            '增长趋势': 12, '投资热度': 12, '近年论文占比': 15, '代表性论文': 50,
            '技术特点': 40, '市场前景': 30, '投资建议': 40
        }
        
        for col_num, (column, width) in enumerate(column_widths.items()):
            if column in ['论文数量', '平均投资评分', '高价值论文数']:
                worksheet.set_column(col_num, col_num, width, number_format)
            else:
                worksheet.set_column(col_num, col_num, width, normal_format)
        
        # 设置表头格式
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
    
    def _write_summary_sheet(self, papers_data: List[Dict], writer, workbook, header_format, normal_format, number_format):
        """写入汇总统计工作表"""
        sheet_name = '汇总统计'
        
        # 计算统计数据
        total_papers = len(papers_data)
        high_value_papers = len([p for p in papers_data if p.get('investment_score', 0) >= 8.0])
        avg_score = np.mean([p.get('investment_score', 0) for p in papers_data]) if papers_data else 0
        
        # 按会议统计
        conference_stats = {}
        for paper in papers_data:
            conf = paper.get('conference', 'Unknown')
            if conf not in conference_stats:
                conference_stats[conf] = {'count': 0, 'avg_score': 0, 'scores': []}
            conference_stats[conf]['count'] += 1
            conference_stats[conf]['scores'].append(paper.get('investment_score', 0))
        
        for conf in conference_stats:
            conference_stats[conf]['avg_score'] = np.mean(conference_stats[conf]['scores'])
        
        # 创建汇总数据
        summary_data = [
            ['统计项目', '数值', '说明'],
            ['论文总数', total_papers, '本次分析的论文总数量'],
            ['高价值论文数', high_value_papers, '投资评分 >= 8.0 的论文数量'],
            ['平均投资评分', f'{avg_score:.2f}', '所有论文的平均投资评分'],
            ['高价值比例', f'{high_value_papers/total_papers*100:.1f}%' if total_papers > 0 else '0%', '高价值论文占比'],
            ['', '', ''],  # 空行
            ['会议统计', '', ''],
        ]
        
        # 添加会议统计
        for conf, stats in sorted(conference_stats.items(), key=lambda x: x[1]['avg_score'], reverse=True):
            summary_data.append([conf, f"{stats['count']} 篇", f"平均评分: {stats['avg_score']:.2f}"])
        
        # 写入数据
        worksheet = workbook.add_worksheet(sheet_name)
        
        for row_num, row_data in enumerate(summary_data):
            for col_num, cell_value in enumerate(row_data):
                if row_num == 0 or row_data[0] == '会议统计':  # 表头行
                    worksheet.write(row_num, col_num, cell_value, header_format)
                else:
                    worksheet.write(row_num, col_num, cell_value, normal_format)
        
        # 设置列宽
        worksheet.set_column(0, 0, 20)  # 统计项目
        worksheet.set_column(1, 1, 15)  # 数值
        worksheet.set_column(2, 2, 30)  # 说明
    
    def _generate_investment_advice(self, paper: Dict) -> str:
        """生成投资建议详情"""
        score = paper.get('investment_score', 0)
        commercial_score = paper.get('commercial_potential_score', 0)
        maturity = paper.get('technology_maturity', '')
        
        advice = []
        
        if score >= 8.5:
            advice.append("🔥 强烈推荐关注：该论文具有极高的投资价值")
        elif score >= 7.0:
            advice.append("⭐ 建议重点关注：具有良好的投资潜力")
        elif score >= 6.0:
            advice.append("👀 可以关注：有一定投资价值")
        else:
            advice.append("📝 暂时观望：投资价值有限")
        
        if commercial_score >= 8.0:
            advice.append("商业化前景优秀")
        elif commercial_score >= 6.0:
            advice.append("具有商业化潜力")
        
        if maturity == '商业化':
            advice.append("技术已达到商业化阶段")
        elif maturity == '发展阶段':
            advice.append("技术处于快速发展期")
        
        if paper.get('startup_indicators', False):
            advice.append("涉及创业公司，值得关注")
        
        return '; '.join(advice)
    
    def _extract_technical_highlights(self, paper: Dict) -> str:
        """提取技术亮点"""
        highlights = []
        
        if paper.get('novelty_score', 0) >= 8.0:
            highlights.append("技术新颖性高")
        
        if paper.get('technical_depth_score', 0) >= 8.0:
            highlights.append("技术深度优秀")
        
        if paper.get('citation_count', 0) >= 100:
            highlights.append(f"高引用({paper.get('citation_count', 0)}次)")
        
        keywords = json.loads(paper.get('keywords', '[]')) if isinstance(paper.get('keywords'), str) else paper.get('keywords', [])
        hot_keywords = ['transformer', 'diffusion', 'large language model', 'multimodal']
        
        for keyword in keywords:
            if keyword.lower() in hot_keywords:
                highlights.append(f"涉及热门技术({keyword})")
                break
        
        return '; '.join(highlights) if highlights else '待评估'
    
    def _categorize_technology(self, keywords: List[str], title: str) -> str:
        """技术领域分类"""
        text = f"{' '.join(keywords)} {title}".lower()
        
        categories = {
            'Large Language Model': ['large language model', 'llm', 'language model', 'gpt', 'bert'],
            'Computer Vision': ['computer vision', 'image', 'visual', 'detection', 'segmentation', 'recognition'],
            'Diffusion Model': ['diffusion', 'diffusion model', 'stable diffusion'],
            'Transformer': ['transformer', 'attention', 'self-attention'],
            'Multimodal': ['multimodal', 'multi-modal', 'vision-language', 'text-image'],
            'Reinforcement Learning': ['reinforcement learning', 'rl', 'policy', 'reward'],
            'Graph Neural Network': ['graph', 'gnn', 'graph neural network'],
            'Natural Language Processing': ['nlp', 'natural language', 'text', 'language'],
            'Autonomous Driving': ['autonomous', 'self-driving', 'vehicle', 'driving'],
            'Robotics': ['robot', 'robotics', 'manipulation', 'navigation'],
            '其他': []
        }
        
        for category, category_keywords in categories.items():
            for keyword in category_keywords:
                if keyword in text:
                    return category
        
        return '其他'
    
    def _get_technology_characteristics(self, tech: str) -> str:
        """获取技术特点"""
        characteristics = {
            'Large Language Model': '通用性强，应用场景广泛，技术门槛高',
            'Computer Vision': '应用成熟，商业化程度高，市场需求大',
            'Diffusion Model': '生成质量高，创意应用多，版权问题需关注',
            'Transformer': '基础架构，应用广泛，持续优化空间大',
            'Multimodal': '跨模态理解，应用前景广阔，技术复杂度高',
            'Reinforcement Learning': '决策优化，游戏和控制应用成熟',
            'Autonomous Driving': '市场巨大，技术挑战大，监管要求高',
            'Robotics': '制造业应用，硬件结合紧密，投入成本高'
        }
        return characteristics.get(tech, '新兴技术领域，需进一步评估')
    
    def _assess_market_prospect(self, tech: str, avg_score: float) -> str:
        """评估市场前景"""
        if avg_score >= 8.0:
            return "市场前景优秀，建议重点关注"
        elif avg_score >= 7.0:
            return "市场前景良好，具有投资价值"
        elif avg_score >= 6.0:
            return "市场前景一般，可适度关注"
        else:
            return "市场前景待观察"
    
    def _get_trend_investment_advice(self, tech: str, avg_score: float, growth_trend: str) -> str:
        """获取趋势投资建议"""
        advice = []
        
        if avg_score >= 8.0 and growth_trend == "增长":
            advice.append("🔥 热门赛道，建议重点布局")
        elif avg_score >= 7.0:
            advice.append("⭐ 优质领域，建议关注优秀团队")
        elif growth_trend == "增长":
            advice.append("📈 增长趋势良好，可关注技术突破")
        else:
            advice.append("📊 保持观察，等待更好时机")
        
        # 特定技术领域的建议
        tech_advice = {
            'Large Language Model': '关注模型效率和应用创新',
            'Computer Vision': '关注垂直领域应用和边缘计算',
            'Autonomous Driving': '关注安全性和法规合规',
            'Robotics': '关注成本控制和实用性'
        }
        
        if tech in tech_advice:
            advice.append(tech_advice[tech])
        
        return '; '.join(advice)


# 使用示例
if __name__ == "__main__":
    # 示例配置
    config = {
        'export': {
            'excel': {
                'filename_template': 'AI_Papers_Analysis_{date}.xlsx',
                'formatting': {
                    'header_color': '366092',
                    'highlight_color': 'FFE699',
                    'font_name': 'Calibri',
                    'font_size': 11
                }
            }
        }
    }
    
    # 示例数据
    sample_papers = [
        {
            'id': 1,
            'title': 'Attention Is All You Need',
            'authors': '["Ashish Vaswani", "Noam Shazeer"]',
            'conference': 'NeurIPS',
            'year': 2017,
            'investment_score': 9.5,
            'investment_recommendation': '强烈推荐',
            'citation_count': 50000,
            'technical_depth_score': 9.0,
            'novelty_score': 9.5,
            'commercial_potential_score': 9.0,
            'keywords': '["transformer", "attention", "neural machine translation"]',
            'technology_maturity': '商业化',
            'market_size_estimate': '千亿级'
        }
    ]
    
    # 创建导出器并生成报告
    exporter = ExcelExporter(config)
    output_file = exporter.create_excel_report(sample_papers)
    print(f"Excel报告已生成: {output_file}")