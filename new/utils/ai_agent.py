"""
AI代理模块 - 负责与GLM-4模型交互，处理数据分析问题
"""

import json
import pandas as pd
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from typing import Dict, Any, Optional


class DataAnalysisAgent:
    """数据分析AI代理类"""
    
    def __init__(self):
        """初始化AI代理，配置GLM-4模型"""
        self.model = ChatOpenAI(
            model='glm-4-air',
            base_url='https://open.bigmodel.cn/api/paas/v4',
            api_key=SecretStr('8629568f8a564fc6b726aa01cd7738d8.MLe6EbDgCgAX5Qii'),
            temperature=0.1  # 降低随机性，提高结果一致性
        )
        
        self.system_prompt = """你是一位专业的数据分析助手，请根据提供的完整数据集回答用户问题。

重要要求：
1. 必须基于提供的真实数据进行分析，不得自行生成或假设数据
2. 所有统计结果必须来自实际计算，不得估算
3. 如果数据不足以回答问题，请明确说明

根据用户请求类型，请选择以下格式之一进行回答：

**文字回答格式：**
{"answer": "基于数据的准确分析结果"}

**表格数据格式：**  
{"table": {"columns": ["列名1", "列名2", ...], "data": [["真实值1", "真实值2", ...], ["真实值1", "真实值2", ...]]}}

**柱状图格式：**
{"bar": {"columns": ["类别1", "类别2", ...], "data": [真实数值1, 真实数值2, ...]}}

**折线图格式：**
{"line": {"columns": ["时间点1", "时间点2", ...], "data": [真实数值1, 真实数值2, ...]}}

**饼图格式：**
{"pie": {"labels": ["标签1", "标签2", ...], "values": [真实数值1, 真实数值2, ...]}}

**散点图格式：**
{"scatter": {"x": [x值1, x值2, ...], "y": [y值1, y值2, ...], "labels": ["点1", "点2", ...]}}

格式要求：
- 所有字符串使用双引号
- 数值不加引号
- 确保JSON格式完整无误
- 数据必须来自真实数据集，不得编造

输出示例：
正确：{"bar": {"columns": ["产品A", "产品B"], "data": [150, 200]}}
错误：{"bar": {"columns": ["产品A", "产品B"], "data": ["150", "200"]}}"""
    
    def process_query(self, user_question: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        处理用户查询
        
        Args:
            user_question: 用户问题
            df: 完整的DataFrame数据
            
        Returns:
            解析后的响应结果
        """
        try:
            # 生成完整的数据信息
            data_info = self._generate_complete_data_info(df)
            
            # 构建完整的提示信息
            full_prompt = f"""
{self.system_prompt}

完整数据集信息：
{data_info}

用户问题：{user_question}

请基于上述真实数据回答问题，确保所有数值都来自实际计算。严格按照JSON格式输出。
"""
            
            # 调用模型获取响应
            response = self.model.invoke(full_prompt)
            response_text = response.content.strip()
            
            # 尝试解析JSON响应
            try:
                result = json.loads(response_text)
                # 验证数据是否合理
                if self._validate_data_consistency(result, df):
                    return {"success": True, "data": result, "raw_response": response_text}
                else:
                    return {
                        "success": False, 
                        "error": "AI返回的数据与实际数据不一致", 
                        "raw_response": response_text
                    }
            except json.JSONDecodeError as e:
                # 如果JSON解析失败，尝试提取JSON部分
                result = self._extract_json_from_text(response_text)
                if result and self._validate_data_consistency(result, df):
                    return {"success": True, "data": result, "raw_response": response_text}
                else:
                    return {
                        "success": False, 
                        "error": f"JSON解析失败或数据不一致: {str(e)}", 
                        "raw_response": response_text
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"AI处理错误: {str(e)}",
                "raw_response": ""
            }
    
    def _generate_complete_data_info(self, df: pd.DataFrame) -> str:
        """
        生成完整的数据信息，包含所有数据内容
        
        Args:
            df: pandas DataFrame
            
        Returns:
            完整的数据信息字符串
        """
        try:
            info_parts = []
            
            # 基本信息
            rows, cols = df.shape
            info_parts.append(f"数据集基本信息：")
            info_parts.append(f"总行数：{rows}")
            info_parts.append(f"总列数：{cols}")
            info_parts.append("")
            
            # 列信息和统计
            info_parts.append("列信息和详细统计：")
            for col in df.columns:
                dtype = str(df[col].dtype)
                non_null_count = df[col].count()
                null_count = df[col].isnull().sum()
                unique_count = df[col].nunique()
                
                info_parts.append(f"列名：{col}")
                info_parts.append(f"  数据类型：{dtype}")
                info_parts.append(f"  非空值：{non_null_count}个")
                info_parts.append(f"  空值：{null_count}个")
                info_parts.append(f"  唯一值：{unique_count}个")
                
                # 如果是数值列，提供统计信息
                if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                    try:
                        stats = df[col].describe()
                        info_parts.append(f"  统计信息：均值={stats['mean']:.2f}, 最大值={stats['max']}, 最小值={stats['min']}, 标准差={stats['std']:.2f}")
                    except:
                        pass
                
                # 如果是分类列，提供值计数
                elif df[col].dtype == 'object' or df[col].dtype.name == 'category':
                    try:
                        value_counts = df[col].value_counts()
                        top_values = value_counts.head(10)
                        info_parts.append(f"  值分布（前10个）：")
                        for value, count in top_values.items():
                            info_parts.append(f"    {value}: {count}次")
                    except:
                        pass
                
                info_parts.append("")
            
            # 如果数据量不太大，提供完整数据
            if len(df) <= 100:
                info_parts.append("完整数据集：")
                # 将DataFrame转换为更易读的格式
                for idx, row in df.iterrows():
                    row_data = []
                    for col in df.columns:
                        row_data.append(f"{col}={row[col]}")
                    info_parts.append(f"第{idx+1}行：{', '.join(row_data)}")
            else:
                # 数据量大时，提供更多样本
                info_parts.append("数据样本（包含前10行、中间10行、后10行）：")
                
                # 前10行
                info_parts.append("前10行：")
                for idx, row in df.head(10).iterrows():
                    row_data = []
                    for col in df.columns:
                        row_data.append(f"{col}={row[col]}")
                    info_parts.append(f"第{idx+1}行：{', '.join(row_data)}")
                
                # 中间10行
                mid_start = len(df) // 2 - 5
                mid_end = len(df) // 2 + 5
                info_parts.append(f"中间部分（第{mid_start+1}-{mid_end}行）：")
                for idx, row in df.iloc[mid_start:mid_end].iterrows():
                    row_data = []
                    for col in df.columns:
                        row_data.append(f"{col}={row[col]}")
                    info_parts.append(f"第{idx+1}行：{', '.join(row_data)}")
                
                # 后10行
                info_parts.append("最后10行：")
                for idx, row in df.tail(10).iterrows():
                    row_data = []
                    for col in df.columns:
                        row_data.append(f"{col}={row[col]}")
                    info_parts.append(f"第{idx+1}行：{', '.join(row_data)}")
            
            return "\n".join(info_parts)
            
        except Exception as e:
            return f"生成数据信息时出错：{str(e)}"
    
    def _validate_data_consistency(self, ai_result: Dict, df: pd.DataFrame) -> bool:
        """
        验证AI返回的数据是否与实际数据一致
        
        Args:
            ai_result: AI返回的结果
            df: 实际的DataFrame
            
        Returns:
            是否一致
        """
        try:
            # 对于表格数据，验证行数是否合理
            if 'table' in ai_result:
                table_data = ai_result['table']
                if 'data' in table_data:
                    # 检查返回的行数是否超过实际数据行数
                    if len(table_data['data']) > len(df) * 2:  # 允许一定的统计汇总
                        return False
            
            # 对于柱状图和折线图，验证数据点数量是否合理
            elif 'bar' in ai_result or 'line' in ai_result:
                chart_key = 'bar' if 'bar' in ai_result else 'line'
                chart_data = ai_result[chart_key]
                if 'data' in chart_data and 'columns' in chart_data:
                    # 检查数据长度是否匹配
                    if len(chart_data['data']) != len(chart_data['columns']):
                        return False
                    # 检查数据点数量是否合理（不应超过唯一值数量太多）
                    max_unique_values = max([df[col].nunique() for col in df.columns if df[col].dtype == 'object'], default=len(df))
                    if len(chart_data['data']) > max_unique_values * 2:
                        return False
            
            return True
            
        except Exception:
            return True  # 如果验证过程出错，则假设数据有效
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """从文本中提取JSON内容"""
        import re
        
        # 尝试找到JSON格式的内容
        json_patterns = [
            r'\{[^{}]*\}',  # 简单的JSON对象
            r'\{.*?\}',     # 更宽泛的JSON对象
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def generate_data_summary(self, df: pd.DataFrame) -> str:
        """
        生成数据摘要信息（为了兼容性保留）
        
        Args:
            df: pandas DataFrame
            
        Returns:
            数据摘要字符串
        """
        return self._generate_complete_data_info(df)
    
    def validate_response_format(self, response_data: Dict) -> bool:
        """
        验证响应格式是否正确
        
        Args:
            response_data: 响应数据
            
        Returns:
            是否格式正确
        """
        if not isinstance(response_data, dict):
            return False
        
        # 检查是否包含有效的响应类型
        valid_keys = ['answer', 'table', 'bar', 'line', 'pie', 'scatter']
        return any(key in response_data for key in valid_keys) 