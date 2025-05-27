import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def clean_data(df):
    """
    Cleans the uploaded DataFrame:
    - Converts 'Date' to datetime.
    - Fills missing 'Engagements' with 0.
    - Standardizes column names.
    """
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('.', '')

    # Convert 'date' to datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Fill missing 'engagements' with 0
    if 'engagements' in df.columns:
        df['engagements'] = df['engagements'].fillna(0)

    return df

def generate_insights(chart_title, data, chart_type):
    """Generates top 3 insights for a given chart."""
    insights = []
    if chart_type == "pie_sentiment":
        total_sentiment = data['count'].sum()
        positive_percent = (data[data['sentiment'] == 'Positive']['count'].sum() / total_sentiment * 100) if total_sentiment > 0 else 0
        negative_percent = (data[data['sentiment'] == 'Negative']['count'].sum() / total_sentiment * 100) if total_sentiment > 0 else 0
        neutral_percent = (data[data['sentiment'] == 'Neutral']['count'].sum() / total_sentiment * 100) if total_sentiment > 0 else 0
        insights.append(f"1. A majority of the sentiment is **{data.iloc[0]['sentiment']}** ({data.iloc[0]['percentage']:.1f}%).")
        insights.append(f"2. Approximately **{positive_percent:.1f}%** of the mentions are positive, indicating a generally favorable perception.")
        insights.append(f"3. Negative sentiment accounts for **{negative_percent:.1f}%**, which might indicate areas for improvement or concerns.")
    elif chart_type == "line_engagement":
        peak_date = data.loc[data['engagements'].idxmax()]
        min_date = data.loc[data['engagements'].idxmin()]
        total_engagements = data['engagements'].sum()
        avg_engagements = data['engagements'].mean()
        insights.append(f"1. Peak engagement occurred on **{peak_date['date'].strftime('%Y-%m-%d')}** with **{int(peak_date['engagements'])}** engagements.")
        insights.append(f"2. The lowest engagement was observed on **{min_date['date'].strftime('%Y-%m-%d')}** with **{int(min_date['engagements'])}** engagements.")
        insights.append(f"3. The average daily engagement over the period is approximately **{avg_engagements:,.0f}**.")
    elif chart_type == "bar_platform":
        top_platform = data.iloc[0]
        insights.append(f"1. **{top_platform['platform']}** is the dominant platform, contributing **{int(top_platform['engagements'])}** engagements.")
        if len(data) > 1:
            second_platform = data.iloc[1]
            insights.append(f"2. **{second_platform['platform']}** is the second most engaging platform with **{int(second_platform['engagements'])}** engagements, significantly less than the top platform." if len(data) > 1 else "")
        total_engagements = data['engagements'].sum()
        insights.append(f"3. These platforms collectively generated **{int(total_engagements)}** engagements, highlighting their importance in the campaign's reach.")
    elif chart_type == "pie_media_type":
        top_media_type = data.iloc[0]
        insights.append(f"1. **{top_media_type['media_type']}** is the most prevalent media type, accounting for **{top_media_type['percentage']:.1f}%** of the content.")
        if len(data) > 1:
            second_media_type = data.iloc[1]
            insights.append(f"2. **{second_media_type['media_type']}** is the second most used media type, making up **{second_media_type['percentage']:.1f}%** of the content." if len(data) > 1 else "")
        insights.append(f"3. The mix of media types indicates a diverse content strategy, with a strong reliance on **{top_media_type['media_type']}**.")
    elif chart_type == "bar_location":
        top_location = data.iloc[0]
        insights.append(f"1. **{top_location['location']}** is the top location for engagements, with **{int(top_location['engagements'])}** engagements.")
        if len(data) > 1:
            second_location = data.iloc[1]
            insights.append(f"2. **{second_location['location']}** follows with **{int(second_location['engagements'])}** engagements, suggesting a strong presence in these two regions." if len(data) > 1 else "")
        insights.append(f"3. The top 5 locations collectively represent a significant portion of the total campaign reach and engagement.")
    return insights

st.set_page_config(layout="wide")
st.title("Interactive Media Intelligence Dashboard – Ramadan Campaign")

