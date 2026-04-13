# 导入所需的模块
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import akshare as ak

# 加载环境变量
load_dotenv()

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

# 获取模型名称
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")



# 定义数据获取函数
def get_stock_basic_info(stock_code):
    # 获取A股全市场行情
    stock_zh_a_spot_df = ak.stock_zh_a_spot()
    # 处理代码，将代码作为唯一索引
    # for i in range(len(stock_zh_a_spot_df["代码"])):
    #     stock_zh_a_spot_df.loc[i, "代码"] = stock_zh_a_spot_df.loc[i, "代码"].[2:]
    stock_zh_a_spot_df["代码"] = stock_zh_a_spot_df["代码"].str[2:]
    stock_zh_a_spot_df.set_index("代码",drop=True,inplace=True)
    # 获取股票信息
    try:
        stock = stock_zh_a_spot_df.loc[stock_code]
    except KeyError:
        return "股票代码错误,未找到该股票,请检查代码"
    stock_basic_info = (f"股票名称为{stock['名称']}，股票价格为{stock['最新价']}，股票涨跌幅为{stock['涨跌幅']}，"
                        f"股票涨跌额为{stock['涨跌额']}，股票成交量为{stock['成交量']}，股票成交额为{stock['成交额']},"
                        f"股票最高价格为{stock['最高']},股票最低价格为{stock['最低']}")
    return stock_basic_info



# 定义ai分析内容生成函数
def generate_ai_analysis(stock_basic_info):
    # 构建提示词
    system_prompt ="""
        你是一个资深股票分析专家，尤其擅长技术面的分析，请根据股票信息进行股票分析，并给出相应的建议。
    """
    user_prompt = f"""
        根据股票信息：{stock_basic_info}
        请提供：
        1. 当前走势分析
        2. 关键价格点位
        3. 投资建议
        4. 风险提示
    """

    try:
        # 调用 API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # 获取结果
        result = response.choices[0].message.content
    except Exception as e:
        result = "AI分析失败"
        print(e)
    return  result



#---------------------------------------------------------------------------------------------------

# 创建 Streamlit 应用

# 页面大标题
st.set_page_config(page_title="A股股票分析", page_icon="📈",layout="wide")
st.title("A股股票分析(技术面)")
st.caption("输入股票代码，获得实时行情与AI简评")

# 输入框
stock_code = st.text_input(label="股票代码",placeholder="如:920001",width=200)

# 创建分析按钮
# st.button("开始分析", type="primary")

# 创建并判断按钮点击
if st.button("开始分析", type="primary"):
    if len(stock_code) != 6 or len(stock_code) == 0:
        st.warning("请输入正确的股票代码")
        st.stop ()
    with st.spinner("🔍 正在获取实时行情..."):
        stock_basic_info = get_stock_basic_info(stock_code)
    st.session_state.stock_info = stock_basic_info
    if stock_basic_info == "股票代码错误,未找到该股票,请检查代码":
        st.error(stock_basic_info)
        st.stop()
    with st.spinner("🤖 AI 正在分析技术面..."):
        result = generate_ai_analysis(stock_basic_info)
    st.session_state.analysis_result = result
    if result == "AI分析失败":
        st.error(result + "请稍后重试")
        st.stop()

# 渲染结果
if "stock_info" in st.session_state and "analysis_result" in st.session_state:
    st.divider ()
    st.subheader("📝股票信息")
    st.markdown(stock_basic_info)
    st.divider ()
    st.subheader("📊 AI 分析报告")
    st.markdown(result)





















# if __name__ == '__main__':
#     print(generate_ai_analysis(get_stock_basic_info('600726')))