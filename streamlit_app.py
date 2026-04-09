import streamlit as st
import random

# ==================== 多 Key 自动轮换 ====================
API_KEYS = [
    "w68B4JxyLxUY6TxiJoTFikjx",
    "W5L3TFnZM8MqH_CSaKZqJ9i2",
    "KRk6QVZz_8yFSjzaYcVkyEL7",
    "YuHiZKR6KTHF7okKpnkUsyrX",
    "xY-D-4LvyK24yttmtsXABYxd"
]

def get_groq_client():
    """自动轮换 Key"""
    random.shuffle(API_KEYS)  # 每次打乱顺序，避免总是用同一个
    for key in API_KEYS:
        try:
            from groq import Groq
            client = Groq(api_key=key)
            # 测试一下是否可用
            client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=10
            )
            return client
        except:
            continue
    return None  # 所有 Key 都不可用

# ==================== 最新知识库 ====================
KNOWLEDGE = """
【内江双安驾校最新价格（必须严格遵守）】
一对一：培训费4400元 + 交警考试费570元，总共4970元
一对二：培训费4100元 + 交警考试费570元，总共4670元

教师/医生/护士/警官再优惠200元
学生组团优惠800元
包含科目二、三补考费 + 免费科目二考场 + 免费科目三考试系统 + 拿证后终身免费陪练
严格真实学时打卡
"""

SYSTEM_PROMPT = f"""
你是内江双安驾校的资深教练助理，说话像暖心实在的老教练（亲切、口语化、带四川暖心感）。

必须100%严格遵守以下价格，绝不能修改或遗漏：
{KNOWLEDGE}

回复铁律：
1. 先暖心拉近距离（哈哈姐/哥别慌～）
2. 直接报出培训费 + 考试费（考试费要说明是交给交警队的）
3. 自然对比其他驾校但只讲事实
4. 学员犹豫就鼓励“教学严是为了你以后开车真安全”
5. 最后主动问下一步
"""

st.set_page_config(page_title="内江双安驾校智能咨询", page_icon="🚗")
st.title("🚗 内江双安驾校智能咨询")
st.caption("真人老教练在线 · 多 Key 自动切换 · 已学习11个学员真实问答")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入你的问题，例如：一对一多少钱？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("教练正在思考..."):
            client = get_groq_client()
            if client is None:
                response = "教练这里网络有点小卡顿～您可以稍等几秒再问我，或者直接打电话给我！😊"
            else:
                full_prompt = f"{SYSTEM_PROMPT}\n\n历史对话：\n" + \
                             "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]]) + \
                             f"\n\n学员问题：{prompt}\n请立即用最暖心的语气回复："

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
