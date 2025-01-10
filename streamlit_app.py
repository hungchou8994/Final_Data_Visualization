import os
import streamlit as st
import pandas as pd
from openai import OpenAI as oai
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.responses.response_parser import ResponseParser

def load_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        st.error(f"Lỗi khi đọc file {file_path}: {e}")
        return ""

# Load dataset-related information
dataset_text = load_file_content("./data/dataset_info.txt")
extra_info = load_file_content("./data/extra_info.txt")
extra_info_2 = load_file_content("./data/extra_info_2.txt")
#density = load_file_content("./data/density.txt")
openai_insights = load_file_content("./data/openai_insights.txt")
#openai_insights_2 = load_file_content("./data/openai_insights_2.txt")
openai_summary = load_file_content("./data/openai_summary.txt")


class StreamlitResponse(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
        st.dataframe(result["value"])
        return

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_other(self, result):
        st.write(result["value"])
        return

df = pd.read_csv('./data/data_dv.csv', encoding="utf-8")

st.write("Trợ lý AI báo cáo dữ liệu")

with st.expander("🔎 Dataframe Preview"):
    st.write(df.tail(3))

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

llm = OpenAI(api_token=OPENAI_API_KEY)

query = st.text_area("🗣️ Chat with Dataframe")

client = oai(
    api_key=OPENAI_API_KEY,
)

def generate_openai_response(prompt, model="gpt-4o-mini", max_tokens=1500):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Bạn là một trợ lý thông minh, có khả năng trả lời các câu hỏi liên quan đến một bộ dữ liệu lớn."},
                {"role": "user", "content": prompt}
            ],
            #max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Lỗi khi gọi API OpenAI: {e}"

def process_user_query(query, openai_answer):
    system_prompt = (
        f"""
Bạn là một trợ lý thông minh với khả năng trả lời các câu hỏi phức tạp liên quan đến bộ dữ liệu lớn và phân tích sâu sắc. Bạn có khả năng giúp người dùng hiểu rõ hơn về các thông tin và các phân tích có sẵn, cũng như hỗ trợ họ đưa ra các quyết định chính xác và hợp lý dựa trên dữ liệu.

**Thông tin về bộ dữ liệu**:
{dataset_text}

**Nhận xét từ con người**:
{extra_info}
{extra_info_2}

**Phân tích và nhận xét từ OpenAI**:
{openai_insights}

**Tóm tắt tổng quan**:
{openai_summary}

**Nhiệm vụ của bạn**:
- Xử lý và chọn lọc các thông tin quan trọng, đặc biệt chú trọng đến những yếu tố có tính trùng lặp cao và bảo đảm tính chính xác trong các phân tích.
- Cung cấp các dự đoán hoặc giải thích dựa trên dữ liệu có sẵn và kết nối các phân tích với các tình huống thực tế. Đảm bảo rằng các dự đoán này dễ hiểu và có thể giúp người dùng hình dung rõ ràng về kết quả có thể xảy ra.
- Phân tích và kết nối các yếu tố dữ liệu để tạo ra những nhận xét có chiều sâu và hữu ích cho người dùng. Đưa ra các nhận xét bổ sung nếu nhận thấy rằng người dùng có thể chưa nhận ra một mối liên hệ quan trọng nào đó trong dữ liệu.
- Khi trả lời câu hỏi, hãy đảm bảo rằng câu trả lời của bạn rõ ràng, dễ hiểu và mạch lạc. Đặc biệt chú trọng đến việc giải quyết các câu hỏi phức tạp hoặc mơ hồ bằng cách cung cấp các giải thích chi tiết và dễ tiếp cận.
- Nếu câu hỏi có sự mơ hồ hoặc không rõ ràng, hãy yêu cầu người dùng cung cấp thêm thông tin và làm rõ các yêu cầu, hoặc đề xuất các giải pháp khả thi mà họ có thể tham khảo để đạt được câu trả lời chính xác hơn.

**Câu hỏi từ người dùng**: {query}

**Câu trả lời mẫu từ OpenAI**: {openai_answer}

Hãy trả lời một cách chi tiết, rõ ràng và chính xác bằng Tiếng Việt. Đảm bảo rằng câu trả lời của bạn không chỉ đầy đủ mà còn có tính linh hoạt, giúp người dùng không chỉ trả lời câu hỏi mà còn khám phá thêm thông tin có giá trị từ bộ dữ liệu.
"""
    )
    return generate_openai_response(system_prompt)

if query:
    query_engine = SmartDataframe(
        df,
        config={
            "llm": llm,
            "response_parser": StreamlitResponse,
            #"custom_whitelisted_dependencies": None,
            # "callback": StreamlitCallback(container),
        },
    )
    user_query =  f"""
    **Câu hỏi từ người dùng**: {query}

    Hãy trả lời một cách chi tiết, rõ ràng và chính xác bằng Tiếng Việt. Đảm bảo rằng câu trả lời của bạn không chỉ đầy đủ mà còn có tính linh hoạt, giúp người dùng không chỉ trả lời câu hỏi mà còn khám phá thêm thông tin có giá trị từ bộ dữ liệu.
    """

    openai_answer = query_engine.chat(user_query)
    answer = process_user_query(query,openai_answer)
    st.write(answer)