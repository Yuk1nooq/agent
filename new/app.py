"""
数据分析智能工具 - 主应用
基于Streamlit框架，集成AI数据分析功能
"""

import streamlit as st
import pandas as pd
from utils.file_handler import FileHandler
from utils.ai_agent import DataAnalysisAgent
from utils.visualizer import DataVisualizer


# 页面配置
st.set_page_config(
    page_title="数据分析智能工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #F24236;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2E86AB;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """初始化会话状态"""
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'ai_agent' not in st.session_state:
        st.session_state.ai_agent = DataAnalysisAgent()
    if 'file_handler' not in st.session_state:
        st.session_state.file_handler = FileHandler()
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = DataVisualizer()


def main():
    """主函数"""
    # 初始化会话状态
    initialize_session_state()
    
    # 应用标题
    st.markdown('<h1 class="main-header">数据分析智能工具</h1>', unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.markdown("### 功能导航")
        
        # 页面选择
        page = st.selectbox(
            "选择功能页面",
            ["数据上传与概览", "AI问答分析", "数据可视化", "数据探索"]
        )
        
        st.markdown("---")
        
        # 文件上传区域
        st.markdown("### 数据文件")
        uploaded_data = st.session_state.file_handler.upload_file()
        
        if uploaded_data is not None:
            st.session_state.data = uploaded_data
            st.success("数据加载成功")
        
        # 示例数据选项
        st.markdown("---")
        if st.button("使用示例数据"):
            st.session_state.data = st.session_state.file_handler.get_sample_data()
            st.success("示例数据已加载")
            st.rerun()
        
        # 数据状态显示
        if st.session_state.data is not None:
            st.markdown("### 当前数据状态")
            st.metric("数据行数", st.session_state.data.shape[0])
            st.metric("数据列数", st.session_state.data.shape[1])
    
    # 主内容区域
    if page == "数据上传与概览":
        show_data_overview()
    elif page == "AI问答分析":
        show_ai_analysis()
    elif page == "数据可视化":
        show_data_visualization()
    elif page == "数据探索":
        show_data_exploration()


def show_data_overview():
    """显示数据概览页面"""
    st.markdown('<h2 class="sub-header">数据概览</h2>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.markdown('<div class="info-box">请先在左侧上传数据文件或使用示例数据</div>', 
                   unsafe_allow_html=True)
        return
    
    # 显示数据概览
    st.session_state.file_handler.display_data_overview(st.session_state.data)
    
    # 数据导出功能
    st.markdown("---")
    st.markdown("### 数据导出")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("下载当前数据"):
            st.session_state.file_handler.export_data(st.session_state.data, "current_data")
    
    with col2:
        if st.button("清除数据"):
            st.session_state.data = None
            st.success("数据已清除")
            st.rerun()


def show_ai_analysis():
    """显示AI问答分析页面"""
    st.markdown('<h2 class="sub-header">AI问答分析</h2>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.markdown('<div class="info-box">请先在左侧上传数据文件或使用示例数据</div>', 
                   unsafe_allow_html=True)
        return
    
    # 问题输入区域
    st.markdown("### 提问区域")
    

    
    # 问题输入
    user_question = st.text_area(
        "请输入您的问题：",
        placeholder="例如：各产品的销售额对比如何？",
        height=100
    )
    
    # 分析按钮
    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_button = st.button("开始分析", type="primary")
    
    # 处理AI分析
    if analyze_button and user_question.strip():
        with st.spinner("AI正在分析中..."):
            try:
                # 直接传递DataFrame给AI代理
                result = st.session_state.ai_agent.process_query(
                    user_question, 
                    st.session_state.data
                )
                
                if result['success']:
                    # 显示AI响应
                    st.markdown("### 分析结果")
                    st.session_state.visualizer.render_response(result['data'])
                    
                    # 显示原始响应（调试用）
                    with st.expander("调试信息"):
                        st.json(result)
                else:
                    st.error(f"分析失败：{result.get('error', '未知错误')}")
                    if result.get('raw_response'):
                        with st.expander("原始响应"):
                            st.text(result['raw_response'])
                            
            except Exception as e:
                st.error(f"处理过程中出现错误：{str(e)}")
    
    elif analyze_button:
        st.warning("请输入问题内容")


def show_data_visualization():
    """显示数据可视化页面"""
    st.markdown('<h2 class="sub-header">数据可视化</h2>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.markdown('<div class="info-box">请先在左侧上传数据文件或使用示例数据</div>', 
                   unsafe_allow_html=True)
        return
    
    # 可视化问题输入
    st.markdown("### 可视化需求")
    

    
    viz_question = st.text_area(
        "描述您想要的可视化内容：",
        placeholder="例如：生成各产品销售额的柱状图",
        height=80
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        viz_button = st.button("生成图表", type="primary")
    
    # 处理可视化请求
    if viz_button and viz_question.strip():
        with st.spinner("正在生成可视化..."):
            try:
                # 添加可视化相关的提示
                enhanced_question = f"请为以下需求生成适当的可视化（柱状图、折线图、饼图、散点图或表格）：{viz_question}"
                
                result = st.session_state.ai_agent.process_query(
                    enhanced_question,
                    st.session_state.data
                )
                
                if result['success']:
                    st.markdown("### 可视化结果")
                    st.session_state.visualizer.render_response(result['data'])
                    
                    with st.expander("技术详情"):
                        st.json(result)
                else:
                    st.error(f"可视化生成失败：{result.get('error', '未知错误')}")
                    
            except Exception as e:
                st.error(f"可视化过程中出现错误：{str(e)}")
    
    elif viz_button:
        st.warning("请描述您的可视化需求")


def show_data_exploration():
    """显示数据探索页面"""
    st.markdown('<h2 class="sub-header">数据探索</h2>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.markdown('<div class="info-box">请先在左侧上传数据文件或使用示例数据</div>', 
                   unsafe_allow_html=True)
        return
    
    # 自动数据探索
    st.session_state.visualizer.create_data_exploration_charts(st.session_state.data)
    
    # 相关性分析
    st.markdown("---")
    if st.button("生成相关性分析"):
        st.session_state.visualizer.create_correlation_heatmap(st.session_state.data)


if __name__ == "__main__":
    main() 