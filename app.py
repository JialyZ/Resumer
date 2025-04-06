import streamlit as st
from chatbot_engine import ask_chatbot
import json
from upload_resume import read_resume
from parse_resume import extract_resume_info
from recommend_jobs import recommend_jobs_tfidf
from resume_score import score_resume_with_deepseek
from job_predictor_live import predict_top_careers
import os
from pathlib import Path
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 设置页面配置
st.set_page_config(
    page_title="Resume Analysis and Job Recommendation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 获取logo的base64编码
try:
    logo_base64 = get_base64_of_bin_file(os.path.join('app', 'static', 'logo.png'))
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="brand-logo" alt="Logo">'
except Exception as e:
    logo_html = ''  # 如果加载失败，不显示logo

# 自定义CSS样式
st.markdown("""
    <style>
    /* 导航栏容器 */
    .nav-container {
        background-color: #1976D2;
        padding: 0.5rem 2rem;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 60px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
    }
    
    /* 左侧品牌名称和logo */
    .brand-container {
        display: flex;
        align-items: center;
        height: 100%;
    }
    
    .brand-logo {
        height: 55px;
        width: 200px;
        object-fit: contain;
        padding-left: 0;
    }
    
    .brand-name {
        color: #ffffff;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
        letter-spacing: 1px;
    }
    
    /* 右侧导航按钮 */
    .nav-buttons {
        display: flex;
        gap: 1rem;
    }
    
    /* 导航按钮样式 */
    .nav-button {
        background-color: transparent;
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: inherit;
    }
    
    .nav-button:hover {
        background-color: rgba(255,255,255,0.1);
        border-color: white;
    }

    /* Streamlit按钮样式 */
    .stButton > button {
        background-color: transparent;
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 0;
    }

    .stButton > button:hover {
        background-color: rgba(255,255,255,0.1);
        border-color: white;
        color: white;
    }

    /* 调整按钮容器样式 */
    [data-testid="column"] {
        padding: 0 !important;
        display: flex;
        align-items: center;
    }

    /* 调整Streamlit默认header的间距 */
    header[data-testid="stHeader"] {
        margin-bottom: 0;  /* 减少header的下边距 */
    }

    /* 确保主内容区域不被导航栏遮挡 */
    .main .block-container {
        padding-top: 0;  /* 减少顶部内边距 */
        max-width: unset;
    }

    /* 美化文件上传组件 */
    .stFileUploader {
        background-color: white !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
        margin: 1rem 0 !important;
    }

    /* 上传按钮样式 */
    .stFileUploader button {
        background-color: #1976D2 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 5px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .stFileUploader button:hover {
        background-color: #1565C0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }

    /* 拖拽区域样式 */
    .stFileUploader [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #1976D2 !important;
        background-color: #f8f9fa !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        min-height: 100px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .stFileUploader [data-testid="stFileUploadDropzone"]:hover {
        border-color: #1565C0 !important;
        background-color: #e3f2fd !important;
    }

    /* 隐藏多余的文字 */
    .stFileUploader [data-testid="stFileUploadDropzone"] p {
        display: none !important;
    }

    /* 文件信息样式 */
    .stFileUploader p {
        color: #666 !important;
        font-size: 0.9rem !important;
        margin: 0.5rem 0 0 0 !important;
    }

    /* 调整列布局样式 */
    [data-testid="stHorizontalBlock"] {
        margin-top: 60px !important;
        display: flex;
        flex-direction: row;
        gap: 0;
    }

    /* 主列样式 */
    [data-testid="column"]:first-child {
        flex: 3;
        height: calc(100vh - 60px);
        overflow-y: auto;
        padding: 2rem !important;
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }

    /* 聊天列样式 */
    [data-testid="column"]:last-child {
        flex: 1;
        height: calc(100vh - 60px);
        padding: 0 !important;
        background-color: #ffffff;
        display: flex;
        flex-direction: column;
        position: sticky;
        top: 60px;
    }

    /* 聊天机器人容器样式 */
    .chat-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: 2rem;
    }

    /* 聊天标题样式 */
    .chat-title {
        padding: 2rem 2rem 1rem 2rem;
        background: #ffffff;
    }
    
    /* 聊天历史区域样式 */
    .chat-history {
        flex: 1;
        overflow-y: auto;
        padding: 0 2rem;
    }
    
    .chat-message {
        margin-bottom: 1rem;
        padding: 0.8rem;
        border-radius: 8px;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 1rem;
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 1rem;
    }

    /* 调整输入框样式 */
    .stTextInput {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 1rem 2rem;
        border-top: 1px solid #e0e0e0;
        margin: 0;
    }

    .stTextInput input {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 0.5rem;
        background-color: white;
        width: 100%;
    }

    /* 隐藏输入框标签 */
    .stTextInput label {
        display: none;
    }

    /* 确保主内容区域不被导航栏遮挡 */
    .main .block-container {
        padding: 0 !important;
        max-width: unset;
    }

    /* 移除Streamlit默认padding */
    .css-1544g2n.e1fqkh3o4 {
        padding: 0 !important;
    }

    /* 调整页面背景 */
    .stApp {
        background: #ffffff;
    }

    /* 隐藏Streamlit默认header */
    header[data-testid="stHeader"] {
        display: none;
    }

    /* 调整卡片样式 */
    .card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .section-header {
        color: #1976D2;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# 创建导航栏
st.markdown(f"""
    <div class="nav-container">
        <div class="brand-container">
            {logo_html}
        </div>
        <div class="nav-buttons">
            <button class="nav-button" onclick="window.parent.location.reload()">Home</button>
            <button class="nav-button">About Us</button>
        </div>
    </div>
""", unsafe_allow_html=True)

# 创建两列布局
main_col, chat_col = st.columns([3, 1])

# 主要内容区域
with main_col:
    # 主标题
    st.markdown("""
        <div style='text-align: center; margin: 2rem 0;'>
            <h1 style='color: #1a237e; margin-bottom: 0.5rem;'>
                Resume In. Career Out.
            </h1>
            <p style='color: #666; font-size: 1.2rem; margin-top: 0.5rem;'>
                Resumer helps you understand your resume — and where it can take you.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 文件上传部分
    uploaded_file = st.file_uploader(
        "",
        type=["docx", "pdf"],
        help="Support .docx or .pdf format, max file size 200MB",
        label_visibility="collapsed"
    )

    # 移除显示上传提示的部分
    if not uploaded_file:
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
            </div>
        """, unsafe_allow_html=True)

if uploaded_file:
    try:
        file_type = uploaded_file.name.split(".")[-1].lower()
        resume_text = read_resume(uploaded_file, file_type)
        resume_data = extract_resume_info(resume_text)

        # 简历预览
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">📝 Resume Preview</h3>', unsafe_allow_html=True)
        st.text_area("", value=resume_text[:500], height=150)
        st.markdown('</div>', unsafe_allow_html=True)

        # 职业方向预测
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">🎯 Predicted Career Fields</h3>', unsafe_allow_html=True)
        try:
            top_roles = predict_top_careers(resume_text)
            if top_roles:
                for role in top_roles:
                    st.markdown(f"""
                        <div style='padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 1rem;'>
                            <h4 style='color: #2c3e50;'>🎯 {role["job_title"]}</h4>
                            <p style='color: #34495e;'>Match Score: <strong>{role["score"]:.2f}%</strong></p>
                            <p style='color: #34495e;'>Matched Skills: {', '.join(role["matched_skills"]) if role["matched_skills"] else "None detected"}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No suitable career fields found.")
        except Exception as e:
            st.error(f"Prediction error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

        # 推荐职业路径
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">🌟 Recommended Career Paths</h3>', unsafe_allow_html=True)
        try:
            with open("job_data.json", "r", encoding="utf-8") as f:
                job_descriptions = json.load(f)
            recommended_jobs = recommend_jobs_tfidf(resume_text, job_descriptions)
            for job in recommended_jobs:
                st.markdown(f"✨ {job}")
        except Exception as e:
            st.error(f"Failed to load job data: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

        # 简历评估
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">📊 Resume Evaluation</h3>', unsafe_allow_html=True)
        with st.spinner("Analyzing your resume..."):
            try:
                score_result = score_resume_with_deepseek(resume_text)
            except Exception as e:
                score_result = f"Error while scoring resume: {e}"
            st.text_area("", value=score_result, height=200)
        st.markdown('</div>', unsafe_allow_html=True)

        # 结构化简历分析
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">📑 Structured Resume Analysis</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div style="padding: 1rem;">', unsafe_allow_html=True)
            st.markdown('<h4 style="color: #2c3e50;">🎓 Education</h4>', unsafe_allow_html=True)
            if resume_data["Education"]:
                for i, edu in enumerate(resume_data["Education"], 1):
                    st.markdown(f"<p style='margin-bottom: 0.5rem;'><strong>{i}.</strong> {edu}</p>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No education experience detected.")

            st.markdown('<h4 style="color: #2c3e50; margin-top: 1rem;">💼 Work Experience</h4>', unsafe_allow_html=True)
            if resume_data["Work Experience"]:
                for i, work in enumerate(resume_data["Work Experience"], 1):
                    st.markdown(f"<p style='margin-bottom: 0.5rem;'><strong>{i}.</strong> {work}</p>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No work experience found.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div style="padding: 1rem;">', unsafe_allow_html=True)
            st.markdown('<h4 style="color: #2c3e50;">🔬 Research / Projects</h4>', unsafe_allow_html=True)
            if resume_data["Research Experience"]:
                for i, res in enumerate(resume_data["Research Experience"], 1):
                    st.markdown(f"<p style='margin-bottom: 0.5rem;'><strong>{i}.</strong> {res}</p>", unsafe_allow_html=True)
            else:
                st.info("ℹ️ Consider adding research or project experience.")

            st.markdown('<h4 style="color: #2c3e50; margin-top: 1rem;">🛠️ Skills & Interests</h4>', unsafe_allow_html=True)
            if resume_data["Skills & Interests"]:
                st.markdown(f"<p style='background-color: #f8f9fa; padding: 1rem; border-radius: 8px;'>{', '.join(resume_data['Skills & Interests'])}</p>", unsafe_allow_html=True)
            else:
                st.info("ℹ️ No skills or interests found. Consider listing relevant tools or languages.")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")

# Chatbot部分移到右侧列
with chat_col:
    # 初始化聊天历史
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "memory_notes" not in st.session_state:
        st.session_state.memory_notes = ""
    
    # ResuBot标题
    st.markdown("""
        <div class="chat-title">
            <h1 style="color: #1976D2; margin-bottom: 0.3rem; font-size: 2rem; text-align: center;">ResuBot</h1>
            <p style="color: #666; font-size: 1.2rem; margin: 0; text-align: center;">Your AI Career & Resume Advisor</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 聊天历史区域
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    if st.session_state.chat_history:
        for speaker, msg in st.session_state.chat_history:
            message_class = "user-message" if speaker == "You" else "assistant-message"
            st.markdown(f"""
                <div class="chat-message {message_class}">
                    <strong>{'🧑' if speaker == 'You' else '🤖'} {speaker}:</strong><br>
                    {msg}
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 定义回调函数
    def on_input_change():
        user_message = st.session_state.chat_input
        if user_message:
            try:
                # 调用chatbot获取回复
                current_resume = resume_text if 'resume_text' in locals() else ""
                reply = ask_chatbot(
                    resume_text=current_resume,
                    chat_history=st.session_state.chat_history,
                    memory_notes=st.session_state.memory_notes,
                    user_input=user_message
                )
                
                # 更新聊天历史
                st.session_state.chat_history.append(("You", user_message))
                st.session_state.chat_history.append(("Assistant", reply))
                st.session_state.memory_notes += f"User asked: {user_message}\nAssistant answered: {reply}\n"
            except Exception as e:
                st.error(f"Error processing your request: {str(e)}")

    # 聊天输入框
    st.text_input(
        "",
        placeholder="Ask a question about your career or resume",
        key="chat_input",
        on_change=on_input_change,
        label_visibility="collapsed"
    ) 