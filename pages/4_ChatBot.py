import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import Image
import base64
import requests
import io
from io import BytesIO
import tempfile
import json
import textwrap
import zipfile
from translate import Translator
from pandasai import SmartDataframe
from pandasai.responses.streamlit_response import StreamlitResponse
from pandasai.engine import set_pd_engine
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

set_pd_engine("pandas")

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
        modelfile = f"""
            FROM llava
            SYSTEM f"Bạn là một chuyên gia phân tích dữ liệu và biểu đồ với chủ đề Tai nạn giao thông ở Việt Nam, bạn có thể sử dụng thông tin dataset ở đây {data}"
            PARAMETER temperature 0.7
            """

        # User input
        img_file_buffer = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        user_input = st.chat_input("Ask me ><:")

        if user_input:
            st.write("Input")
            # Create PDF in memory
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=letter)

            # Add the paragraph
            c.setFont("BeVietNamPro", 12)

            # Tọa độ bắt đầu
            x_position = 100  # Vị trí x cố định
            y_position = 750  # Vị trí y bắt đầu từ trên xuống
            max_width = 450  # Chiều rộng tối đa của một dòng

            # Tạo một đối tượng TextObject để chèn toàn bộ đoạn văn mà không cần dùng strip
            text_object = c.beginText(x_position, y_position)
            text_object.setFont("BeVietNamPro", 12)
            text_object.setTextOrigin(x_position, y_position)

        # Hiển thị hình ảnh nếu người dùng tải lên
            for image in img_file_buffer:
                if image:
                    image = Image.open(image)
                    # st.image(image, caption="Ảnh đã tải lên", width=500)
                    image = image.resize((512, 200))
                    # image = image.convert("L")

                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                    # Xử lý hình ảnh với API Ollama (LLaVA)
                    try:
                        # user_input = """This is one of the charts in the traffic accident data in Vietnam for the years 2020-2021, analyze this chart."""
                        user_input = 'Phân tích biểu đồ này, đây là một trong những biểu đồ về bộ dữ liệu tai nạn giao thông ở Việt Nam 2020-2021. Chủ đề là tai nạn giao thông'
                        # # Duyệt qua tất cả các cột và dữ liệu
                        # for col in data.columns:
                        #     user_input += f"{col}: {data[col].tolist()}\n"

                        #####################################
                        # Gửi yêu cầu đến API Ollama
                        response = requests.post(
                            "https://e70b-14-161-7-63.ngrok-free.app/api/generate",
                            json={"modelfile": modelfile, "model": "llava", "prompt": user_input, "images":[img_base64], "stream": False}
                        )
                        translator_ollava = Translator(to_lang="vi", from_lang="en")
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.write("**Trả lời:**")

                            # Save image temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                                image.save(tmp_file, format="PNG")
                                tmp_file_path = tmp_file.name

                            c.drawImage(tmp_file_path, x_position, y_position - 200, width=450 ,height=200)
                            # st.write(translator_ollava.translate(result['response']))

                            # Giảm y_position sau khi thêm ảnh
                            y_position -= 220

                            # response_text = translator_ollava.translate(result['response'])
                            response_text = result['response']
                            st.write(response_text)
                            wrapped_text = textwrap.wrap(response_text, width=80)

                            for line in wrapped_text:
                                if y_position < 100:  # Nếu hết trang
                                    c.showPage()
                                    text_object = c.beginText(x_position, 750)
                                    text_object.setFont("BeVietNamPro", 12)
                                    y_position = 750

                                text_object.setTextOrigin(x_position, y_position)
                                text_object.textLine(line)
                                y_position -= 15  # Giảm y_position cho mỗi dòng

                            c.drawText(text_object)

                            os.remove(tmp_file_path)
                            st.success("Analysis added to the PDF!")
                        elif response.status_code == 403:
                            st.error("🚫 Forbidden: Check if the API endpoint requires authentication or IP whitelisting.")
                        elif response.status_code == 404:
                            st.error("🔍 API endpoint not found. Verify the URL.")
                        else:
                            st.error(f"⚠️ Unexpected Error: {response.status_code}, {response.text}")
                        ####################################

                        # res = ollama.generate(model="data_science_assistant", prompt=user_input, images=[img_base64])

                        # st.write("Chatbot")
                        # st.write(res["response"])
                    except Exception as e:
                        st.error(f"Lỗi xử lý hình ảnh: {e}")

            c.save()
            pdf_buffer.seek(0)

            st.write("Done")

            # Provide Download Button
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="output.pdf",
                mime="application/pdf"
            )

# export_folder = os.path.join(os.getcwd(), "exports")
# sdf = SmartDataframe(data, config={"save_charts": True, "save_charts_path": export_folder, "verbose": True, "response_parser": StreamlitResponse, "custom_whitelisted_dependencies": ["to_numeric"]})
# with st.container():
#     # File uploader widget to upload a CSV file
#     config_file = st.file_uploader("Upload your config file", type=["json"])

#     images = []

#     if 'Send_button' not in st.session_state:
#         st.session_state.send_button = False
    
#     if st.button("Send"):
#         st.session_state.send_button = True

#     if st.session_state.send_button and config_file is not None:
#         # Open and read the JSON file
#         data = json.load(config_file)

#         report_name = data["Report Name"]
#         reporter_name = data["Reporter Name"]
#         graph_lists_name = data['Graphs']
#         colors = data["Colors"]

#         # Clear export folder before generating images
#         for file in os.listdir(export_folder):
#             file_path = os.path.join(export_folder, file)
#             if os.path.isfile(file_path) and file.lower().endswith(('.png', '.jpg', '.jpeg')):
#                 os.remove(file_path)

#         for index, graph in enumerate(graph_lists_name):
#             translated_graph_name = translator.translate(graph)

#             # translated_input = "Draw " + translated_graph_name + "with matplotlib and seaborn"
#             translated_input = "Plot " + translated_graph_name

#             response = sdf.chat(translated_input)

#             # Check if the response contains an image path
#             if isinstance(response, str) and os.path.isfile(response):  # If it's an image path
#                 image = Image.open(response)
#                 st.image(image)
#             else:
#                 # If the response isn't an image path, handle the output as text or other content
#                 st.write(response)

#             image_files = [f for f in os.listdir(export_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
#             st.write(image_files)

#             if image_files:
#                 image_path = os.path.join(export_folder, image_files[0])
#                 st.Image(image_path)
#                 images.append(Image.open(image_path))

        
#         for image in images:
#             st.Image(image)

#         st.session_state.send_button = False
