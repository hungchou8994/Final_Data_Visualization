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
from pandasai.engine import set_pd_engine
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from openai import OpenAI

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import cm

set_pd_engine("pandas")

# OpenAI API Key

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Đăng ký font Be VietNam Pro
pdfmetrics.registerFont(TTFont('BeVietNamPro', r'Be_Vietnam_Pro/BeVietnamPro-Light.ttf'))

export_folder = os.path.join(os.getcwd(), "exports")

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
st.markdown("<h3 style='text-align: center;'>ChatBot</h3>", unsafe_allow_html=True)

####################################################
st.markdown("![Alt Text](https://media.giphy.com/media/G56u3vJFPIevIfVnEK/giphy.gif)")
####################################################


translator = Translator(to_lang="en", from_lang="vi")

with st.container():
    col1, col2 = st.columns(2)
    with col1.container(border=True):
        os.environ["PANDASAI_API_KEY"] = "$2a$10$GEsfXrwFuOWndHnBgXcSkecd3RlY3ffzDyDk19gXMRue4Dr.oqz4m"

        sdf = SmartDataframe(data, config={"save_charts": True, "save_charts_path": export_folder, "verbose": True, "response_parser": StreamlitResponse, "custom_whitelisted_dependencies": ["to_numeric"]})

        user_input = st.chat_input("Ask me:")

        if user_input:
            with st.container(border=True):
                with st.chat_message("assistant"):

                    translated_text = translator.translate(user_input)

                    response = sdf.chat(translated_text)

                    if isinstance(response, pd.DataFrame):
                        # Display the DataFrame directly
                        st.write(f"Chatbot:")
                        st.write(response)
                    else:
                        # If the response is a string (e.g., some text or CSV), handle it accordingly
                        # For example, if it's a CSV-like string:
                        st.write(f"Chatbot: {response}")

    with col2.container(border=True):
        
        modelfile = f"""Bạn là một chuyên gia phân tích dữ liệu và biểu đồ với chủ đề Tai nạn giao thông ở Việt Nam, bạn có thể sử dụng thông tin dataset ở đây {data}"""

        # User input
        img_file_buffer = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        user_input = st.chat_input("Ask me ><:")

        if user_input:
            st.write("Input")

            introduce_dataset_input = """Hãy viết một bản báo cáo giới thiệu sơ lược về tập dữ liệu tai nạn giao thông ở Việt Nam, mô tả các thuộc tính cũng như sử dụng các phép toán thống kê đơn giản cho tập dữ liệu"""

            result = client.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": modelfile},
                                {"role": "user", "content": introduce_dataset_input}
                            ],
                            max_tokens=500
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
                        result = client.chat.completions.create(
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
                            max_tokens=500
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
