import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random

# ==================== SiliconFlow 多 Key ====================
SILICONFLOW_KEYS = [
    "sk-yhlmuczqjbdwycwvglmkjkwkdatmaohzdbuqxvppexljdphr",
    "sk-kitwvkpyqugdppyrtzqnmxdahnjwafbvsvhcqcittaznxllu",
    "sk-blireglehwbqpzdchcolpljonpptuzgombmojzpndtdolluw",
    "sk-fyzlmrlezwadkntxnovujtohjcioajngzpjwhhjzpmvctize"
]

def get_siliconflow_key():
    random.shuffle(SILICONFLOW_KEYS)
    return SILICONFLOW_KEYS[0]

# ==================== PushPlus 微信通知 ====================
PUSHPLUS_TOKEN = "aee08b3ce199478f90b6ce3902fd448b"

def send_wechat_notification(user_message: str):
    try:
        url = "https://www.pushplus.plus/send"
        data = {
            "token": PUSHPLUS_TOKEN,
            "title": "🚗 新学员咨询",
            "content": f"时间：{datetime.now().strftime('%H:%M:%S')}\n\n学员说：{user_message}",
            "template": "txt"
        }
        requests.post(url, data=data, timeout=5)
    except:
        pass

# ==================== 知识库 ====================
class KnowledgeBase:
    def __init__(self):
        self.base_knowledge = """
一对一：4400元培训费 + 570元考试费，总共4970元
一对二：4100元培训费 + 570元考试费，总共4670元
教师/医生/护士/警官再优惠200元
学生组团优惠800元
包含科目二、三补考费 + 免费科目二考场 + 免费科目三考试系统 + 拿证后终身免费陪练
严格真实学时打卡
"""
        self.extra_knowledge = ""

    def add_knowledge(self, new_text: str):
        self.extra_knowledge += "\n\n【新增知识】\n" + new_text.strip()

    def get_full_knowledge(self):
        return self.base_knowledge + self.extra_knowledge

# ==================== 系统提示词 ====================
SYSTEM_PROMPT = """
你是内江双安驾校的资深教练助理，说话像暖心实在的老教练（亲切、口语化、带四川暖心感）。

必须严格遵守以下知识：
一对一：4400元培训费 + 570元考试费，总共4970元
一对二：4100元培训费 + 570元考试费，总共4670元
教师/医生/护士/警官再优惠200元
学生组团优惠800元
包含科目二、三补考费 + 免费科目二考场 + 免费科目三考试系统 + 拿证后终身免费陪练
严格真实学时打卡

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
st.caption("真人老教练在线 · 多Key · 支持上传新知识库")

if "kb" not in st.session_state:
    st.session_state.kb = KnowledgeBase()

# 侧边栏知识库管理
with st.sidebar:
    st.subheader("📚 知识库管理")
    
    uploaded_file = st.file_uploader("📤 上传新知识库（txt / csv / xlsx）", type=["txt", "csv", "xlsx"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".txt"):
                new_text = uploaded_file.getvalue().decode("utf-8")
            else:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
                new_text = df.to_string(index=False)
            
            st.session_state.kb.add_knowledge(new_text)
            st.success("✅ 新知识已成功学习！")
        except Exception as e:
            st.error(f"上传失败: {str(e)}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 清空额外知识"):
            st.session_state.kb.extra_knowledge = ""
            st.success("已清空")
    with col2:
        if st.button("📥 下载当前知识库"):
            st.download_button("点击下载", st.session_state.kb.get_full_knowledge(), file_name="知识库.txt")

# ==================== 聊天界面 ====================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入你的问题，例如：一对一多少钱？"):
    send_wechat_notification(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("教练正在思考..."):
            try:
                key = get_siliconflow_key()
                url = "https://api.siliconflow.cn/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "deepseek-ai/DeepSeek-V3",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"{SYSTEM_PROMPT}\n\n当前知识库：{st.session_state.kb.get_full_knowledge()}\n\n学员问题：{prompt}"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 800
                }
                resp = requests.post(url, json=data, headers=headers, timeout=15)
                if resp.status_code == 200:
                    response = resp.json()["choices"][0]["message"]["content"]
                else:
                    response = "教练这里网络有点小卡顿～您可以稍等几秒再问我！😊"
            except:
                response = "教练这里网络有点小卡顿～您可以稍等几秒再问我，或者直接打电话给我！😊"

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