st.sidebar.header("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("File uploaded successfully!")

    df = clean_data(df.copy()) # Use .copy() to avoid SettingWithCopyWarning

    if not all(col in df.columns for col in ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']):
        st.error("Error: The uploaded CSV must contain the columns: 'Date', 'Platform', 'Sentiment', 'Location', 'Engagements', 'Media Type'. Please check your file.")
        st.stop()

    st.header("1. Sentiment Breakdown")
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['sentiment', 'count']
    sentiment_counts['percentage'] = (sentiment_counts['count'] / sentiment_counts['count'].sum()) * 100
    fig_sentiment = px.pie(sentiment_counts, names='sentiment', values='count',
                           title='Sentiment Breakdown', hole=0.3,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_sentiment, use_container_width=True)
    st.markdown("---")
    st.subheader("Insights:")
    for insight in generate_insights("Sentiment Breakdown", sentiment_counts, "pie_sentiment"):
        st.markdown(f"- {insight}")
    st.markdown("---")


    st.header("2. Engagement Trend Over Time")
    df_engagements_daily = df.groupby('date')['engagements'].sum().reset_index()
    fig_engagement_trend = px.line(df_engagements_daily, x='date', y='engagements',
                                   title='Daily Engagement Trend',
                                   labels={'date': 'Date', 'engagements': 'Total Engagements'})
    fig_engagement_trend.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig_engagement_trend, use_container_width=True)
    st.markdown("---")
    st.subheader("Insights:")
    for insight in generate_insights("Engagement Trend Over Time", df_engagements_daily, "line_engagement"):
        st.markdown(f"- {insight}")
    st.markdown("---")


    st.header("3. Engagements by Platform")
    platform_engagements = df.groupby('platform')['engagements'].sum().sort_values(ascending=False).reset_index()
    fig_platform_engagements = px.bar(platform_engagements, x='platform', y='engagements',
                                      title='Total Engagements by Platform',
                                      labels={'platform': 'Platform', 'engagements': 'Total Engagements'},
                                      color='platform')
    st.plotly_chart(fig_platform_engagements, use_container_width=True)
    st.markdown("---")
    st.subheader("Insights:")
    for insight in generate_insights("Engagements by Platform", platform_engagements, "bar_platform"):
        st.markdown(f"- {insight}")
    st.markdown("---")


    st.header("4. Media Type Mix")
    media_type_counts = df['media_type'].value_counts().reset_index()
    media_type_counts.columns = ['media_type', 'count']
    media_type_counts['percentage'] = (media_type_counts['count'] / media_type_counts['count'].sum()) * 100
    fig_media_type = px.pie(media_type_counts, names='media_type', values='count',
                           title='Media Type Mix', hole=0.3,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_media_type, use_container_width=True)
    st.markdown("---")
    st.subheader("Insights:")
    for insight in generate_insights("Media Type Mix", media_type_counts, "pie_media_type"):
        st.markdown(f"- {insight}")
    st.markdown("---")


    st.header("5. Top 5 Locations by Engagements")
    location_engagements = df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(5).reset_index()
    fig_top_locations = px.bar(location_engagements, x='location', y='engagements',
                               title='Top 5 Locations by Engagements',
                               labels={'location': 'Location', 'engagements': 'Total Engagements'},
                               color='location')
    st.plotly_chart(fig_top_locations, use_container_width=True)
    st.markdown("---")
    st.subheader("Insights:")
    for insight in generate_insights("Top 5 Locations by Engagements", location_engagements, "bar_location"):
        st.markdown(f"- {insight}")
    st.markdown("---")

else:
    st.info("Please upload a CSV file to get started.")
    st.markdown("""
        **Expected CSV Format:**
        Your CSV file should have the following columns:
        - `Date` (e.g., 'YYYY-MM-DD')
        - `Platform` (e.g., 'Facebook', 'Twitter', 'Instagram')
        - `Sentiment` (e.g., 'Positive', 'Negative', 'Neutral')
        - `Location` (e.g., 'New York', 'London')
        - `Engagements` (numeric)
        - `Media Type` (e.g., 'Image', 'Video', 'Text')
    """)
