import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import Image as PILImage
import base64
import io
from io import BytesIO
import tempfile
from translate import Translator
from pandasai import SmartDataframe
from pandasai.responses.streamlit_response import StreamlitResponse
from pandasai.responses.response_parser import ResponseParser

from pandasai.engine import set_pd_engine
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from openai import OpenAI
from pandasai.llm import OpenAI as pOpenAI


from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import cm

set_pd_engine("pandas")

# OpenAI API Key

# Đăng ký font Be VietNam Pro
pdfmetrics.registerFont(TTFont('BeVietNamPro', r'Be_Vietnam_Pro/BeVietnamPro-Light.ttf'))

# Load data
file_path = 'data_dv.csv'  # Replace with your uploaded file path
data = pd.read_csv(file_path)

# Page configuration
st.set_page_config(page_title="ChatBot", layout="wide")

# Tùy chỉnh CSS để đẩy Markdown sát trên cùng
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem; /* Loại bỏ khoảng cách phía trên */
        }
        h1 {
            text-align: center;
            margin-top: 0;
            padding-top: 0;
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown("<h3 style='text-align: center;'>Traffic Accident Advisory ChatBot</h3>", unsafe_allow_html=True)

####################################################
c1, c2 = st.columns([1, 7])
with c1:
    st.image("Animation - 1736347933572.gif")
with c2:
    st.markdown("""
Chào mừng bạn đến với **Traffic Accident Advisory ChatBot**, một trợ lý ảo thông minh được phát triển để giúp bạn dễ dàng truy vấn thông tin và tạo ra các báo cáo chi tiết về tình hình tai nạn giao thông ở thành phố Hồ Chí Minh 2020-2021.
Dựa trên một tập dữ liệu phong phú và cập nhật, ChatBot có khả năng trả lời nhanh chóng và chính xác các câu hỏi liên quan đến số lượng, loại hình, địa điểm và nguyên nhân của các vụ tai nạn giao thông trong khu vực.
Với khả năng phân tích dữ liệu mạnh mẽ, ChatBot không chỉ đơn giản trả lời câu hỏi mà còn có thể tạo ra các báo cáo tùy chỉnh theo yêu cầu của bạn. Bạn có thể yêu cầu các báo cáo về:
- Tình hình tai nạn giao thông theo từng năm, từng khu vực.
- Mối liên hệ giữa các yếu tố như thời tiết, giờ cao điểm và số lượng tai nạn.
- Phân tích nguyên nhân tai nạn và các nhóm đối tượng liên quan.
- Dự đoán xu hướng tai nạn giao thông trong tương lai dựa trên các dữ liệu hiện tại.

**Traffic Accident Advisory ChatBot** sẽ giúp bạn tiết kiệm thời gian và công sức khi tìm kiếm thông tin và tạo báo cáo, đồng thời cung cấp một công cụ hữu ích để nắm bắt và phân tích tình hình tai nạn giao thông một cách dễ dàng và trực quan.""")
####################################################


with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1.container(border=True):
        client1 = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # from openai import OpenAI as oai

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

        # df = pd.read_csv('./data/data_dv.csv', encoding="utf-8")

        st.header("Questions and Answers")

        # OPENAI_API_KEY= os.getenv('OPENAI_API_KEY')

        llm = pOpenAI(api_token=os.getenv('OPENAI_API_KEY'))

        # query = st.text_area("🗣️ Chat with Dataframe")
        query = st.chat_input("Chat with Dataframe >.< ")
        # client = OpenAI(
        #     api_key=OPENAI_API_KEY,
        # )

        def generate_openai_response(client, prompt, model="gpt-4o-mini", max_tokens=1500):
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

        def process_user_query(client1, query, openai_answer):
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

        # **Câu trả lời mẫu từ OpenAI**: {openai_answer}

        Hãy trả lời một cách chi tiết, rõ ràng và chính xác bằng Tiếng Việt. Đảm bảo rằng câu trả lời của bạn không chỉ đầy đủ mà còn có tính linh hoạt, giúp người dùng không chỉ trả lời câu hỏi mà còn khám phá thêm thông tin có giá trị từ bộ dữ liệu.
        """
            )
            return generate_openai_response(client1, system_prompt)

        if query:
            query_engine = SmartDataframe(
                data,
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
            answer = process_user_query(client1, query, openai_answer)
            st.write(answer)

    ###############################################################################################

    with col2.container(border=True):
        client2 = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        st.header("Report Generator")
        
        modelfile = f"""Bạn là một chuyên gia phân tích dữ liệu và biểu đồ với chủ đề Tai nạn giao thông ở Việt Nam, bạn có thể sử dụng thông tin dataset ở đây {data}"""

        # User input
        img_file_buffer = st.file_uploader("Thêm các ảnh bạn muốn phân tích vào báo cáo", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        user_input = st.chat_input("Ask me >.< ")

        if user_input:
            st.write("Input")

            introduce_dataset_input = """Hãy viết một bản báo cáo giới thiệu sơ lược về tập dữ liệu tai nạn giao thông ở Việt Nam, mô tả các thuộc tính cũng như sử dụng các phép toán thống kê đơn giản cho tập dữ liệu"""

            result = client2.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": modelfile},
                                {"role": "user", "content": introduce_dataset_input}
                            ],
                            max_tokens=1500
                        )
            response_text = result.choices[0].message.content
            st.write(response_text)


            ##################################
            # Tạo file PDF
            pdf_buffer = io.BytesIO()

            pdf = SimpleDocTemplate(pdf_buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Tùy chỉnh các style
            title_style = ParagraphStyle(
                'TitleStyle', fontName='BeVietNamPro', fontSize=18, alignment=1, spaceAfter=12
            )
            body_style = ParagraphStyle(
                'BodyStyle', fontName='BeVietNamPro', fontSize=12, leading=14, spaceAfter=10
            )
            custom_style = ParagraphStyle(
                'CustomStyle', parent=body_style, alignment=0, spaceAfter=10
            )
            
            # Nội dung PDF
            content = []
            content.append(Paragraph('Báo Cáo Tai Nạn Giao Thông', title_style))
            content.append(Spacer(1, 0.5 * cm))
            
            # Lặp 3 lần để chèn văn bản và ảnh
            paragraphs = response_text.split('\n')
            for para in paragraphs:
                if para.strip():
                    content.append(Paragraph(para.strip(), custom_style))
                    content.append(Spacer(1, 0.2 * cm))
            
            #################################

            st.success("Introduction added to the PDF!")


        # Hiển thị hình ảnh nếu người dùng tải lên
            for image in img_file_buffer:
                if image:
                    image = PILImage.open(image)
                    # st.image(image, caption="Ảnh đã tải lên", width=500)
                    # image = image.resize((512, 200))
                    # image = image.convert("L")

                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                    # Xử lý hình ảnh với API Ollama (LLaVA)
                    try:
                        # user_input = """Từ tập dữ liệu "$(data_dv.csv)" Phân tích biểu đồ này, mô tả title của biểu đồ, là dòng chữ phía trên bên trái của biểu đồ, phía sau kí tự '📊', mô tả các trục của biểu đồ, mô tả các điểm quan trọng của biểu đồ, từ biểu đồ đó rút ra mô tả xu hướng của biểu đồ."""
                        chart_analysis_input = """Bạn là một chuyên gia phân tích dữ liệu và trực quan hóa, có kỹ năng đọc hiểu biểu đồ chuyên sâu. Dựa trên biểu đồ cũng như tập dữ liệu được cung cấp, hãy viết một báo cáo phân tích chi tiết, rõ ràng và mạch lạc. Báo cáo cần bao gồm các phần sau:
                                                Tổng quan: Mô tả loại biểu đồ, mục đích và ý nghĩa tổng quát. Xác định chủ đề chính và phạm vi dữ liệu.
                                                Xu hướng chính: Phân tích các xu hướng nổi bật, sự thay đổi đáng chú ý và mối quan hệ giữa các yếu tố trong biểu đồ.
                                                Chi tiết đặc trưng: Làm rõ các điểm dữ liệu quan trọng, giá trị cao nhất, thấp nhất, và các ngoại lệ.
                                                Phát hiện ẩn: Nhận diện các xu hướng hoặc mẫu dữ liệu tinh tế mà người xem thông thường có thể bỏ qua.
                                                Kết luận: Tóm tắt lại các phát hiện quan trọng, đưa ra nhận định tổng thể và ý nghĩa từ biểu đồ.
                                                Sử dụng ngôn ngữ chuyên nghiệp, chính xác, có dẫn chứng số liệu cụ thể từ biểu đồ. Hãy đảm bảo phân tích toàn diện, không bỏ sót thông tin quan trọng nào và rút ra được những kết luận sâu sắc."""
                        # # Duyệt qua tất cả các cột và dữ liệu
                        # for col in data.columns:
                        #     user_input += f"{col}: {data[col].tolist()}\n"
                        result = client2.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": modelfile},
                                {"role": "user", "content":[
                                    {
                                        "type": "text",
                                        "text": chart_analysis_input
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64, {img_base64}"
                                        }
                                    }
                                ]}
                            ],
                            max_tokens=1500
                        )
                        
                        # Save image temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                            image.save(tmp_file, format="PNG")
                            tmp_file_path = tmp_file.name

                            # pil_image = PILImage.new('RGB', (200, 100), color='blue')  # Example image
                            # pil_image.save(tmp_file_path, format="PNG")     

                            f = open(tmp_file_path, 'rb')

                            #################################
                            response_text = result.choices[0].message.content
                            st.write(response_text)

                            content.append(Image(f, width=10*cm, height=6*cm))
                            content.append(Spacer(1, 0.5 * cm))

                            paragraphs = response_text.split('\n')
                            for para in paragraphs:
                                if para.strip():
                                    content.append(Paragraph(para.strip(), custom_style))
                                    content.append(Spacer(1, 0.2 * cm))
                        ##################################

                        # c.drawText(text_object)

                            os.remove(tmp_file_path)
                            st.success("Analysis added to the PDF!")
                    except Exception as e:
                        st.error(f"Lỗi xử lý hình ảnh: {e}")

            pdf.build(content)
            pdf_buffer.seek(0)

            st.write("Done")

            # Provide Download Button
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="output.pdf",
                mime="application/pdf"
            )
