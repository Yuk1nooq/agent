"""
文件处理模块 - 负责文件上传、解析和数据预处理
"""

import pandas as pd
import streamlit as st
from typing import Optional, Tuple
import io


class FileHandler:
    """文件处理类"""
    
    def __init__(self):
        """初始化文件处理器"""
        self.supported_formats = ['csv', 'xlsx', 'xls']
        self.max_file_size_mb = 200
    
    def upload_file(self) -> Optional[pd.DataFrame]:
        """
        处理文件上传
        
        Returns:
            上传成功时返回DataFrame，否则返回None
        """
        uploaded_file = st.file_uploader(
            "上传数据文件",
            type=self.supported_formats,
            help=f"支持的格式: {', '.join(self.supported_formats)}，最大文件大小: {self.max_file_size_mb}MB"
        )
        
        if uploaded_file is not None:
            try:
                # 检查文件大小
                file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                if file_size_mb > self.max_file_size_mb:
                    st.error(f"文件大小超过限制（{self.max_file_size_mb}MB）")
                    return None
                
                # 根据文件扩展名解析文件
                file_extension = uploaded_file.name.split('.')[-1].lower()
                df = self._parse_file(uploaded_file, file_extension)
                
                if df is not None:
                    st.success(f"文件上传成功！数据维度：{df.shape[0]}行 × {df.shape[1]}列")
                    return df
                else:
                    st.error("文件解析失败，请检查文件格式")
                    return None
                    
            except Exception as e:
                st.error(f"文件处理出错：{str(e)}")
                return None
        
        return None
    
    def _parse_file(self, uploaded_file, file_extension: str) -> Optional[pd.DataFrame]:
        """
        解析上传的文件
        
        Args:
            uploaded_file: Streamlit上传的文件对象
            file_extension: 文件扩展名
            
        Returns:
            解析成功时返回DataFrame，否则返回None
        """
        try:
            if file_extension == 'csv':
                # 尝试不同的编码格式
                encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
                for encoding in encodings:
                    try:
                        uploaded_file.seek(0)  # 重置文件指针
                        df = pd.read_csv(uploaded_file, encoding=encoding)
                        return self._clean_dataframe(df)
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        if encoding == encodings[-1]:  # 最后一个编码尝试失败
                            raise e
                        continue
                        
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(uploaded_file)
                return self._clean_dataframe(df)
            
            return None
            
        except Exception as e:
            st.error(f"文件解析错误：{str(e)}")
            return None
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清理DataFrame数据
        
        Args:
            df: 原始DataFrame
            
        Returns:
            清理后的DataFrame
        """
        try:
            # 删除完全为空的行和列
            df = df.dropna(axis=0, how='all')  # 删除全空行
            df = df.dropna(axis=1, how='all')  # 删除全空列
            
            # 重置索引
            df = df.reset_index(drop=True)
            
            # 清理列名（去除前后空格）
            df.columns = df.columns.astype(str).str.strip()
            
            # 限制数据行数（避免处理过大的数据集）
            max_rows = 10000
            if len(df) > max_rows:
                st.warning(f"数据量较大，仅显示前{max_rows}行")
                df = df.head(max_rows)
            
            return df
            
        except Exception as e:
            st.error(f"数据清理错误：{str(e)}")
            return df
    
    def display_data_overview(self, df: pd.DataFrame) -> None:
        """
        显示数据概览
        
        Args:
            df: DataFrame数据
        """
        if df is None or df.empty:
            st.warning("暂无数据")
            return
        
        # 基本信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总行数", df.shape[0])
        with col2:
            st.metric("总列数", df.shape[1])
        with col3:
            st.metric("缺失值", df.isnull().sum().sum())
        
        # 数据预览
        st.subheader("数据预览")
        st.dataframe(df.head(10), use_container_width=True)
        
        # 数据类型信息
        with st.expander("列信息详情"):
            col_info = pd.DataFrame({
                '列名': df.columns,
                '数据类型': df.dtypes.astype(str),
                '非空值数量': df.count().values,
                '空值数量': df.isnull().sum().values,
                '唯一值数量': [df[col].nunique() for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True)
        
        # 数值列统计
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            with st.expander("数值列统计"):
                st.dataframe(numeric_df.describe(), use_container_width=True)
    
    def get_sample_data(self) -> pd.DataFrame:
        """
        生成示例数据（用于演示）
        
        Returns:
            示例DataFrame
        """
        import numpy as np
        
        # 生成示例销售数据
        np.random.seed(42)
        products = ['产品A', '产品B', '产品C', '产品D', '产品E']
        months = ['1月', '2月', '3月', '4月', '5月', '6月']
        
        data = []
        for product in products:
            for month in months:
                sales = np.random.randint(100, 1000)
                profit = sales * np.random.uniform(0.1, 0.3)
                data.append({
                    '产品名称': product,
                    '月份': month,
                    '销售额': sales,
                    '利润': round(profit, 2)
                })
        
        return pd.DataFrame(data)
    
    def export_data(self, df: pd.DataFrame, filename: str = "processed_data") -> None:
        """
        导出数据
        
        Args:
            df: 要导出的DataFrame
            filename: 文件名
        """
        try:
            # 转换为CSV格式的字节流
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_data = csv_buffer.getvalue().encode('utf-8-sig')
            
            # 提供下载按钮
            st.download_button(
                label="下载处理后的数据",
                data=csv_data,
                file_name=f"{filename}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"数据导出失败：{str(e)}") 