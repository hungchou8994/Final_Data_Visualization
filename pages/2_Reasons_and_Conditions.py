import streamlit as st
import pandas as pd
import plotly.express as px
from overview_parameters import filter_string, create_widgets, filter_df
import ast


# Load data
file_path = 'data_dv.csv'  # Replace with your uploaded file path
data = pd.read_csv(file_path)

# Page configuration
st.set_page_config(page_title="Reasons and Conditions", layout="wide")


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
st.markdown("<h3 style='text-align: center;'>Nguyên nhân và điều kiện khách quan</h3>", unsafe_allow_html=True)

###########################################

st.sidebar.title("Control Panel")

# Nhập gi
with st.sidebar.container():
    col1, col2 = st.sidebar.columns(2)
    from_hour_input = col1.selectbox("Giờ bắt đầu (24h)", options=range(0, 24))
    to_hour_input = col2.selectbox("Giờ kết thúc (24h)", options=range(0, 24), index=23)

collision_input = st.sidebar.multiselect("Hình thức va chạm", options=data['Hình thức va chạm'].unique())
accident_type_input = st.sidebar.multiselect("Phân loại tai nạn", options=data['Phân loại tai nạn'].unique())

# Filtering function
def filter_df(df, from_hour_input, to_hour_input, collision_input, accident_type_input):
    df['Thời gian xảy ra tai nạn'] = pd.to_datetime(df['Thời gian xảy ra tai nạn'], errors='coerce')

    df['Hour'] = df['Thời gian xảy ra tai nạn'].dt.hour

    df_filtered = df[(df['Hour'] >= from_hour_input) & (df['Hour'] <= to_hour_input)]
    
    if collision_input:
        df_filtered = df_filtered[df_filtered['Hình thức va chạm'].isin(collision_input)]

    if accident_type_input:
        df_filtered = df_filtered[df_filtered['Phân loại tai nạn'].isin(accident_type_input)]
    
    return df_filtered

# Apply the filtering based on user input from the sidebar
filtered_df = filter_df(data, from_hour_input, to_hour_input, collision_input, accident_type_input)

#############################################


