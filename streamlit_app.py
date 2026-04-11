import streamlit as st
import requests
from datetime import datetime

# ==================== PushPlus 配置 ====================
PUSHPLUS_TOKEN = "aee08b3ce199478f90b6ce3902fd448b"

def send_wechat_notification(user_message: str):
    """发送微信通知给你"""
    try:
        url = f"https://www.pushplus.plus/send"
        data = {
            "token": PUSHPLUS_TOKEN,
            "title": "🚗 新学员咨询",
            "content": f"时间：{datetime.now().strftime('%H:%M:%S')}\n\n学员说：{user_message}",
            "template": "txt"
        }
        requests.post(url, data=data, timeout=5)
    except:
        pass  # 通知失败也不影响智能体运行

# ==================== 知识库 ====================
KNOWLEDGE = """
一对一：4400元培训费 + 570元考试费，总共4970元
一对二：4100元培训费 + 570元考试费，总共4670元
教师/医生/护士/警官再优惠200元
学生组团优惠800元
包含科目二、三补考费 + 免费考场 + 终身陪练
严格真实学时打卡
"""

SYSTEM_PROMPT = f"""
你是内江双安驾校的资深教练助理，说话像暖心实在的老教练（亲切、口语化、带四川暖心感）。

必须严格遵守以下知识：
{KNOWLEDGE}

回复铁律：
1. 先暖心拉近距离（哈哈姐/哥别慌～）
2. 直接说清楚价格、优惠、优势
3. 自然对比其他驾校但只讲事实
4. 学员犹豫就鼓励“教学严是为了你以后开车真安全”
5. 最后主动问下一步
"""

st.set_page_config(page_title="内江双安驾校智能咨询", page_icon="🚗")
st.title("🚗 内江双安驾校智能咨询")
st.caption("真人老教练在线 · 已学习11个学员真实问答 · 已开启微信通知")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入你的问题，例如：一对一多少钱？"):
    # 发送微信通知给你
    send_wechat_notification(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("教练正在思考..."):
            full_prompt = f"{SYSTEM_PROMPT}\n\n历史对话：\n" + \
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
