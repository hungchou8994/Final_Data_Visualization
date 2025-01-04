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

set_pd_engine("pandas")

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
            SYSTEM "Act as a professional Data Scientist specializing in interpreting complex charts, graphs, and diagrams. For the given visualization:
                    - Describe the visualized data: Identify the chart type (bar, line, scatter, etc.), explain the axes, variables, and any key markers, such as titles or legends.
                    - Analyze trends and patterns: Observe the overall shape of the data. Identify relationships, correlations, peaks, troughs, and significant changes over time or between variables.
                    - Highlight anomalies: Point out unusual data points or outliers. Suggest reasons for any unexpected results or data behaviors.
                    - Derive conclusions: Summarize key insights from the chart and suggest actionable conclusions based on the visualized trends and patterns.
                    - Provide recommendations: Suggest potential actions, strategic decisions, or areas for further analysis based on the findings. Highlight areas that require attention or optimization.
                    - For specific types of charts (e.g., line graphs, scatter plots), analyze the distribution of data, clustering, trends over time, and the significance of extreme points."
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
            c.setFont("Helvetica", 12)

            # Tọa độ bắt đầu
            x_position = 100  # Vị trí x cố định
            y_position = 750  # Vị trí y bắt đầu từ trên xuống
            max_width = 450  # Chiều rộng tối đa của một dòng

            # Tạo một đối tượng TextObject để chèn toàn bộ đoạn văn mà không cần dùng strip
            text_object = c.beginText(x_position, y_position)
            text_object.setFont("Helvetica", 12)
            text_object.setTextOrigin(x_position, y_position)   

            # Build the prompt
            user_input = """As a professional Data Scientist, your task is write a paragraph (about 300-400 characters) to analyze given chart images. 
            Begin by identifying the chart type (e.g., bar chart, line graph, scatter plot, pie chart, histogram) and briefly explain their purpose and what they convey. 
            Describe the axes, including the variables on the x-axis and y-axis, and note any important markers such as trends, categories, or data points. 
            Analyze the overall data patterns, highlighting trends (e.g., increasing, decreasing), correlations between variables, and any visible clusters or groupings. 
            Summarize the main insights drawn from the charts, considering how the data aligns with or challenges expectations. 
            Based on your analysis, suggest actionable insights, potential decisions, or further areas for investigation.\n"""

            # Add data columns (if available)
            try:
                for col in data.columns:
                    user_input += f"{col}: {data[col].tolist()}\n"
            except NameError:
                st.warning("⚠️ Data is not defined. Skipping data columns in the prompt.")
            
            # List to store all encoded images
            img_base64_list = []
            user_input_list = []

            # Loop to process images and convert them to Base64
            for image in img_file_buffer:
                if image:
                    image = Image.open(image)

                    # Convert image to Base64
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    img_base64_list.append(img_base64)

                    user_input_list.append(user_input)

            # Send a single API request
            try:
                response = requests.post(
                    "https://ea4e-115-78-15-156.ngrok-free.app/api/generate",
                    json={
                        "modelfile": modelfile,
                        "model": "llava",
                        "prompt": user_input_list,
                        "images": img_base64_list,
                        "stream": False
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    st.write("**Trả lời:**")

                    response_text = result['response']
                    wrapped_text = textwrap.wrap(response_text, width=70)

                    text_object = c.beginText(x_position, y_position)
                    text_object.setFont("Helvetica", 12)

                    for line in wrapped_text:
                        if y_position < 100:  # Check for page overflow
                            c.showPage()
                            text_object = c.beginText(x_position, 750)
                            text_object.setFont("Helvetica", 12)
                            y_position = 750

                        text_object.setTextOrigin(x_position, y_position)
                        text_object.textLine(line)
                        y_position -= 15

                    c.drawText(text_object)

                    st.write(response_text)
                    st.success("Analysis added to the PDF!")

                elif response.status_code == 403:
                    st.error("🚫 Forbidden: Check if the API endpoint requires authentication or IP whitelisting.")
                elif response.status_code == 404:
                    st.error("🔍 API endpoint not found. Verify the URL.")
                else:
                    st.error(f"⚠️ Unexpected Error: {response.status_code}, {response.text}")

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
