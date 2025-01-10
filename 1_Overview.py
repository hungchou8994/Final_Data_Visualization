import streamlit as st
import pandas as pd
import plotly.express as px
from overview_parameters import filter_string, create_widgets, filter_df

# Load data
file_path = 'data_dv.csv'  # Replace with your uploaded file path
data = pd.read_csv(file_path)

# Page configuration
st.set_page_config(page_title="Overview", layout="wide")

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
st.markdown("<h3 style='text-align: center;'>Tổng quan về tai nạn giao thông</h3>", unsafe_allow_html=True)

###########################################
st.sidebar.title("Bộ lọc")

# Nhập ngày
with st.sidebar.container():
    col1, col2 = st.sidebar.columns(2)
    from_date_input = col1.date_input("Ngày bắt đầu", value="2020-01-01", min_value="2020-01-01", max_value="2021-12-31")
    to_date_input = col2.date_input("Ngày kết thúc", value="2021-12-31", min_value="2020-01-01", max_value="2021-12-31")

district_input = st.sidebar.multiselect("Quận/Huyện", options=data['Quận/Huyện'].unique())
road_type_input = st.sidebar.multiselect("Loại đường", options=data['Loại đường'].unique())
weather_type_input = st.sidebar.multiselect("Tình trạng thời tiết", options=data['Tình trạng thời tiết'].unique())

# Convert 'Ngày xảy ra tai nạn' to datetime if it's not already
data['Ngày xảy ra tai nạn'] = pd.to_datetime(data['Ngày xảy ra tai nạn'], errors='coerce')

# Convert date inputs to datetime64[ns]
from_date_input = pd.to_datetime(from_date_input)
to_date_input = pd.to_datetime(to_date_input)

# Filtering function
def filter_df(df, from_date, to_date, district, road_type, weather_type):
    # Ensure 'Ngày xảy ra tai nạn' is in datetime format
    df['Ngày xảy ra tai nạn'] = pd.to_datetime(df['Ngày xảy ra tai nạn'], errors='coerce')
    
    # Filter by date range
    df_filtered = df[(df['Ngày xảy ra tai nạn'] >= from_date) & (df['Ngày xảy ra tai nạn'] <= to_date)]
    
    # Filter by selected districts
    if district:
        df_filtered = df_filtered[df_filtered['Quận/Huyện'].isin(district)]
    
    # Filter by selected road types
    if road_type:
        df_filtered = df_filtered[df_filtered['Loại đường'].isin(road_type)]
    
    # Filter by selected weather conditions
    if weather_type:
        df_filtered = df_filtered[df_filtered['Tình trạng thời tiết'].isin(weather_type)]
    
    return df_filtered

# Apply the filtering based on user input from the sidebar
filtered_df = filter_df(data, from_date_input, to_date_input, district_input, road_type_input, weather_type_input)

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

