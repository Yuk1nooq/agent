"""
可视化模块 - 负责生成图表和表格展示
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Dict, List, Any, Optional


class DataVisualizer:
    """数据可视化类"""
    
    def __init__(self):
        """初始化可视化器"""
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def render_response(self, response_data: Dict[str, Any]) -> None:
        """
        根据AI响应数据渲染相应的可视化内容
        
        Args:
            response_data: AI返回的响应数据
        """
        if not response_data:
            st.warning("没有可显示的内容")
            return
        
        try:
            # 文字回答
            if 'answer' in response_data:
                self._render_text_answer(response_data['answer'])
            
            # 表格数据
            elif 'table' in response_data:
                self._render_table(response_data['table'])
            
            # 柱状图
            elif 'bar' in response_data:
                self._render_bar_chart(response_data['bar'])
            
            # 折线图
            elif 'line' in response_data:
                self._render_line_chart(response_data['line'])
            
            # 饼图
            elif 'pie' in response_data:
                self._render_pie_chart(response_data['pie'])
            
            # 散点图
            elif 'scatter' in response_data:
                self._render_scatter_chart(response_data['scatter'])
            
            else:
                st.warning("不支持的响应格式")
                
        except Exception as e:
            st.error(f"可视化渲染错误：{str(e)}")
            # 显示原始数据以便调试
            with st.expander("原始响应数据"):
                st.json(response_data)
    
    def _render_text_answer(self, answer: str) -> None:
        """
        渲染文字回答
        
        Args:
            answer: 文字答案
        """
        st.info(f"分析结果: {answer}")
    
    def _render_table(self, table_data: Dict[str, Any]) -> None:
        """
        渲染表格数据
        
        Args:
            table_data: 表格数据，包含columns和data
        """
        try:
            columns = table_data.get('columns', [])
            data = table_data.get('data', [])
            
            if not columns or not data:
                st.warning("表格数据为空")
                return
            
            # 创建DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # 显示表格
            st.subheader("表格数据")
            st.dataframe(df, use_container_width=True)
            
            # 提供数据下载
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="下载表格数据",
                data=csv.encode('utf-8-sig'),
                file_name="table_data.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"表格渲染错误：{str(e)}")
    
    def _render_bar_chart(self, chart_data: Dict[str, Any]) -> None:
        """
        渲染柱状图
        
        Args:
            chart_data: 图表数据，包含columns和data
        """
        try:
            columns = chart_data.get('columns', [])
            data = chart_data.get('data', [])
            
            if not columns or not data:
                st.warning("图表数据为空")
                return
            
            # 检查数据长度是否匹配
            if len(columns) != len(data):
                st.error("列名和数据长度不匹配")
                return
            
            # 创建柱状图
            fig = go.Figure(data=[
                go.Bar(
                    x=columns,
                    y=data,
                    marker_color=self.color_palette[:len(columns)],
                    text=data,
                    textposition='outside'
                )
            ])
            
            # 设置图表样式
            fig.update_layout(
                title="柱状图分析",
                xaxis_title="类别",
                yaxis_title="数值",
                showlegend=False,
                height=500,
                template="plotly_white"
            )
            
            # 显示图表
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示数据摘要
            with st.expander("数据详情"):
                summary_df = pd.DataFrame({
                    '类别': columns,
                    '数值': data
                })
                st.dataframe(summary_df, use_container_width=True)
                
        except Exception as e:
            st.error(f"柱状图渲染错误：{str(e)}")
    
    def _render_line_chart(self, chart_data: Dict[str, Any]) -> None:
        """
        渲染折线图
        
        Args:
            chart_data: 图表数据，包含columns和data
        """
        try:
            columns = chart_data.get('columns', [])
            data = chart_data.get('data', [])
            
            if not columns or not data:
                st.warning("图表数据为空")
                return
            
            # 检查数据长度是否匹配
            if len(columns) != len(data):
                st.error("列名和数据长度不匹配")
                return
            
            # 创建折线图
            fig = go.Figure(data=[
                go.Scatter(
                    x=columns,
                    y=data,
                    mode='lines+markers',
                    line=dict(color=self.color_palette[0], width=3),
                    marker=dict(size=8, color=self.color_palette[1]),
                    text=data,
                    textposition='top center'
                )
            ])
            
            # 设置图表样式
            fig.update_layout(
                title="趋势分析",
                xaxis_title="时间/类别",
                yaxis_title="数值",
                showlegend=False,
                height=500,
                template="plotly_white"
            )
            
            # 显示图表
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示数据摘要
            with st.expander("数据详情"):
                summary_df = pd.DataFrame({
                    '时间/类别': columns,
                    '数值': data
                })
                st.dataframe(summary_df, use_container_width=True)
                
        except Exception as e:
            st.error(f"折线图渲染错误：{str(e)}")
    
    def _render_pie_chart(self, chart_data: Dict[str, Any]) -> None:
        """
        渲染饼图
        
        Args:
            chart_data: 图表数据，包含labels和values
        """
        try:
            labels = chart_data.get('labels', [])
            values = chart_data.get('values', [])
            
            if not labels or not values:
                st.warning("图表数据为空")
                return
            
            # 检查数据长度是否匹配
            if len(labels) != len(values):
                st.error("标签和数值长度不匹配")
                return
            
            # 创建饼图
            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,  # 创建圆环图效果
                    marker_colors=self.color_palette[:len(labels)]
                )
            ])
            
            # 设置图表样式
            fig.update_layout(
                title="比例分析",
                height=500,
                template="plotly_white"
            )
            
            # 显示图表
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示数据摘要
            with st.expander("数据详情"):
                summary_df = pd.DataFrame({
                    '类别': labels,
                    '数值': values,
                    '占比': [f"{v/sum(values)*100:.1f}%" for v in values]
                })
                st.dataframe(summary_df, use_container_width=True)
                
        except Exception as e:
            st.error(f"饼图渲染错误：{str(e)}")
    
    def _render_scatter_chart(self, chart_data: Dict[str, Any]) -> None:
        """
        渲染散点图
        
        Args:
            chart_data: 图表数据，包含x、y和labels
        """
        try:
            x_data = chart_data.get('x', [])
            y_data = chart_data.get('y', [])
            labels = chart_data.get('labels', [])
            
            if not x_data or not y_data:
                st.warning("图表数据为空")
                return
            
            # 检查数据长度是否匹配
            if len(x_data) != len(y_data):
                st.error("X和Y数据长度不匹配")
                return
            
            # 如果没有提供标签，使用索引
            if not labels:
                labels = [f"点{i+1}" for i in range(len(x_data))]
            elif len(labels) != len(x_data):
                labels = [f"点{i+1}" for i in range(len(x_data))]
            
            # 创建散点图
            fig = go.Figure(data=[
                go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=self.color_palette[0],
                        opacity=0.7
                    ),
                    text=labels,
                    textposition='top center'
                )
            ])
            
            # 设置图表样式
            fig.update_layout(
                title="散点分析",
                xaxis_title="X轴",
                yaxis_title="Y轴",
                showlegend=False,
                height=500,
                template="plotly_white"
            )
            
            # 显示图表
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示数据摘要
            with st.expander("数据详情"):
                summary_df = pd.DataFrame({
                    '标签': labels,
                    'X值': x_data,
                    'Y值': y_data
                })
                st.dataframe(summary_df, use_container_width=True)
                
        except Exception as e:
            st.error(f"散点图渲染错误：{str(e)}")
    
    def create_data_exploration_charts(self, df: pd.DataFrame) -> None:
        """
        创建数据探索图表
        
        Args:
            df: DataFrame数据
        """
        if df is None or df.empty:
            st.warning("无数据可供分析")
            return
        
        st.subheader("数据探索")
        
        # 数值列分布图
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                if len(numeric_cols) > 0:
                    selected_col = st.selectbox("选择数值列", numeric_cols)
                    if selected_col:
                        fig = px.histogram(
                            df, 
                            x=selected_col, 
                            title=f"{selected_col} 分布图",
                            color_discrete_sequence=self.color_palette
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if len(numeric_cols) >= 2:
                    col_x = st.selectbox("X轴", numeric_cols, key="x_axis")
                    col_y = st.selectbox("Y轴", numeric_cols, index=1, key="y_axis")
                    
                    if col_x and col_y:
                        fig = px.scatter(
                            df, 
                            x=col_x, 
                            y=col_y, 
                            title=f"{col_x} vs {col_y}",
                            color_discrete_sequence=self.color_palette
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
        
        # 分类列统计
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            st.subheader("分类数据统计")
            selected_cat_col = st.selectbox("选择分类列", categorical_cols)
            
            if selected_cat_col:
                value_counts = df[selected_cat_col].value_counts().head(10)
                
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"{selected_cat_col} 分布",
                    color_discrete_sequence=self.color_palette
                )
                fig.update_layout(
                    xaxis_title=selected_cat_col,
                    yaxis_title="数量",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def create_correlation_heatmap(self, df: pd.DataFrame) -> None:
        """
        创建相关性热力图
        
        Args:
            df: DataFrame数据
        """
        numeric_df = df.select_dtypes(include=['number'])
        
        if len(numeric_df.columns) < 2:
            st.info("需要至少2个数值列才能生成相关性分析")
            return
        
        # 计算相关性矩阵
        corr_matrix = numeric_df.corr()
        
        # 创建热力图
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="数值列相关性热力图",
            color_continuous_scale="RdBu_r"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True) 