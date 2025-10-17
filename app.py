# app.py
import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="多智能体AI求职助手（Qwen）", layout="wide")
st.title("🤖 多智能体 AI 求职助手 （基于通义千问）")

st.sidebar.header("操作")
if st.sidebar.button("构建/重建知识库 (KB)"):
    r = requests.post(f"{API_BASE}/build_kb")
    st.sidebar.write(r.json())

st.header("1. 上传简历 & 解析技能")
uploaded_file = st.file_uploader("上传你的简历 (PDF/DOCX/TXT)", type=["pdf","docx","txt"])
if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    r = requests.post(f"{API_BASE}/parse_resume", files=files)
    st.subheader("解析结果预览")
    st.json(r.json())

st.header("2. 匹配职位 (计算Match Score)")
jd = st.text_area("输入职位描述 (Job Description)")
if uploaded_file and jd:
    if st.button("计算匹配度"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        data = {"jd": jd}
        r = requests.post(f"{API_BASE}/match_score", files=files, data=data)
        st.success(f"匹配度（0-100）: {r.json().get('match_score')}")

st.header("3. 生成面试题 & 模拟面试")
if jd:
    if st.button("生成面试题 (5题)"):
        r = requests.post(f"{API_BASE}/gen_questions", data={"jd": jd, "n": 5})
        qs = r.json().get("questions", [])
        for i,q in enumerate(qs,1):
            st.write(f"**Q{i}.** {q}")
        st.session_state.questions = qs

if "questions" in st.session_state:
    st.subheader("选择题目进行模拟")
    qsel = st.selectbox("选择问题", options=st.session_state.questions)
    ans = st.text_area("你的回答")
    if st.button("评估回答"):
        data = {"jd": jd, "question": qsel, "answer": ans}
        r = requests.post(f"{API_BASE}/evaluate", data=data)
        st.json(r.json())