with st.container(border=False):
    chart_col1, chart_col2 = st.columns(2)
    ######################################################
    with chart_col1.container(border=True):
        # Chuyển đổi ngày với định dạng phù hợp
        filtered_df['Ngày xảy ra tai nạn'] = pd.to_datetime(filtered_df['Ngày xảy ra tai nạn'], format='%d/%m/%Y', errors='coerce')

        # Loại bỏ các giá trị không hợp lệ (NaT)
        filtered_df = filtered_df.dropna(subset=['Ngày xảy ra tai nạn'])

        # Trích xuất tháng từ cột 'Ngày xảy ra tai nạn'
        filtered_df['Tháng'] = filtered_df['Ngày xảy ra tai nạn'].dt.month

        # Đếm số vụ tai nạn theo từng tháng
        monthly_accidents = filtered_df['Tháng'].value_counts().sort_index().reset_index()
        monthly_accidents.columns = ['Tháng', 'Số vụ']

        # Vẽ biểu đồ miền
        fig = px.area(
            monthly_accidents,
            x='Tháng',
            y='Số vụ',
            title='📊 Xu hướng số vụ tai nạn theo từng tháng',
            # title=' ',
            labels={'Tháng': 'Tháng trong năm', 'Số vụ': 'Số vụ tai nạn'},
            # color_discrete_sequence=['#636EFA']  # Màu biểu đồ
            color_discrete_sequence=px.colors.sequential.Cividis
        )

        # Tùy chỉnh hiển thị biểu đồ
        fig.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            title_x=0.5,
            title_y=0.9,
            title_pad=dict(t=5),
            # xaxis=dict(tickmode='linear', dtick=1, title_font=dict(size=14, color='black')),
            # yaxis=dict(title_font=dict(size=14, color='black')),
            # xaxis_title='Tháng trong năm',
            # yaxis_title='Số vụ tai nạn',
            # font=dict(size=12),
            # # width=900,
            # height=300
            xaxis=dict(
                tickmode='linear',
                dtick=1,
                title='Tháng trong năm',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục X
                tickfont=dict(size=12, color='black')
            ),
            yaxis=dict(
                title='Số vụ tai nạn',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục Y
                tickfont=dict(size=12, color='black')
            ),
            title=dict(
                x=0,  # Di chuyển tiêu đề sang bên trái
                xanchor='left',  # Căn chỉnh tiêu đề với phía bên trái
                yanchor='top'  # Căn chỉnh theo chiều dọc ở phía trên
            ),
            font=dict(size=12),
            height=300
        )

        # Hiển thị trên Streamlit
        # st.markdown("**📊 Xu hướng số vụ tai nạn theo từng tháng**")
        st.plotly_chart(fig, use_container_width=True)
    ######################################################
    with chart_col2.container(border=True):
        # Chuyển đổi ngày với định dạng phù hợp
        filtered_df['Ngày xảy ra tai nạn'] = pd.to_datetime(filtered_df['Ngày xảy ra tai nạn'], format='%d/%m/%Y', errors='coerce')

        # Loại bỏ các giá trị không hợp lệ (NaT)
        filtered_df = filtered_df.dropna(subset=['Ngày xảy ra tai nạn'])

        # Trích xuất ngày từ cột 'Ngày xảy ra tai nạn'
        filtered_df['Ngày'] = filtered_df['Ngày xảy ra tai nạn'].dt.day

        # Đếm số vụ tai nạn theo từng ngày trong tháng
        daily_accidents = filtered_df['Ngày'].value_counts().sort_index().reset_index()
        daily_accidents.columns = ['Ngày', 'Số vụ']

        # Vẽ biểu đồ xu hướng số vụ tai nạn theo ngày trong tháng
        fig_daily = px.line(
            daily_accidents,
            x='Ngày',
            y='Số vụ',
            title='📊 Xu hướng số vụ tai nạn theo ngày trong tháng',
            # title=' ',
            labels={'Ngày': 'Ngày', 'Số vụ': 'Số vụ tai nạn'},
            markers=True
        )

        # Tùy chỉnh hiển thị biểu đồ
        fig_daily.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            title_x=0.5,  # Căn giữa tiêu đề
            title_y=0.9,  # Đưa tiêu đề lên gần biểu đồ hơn
            # xaxis=dict(tickmode='linear', dtick=1),  # Hiển thị đầy đủ các ngày
            # xaxis_title='Ngày',
            # yaxis_title='Số vụ tai nạn',
            # # width=900,  # Độ rộng biểu đồ
            # height=300,  # Chiều cao biểu đồ
            # font=dict(size=12)  # Kích thước font chữ
            xaxis=dict(
                tickmode='linear',
                dtick=1,
                title='Ngày',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục X
                tickfont=dict(size=12, color='black')
            ),
            yaxis=dict(
                title='Số vụ tai nạn',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục Y
                tickfont=dict(size=12, color='black')
            ),
            title=dict(
                x=0,  # Di chuyển tiêu đề sang bên trái
                xanchor='left',  # Căn chỉnh tiêu đề với phía bên trái
                yanchor='top'  # Căn chỉnh theo chiều dọc ở phía trên
            ),
            font=dict(size=12),
            height=300
        )

        # Hiển thị biểu đồ trên Streamlit
        # st.markdown("**📊 Xu hướng số vụ tai nạn theo ngày trong tháng**")
        st.plotly_chart(fig_daily, use_container_width=True)
    ######################################################

