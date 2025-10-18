# 🤖 多智能体AI求职助手 (AI Job Assistant)

## 项目简介

“多智能体AI求职助手” 是一个基于 **千问大模型 (Qwen)** 的智能应用项目，旨在为求职者提供：
- 简历解析与优化建议  
- 面试问题模拟与反馈评估  

项目展示了一个AI工程师所需的核心能力，包括：
- 大模型微调与Prompt设计  
- 智能体（Agent）系统构建  
- RAG（检索增强生成）技术  
- Web API与前端整合  
- 云端部署与版本管理  

---

## 🧩 系统架构

AIJobAssistant/
├── config/ # 配置文件
│ └── config.py
├── data/ # 数据与知识库
│ ├── sample_jd.txt
│ ├── interview_knowledge/tips.txt
│ └── resumes/
│   ├── resume_1.txt
│   └── resume_2.txt
├── src/
│ ├── api/main.py # FastAPI后端接口
│ ├── agents/qwen_client # 智能体定义
│ ├── utils/ # 工具函数
│    ├── file_parse.py
│    ├── interview_agent.py
│    ├── text_analysis.py
│    └── knowledge_base.py # 知识库构建逻辑
├── models_kb/
│ ├── faiss_index.index
│ └── faiss_index_chunks.pkl
├── main.py # FastAPI后端接口
├── app.py # Streamlit前端
├── DockerFile
├── README.md
└── requirements.txt # 环境依赖

yaml
复制代码

---

## 🚀 功能特性

### 🧠 1. 简历解析与优化智能体
- 使用千问大模型API从简历中提取结构化信息；
- 根据职位描述计算匹配度（余弦相似度）；
- 输出针对性优化建议。

### 💬 2. 面试模拟与反馈智能体
- 基于知识库（FAISS + LangChain）生成面试问题；
- 与用户进行多轮模拟面试；
- 根据回答内容进行分析与反馈。

---

## 🧰 技术栈

| 模块 | 技术栈 |
|------|---------|
| 模型调用 | Qwen API (千问模型) |
| 智能体框架 | LangChain |
| 向量数据库 | FAISS |
| 后端框架 | FastAPI |
| 前端界面 | Streamlit |
| 相似度计算 | Scikit-learn |

---

## ⚙️ 环境配置

### 1️⃣ 创建虚拟环境
```bash
conda create -n jobassistant python=3.10
conda activate jobassistant

2️⃣ 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

3️⃣ 配置千问API密钥

在根目录创建 .env 文件：

QWEN_API_KEY=你的千问API密钥

🧾 使用说明
启动后端
uvicorn src.api.main:app --reload


访问接口文档：
👉 http://127.0.0.1:8000/docs

启动前端
streamlit run app.py

📦 部署说明

构建Docker镜像：

docker build -t ai-job-assistant:v0.01 .


运行容器：

docker run -d -p 8000:8000 ai-job-assistant:v0.01

🧭 项目路线图
阶段	目标	状态
v0.01	项目初始化 + 简历解析 + 模拟面试原型	✅ 已完成
v0.1	加入千问微调模型 + 自动评估功能	🕓 进行中
v0.2	云端部署 + 多语言支持	🚧 计划中
👨‍💻 作者与版权

作者：MadPrinter
## 📦 Version v0.02
- 移除 parse_resume 中的重复匹配度计算逻辑
- 统一匹配度逻辑至 match_score.py
- 优化结果展示