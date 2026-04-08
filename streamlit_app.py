import streamlit as st
import pandas as pd

# ==================== 知识库（已集成你上传的11个问答）===================
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

【学员真实问答库（已学习）】
1. 培训模式选择：一对一4400元（灵活）、一对二4100元（快节奏）、VIP6800元（包接送）
2. 费用说明：只有培训费+570考试费，无其他隐藏收费，科目二三补考费全包
3. 为什么比其他驾校贵：真实学时打卡，不混卡，安全第一
4. 优惠政策：普通100元、资格证300元、学生组团800元
5. 考场与练车：免费练科目二考场 + 免费科目三考试系统
6. 拿证后终身免费陪练
7. 真实打卡承诺
8. 可以自由选教练，随时换教练
9. 投诉机制直达校长
10. 欢迎先来看场地
11. 报名准备材料及最快练车时间
"""
        self.extra_knowledge = ""   # 以后你继续上传的新知识会追加在这里

    def add_knowledge(self, new_text: str):
        self.extra_knowledge += "\n\n【新知识】\n" + new_text.strip()

    def get_full_knowledge(self):
        return self.base_knowledge + self.extra_knowledge

# ==================== 系统提示词 ====================
SYSTEM_PROMPT = """
你是内江双安驾校的资深教练助理，说话像暖心实在的老教练（亲切、口语化、带四川暖心感）。
你现在已经学习了完整的11个学员真实问答，必须100%基于这些知识回答。
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
    if "kb" not in st.session_state:
        st.session_state.kb = KnowledgeBase()

    uploaded_file = st.file_uploader("📤 上传新知识库（txt/csv/xlsx）", type=["txt", "csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".txt"):
                new_text = uploaded_file.getvalue().decode("utf-8")
            else:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
                new_text = df.to_string(index=False)
            st.session_state.kb.add_knowledge(new_text)
            st.success("✅ 新知识已成功学习！")
        except:
            st.error("上传失败，请检查文件格式")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 清空额外知识"):
            st.session_state.kb.extra_knowledge = ""
            st.success("已清空")
    with col2:
        if st.button("📥 下载当前完整知识库"):
            st.download_button("点击下载", st.session_state.kb.get_full_knowledge(), file_name="内江双安驾校知识库.txt")

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
            full_prompt = f"{SYSTEM_PROMPT}\n\n当前完整知识库：\n{st.session_state.kb.get_full_knowledge()}\n\n历史对话：\n" + \
                         "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]]) + \
                         f"\n\n学员问题：{prompt}\n请立即用最暖心的语气回复："

            import os
            from groq import Groq
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": SYSTEM_PROMPT},
                          {"role": "user", "content": full_prompt}],
                temperature=0.7,
                max_tokens=800,
            )
            response = completion.choices[0].message.content

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