with st.container(border=False):
    chart_col1, chart_col2 = st.columns(2)
    ######################################################
    with chart_col1.container(border=True):
        # Chuyển đổi 'Thời gian xảy ra tai nạn' sang datetime và trích xuất giờ
        filtered_df['Giờ'] = pd.to_datetime(filtered_df['Thời gian xảy ra tai nạn'], format='%H:%M:%S', errors='coerce').dt.hour

        # Đếm số vụ tai nạn theo từng giờ
        hourly_accidents = filtered_df['Giờ'].value_counts().sort_index().reset_index()
        hourly_accidents.columns = ['Giờ', 'Số vụ']

        # Vẽ biểu đồ số vụ tai nạn theo khung giờ
        fig_hourly = px.bar(
            hourly_accidents,
            x='Giờ',
            y='Số vụ',
            title='📊 Số vụ tai nạn theo khung giờ',
            # title=' ',
            text='Số vụ',
            color='Số vụ',
            # color_continuous_scale='Plasma'  # Thang màu Plasma
            color_continuous_scale='Viridis'
        )

        # Tùy chỉnh hiển thị biểu đồ
        fig_hourly.update_traces(textposition='outside')
        fig_hourly.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            title_x=0.5,  # Căn giữa tiêu đề
            # xaxis_title='Giờ trong ngày',
            # yaxis_title='Số vụ tai nạn',
            # xaxis=dict(tickmode='linear', dtick=1),  # Hiển thị đầy đủ giờ
            # # width=900,  # Độ rộng biểu đồ
            # height=300,  # Chiều cao biểu đồ
            # font=dict(size=12)  # Kích thước font chữ
            xaxis=dict(
                tickmode='linear',
                dtick=1,
                title='Giờ trong ngày',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục X
                tickfont=dict(size=12, color='black')
            ),
            yaxis=dict(
                title='Số vụ tai nạn',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục Y
                tickfont=dict(size=12, color='black')
            ),
            title=dict(
                x=0,  # Di chuyển tiêu đề sang bên trái
                xanchor='left',  # Căn chỉnh tiêu đề với phía bên trái
                yanchor='top'  # Căn chỉnh theo chiều dọc ở phía trên
            ),
            font=dict(size=12),
            height=300
        )

        # Hiển thị biểu đồ trên Streamlit
        # st.markdown("**📊 Số vụ tai nạn theo khung giờ**")
        st.plotly_chart(fig_hourly, use_container_width=True)
    ######################################################
    with chart_col2.container(border=True):
        data['Ngày xảy ra tai nạn'] = pd.to_datetime(data['Ngày xảy ra tai nạn'], format='%d/%m/%Y')
        data['Thứ trong tuần'] = data['Ngày xảy ra tai nạn'].dt.day_name()

        # Map English day names to Vietnamese day names
        day_name_mapping = {
            'Monday': 'Thứ Hai',
            'Tuesday': 'Thứ Ba',
            'Wednesday': 'Thứ Tư',
            'Thursday': 'Thứ Năm',
            'Friday': 'Thứ Sáu',
            'Saturday': 'Thứ Bảy',
            'Sunday': 'Chủ Nhật'
        }
        data['Thứ trong tuần'] = data['Thứ trong tuần'].map(day_name_mapping)

        # Group by day of the week and count the number of accidents, ensuring the correct order
        accidents_by_day_vn = data['Thứ trong tuần'].value_counts().reindex(
            ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']
        )

        fig = px.bar(
            x=accidents_by_day_vn.index,
            y=accidents_by_day_vn.values,
            labels={'x': 'Thứ trong tuần', 'y': 'Số vụ tai nạn'},
            title='📊 Số vụ tai nạn theo các thứ trong tuần',
            text=accidents_by_day_vn.values,
            color=accidents_by_day_vn.values,
            color_continuous_scale=px.colors.sequential.Cividis  # Thân thiện cho người mù màu
        )

        # Customize the layout with size adjustments
        fig.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            # xaxis_title='Thứ trong tuần',
            # yaxis_title='Số vụ tai nạn',
            # title_font_size=18,
            title_x=0.5,
            xaxis_tickangle=0,
            template='plotly_white',
            # width=800,  # Độ rộng biểu đồ
            # height=500  # Chiều cao biểu đồ
            xaxis=dict(
                tickmode='linear',
                dtick=1,
                title='Thứ trong tuần',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục X
                tickfont=dict(size=12, color='black')
            ),
            yaxis=dict(
                title='Số vụ tai nạn',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục Y
                tickfont=dict(size=12, color='black')
            ),
            title=dict(
                x=0,  # Di chuyển tiêu đề sang bên trái
                xanchor='left',  # Căn chỉnh tiêu đề với phía bên trái
                yanchor='top'  # Căn chỉnh theo chiều dọc ở phía trên
            ),
            font=dict(size=12),
            height=300
        )



        # Show the chart
        # fig.show()
        st.plotly_chart(fig, use_container_width=True)

    ######################################################
    # with chart_col2.container(border=True):
    #     # Đếm số vụ tai nạn theo từng quận/huyện và lấy top 10
    #     district_accidents = (
    #         filtered_df['Quận/Huyện']
    #         .value_counts()
    #         .head(10)
    #         .reset_index()
    #         .rename(columns={'Quận/Huyện': 'Quận/Huyện', 'Số vụ': 'Số vụ tai nạn'})
    #     )

    #     district_accidents['index'] = district_accidents['index'].astype(str) + ' <span style="color:white;">a</span>'

    #     # Sắp xếp tăng dần theo số vụ tai nạn
    #     district_accidents = district_accidents.sort_values(by='Quận/Huyện', ascending=True)

    #     # Vẽ biểu đồ Horizontal Bar Chart
    #     fig_district = px.bar(
    #         district_accidents,
    #         x='Quận/Huyện',
    #         y='index',
    #         orientation='h',  # Biểu đồ ngang
    #         title='📊 Top 10 quận/huyện có số vụ tai nạn cao nhất (Sắp xếp tăng dần)',
    #         # title=' ',
    #         labels={'Quận/Huyện': 'Quận/Huyện', 'index': 'index'},
    #         color='Quận/Huyện',
    #         # color_continuous_scale='Viridis'  # Thang màu Viridis
    #         color_continuous_scale=px.colors.sequential.Cividis
    #     )

    #     # Tùy chỉnh hiển thị biểu đồ
    #     fig_district.update_layout(
    #         margin=dict(l=0, r=0, t=70, b=0),
    #         title_x=0.5,  # Căn giữa tiêu đề
    #         # xaxis_title='Số vụ tai nạn',
    #         # yaxis_title='Quận/Huyện',
    #         # # width=900,  # Độ rộng biểu đồ
    #         # height=300,  # Chiều cao biểu đồ
    #         # font=dict(size=12)  # Kích thước font chữ
    #         xaxis=dict(
    #             tickmode='linear',
    #             dtick=100,
    #             title='Số vụ tai nạn',
    #             title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục X
    #             tickfont=dict(size=12, color='black')
    #         ),
    #         yaxis=dict(
    #             title='Quận/Huyện',
    #             title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục Y
    #             tickfont=dict(size=12, color='black')
    #         ),
    #         title=dict(
    #             x=0,  # Di chuyển tiêu đề sang bên trái
    #             xanchor='left',  # Căn chỉnh tiêu đề với phía bên trái
    #             yanchor='top'  # Căn chỉnh theo chiều dọc ở phía trên
    #         ),
    #         font=dict(size=12),
    #         height=300
    #     )

    #     # Hiển thị biểu đồ trên Streamlit
    #     # st.markdown("**📊 Top 10 Quận/Huyện Có Số Vụ Tai Nạn Cao Nhất**")
    #     st.plotly_chart(fig_district, use_container_width=True)

