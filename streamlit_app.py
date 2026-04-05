import streamlit as st

class KnowledgeBase:
    def __init__(self):
        self.school_name = "内江双安驾校"
        self.fees = {
            "一对一": "4300元培训费 + 570元考试费",
            "一对多(含一对二)": "4000元培训费 + 570元考试费"
        }
        self.discounts = "教师/医生/护士/警官再优惠200元；内江职院、师院、卫健院学生组团总优惠800元"
        self.advantages = [
            "包含科目二、三补考费",
            "免费练科目二考场",
            "免费使用科目三考试模拟系统",
            "拿证后终身免费陪练",
            "严格教学大纲：上车进卡、下车退卡、真实学时",
            "零隐形收费，随时换教练，投诉成立可全额退费"
        ]
        self.contrast = "其他驾校可能表面便宜，但练车时间少（路边打卡），安全隐患大。我们双安就是为了让你真正学会，以后开车更安全！"

    def get_summary(self):
        return f"【{self.school_name}】\n一对一：{self.fees['一对一']}\n一对多：{self.fees['一对多(含一对二)']}\n优惠：{self.discounts}\n优势：{'、'.join(self.advantages)}\n{self.contrast}"

SYSTEM_PROMPT = """
你是内江双安驾校的资深教练助理，说话像暖心实在的老教练（亲切、口语化、带四川暖心感）。
核心知识必须100%准确：
- 一对一：4300元培训费 + 570元考试费
- 一对多（含一对二）：4000元培训费 + 570元考试费
- 教师/医生/护士/警官再优惠200元
- 内江职院、师院、卫健院学生组团总优惠800元
- 包含科目二、三补考费 + 免费科目二考场 + 免费科目三考试系统 + 拿证后终身免费陪练
- 严格教学大纲：上车进卡、下车退卡、真实学时
- 其他驾校常有隐形收费 + 练车时间不足，安全隐患大

回复铁律：1. 先暖心拉近距离（哈哈姐/哥别慌～）；2. 直接说价格优惠优势；3. 自然对比其他驾校但只讲事实；4. 学员犹豫就鼓励“教学严是为了你以后开车真安全”；5. 最后主动问下一步。

用最像真教练的语气回复。
"""

class DrivingSchoolAgent:
    def __init__(self):
        self.kb = KnowledgeBase()
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def generate_response(self, user_question: str):
        context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-4:]])
        full_prompt = f"{SYSTEM_PROMPT}\n\n历史对话：\n{context}\n\n学员问题：{user_question}\n请立即用最暖心的语气回复："
        
        # 目前是模拟回复（后面我们改成自动）
        return "哈哈，姐/哥别慌～我来给你算算！一对一现在只要4300+570，你这种情况最划算。要不要我帮你算算组团优惠？周末我安排你来看看场地和教练？"

st.set_page_config(page_title="内江双安驾校智能咨询", page_icon="🚗")
st.title("🚗 内江双安驾校智能咨询")
st.caption("真人老教练在线，随时问报名、费用、优惠、考试～")

agent = DrivingSchoolAgent()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("输入你的问题，例如：一对一多少钱？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("教练正在思考..."):
            response = agent.generate_response(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

st.sidebar.success("✅ 已连接内江双安驾校知识库")
st.sidebar.info("学员在微信里点开就能聊天！")
