import streamlit as st
import pandas as pd
from datetime import datetime

# ==================== 知识库（支持动态上传） ====================
class KnowledgeBase:
    def __init__(self):
        self.school_name = "内江双安驾校"
        self.base_knowledge = """
一对一：4300元培训费 + 570元考试费
一对多（含一对二）：4000元培训费 + 570元考试费
教师/医生/护士/警官再优惠200元
内江职院、师院、卫健院学生组团总优惠800元
包含科目二、三补考费 + 免费科目二考场 + 免费科目三考试系统 + 拿证后终身免费陪练
严格教学大纲：上车进卡、下车退卡、真实学时
其他驾校常有隐形收费 + 练车时间不足，安全隐患大
"""
        self.extra_knowledge = ""   # 后面上传的新知识会追加在这里

    def add_knowledge(self, new_text: str):
        self.extra_knowledge += "\n\n【新知识】\n" + new_text.strip()

    def get_full_knowledge(self):
        return self.base_knowledge + self.extra_knowledge

# ==================== 系统提示词 ====================
SYSTEM_PROMPT = """
你是内江双安驾校的资深教练助理，说话像暖心实在的老教练（亲切、口语化、带四川暖心感）。
回复铁律：
1. 先暖心拉近距离（哈哈姐/哥别慌～）
2. 直接说清楚价格、优惠、优势
3. 自然对比其他驾校但只讲事实
4. 学员犹豫就鼓励“教学严是为了你以后开车真安全”
5. 最后主动问下一步
"""

# ==================== 主界面 ====================
st.set_page_config(page_title="内江双安驾校智能咨询", page_icon="🚗")
st.title("🚗 内江双安驾校智能咨询")
st.caption("真人老教练在线，随时问报名、费用、优惠、考试～")

# 侧边栏 - 知识库管理
with st.sidebar:
    st.subheader("📚 知识库管理")
    
    uploaded_file = st.file_uploader("📤 上传新知识库（txt/csv/xlsx）", 
                                   type=["txt", "csv", "xlsx"], 
                                   help="上传后智能体立即学习")
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".txt"):
            new_text = uploaded_file.getvalue().decode("utf-8")
        else:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            new_text = df.to_string(index=False)
        
        st.session_state.kb.add_knowledge(new_text)
        st.success(f"✅ 已成功学习 {len(new_text)} 个字符的新知识！")
    
    if st.button("🗑️ 清空额外知识库"):
        st.session_state.kb.extra_knowledge = ""
        st.success("已清空额外知识库")
    
    if st.button("📥 下载当前完整知识库"):
        full = st.session_state.kb.get_full_knowledge()
        st.download_button("点击下载 knowledge.txt", full, file_name="knowledge.txt")

# 初始化知识库
if "kb" not in st.session_state:
    st.session_state.kb = KnowledgeBase()

# ==================== 聊天界面 ====================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("输入你的问题，例如：一对一多少钱？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("教练正在思考..."):
            # 构造完整提示词
            full_prompt = f"{SYSTEM_PROMPT}\n\n当前完整知识库：\n{st.session_state.kb.get_full_knowledge()}\n\n历史对话：\n" + \
                         "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]]) + \
                         f"\n\n学员问题：{prompt}\n请立即用最暖心的语气回复："

            # 调用 Groq
            import os
            from groq import Groq
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=800,
            )
            response = completion.choices[0].message.content

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
