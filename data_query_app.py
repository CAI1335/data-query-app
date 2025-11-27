import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime

# --- 配置 Streamlit 页面 ---
st.set_page_config(
    page_title="文件数据查询工具 - 查询优先",
    layout="wide", 
    initial_sidebar_state="expanded" # 展开侧边栏，用于上传功能
)

# ----------------------------------------------------
# 📌 固定的列设置
# ----------------------------------------------------
# 目标列：第 4 列
N_COLUMN_INDEX_USER = 4
# Pandas 索引从 0 开始，所以是第 3 个索引
N_COLUMN_INDEX_PANDAS = N_COLUMN_INDEX_USER - 1

# ----------------------------------------------------
# 📌 初始化 Session State (确保数据和状态持久化)
# ----------------------------------------------------
# 这个函数只在程序第一次运行时执行
def initialize_session_state():
    if 'df_data' not in st.session_state:
        st.session_state.df_data = pd.DataFrame()
    if 'data_loaded_status' not in st.session_state:
        st.session_state.data_loaded_status = "未加载数据"
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None

initialize_session_state()

# ----------------------------------------------------
# 📌 文件上传函数 (部署在侧边栏，只在有新文件时运行)
# ----------------------------------------------------
def upload_file_ui():
    """在侧边栏处理文件上传和数据加载"""
    st.sidebar.header("📊 数据加载与文件上传")
    st.sidebar.caption("这里用于上传或更新查询的原始数据。")
    
    uploaded_file = st.sidebar.file_uploader(
        "选择 Excel 或 CSV 文件",
        type=['csv', 'xlsx']
    )

    if uploaded_file:
        try:
            # 仅在文件发生变化时重新加载数据
            if st.session_state.uploaded_file_name != uploaded_file.name:
                
                # 读取文件
                if uploaded_file.name.endswith('.csv'):
                    # 尝试用 utf-8-sig 应对中文 CSV 乱码
                    df = pd.read_csv(uploaded_file, encoding='utf-8') 
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                
                # 检查列数是否满足查询要求
                if N_COLUMN_INDEX_PANDAS >= len(df.columns):
                    st.sidebar.error(f"❌ 文件只有 {len(df.columns)} 列，查询第 {N_COLUMN_INDEX_USER} 列失败。")
                    return

                # 更新 Session State
                st.session_state.df_data = df
                st.session_state.uploaded_file_name = uploaded_file.name
                col_name = df.columns[N_COLUMN_INDEX_PANDAS]
                st.session_state.data_loaded_status = f"数据已加载 ({len(df)} 条，目标列：{col_name})"
                
                st.sidebar.success(f"文件 **{uploaded_file.name}** 加载成功！")
                
        except Exception as e:
            st.sidebar.error(f"处理文件时发生错误。请检查文件格式和编码。错误详情: {e}")
            st.session_state.df_data = pd.DataFrame()
            st.session_state.data_loaded_status = "数据加载失败"
            st.session_state.uploaded_file_name = None


# ----------------------------------------------------
# 📌 主程序 (查询优先，布局易操作)
# ----------------------------------------------------
def run_data_query_app():
    """主函数：运行 Streamlit 应用"""
    st.title("📱 数据查询中心 (手机友好)")
    st.markdown("---")
    
    # 运行侧边栏上传功能
    upload_file_ui() 

    # --------------------------------------------------------------------------
    # --- 查询功能区 (主要界面) ---
    # --------------------------------------------------------------------------
    st.header("1. 查询功能")
    st.info(f"当前状态：{st.session_state.data_loaded_status}")

    df = st.session_state.df_data
    
    # 检查是否有数据可供查询
    if df.empty:
        st.warning("请先通过左侧的**侧边栏**上传数据文件。")
        return

    # 获取目标列名 (第 4 列)
    col_name = df.columns[N_COLUMN_INDEX_PANDAS]
    st.caption(f"查询目标：已加载文件，在第 **{N_COLUMN_INDEX_USER}** 列（**{col_name}**）中查询。")


    # --- 查询输入 ---
    query_input = st.text_input(
        "请输入要查询的 **后 5 位字符**:",
        placeholder="例如：输入 01771",
        key="query_box" # 保持查询框的持久性
    )
    
    # --------------------------------------------------------------------------
    # --- 结果显示 ---
    # --------------------------------------------------------------------------
    st.header("2. 查询结果")
    
    if query_input:
        # 核心查询逻辑
        try:
            # 确保目标列是字符串类型
            target_series = df[col_name].astype(str)
            
            # 筛选：第 4 列的后 5 位字符 == 输入值
            filtered_df = df[
                target_series.str.len() >= 5 # 确保字符串长度足够
            ][
                target_series.str[-5:] == query_input
            ]
            
            if filtered_df.empty:
                st.warning(f"未找到任何匹配后 5 位 '{query_input}' 的记录。")
            else:
                st.success(f"找到 **{len(filtered_df)}** 条匹配记录。")
                # 使用 st.dataframe 显示结果，它在移动端有很好的滚动和缩放支持
                st.dataframe(filtered_df)
                
        except Exception as e:
            st.error(f"执行查询时发生错误: {e}")
    else:
        st.info("⬆️ 请在上方输入查询值以开始查找。")


if __name__ == "__main__":
    run_data_query_app()
