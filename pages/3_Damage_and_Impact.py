import streamlit as st
import pandas as pd
import plotly.express as px
from overview_parameters import filter_string, create_widgets, filter_df
import ast

# Load data
file_path = 'data_dv.csv'  # Replace with your uploaded file path
data = pd.read_csv(file_path)

# Page configuration
st.set_page_config(page_title="Damage and Impact", layout="wide")

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
st.markdown("<h3 style='text-align: center;'>Thiệt hại và tác động</h3>", unsafe_allow_html=True)

###########################################

st.sidebar.title("Bộ lọc")

# Nhập gi
district_input = st.sidebar.multiselect("Quận/Huyện", options=data['Quận/Huyện'].unique())
road_type_input = st.sidebar.multiselect("Loại đường", options=data['Loại đường'].unique())
weather_type_input = st.sidebar.multiselect("Tình trạng thời tiết", options=data['Tình trạng thời tiết'].unique())

# Filtering function
def filter_df(df, district_input, road_type_input, weather_type_input):
    
    # Filter by selected districts
    if district_input:
        df = df[df['Quận/Huyện'].isin(district_input)]
    
    # Filter by selected road types
    if road_type_input:
        df = df[df['Loại đường'].isin(road_type_input)]
    
    # Filter by selected weather conditions
    if weather_type_input:
        df = df[df['Tình trạng thời tiết'].isin(weather_type_input)]
    
    return df