with st.container():
    col1, col2, col3 = st.columns(3)

    number_of_unique_district = len(filtered_df['Quận/Huyện'].unique())
    number_of_accident = filtered_df.shape[0]
    number_of_dead = filtered_df['Số người chết'].sum()

    col1.markdown(
        f"""
        <div style="
            background-color: #FF6363;
            border-radius: 10px;
            text-align: center;">
            <span>Số Quận/Huyện</span>
            <p style="font-size: 25px; font-weight: bold;">{number_of_unique_district}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col2.markdown(
        f"""
        <div style="
            background-color: #FFB001;
            border-radius: 10px;
            text-align: center;">
            <span>Số Người Chết</span>
            <p style="font-size: 25px; font-weight: bold;">{number_of_dead}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col3.markdown(
        f"""
        <div style="
            background-color: #FFB001;
            border-radius: 10px;
            text-align: center;">
            <span>Số Vụ Tai Nạn</span>
            <p style="font-size: 25px; font-weight: bold;">{number_of_accident}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    # col1.metric("Số Quận/Huyện", number_of_unique_district, border=True)
    # col2.metric("Số người chết", number_of_dead, border=True)
    # col3.metric("Số người vụ tai nạn", number_of_accident, border=True)

chart_col1, chart_col2 = st.columns(2)
with chart_col1.container():
    with st.container(border=True):
        # Prepare filtered_df for the pie chart
        weather_condition_counts = filtered_df['Tình trạng thời tiết'].value_counts().reset_index()
        weather_condition_counts.columns = ['Tình trạng thời tiết', 'Số vụ']

        # Plot the pie chart using Plotly
        fig = px.pie(
            weather_condition_counts, 
            values='Số vụ', 
            names='Tình trạng thời tiết', 
            title='📊 Tỷ lệ tai nạn dựa trên tình trạng thời tiết',
            # title=' ',
            color_discrete_sequence=px.colors.sequential.Viridis  # Changed to Viridis for better contrast
        )

        # Customize labels and layout
        fig.update_traces(
            textinfo='percent+label', 
            pull=[0.1 if value < 0.05 * weather_condition_counts['Số vụ'].sum() else 0 for value in weather_condition_counts['Số vụ']],
            textfont_size=12  # Adjust font size for better readability
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            title_x=0.5,  # Center the title
            legend_title="Tình trạng thời tiết",
            # width=900,  # Adjusted width for better visualization
            height=300,  # Adjusted height for better visualization
            font=dict(size=10),  # Set default font size
            title=dict(
                x=0,  # Di chuyển tiêu đề sang bên trái
                xanchor='left',  # Căn chỉnh tiêu đề với phía bên trái
                yanchor='top'  # Căn chỉnh theo chiều dọc ở phía trên
            ),
            # autosize=True
        )


        # Hiển thị biểu đồ trên Streamlit
        # st.markdown("**📊 Tỷ lệ tai nạn dựa trên tình trạng thời tiết**")
        st.plotly_chart(fig, use_container_width=True)
    ############################################################
    with st.container(border=True):
        # Extract individual causes from the 'Nguyên nhân và Lỗi vi phạm' column
        filtered_df['Nguyên nhân'] = filtered_df['Nguyên nhân và Lỗi vi phạm'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else []
        )

        # Explode the list of causes into separate rows
        exploded_causes = filtered_df.explode('Nguyên nhân')

        # Filter for accidents with at least one death
        fatal_accidents = exploded_causes[exploded_causes['Số người chết'] >= 1]

        # Count the top 10 individual causes
        cause_counts = fatal_accidents['Nguyên nhân'].value_counts().head(10).reset_index()
        cause_counts.columns = ['Nguyên nhân', 'Số vụ']

        # Abbreviate the top causes as NV1, NV2, ..., and create a mapping for the legend
        cause_counts['Abbreviation'] = ['NV' + str(i + 1) for i in range(len(cause_counts))]

        # Plot the data with Plotly
        fig = px.bar(
            cause_counts, 
            x='Abbreviation', 
            y='Số vụ', 
            text='Số vụ',
            color='Số vụ', 
            title='📊 Top 10 Nguyên nhân gây tai nạn có người chết',
            # title=' ',
            color_continuous_scale='Viridis',
            labels={'Abbreviation': 'Nguyên nhân (Rút gọn)', 'Số vụ': 'Số vụ'}
        )

        # Add full cause descriptions as hover data
        fig.update_traces(
            hovertemplate="Nguyên nhân: %{customdata[0]}<br>Số vụ: %{y}",
            customdata=cause_counts[['Nguyên nhân']].values
        )

        # Add annotations for the legend
        annotations_text = "<br>".join([f"{row['Abbreviation']}: {row['Nguyên nhân']}" for _, row in cause_counts.iterrows()])
        fig.add_annotation(
            text=annotations_text,
            xref="paper", yref="paper",
            x=1, y=1,  # Position the legend to the right of the chart
            showarrow=False,
            align="left",
            font=dict(size=9),
            bgcolor="rgba(255, 255, 255, 0.8)",  # Add background color
            bordercolor="black",
            borderwidth=1.5
        )

        fig.update_traces(textposition='outside')
        # Customize layout
        fig.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            title_x=0.5,  # Center the title
            # xaxis_title='Nguyên nhân (Rút gọn)',
            # yaxis_title='Số vụ',
            font=dict(size=12),  # Set default font size
            # legend_title="Nguyên nhân",
            # width=1000,  # Adjust width to make room for annotations
            # height=600  # Adjust height
            height=300,
            xaxis=dict(
                title='Nguyên nhân (Rút gọn)',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục X
                tickfont=dict(size=12, color='black')
            ),
            yaxis=dict(
                title='Số vụ',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục Y
                tickfont=dict(size=12, color='black')
            ),
            title=dict(
                x=0,  # Di chuyển tiêu đề sang bên trái
                xanchor='left',  # Căn chỉnh tiêu đề với phía bên trái
                yanchor='top'  # Căn chỉnh theo chiều dọc ở phía trên
            ),
            legend=dict(
                title=dict(text='Nguyên nhân', font=dict(size=14, color='black')),  # Tiêu đề legend in đậm
                font=dict(size=12, color='black')  # Văn bản trong legend in đậm
            ),
        )

        # Hiển thị biểu đồ trên Streamlit
        # st.markdown("**📊 Top 10 Nguyên nhân gây tai nạn có người chết**")
        st.plotly_chart(fig, use_container_width=True)

##########################################################
with chart_col2.container():
    with st.container(border=True):
        # Đếm số vụ tai nạn theo từng loại đường và lấy top 10
        road_type_accidents = filtered_df['Loại đường'].value_counts().head(10).reset_index()
        road_type_accidents.columns = ['Loại đường', 'Số vụ']

        # Sắp xếp dữ liệu theo số vụ tai nạn từ cao đến thấp
        road_type_accidents = road_type_accidents.sort_values(by='Số vụ', ascending=True)

        # Vẽ biểu đồ Horizontal Bar Chart
        fig_road_type = px.bar(
            road_type_accidents,
            x='Số vụ',
            y='Loại đường',
            orientation='h',  # Horizontal bar chart
            title='📊 Top 10 loại đường có số vụ tai nạn cao nhất',
            # title=' ',
            labels={'Số vụ': 'Số vụ tai nạn', 'Loại đường': 'Loại đường'},
            color='Số vụ',
            color_continuous_scale='Plasma'  # Thang màu
        )

        # Tùy chỉnh hiển thị biểu đồ
        fig_road_type.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            title_x=0.5,  # Căn giữa tiêu đề
            # xaxis_title='Số vụ tai nạn',
            # yaxis_title='Loại đường',
            # width=900,  # Độ rộng biểu đồ
            height=300,  # Chiều cao biểu đồ
            font=dict(size=12),  # Kích thước font chữ
            xaxis=dict(
                title='Số vụ tai nạn',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục X
                tickfont=dict(size=12, color='black')
            ),
            yaxis=dict(
                title='Loại đường',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục Y
                tickfont=dict(size=12, color='black')
            ),
            title=dict(
                x=0,  # Di chuyển tiêu đề sang bên trái
                xanchor='left',  # Căn chỉnh tiêu đề với phía bên trái
                yanchor='top'  # Căn chỉnh theo chiều dọc ở phía trên
            ),
        )

        # Hiển thị biểu đồ trên Streamlit
        # st.markdown("**📊 Top 10 loại đường có số vụ tai nạn cao nhất**")
        st.plotly_chart(fig_road_type, use_container_width=True)
    ######################################################
    with st.container(border=True):

        # Chuẩn bị dữ liệu
        # Loại bỏ các hàng có giá trị thiếu trong 'Nhóm PT1' và 'Quận/Huyện'
        treemap_data = filtered_df.dropna(subset=['Nhóm PT1', 'Quận/Huyện'])

        # Đổi tên cột 'Nhóm PT1' thành 'Loại phương tiện' để dễ đọc hơn
        treemap_data = treemap_data.rename(columns={'Nhóm PT1': 'Loại phương tiện'})

        # Đếm số vụ tai nạn theo 'Loại phương tiện' và 'Quận/Huyện'
        treemap_summary = treemap_data.groupby(['Quận/Huyện', 'Loại phương tiện']).size().reset_index(name='Số vụ')

        # Vẽ biểu đồ Treemap
        fig = px.treemap(
            treemap_summary,
            path=['Quận/Huyện', 'Loại phương tiện'],  # Cấp độ: Quận/Huyện -> Loại phương tiện
            values='Số vụ',
            title='📊 Phân tích tai nạn theo loại phương tiện và quận/huyện',
            # title=' ',
            color='Số vụ',
            color_continuous_scale='Viridis',  # Thang màu
            labels={'Số vụ': 'Số vụ tai nạn'}
        )

        # Tùy chỉnh hiển thị
        fig.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            title_x=0.5,  # Căn giữa tiêu đề
            height=300,  # Chiều cao biểu đồ
            # width=900,  # Độ rộng biểu đồ
            font=dict(size=12),  # Kích thước font chữ
            title=dict(
                x=0,  # Di chuyển tiêu đề sang bên trái
                xanchor='left',  # Căn chỉnh tiêu đề với phía bên trái
                yanchor='top'  # Căn chỉnh theo chiều dọc ở phía trên
            ),
        )

        # Hiển thị biểu đồ trên Streamlit
        # st.markdown("**📊 Phân tích tai nạn theo loại phương tiện và quận/huyện**")
        st.plotly_chart(fig, use_container_width=True)