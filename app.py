import streamlit as st
import requests

# 后端 API 地址（确保与 FastAPI 服务地址一致）
API_BASE = "http://127.0.0.1:8000"

# 页面基础配置
st.set_page_config(page_title="多智能体AI求职助手（Qwen）", layout="wide")
st.title("🤖 多智能体 AI 求职助手 （基于通义千问）")

# ---------------------- 1. 全局 JD 输入（让用户统一输入，所有模块复用）----------------------
# 用 st.session_state 存储 JD，实现跨模块复用（用户输入一次，其他模块可直接用）
if "jd" not in st.session_state:
    st.session_state.jd = ""

# 单独的 JD 输入区域（放在页面顶部，更醒目，用户一次输入全局可用）
st.subheader("📝 输入职位描述（JD）")
jd_input = st.text_area(
    "请粘贴你要申请的岗位的职位描述（包含岗位职责、任职要求等）",
    value=st.session_state.jd,  # 保留上次输入的 JD
    height=200,
    help="示例：Python工程师岗位要求：1. 熟练使用Python；2. 熟悉MySQL；3. 有AI项目经验"
)
# 实时更新 session_state 中的 JD（用户输入变化时同步）
if jd_input != st.session_state.jd:
    st.session_state.jd = jd_input

# ---------------------- 2. 侧边栏：构建知识库 ----------------------
st.sidebar.header("操作中心")
if st.sidebar.button("构建/重建知识库 (KB)"):
    with st.spinner("正在构建知识库...（可能需要几秒）"):
        try:
            r = requests.post(f"{API_BASE}/build_kb", timeout=30)
            r.raise_for_status()  # 捕获 HTTP 错误
            st.sidebar.success("知识库构建成功！")
        except Exception as e:
            st.sidebar.error(f"构建失败：{str(e)}")

# ---------------------- 3. 上传简历 & 解析技能（支持结合 JD 解析）----------------------
st.header("1. 📄 上传简历 & 解析技能")
uploaded_file = st.file_uploader("上传你的简历 (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

# 新增：是否结合 JD 解析（让用户选择是否需要基于 JD 突出相关技能）
use_jd_for_parse = st.checkbox("结合上方 JD 解析（优先展示与 JD 相关的技能）", value=True)

if uploaded_file is not None:
    st.info(f"已上传简历：{uploaded_file.name}")
    if st.button("开始解析简历"):
        with st.spinner("正在解析简历..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                r = requests.post(f"{API_BASE}/parse_resume", files=files, timeout=30)
                r.raise_for_status()
                result = r.json()

                st.subheader("📄 简历解析结果")
                st.write("**简历文本片段（前1000字符）**：")
                st.text(result.get("text_snippet", "")[:1000])
                st.write("**提取的技能关键词：**")
                skills = result.get("skills", [])
                if skills:
                    st.markdown(", ".join([f"✅ {s}" for s in skills]))
                else:
                    st.warning("未提取到明显技能，请检查简历格式是否清晰。")

            except Exception as e:
                st.error(f"解析失败：{e}")

# ---------------------- 4. 匹配职位（复用全局 JD，无需重复输入）----------------------
st.header("2️⃣ 简历与 JD 匹配度计算")
if not st.session_state.jd.strip():
    st.warning("请先在顶部输入职位描述（JD）！")
elif not uploaded_file:
    st.warning("请先上传简历文件！")
else:
    if st.button("计算匹配度"):
        with st.spinner("正在计算匹配度..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                data = {"jd": st.session_state.jd}
                r = requests.post(f"{API_BASE}/match_score", files=files, data=data, timeout=20)
                r.raise_for_status()
                score = r.json().get("match_score", 0)

                st.success(f"🎯 匹配度：{score} / 100")
                if score >= 80:
                    st.info("✅ 匹配度优秀！你的简历与岗位高度契合。")
                elif score >= 60:
                    st.info("🟡 匹配度良好，可优化重点技能描述。")
                else:
                    st.info("🔴 匹配度一般，建议针对性补充相关经验。")

            except Exception as e:
                st.error(f"计算失败：{e}")

# ---------------------- 5. 生成面试题 & 模拟面试（复用全局 JD）----------------------
st.header("3️⃣ 智能生成面试题 & 回答评估")
if not st.session_state.jd.strip():
    st.warning("请先输入 JD！")
else:
    n_questions = st.slider("生成题目数量", 3, 10, 5)
    if st.button("生成面试题"):
        with st.spinner("正在生成面试题..."):
            try:
                data = {"jd": st.session_state.jd, "n": n_questions}
                r = requests.post(f"{API_BASE}/gen_questions", data=data, timeout=60)
                r.raise_for_status()
                qs = r.json().get("questions", [])
                if qs:
                    st.success(f"成功生成 {len(qs)} 道面试题：")
                    st.session_state.questions = qs
                    for i, q in enumerate(qs, 1):
                        st.write(f"**Q{i}.** {q}")
                else:
                    st.warning("未生成题目，请检查 JD 内容。")
            except Exception as e:
                st.error(f"生成失败：{e}")

if "questions" in st.session_state:
    st.subheader("💬 模拟面试评估")
    qsel = st.selectbox("请选择一个问题", options=st.session_state.questions)
    ans = st.text_area("请输入你的回答：", height=150)
    if st.button("提交评估"):
        if not ans.strip():
            st.warning("请输入回答！")
        else:
            with st.spinner("AI 正在评估你的回答..."):
                try:
                    data = {"jd": st.session_state.jd, "question": qsel, "answer": ans}
                    r = requests.post(f"{API_BASE}/evaluate", data=data, timeout=60)
                    r.raise_for_status()
                    eval_res = r.json()
                    st.json(eval_res)
                except Exception as e:
                    st.error(f"评估失败：{e}")

# ---------------- 6. 知识库搜索 ----------------
st.header("4️⃣ 知识库搜索（面试技巧与资料）")
search_query = st.text_input("请输入查询内容（如“Python 面试技巧”）")
if st.button("搜索知识库"):
    if not search_query.strip():
        st.warning("请输入查询词！")
    else:
        with st.spinner("正在检索知识库..."):
            try:
                data = {"q": search_query, "top_k": 3}
                r = requests.post(f"{API_BASE}/kb_search", data=data, timeout=15)
                r.raise_for_status()
                results = r.json().get("results", [])
                if results:
                    for i, doc in enumerate(results, 1):
                        st.write(f"**结果 {i}:**")
                        st.text(doc[:500] + "..." if len(doc) > 500 else doc)
                else:
                    st.warning("未找到相关资料。")
            except Exception as e:
                st.error(f"搜索失败：{e}")