# Apply the filtering based on user input from the sidebar
filtered_df = filter_df(data, district_input, road_type_input, weather_type_input)

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
        
        # Chuẩn bị dữ liệu
        # Loại bỏ các hàng có giá trị thiếu trong 'Quận/Huyện', 'Số người chết', và 'Số người bị thương'
        stacked_data = filtered_df.dropna(subset=['Quận/Huyện', 'Số người chết', 'Số người bị thương'])
        stacked_data['Quận/Huyện'] = stacked_data['Quận/Huyện'].astype(str) + ' <span style="color:white;">a</span>'


        # Nhóm dữ liệu theo 'Quận/Huyện' và tính tổng số người chết và bị thương
        stacked_summary = stacked_data.groupby('Quận/Huyện').agg(
            {'Số người chết': 'sum', 'Số người bị thương': 'sum'}
        ).reset_index()

        # Chuyển dữ liệu sang định dạng phù hợp cho Stacked Bar Chart
        stacked_melted = stacked_summary.melt(
            id_vars='Quận/Huyện',
            value_vars=['Số người chết', 'Số người bị thương'],
            var_name='Loại thống kê',
            value_name='Số lượng'
        )

        # Vẽ biểu đồ Stacked Bar Chart với bảng màu phân biệt
        fig = px.bar(
            stacked_melted,
            x='Quận/Huyện',
            y='Số lượng',
            color='Loại thống kê',
            title='📊 Số người chết và bị thương theo quận/huyện',
            # title=' ',
            labels={'Số lượng': 'Số người', 'Quận/Huyện': 'Quận/Huyện', 'Loại thống kê': 'Loại thống kê'},
            # color_discrete_sequence=px.colors.qualitative.Set2  # Sử dụng bảng màu Set1
            color_discrete_sequence=px.colors.qualitative.D3
        )

        # Tùy chỉnh hiển thị
        fig.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            title_x=0.5,  # Căn giữa tiêu đề
            # xaxis_title='Quận/Huyện',
            # yaxis_title='Số người',
            barmode='stack',  # Biểu đồ dạng stacked
            font=dict(size=12),  # Kích thước font chữ
            height=300,  # Chiều cao biểu đồ
            # width=1000,  # Độ rộng biểu đồ
            # xaxis=dict(tickangle=45),  # Xoay nhãn trục X nếu cần
            xaxis=dict(
                tickangle=45,
                title='Quận/Huyện',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục X
                tickfont=dict(size=12, color='black')
            ),
            yaxis=dict(
                title='Số người',
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
        # st.markdown("**📊 Số người chết và bị thương theo quận/huyện**")
        st.plotly_chart(fig, use_container_width=True)


    ############################################################
    with st.container(border=True):

        # Chuẩn bị dữ liệu
        # Gộp dữ liệu từ Nhóm PT1 và Nhóm PT2 thành một cột 'Loại phương tiện'
        vehicle_data = pd.concat([
            filtered_df[['Nhóm PT1', 'Số người chết', 'Số người bị thương']].rename(columns={'Nhóm PT1': 'Loại phương tiện'}),
            filtered_df[['Nhóm PT2', 'Số người chết', 'Số người bị thương']].rename(columns={'Nhóm PT2': 'Loại phương tiện'})
        ])

        # Loại bỏ các hàng thiếu dữ liệu
        vehicle_data = vehicle_data.dropna(subset=['Loại phương tiện', 'Số người chết', 'Số người bị thương'])

        # Tính tổng số người chết và bị thương theo loại phương tiện
        vehicle_summary = vehicle_data.groupby('Loại phương tiện').agg(
            Số_người_chết=('Số người chết', 'sum'),
            Số_người_bị_thương=('Số người bị thương', 'sum')
        ).reset_index()

        # Chuyển đổi dữ liệu sang định dạng phù hợp cho Stacked Bar Chart
        vehicle_melted = vehicle_summary.melt(
            id_vars='Loại phương tiện',
            value_vars=['Số_người_chết', 'Số_người_bị_thương'],
            var_name='Loại thống kê',
            value_name='Số lượng'
        )

        # Vẽ biểu đồ Stacked Bar Chart
        fig_stacked_bar = px.bar(
            vehicle_melted,
            x='Loại phương tiện',
            y='Số lượng',
            color='Loại thống kê',
            title='📊 Số người chết và bị thương theo loại phương tiện',
            # title=' ',
            labels={
                'Loại phương tiện': 'Loại phương tiện',
                'Số lượng': 'Số người',
                'Loại thống kê': 'Loại thống kê'
            },
            barmode='stack',  # Biểu đồ dạng stacked
            # color_discrete_sequence=px.colors.qualitative.Set2  # Bảng màu
            color_discrete_sequence=px.colors.qualitative.D3
        )

        # Tùy chỉnh hiển thị
        fig_stacked_bar.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            title_x=0.5,  # Căn giữa tiêu đề
            # xaxis_title='Loại phương tiện',
            # yaxis_title='Số người',
            font=dict(size=12),  # Kích thước font chữ
            height=300,  # Chiều cao biểu đồ
            # width=900,  # Độ rộng biểu đồ
            # xaxis=dict(tickangle=45),  # Xoay nhãn trục X nếu cần
            xaxis=dict(
                tickangle=45,
                title='Loại phương tiện',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục X
                tickfont=dict(size=12, color='black')
            ),
            yaxis=dict(
                title='Số người',
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
        # st.markdown("**📊 Số người chết và bị thương theo loại phương tiện**")
        st.plotly_chart(fig_stacked_bar, use_container_width=True)


##########################################################
with chart_col2.container():
    with st.container(border=True):
        
        # Chuẩn bị dữ liệu
        # Tính tổng số vụ, tổng thiệt hại và thiệt hại trung bình mỗi vụ theo quận/huyện
        bubble_data = filtered_df.groupby('Quận/Huyện').agg(
            Tổng_số_vụ=('Quận/Huyện', 'size'),
            Tổng_thiệt_hại=('Thiệt hại ước tính (triệu đồng)', 'sum'),
            Thiệt_hại_trung_bình=('Thiệt hại ước tính (triệu đồng)', 'mean')
        ).reset_index()

        bubble_data['Quận/Huyện'] = bubble_data['Quận/Huyện'].astype(str) + ' <span style="color:white;">a</span>'
        bubble_data['Tổng_thiệt_hại'] = bubble_data['Tổng_thiệt_hại'].astype(float)

        # Loại bỏ các giá trị NaN trong dữ liệu
        bubble_data = bubble_data.dropna(subset=['Tổng_thiệt_hại', 'Thiệt_hại_trung_bình'])

        # Vẽ biểu đồ Bubble Chart
        fig_bubble = px.scatter(
            bubble_data,
            x='Tổng_số_vụ',
            y='Tổng_thiệt_hại',
            size='Thiệt_hại_trung_bình',
            color='Quận/Huyện',
            title='📊 Phân tích thiệt hại theo quận/huyện',
            # title=' ',
            labels={
                'Tổng_số_vụ': 'Số vụ tai nạn',
                'Tổng_thiệt_hại': 'Tổng thiệt hại (triệu đồng)',
                'Thiệt_hại_trung_bình': 'Thiệt hại trung bình (triệu đồng)',
                'Quận/Huyện': 'Quận/Huyện'
            },
            size_max=60,  # Kích thước lớn nhất của bong bóng
            color_discrete_sequence=px.colors.sequential.Viridis  # Thang màu
        )

        # Tùy chỉnh hiển thị
        fig_bubble.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            title_x=0.5,  # Căn giữa tiêu đề
            font=dict(size=12),  # Kích thước font chữ
            height=300,  # Chiều cao biểu đồ
            legend=dict(
                orientation='h',  # Horizontal orientation
                x=0.5,  # Căn giữa legend
                xanchor='center',  # Căn giữa legend
                y=-0.2,  # Vị trí của legend (ở dưới biểu đồ)
                yanchor='top',  # Chỉnh legend nằm ở phía trên
                itemsizing='constant',  # Đảm bảo mỗi mục có kích thước giống nhau
                traceorder='normal',
                font=dict(size=10),
                title=dict(text='Quận/Huyện', font=dict(size=12))
            ),
            title=dict(
                x=0,  # Di chuyển tiêu đề sang bên trái
                xanchor='left',  # Căn chỉnh tiêu đề với phía bên trái
                yanchor='top'  # Căn chỉnh theo chiều dọc ở phía trên
            ),
        )
        # Hiển thị biểu đồ trên Streamlit
        # st.markdown("**📊 Phân tích thiệt hại theo quận/huyện**")
        st.plotly_chart(fig_bubble, use_container_width=True)

    ########################################################
    with st.container(border=True):
        
        # Kết hợp cả 'Nhóm PT1' và 'Nhóm PT2' thành một cột duy nhất
        vehicles_damage = pd.concat([
            filtered_df[['Nhóm PT1', 'Thiệt hại ước tính (triệu đồng)']].rename(columns={'Nhóm PT1': 'Loại phương tiện'}),
            filtered_df[['Nhóm PT2', 'Thiệt hại ước tính (triệu đồng)']].rename(columns={'Nhóm PT2': 'Loại phương tiện'})
        ])

        vehicles_damage = vehicles_damage[vehicles_damage['Thiệt hại ước tính (triệu đồng)'] <= 1000]

        # Loại bỏ các hàng có NaN trong cả 'Loại phương tiện' và 'Thiệt hại ước tính'
        vehicles_damage = vehicles_damage.dropna(subset=['Loại phương tiện', 'Thiệt hại ước tính (triệu đồng)'])

        # Tính thiệt hại trung bình cho từng loại phương tiện
        avg_damage_by_vehicle = vehicles_damage.groupby('Loại phương tiện')['Thiệt hại ước tính (triệu đồng)'].mean().reset_index()
        avg_damage_by_vehicle.columns = ['Loại phương tiện', 'Thiệt hại trung bình']

        # Kiểm tra giá trị trung gian
        print(avg_damage_by_vehicle)
        avg_damage_by_vehicle = avg_damage_by_vehicle.sort_values(by='Thiệt hại trung bình', ascending=True)

        # Vẽ biểu đồ thanh ngang
        fig = px.bar(
            avg_damage_by_vehicle,
            x='Thiệt hại trung bình',
            y='Loại phương tiện',
            orientation='h',
            title='📊 Thiệt hại trung bình theo loại phương tiện',
            # title=' ',
            color='Thiệt hại trung bình',
            color_continuous_scale='viridis',
            labels={'Thiệt hại trung bình': 'Thiệt hại trung bình (triệu đồng)', 'Loại phương tiện': 'Loại phương tiện'}
        )

        # Tùy chỉnh hiển thị
        fig.update_layout(
            margin=dict(l=0, r=0, t=70, b=0),
            title_x=0.5,
            # xaxis_title='Thiệt hại trung bình (triệu đồng)',
            # yaxis_title='Loại phương tiện',
            font=dict(size=12),
            height=300,
            xaxis=dict(
                title='Thiệt hại trung bình (triệu đồng)',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục X
                tickfont=dict(size=12, color='black')
            ),
            yaxis=dict(
                title='Loại phương tiện',
                title_font=dict(size=14, color='black'),  # Bôi đen nhãn trục Y
                tickfont=dict(size=12, color='black')
            ),
            title=dict(
                x=0,  # Di chuyển tiêu đề sang bên trái
                xanchor='left',  # Căn chỉnh tiêu đề với phía bên trái
                yanchor='top'  # Căn chỉnh theo chiều dọc ở phía trên
            ),
            # width=900
        )
        # Hiển thị biểu đồ trên Streamlit
        # st.markdown("**📊 Thiệt hại trung bình theo loại phương tiện**")
        st.plotly_chart(fig, use_container_width=True)


    ######################################################