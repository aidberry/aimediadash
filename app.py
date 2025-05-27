
import streamlit as st
import pandas as pd
import plotly.express as px
import openai

# Set app title
st.set_page_config(page_title="📊 Interactive Media Intelligence Dashboard – Ramadan Campaign 🌙")
st.title("📊 Interactive Media Intelligence Dashboard – Ramadan Campaign 🌙")

# User info section
st.sidebar.header("👤 User Information")
user_name = st.sidebar.text_input("Name")
user_team = st.sidebar.text_input("Team/Group")
user_email = st.sidebar.text_input("Email")

st.sidebar.markdown(f"**User:** {user_name} | **Team:** {user_team} | **Email:** {user_email}")

# Upload CSV
data_file = st.file_uploader("📥 Upload your CSV file", type=["csv"])
if data_file:
    df = pd.read_csv(data_file)
    
    # Data cleaning
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['engagements'] = df['engagements'].fillna(0)

    # Filters
    platform_filter = st.sidebar.multiselect("Select Platform", df['platform'].unique())
    sentiment_filter = st.sidebar.multiselect("Select Sentiment", df['sentiment'].unique())
    media_filter = st.sidebar.multiselect("Select Media Type", df['media_type'].unique())
    location_filter = st.sidebar.multiselect("Select Location", df['location'].unique())
    date_range = st.sidebar.date_input("Select Date Range", [df['date'].min(), df['date'].max()])

    filtered_df = df
    if platform_filter:
        filtered_df = filtered_df[filtered_df['platform'].isin(platform_filter)]
    if sentiment_filter:
        filtered_df = filtered_df[filtered_df['sentiment'].isin(sentiment_filter)]
    if media_filter:
        filtered_df = filtered_df[filtered_df['media_type'].isin(media_filter)]
    if location_filter:
        filtered_df = filtered_df[filtered_df['location'].isin(location_filter)]
    filtered_df = filtered_df[(filtered_df['date'] >= pd.to_datetime(date_range[0])) & (filtered_df['date'] <= pd.to_datetime(date_range[1]))]

    # Charts
    st.header("📊 Sentiment Breakdown")
    fig1 = px.pie(filtered_df, names='sentiment')
    st.plotly_chart(fig1)

    st.header("📈 Engagement Trend Over Time")
    fig2 = px.line(filtered_df, x='date', y='engagements')
    st.plotly_chart(fig2)

    st.header("📊 Platform Engagements")
    fig3 = px.bar(filtered_df.groupby('platform')['engagements'].sum().reset_index(), x='platform', y='engagements')
    st.plotly_chart(fig3)

    st.header("📊 Media Type Mix")
    fig4 = px.pie(filtered_df, names='media_type')
    st.plotly_chart(fig4)

    st.header("📍 Top 5 Locations")
    top_locations = filtered_df['location'].value_counts().head(5).reset_index()
    top_locations.columns = ['location', 'count']
    fig5 = px.bar(top_locations, x='location', y='count')
    st.plotly_chart(fig5)

    # AI Insights
    st.header("🤖 AI-Generated Insights")
    api_key = st.text_input("Enter your OpenRouter API Key", type="password")
    if api_key:
        openai.api_key = api_key
        prompt_text = f"Generate 3 key insights from this media data: {filtered_df.describe().to_string()}"

        response = openai.ChatCompletion.create(
            model="meta-llama/llama-3.3-8b-instruct:free",
            messages=[{"role": "user", "content": prompt_text}]
        )
        insights = response['choices'][0]['message']['content']
        st.write(insights)

    st.success("✅ Dashboard generated successfully! You can now export as PDF using your browser's print to PDF.")
