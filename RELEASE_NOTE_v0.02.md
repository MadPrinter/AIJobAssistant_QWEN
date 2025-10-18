# Release v0.02 - 优化解析与匹配模块

### 🧩 更新内容
- 删除 parse_resume.py 中重复的匹配度计算逻辑；
- 统一匹配度计算到 match_score.py；
- 优化了结果展示，去掉了不必要的 JSON 输出；
- 提高了系统运行稳定性。

### ⚙️ 环境
- Python 3.10+
- FastAPI 0.119+
- Streamlit 1.26+
- Qwen API

### 🚀 启动方式
```bash
uvicorn backend.main:app --reload
streamlit run app.py
