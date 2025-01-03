import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import Image
import base64
import requests
import io
import json
import zipfile
from translate import Translator
from pandasai import SmartDataframe
from pandasai.responses.streamlit_response import StreamlitResponse
from pandasai.engine import set_pd_engine

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
            SYSTEM "Act as a professional Data Scientist capable of interpreting complex charts, graphs, and diagrams. For the given visualization:
                    Describe the visualized data: Explain the axes, variables, and any key markers.
                    Analyze trends and patterns: Identify relationships, peaks, dips, or significant changes.
                    Highlight anomalies: Point out unusual data points or outliers.
                    Derive conclusions: Summarize the main insights in a clear, actionable manner.
                    Provide recommendations: Suggest potential actions or strategic decisions based on the findings."
            PARAMETER temperature 0.7
            """

        # User input
        img_file_buffer = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        user_input = st.text_input("Ask me:")

        if user_input:
        # Hiển thị hình ảnh nếu người dùng tải lên
            if img_file_buffer:
                image = Image.open(img_file_buffer)
                st.image(image, caption="Ảnh đã tải lên", width=500)

                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                # Xử lý hình ảnh với API Ollama (LLaVA)
                try:

                    #####################################
                    # Gửi yêu cầu đến API Ollama
                    response = requests.post(
                        "https://229e-115-78-15-156.ngrok-free.app/api/generate",
                        json={"modelfile": modelfile, "model": "llava", "prompt": user_input, "images":[img_base64], "stream": False}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.write("**Trả lời:**")
                        st.write(result['response'])
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

with st.container():
    # File uploader widget to upload a CSV file
    config_file = st.file_uploader("Upload your config file", type=["json"])

    if config_file is not None:
        # Open and read the JSON file
        data = json.load(config_file)

        report_name = data["Report Name"]
        reporter_name = data["Reporter Name"]
        graph_lists_name = data['Graphs']
        colors = data["Colors"]

        for index, graph in enumerate(graph_lists_name):
            translated_graph_name = translator.translate(graph)

            translated_input = "Draw " + translated_graph_name + "with plotly"

            response = sdf.chat(translated_input)

    if st.button("Download images"):
        # List all image files in the folder
        image_files = [f for f in os.listdir(export_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for image in image_files:
                image_path = os.path.join(export_folder, image)
                zip_file.write(image_path, arcname=image)
        
        # Reset buffer position to the beginning
        zip_buffer.seek(0)

        # Provide download button for the zip file
        st.download_button(
            label="Download All Images as ZIP",
            data=zip_buffer,
            file_name="images.zip",
            mime="application/zip"
        )