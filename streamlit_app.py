import streamlit as st

# ==================== 你的完整知识库（已硬编码，永不丢失） ====================
FULL_KNOWLEDGE = """
【内江双安驾校完整学员问答库（11问）】

1. 培训模式：一对一4400元（灵活）、一对二4100元（快节奏）、VIP6800元（包接送）
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

核心价格（必须严格遵守）：
- 一对一：4300元培训费 + 570元考试费
- 一对多（含一对二）：4000元培训费 + 570元考试费
"""

# ==================== 系统提示词（强制遵守知识库） ====================
SYSTEM_PROMPT = f"""
你是内江双安驾校的资深教练助理，说话像暖心实在的老教练（亲切、口语化、带四川暖心感）。

【必须100%严格遵守以下知识库，绝不能编造或修改任何价格和内容】：
{FULL_KNOWLEDGE}

回复铁律（必须严格遵守）：
1. 先暖心拉近距离（哈哈姐/哥别慌～）
2. 直接说清楚价格、优惠、优势
3. 自然对比其他驾校但只讲事实
4. 学员犹豫就鼓励“教学严是为了你以后开车真安全”
5. 最后主动问下一步

现在，请用最人性化、最像真教练的语气回复学员咨询。
"""

# ==================== 主界面 ====================
st.set_page_config(page_title="内江双安驾校智能咨询", page_icon="🚗")
st.title("🚗 内江双安驾校智能咨询")
st.caption("真人老教练在线，随时问报名、费用、优惠、考试～")

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
            full_prompt = f"{SYSTEM_PROMPT}\n\n历史对话：\n" + \
                         "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]]) + \
                         f"\n\n学员问题：{prompt}\n请立即回复："

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
