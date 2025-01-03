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
            title=' ',
            color_discrete_sequence=px.colors.sequential.Viridis  # Changed to Viridis for better contrast
        )

        # Customize labels and layout
        fig.update_traces(
            textinfo='percent+label', 
            pull=[0.1 if value < 0.05 * weather_condition_counts['Số vụ'].sum() else 0 for value in weather_condition_counts['Số vụ']],
            textfont_size=12  # Adjust font size for better readability
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            title_x=0.5,  # Center the title
            legend_title="Tình trạng thời tiết",
            # width=900,  # Adjusted width for better visualization
            height=300,  # Adjusted height for better visualization
            font=dict(size=10),  # Set default font size
            # autosize=True
        )


        # Hiển thị biểu đồ trên Streamlit
        st.markdown("**📊 Tỷ lệ tai nạn dựa trên tình trạng thời tiết**")
        st.plotly_chart(fig, use_container_width=True)
    ############################################################
    with st.container(border=True):
        # Extract individual causes from the 'Nguyên nhân và Lỗi vi phạm' column
        data['Nguyên nhân'] = data['Nguyên nhân và Lỗi vi phạm'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else []
        )

        # Explode the list of causes into separate rows
        exploded_causes = data.explode('Nguyên nhân')

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
            title=' ',
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
            font=dict(size=12),
            bgcolor="rgba(255, 255, 255, 0.8)",  # Add background color
            bordercolor="black",
            borderwidth=1.5
        )

        fig.update_traces(textposition='outside')
        # Customize layout
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            title_x=0.5,  # Center the title
            xaxis_title='Nguyên nhân (Rút gọn)',
            yaxis_title='Số vụ',
            font=dict(size=12),  # Set default font size
            legend_title="Nguyên nhân",
            # width=1000,  # Adjust width to make room for annotations
            # height=600  # Adjust height
            height=300,
        )

        # Hiển thị biểu đồ trên Streamlit
        st.markdown("**📊 Top 10 Nguyên nhân gây tai nạn có người chết**")
        st.plotly_chart(fig, use_container_width=True)


