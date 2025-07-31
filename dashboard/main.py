"""
Nsight AI Budgeting System - Streamlit Dashboard
Interactive web interface for AI-powered budgeting, forecasting, and anomaly detection.
Professional dark blue theme.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Nsight AI Budgeting System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Professional Dark Blue CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Root styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
        color: white;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(30, 64, 175, 0.3);
        border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        text-shadow: 0 4px 8px rgba(0,0,0,0.2);
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* Section containers */
    .section-container {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(59, 130, 246, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .section-header {
        color: #e2e8f0;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(59, 130, 246, 0.3);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 24px rgba(30, 64, 175, 0.3);
        border: 1px solid rgba(59, 130, 246, 0.2);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(30, 64, 175, 0.4);
    }
    
    /* Alert boxes */
    .alert-box {
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
        border: 1px solid;
        backdrop-filter: blur(10px);
    }
    
    .alert-high {
        background: rgba(239, 68, 68, 0.1);
        border-color: #ef4444;
        color: #fca5a5;
    }
    
    .alert-medium {
        background: rgba(245, 158, 11, 0.1);
        border-color: #f59e0b;
        color: #fbbf24;
    }
    
    .alert-low {
        background: rgba(139, 92, 246, 0.1);
        border-color: #8b5cf6;
        color: #c4b5fd;
    }
    
    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border-color: #10b981;
        color: #6ee7b7;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
        border: 1px solid;
        backdrop-filter: blur(10px);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Professional icons */
    .icon {
        display: inline-block;
        width: 18px;
        height: 18px;
        margin-right: 8px;
        text-align: center;
        font-weight: bold;
        background: #3b82f6;
        color: white;
        border-radius: 4px;
        font-size: 10px;
        line-height: 18px;
    }
    
    /* Consistent typography */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #e2e8f0;
        font-weight: 600;
    }
    
    .stMarkdown p {
        color: #94a3b8;
        line-height: 1.6;
    }
    
    /* Data tables */
    .stDataFrame {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Charts */
    .js-plotly-plot {
        background: transparent !important;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
    
    /* Input styling */
    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 8px;
        color: #e2e8f0;
    }
    
    .stTextInput > div > div > input {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 8px;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# API Helper Functions
@st.cache_data(ttl=60)  # Cache for 1 minute
def call_api(endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
    """Make API calls with error handling and caching."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return None
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to API backend. Please start the API server first.")
        st.info("Run: `py -m uvicorn src.api.main:app --reload --port 8000`")
        return None
    except requests.exceptions.Timeout:
        st.error("⏰ API request timed out")
        return None
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

def check_api_health() -> bool:
    """Check if API backend is running."""
    health = call_api("/health")
    return health is not None and health.get("status") == "healthy"

# Dashboard Pages
def show_overview_page():
    """Display the main dashboard overview."""
    st.markdown('''
    <div class="main-header">
        <h1>Nsight AI Budgeting System</h1>
        <p>Intelligent Financial Management & Analytics Platform</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # API Health Check
    if not check_api_health():
        st.markdown('''
        <div class="alert-box alert-high">
            <strong>STATUS:</strong> API Backend is not running! Please start the backend server: <code>py -m uvicorn src.api.main:app --reload --port 8000</code>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    st.markdown('''
    <div class="success-box">
        <strong>STATUS:</strong> Successfully connected to AI Budgeting Backend
    </div>
    ''', unsafe_allow_html=True)

    # Get dashboard stats
    stats = call_api("/dashboard/stats")
    
    if stats:
        # Key Metrics Section
        st.markdown('''
        <div class="section-container">
            <div class="section-header">
                <span class="icon">KPI</span>Key Performance Indicators
            </div>
        ''', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Expenses",
                value=f"{stats['total_expenses']:,}",
                delta=f"${stats['total_spent']:,.0f} spent"
            )
        
        with col2:
            st.metric(
                label="Total Budgets",
                value=f"{stats['total_budgets']:,}",
                delta=f"${stats['total_allocated']:,.0f} allocated"
            )
        
        with col3:
            anomaly_rate = stats.get('anomaly_rate', 0)
            st.metric(
                label="Anomaly Rate",
                value=f"{anomaly_rate:.1f}%",
                delta="Real-time detection"
            )
        
        with col4:
            budget_utilization = (stats['total_spent'] / stats['total_allocated'] * 100) if stats['total_allocated'] > 0 else 0
            st.metric(
                label="Budget Utilization",
                value=f"{budget_utilization:.1f}%",
                delta="Actual vs Planned"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent Activity Section
        st.markdown('''
        <div class="section-container">
            <div class="section-header">
                <span class="icon">LOG</span>Recent Expense Activity
            </div>
        ''', unsafe_allow_html=True)
        
        # Currency filter for expense logs
        currency_filter_options = {
            "ALL": "All Currencies",
            "USD": "US Dollar (USD)",
            "INR": "Indian Rupee (INR)", 
            "CAD": "Canadian Dollar (CAD)",
            "TRY": "Turkish Lira (TRY)"
        }
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            selected_currency = st.selectbox(
                "Filter by Currency", 
                options=list(currency_filter_options.keys()),
                format_func=lambda x: currency_filter_options[x],
                key="expense_log_currency"
            )
        
        with col2:
            st.write("")  # Empty space for alignment
        
        with col3:
            if st.button("Refresh", key="refresh_expenses"):
                st.cache_data.clear()
                st.rerun()
        
        # Get filtered expenses based on currency selection
        if selected_currency == "ALL":
            # Get all expenses with recent activity endpoint
            if stats.get('recent_expenses'):
                df_recent = pd.DataFrame(stats['recent_expenses'])
                # Add currency display and ensure all currencies show
                filtered_expenses = df_recent
            else:
                filtered_expenses = pd.DataFrame()
        else:
            # Get expenses filtered by specific currency
            expense_endpoint = f"/expenses?currency={selected_currency}&limit=20&sort=created_at_desc"
            expense_data = call_api(expense_endpoint)
            
            if expense_data and expense_data.get('data'):
                filtered_expenses = pd.DataFrame(expense_data['data'])
            else:
                filtered_expenses = pd.DataFrame()
        
        # Display filtered expenses
        if not filtered_expenses.empty:
            # Format the dataframe for better display
            display_df = filtered_expenses.copy()
            
            # Ensure currency column exists and format amount with currency
            if 'currency' in display_df.columns and 'amount' in display_df.columns:
                display_df['Amount'] = display_df.apply(
                    lambda row: f"{row['amount']:,.2f} {row['currency']}", axis=1
                )
                # Remove the original amount and currency columns for cleaner display
                columns_to_show = [col for col in display_df.columns if col not in ['amount', 'currency', 'id', 'created_at']]
                display_df = display_df[columns_to_show]
            
            # Display the expenses table
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Show currency summary
            if selected_currency == "ALL" and 'currency' in filtered_expenses.columns:
                currency_summary = filtered_expenses.groupby('currency').agg({
                    'amount': ['count', 'sum']
                }).round(2)
                currency_summary.columns = ['Count', 'Total Amount']
                
                st.subheader("Currency Summary")
                st.dataframe(currency_summary, use_container_width=True)
        else:
            if selected_currency == "ALL":
                st.info("No recent expenses found")
            else:
                st.info(f"No expenses found for {currency_filter_options[selected_currency]}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Actions Section
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">ACT</span>Quick Actions
        </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("View Analytics", use_container_width=True):
            st.session_state.page = "Analytics"
            st.rerun()
    
    with col2:
        if st.button("ML Predictions", use_container_width=True):
            st.session_state.page = "Expense Classification"
            st.rerun()
    
    with col3:
        if st.button("Forecasting", use_container_width=True):
            st.session_state.page = "Forecasting"
            st.rerun()
    
    with col4:
        if st.button("Anomaly Alerts", use_container_width=True):
            st.session_state.page = "Anomaly Detection"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_analytics_page():
    """Display analytics and visualizations."""
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">CHT</span>Spending Analytics & Insights
        </div>
    ''', unsafe_allow_html=True)
    
    # Department Spending Section
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">ORG</span>Spending by Department
        </div>
    ''', unsafe_allow_html=True)

    dept_data = call_api("/dashboard/spending-by-department?months=12")
    
    if dept_data and 'data' in dept_data:
        # Extract the actual data from the API response (list of dicts)
        spending_data = dept_data['data']
        # Convert list of dicts to DataFrame for visualization
        if spending_data:
            df_dept = pd.DataFrame(spending_data)
        else:
            df_dept = pd.DataFrame(columns=['department', 'total_amount'])
        
        # Create pie chart
        fig_pie = px.pie(
            df_dept, 
            values='total_amount', 
            names='department',
            title="Department Spending Distribution (Last 12 Months)",
            color_discrete_sequence=['#3b82f6', '#60a5fa', '#93c5fd', '#1e40af', '#2563eb', '#1d4ed8', '#1e3a8a']
        )
        fig_pie.update_layout(
            title_font_size=16,
            font_family="Inter",
            title_font_color="#e2e8f0",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Create bar chart
        fig_bar = px.bar(
            df_dept, 
            x='department', 
            y='total_amount',
            title="Department Spending Amounts",
            color='total_amount',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(
            xaxis_tickangle=-45,
            title_font_size=16,
            font_family="Inter",
            title_font_color="#e2e8f0",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            xaxis=dict(gridcolor='rgba(59, 130, 246, 0.1)'),
            yaxis=dict(gridcolor='rgba(59, 130, 246, 0.1)')
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Category Spending Section
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">CAT</span>Spending by Category
        </div>
    ''', unsafe_allow_html=True)
    
    cat_data = call_api("/dashboard/spending-by-category?months=12")
    
    if cat_data and 'data' in cat_data:
        # Extract the actual data from the API response (list of dicts)
        category_data = cat_data['data']
        # Convert list of dicts to DataFrame for visualization
        if category_data:
            df_cat = pd.DataFrame(category_data)
        else:
            df_cat = pd.DataFrame(columns=['category', 'total_amount'])
        
        # Create horizontal bar chart
        fig_cat = px.bar(
            df_cat.head(10), 
            x='total_amount', 
            y='category',
            orientation='h',
            title="Top 10 Categories by Spending",
            color='total_amount',
            color_continuous_scale='Blues'
        )
        fig_cat.update_layout(
            title_font_size=16,
            font_family="Inter",
            title_font_color="#e2e8f0",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            xaxis=dict(gridcolor='rgba(59, 130, 246, 0.1)'),
            yaxis=dict(gridcolor='rgba(59, 130, 246, 0.1)')
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Monthly Trends Section
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">TRD</span>Monthly Spending Trends
        </div>
    ''', unsafe_allow_html=True)
    
    trends_data = call_api("/dashboard/monthly-trends?months=12")
    
    if trends_data and 'data' in trends_data:
        # Extract the actual data from the API response (list of dicts)
        monthly_data = trends_data['data']
        # Convert list of dicts to DataFrame for visualization
        if monthly_data:
            df_trends = pd.DataFrame(monthly_data)
        else:
            df_trends = pd.DataFrame(columns=['month', 'total_amount'])
        df_trends['month'] = pd.to_datetime(df_trends['month'])
        
        # Create line chart
        fig_trends = px.line(
            df_trends, 
            x='month', 
            y='total_amount',
            title="Monthly Spending Trends (Last 12 Months)",
            markers=True
        )
        fig_trends.update_layout(
            xaxis_title="Month",
            yaxis_title="Total Amount ($)",
            title_font_size=16,
            font_family="Inter",
            title_font_color="#e2e8f0",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            xaxis=dict(gridcolor='rgba(59, 130, 246, 0.1)'),
            yaxis=dict(gridcolor='rgba(59, 130, 246, 0.1)')
        )
        fig_trends.update_traces(line_color='#3b82f6', marker_color='#60a5fa')
        st.plotly_chart(fig_trends, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_ml_features_page():
    """Display ML features and predictions."""
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">ML</span>Expense Classification & Prediction
        </div>
    ''', unsafe_allow_html=True)
    
    # ML Model Info Section
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">MDL</span>Model Information
        </div>
    ''', unsafe_allow_html=True)
    
    ml_info = call_api("/ml/info")
    
    if ml_info:
        if ml_info.get('status') == 'ML classifier not available':
            st.markdown('''
            <div class="alert-box alert-medium">
                <strong>NOTICE:</strong> ML classifier not trained yet. Train the model first: <code>py -m src.cli train-ml</code>
            </div>
            ''', unsafe_allow_html=True)
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Model Accuracy", f"{ml_info.get('accuracy', 0):.1%}")
            with col2:
                st.metric("Training Samples", f"{ml_info.get('training_samples', 0):,}")
            with col3:
                st.metric("Categories", f"{ml_info.get('categories_count', 0)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Expense Category Prediction Section
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">PRD</span>Expense Category Prediction
        </div>
    ''', unsafe_allow_html=True)
    
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            vendor = st.text_input("Vendor Name", placeholder="e.g., Microsoft Azure")
        
        with col2:
            description = st.text_input("Description (optional)", placeholder="e.g., Cloud hosting services")
        
        predict_button = st.form_submit_button("Predict Category", use_container_width=True)
        
        if predict_button and vendor:
            prediction = call_api("/ml/predict", "POST", {
                "vendor": vendor,
                "description": description
            })
            
            if prediction:
                st.markdown(f'''
                <div class="success-box">
                    <strong>PREDICTION:</strong> Category: <strong>{prediction['predicted_category']}</strong><br>
                    <strong>CONFIDENCE:</strong> {prediction['confidence']:.1%}<br>
                    <strong>MODEL:</strong> {prediction['model_info']}
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('''
                <div class="alert-box alert-high">
                    <strong>ERROR:</strong> Prediction failed. Please try again.
                </div>
                ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_forecasting_page():
    """Display budget forecasting features."""
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">FOR</span>Budget Forecasting & Trends
        </div>
    ''', unsafe_allow_html=True)
    
    # Forecasting Controls Section
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">GEN</span>Generate Spending Forecast
        </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        forecast_months = st.slider("Forecast Period (months)", 1, 12, 6)
    
    with col2:
        confidence_level = st.slider("Confidence Level", 0.80, 0.99, 0.95, 0.01)
        
    if st.button("Generate Forecast", use_container_width=True):
        with st.spinner("Generating forecast..."):
            forecast_data = call_api("/forecast/spending", "POST", {
                "months": forecast_months,
                "confidence_level": confidence_level
            })
            
            if forecast_data:
                st.markdown('''
                <div class="success-box">
                    <strong>SUCCESS:</strong> Forecast generated successfully!
                </div>
                ''', unsafe_allow_html=True)
                
                # Debug: Show the forecast data structure
                st.write("Debug - Forecast data keys:", list(forecast_data.keys()) if isinstance(forecast_data, dict) else type(forecast_data))
                
                # Display forecast results immediately
                if isinstance(forecast_data, dict):
                    st.subheader("📊 Forecast Results")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    # Use correct field names from BudgetForecaster API
                    total_forecasted = forecast_data.get('total_forecasted', 0)
                    forecast_period = forecast_data.get('forecast_period', forecast_months)
                    
                    with col1:
                        st.metric(
                            "Total Forecast",
                            f"${total_forecasted:,.0f}",
                            f"{forecast_period} months"
                        )
                    
                    with col2:
                        monthly_avg = total_forecasted / forecast_period if forecast_period > 0 else 0
                        st.metric(
                            "Monthly Average",
                            f"${monthly_avg:,.0f}",
                            "Predicted"
                        )
                    
                    with col3:
                        confidence_level_actual = forecast_data.get('confidence_level', confidence_level)
                        st.metric(
                            "Confidence Level",
                            f"{confidence_level_actual:.0%}",
                            "Model accuracy"
                        )
                    
                    # Display monthly forecasts if available
                    monthly_forecasts = forecast_data.get('monthly_forecasts', [])
                    if monthly_forecasts:
                        st.subheader("Monthly Breakdown")
                        
                        # Create DataFrame for monthly forecasts
                        monthly_data = []
                        for forecast in monthly_forecasts:
                            monthly_data.append({
                                'Month': forecast.get('month', 'Unknown'),
                                'Predicted Amount': f"${forecast.get('predicted_amount', 0):,.0f}",
                                'Lower Bound': f"${forecast.get('confidence_lower', 0):,.0f}",
                                'Upper Bound': f"${forecast.get('confidence_upper', 0):,.0f}",
                                'Seasonal Factor': f"{forecast.get('seasonal_factor', 1.0):.2f}"
                            })
                        
                        df_monthly = pd.DataFrame(monthly_data)
                        st.dataframe(df_monthly, use_container_width=True)
                    
                    # Display category forecasts if available
                    category_forecasts = forecast_data.get('category_forecasts', {})
                    if category_forecasts:
                        st.subheader("Category Forecasts")
                        
                        for category, data in category_forecasts.items():
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.write(f"**{category}**")
                            with col2:
                                st.write(f"${data.get('total_forecast', 0):,.0f}")
                            with col3:
                                st.write(f"${data.get('monthly_average', 0):,.0f}")
                            with col4:
                                trend = data.get('trend', 'stable')
                                if trend == 'increasing':
                                    st.write("📈 Increasing")
                                elif trend == 'decreasing':
                                    st.write("📉 Decreasing")
                                else:
                                    st.write("➡️ Stable")
                    
                    # Display department forecasts if available
                    department_forecasts = forecast_data.get('department_forecasts', {})
                    if department_forecasts:
                        st.subheader("Department Forecasts")
                        
                        for department, data in department_forecasts.items():
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.write(f"**{department}**")
                            with col2:
                                st.write(f"${data.get('total_forecast', 0):,.0f}")
                            with col3:
                                st.write(f"${data.get('monthly_average', 0):,.0f}")
                            with col4:
                                trend = data.get('trend', 'stable')
                                if trend == 'increasing':
                                    st.write("📈 Increasing")
                                elif trend == 'decreasing':
                                    st.write("📉 Decreasing")
                                else:
                                    st.write("➡️ Stable")
                    
                    # Show all available forecast data for debugging
                    with st.expander("Debug: Raw Forecast Data"):
                        st.json(forecast_data)
                
                else:
                    st.error("No forecast data received. Please try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_anomaly_detection_page():
    """Display anomaly detection and alerts."""
    st.header("Anomaly Detection & Security Alerts")
    
    # Real-time Anomaly Detection
    st.subheader("Real-time Anomaly Scanning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        threshold = st.slider("Detection Sensitivity", 0.5, 0.9, 0.6, 0.05)
        st.caption("Lower = More sensitive (more alerts)")
    
    with col2:
        save_report = st.checkbox("Save detailed report")
    
    if st.button("Scan for Anomalies", use_container_width=True):
        with st.spinner("Scanning for anomalies..."):
            anomaly_data = call_api("/anomalies/detect", "POST", {
                "threshold": threshold,
                "save_report": save_report
            })
            
            if anomaly_data:
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Expenses Analyzed",
                        f"{anomaly_data['total_expenses']:,}",
                        "Complete dataset"
                    )
                
                with col2:
                    st.metric(
                        "Anomalies Found",
                        f"{anomaly_data['anomalies_detected']:,}",
                        f"{anomaly_data['anomaly_rate']:.1f}% rate"
                    )
                
                with col3:
                    high_severity = anomaly_data.get('severity_breakdown', {}).get('High', 0)
                    st.metric(
                        "🔴 High Priority",
                        f"{high_severity}",
                        "Immediate review"
                    )
                
                # Display anomalies if found
                if anomaly_data.get('anomalies'):
                    st.subheader("🔴 Top Anomalies Detected")
                    
                    for i, anomaly in enumerate(anomaly_data['anomalies'][:5], 1):
                        severity_color = {
                            'High': 'alert-high',
                            'Medium': 'alert-medium',
                            'Low': 'alert-low'
                        }.get(anomaly['severity'], 'alert-low')
                        
                        st.markdown(f'''
                        <div class="alert-box {severity_color}">
                            <strong>#{i} - {anomaly['severity']} Priority</strong><br>
                            <strong>${anomaly['amount']:,.0f}</strong> - {anomaly['vendor']} ({anomaly['department']})<br>
                            Date: {anomaly['date']} | Score: {anomaly['anomaly_score']:.2f}<br>
                            Reasons: {", ".join(anomaly['reasons'])}
                        </div>
                        ''', unsafe_allow_html=True)

def show_data_management_page():
    """Display data management features with multi-currency support."""
    st.markdown('''
    <div class="main-header">
        <h1>Data Management</h1>
        <p>Manage budgets and expenses across global operations</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Currency options for Nsight operations
    currency_options = {
        "USD": "US Dollar (USD)",
        "INR": "Indian Rupee (INR)", 
        "CAD": "Canadian Dollar (CAD)",
        "TRY": "Turkish Lira (TRY)"
    }
    
    # Tabs for different management features
    tab1, tab2, tab3, tab4 = st.tabs(["Add Expense", "Add Budget", "Import Expenses", "Import Budgets"])
    
    # Tab 1: Add New Expense
    with tab1:
        st.markdown('''
        <div class="section-container">
            <div class="section-header">
                Add New Expense
            </div>
        ''', unsafe_allow_html=True)
        
        with st.form("add_expense_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                expense_date = st.date_input("Date", datetime.now())
                amount = st.number_input("Amount", min_value=0.01, step=0.01)
                currency = st.selectbox("Currency", options=list(currency_options.keys()), 
                                      format_func=lambda x: currency_options[x])
                vendor = st.text_input("Vendor")
            
            with col2:
                description = st.text_input("Description")
                department = st.selectbox("Department", [
                    "Engineering", "Marketing", "Sales", "HR", "Finance", "Operations", "Executive"
                ])
                category = st.selectbox("Category", [
                    "IT Infrastructure", "Marketing", "Travel", "Office Supplies", 
                    "Personnel", "Utilities", "Professional Services", "Training", 
                    "Equipment", "Other"
                ])
            
            if st.form_submit_button("Add Expense", use_container_width=True):
                expense_data = {
                    "date": expense_date.strftime("%Y-%m-%d"),
                    "amount": amount,
                    "currency": currency,
                    "vendor": vendor,
                    "description": description,
                    "department": department,
                    "category": category
                }
                
                result = call_api("/expenses", "POST", expense_data)
                
                if result:
                    st.markdown('''
                    <div class="success-box">
                        <strong>SUCCESS:</strong> Expense added successfully!
                    </div>
                    ''', unsafe_allow_html=True)
                    st.cache_data.clear()
                else:
                    st.markdown('''
                    <div class="alert-box alert-high">
                        <strong>ERROR:</strong> Failed to add expense
                    </div>
                    ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: Add New Budget
    with tab2:
        st.markdown('''
        <div class="section-container">
            <div class="section-header">
                Add New Budget
            </div>
        ''', unsafe_allow_html=True)
        
        with st.form("add_budget_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                budget_department = st.selectbox("Department", [
                    "Engineering", "Marketing", "Sales", "HR", "Finance", "Operations", "Executive"
                ], key="budget_dept")
                budget_category = st.selectbox("Category", [
                    "IT Infrastructure", "Marketing", "Travel", "Office Supplies", 
                    "Personnel", "Utilities", "Professional Services", "Training", 
                    "Equipment", "Other"
                ], key="budget_cat")
            
            with col2:
                period_start = st.date_input("Period Start", datetime.now().replace(day=1))
                period_end = st.date_input("Period End", datetime.now().replace(day=28))
                allocated_amount = st.number_input("Allocated Amount", min_value=0.01, step=0.01)
                budget_currency = st.selectbox("Currency", options=list(currency_options.keys()), 
                                             format_func=lambda x: currency_options[x], key="budget_currency")
            
            if st.form_submit_button("Add Budget", use_container_width=True):
                budget_data = {
                    "department": budget_department,
                    "category": budget_category,
                    "period_start": period_start.strftime("%Y-%m-%d"),
                    "period_end": period_end.strftime("%Y-%m-%d"),
                    "allocated_amount": allocated_amount,
                    "currency": budget_currency
                }
                
                result = call_api("/budgets", "POST", budget_data)
                
                if result:
                    st.markdown('''
                    <div class="success-box">
                        <strong>SUCCESS:</strong> Budget added successfully!
                    </div>
                    ''', unsafe_allow_html=True)
                    st.cache_data.clear()
                else:
                    st.markdown('''
                    <div class="alert-box alert-high">
                        <strong>ERROR:</strong> Failed to add budget
                    </div>
                    ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 3: Import Expenses CSV
    with tab3:
        st.markdown('''
        <div class="section-container">
            <div class="section-header">
                Import Expenses from CSV
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="alert-box alert-low">
            <strong>CSV FORMAT:</strong> Your CSV should include columns: date, amount, currency, vendor, description, department, category<br>
            <strong>EXAMPLE:</strong> 2024-01-15, 150.00, USD, Microsoft, Azure subscription, Engineering, IT Infrastructure
        </div>
        ''', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            expense_file = st.file_uploader("Choose CSV file", type="csv", key="expense_csv")
        
        with col2:
            default_expense_currency = st.selectbox("Default Currency", 
                                                   options=list(currency_options.keys()),
                                                   format_func=lambda x: currency_options[x],
                                                   key="default_exp_currency")
        
        if expense_file is not None and st.button("Import Expenses", use_container_width=True):
            with st.spinner("Importing expenses..."):
                files = {"file": expense_file}
                data = {"default_currency": default_expense_currency}
                
                try:
                    import requests
                    response = requests.post(f"{API_BASE_URL}/expenses/import", files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            st.markdown(f'''
                            <div class="success-box">
                                <strong>SUCCESS:</strong> {result.get("message", "Import completed")}<br>
                                <strong>RECORDS PROCESSED:</strong> {result.get("records_processed", 0)}
                            </div>
                            ''', unsafe_allow_html=True)
                            st.cache_data.clear()
                        else:
                            st.markdown(f'''
                            <div class="alert-box alert-high">
                                <strong>ERROR:</strong> {result.get("message", "Import failed")}
                            </div>
                            ''', unsafe_allow_html=True)
                            if result.get("errors"):
                                with st.expander("View Errors"):
                                    for error in result["errors"]:
                                        st.write(f"• {error}")
                    else:
                        st.markdown('''
                        <div class="alert-box alert-high">
                            <strong>ERROR:</strong> Failed to upload file
                        </div>
                        ''', unsafe_allow_html=True)
                        
                except Exception as e:
                    st.markdown(f'''
                    <div class="alert-box alert-high">
                        <strong>ERROR:</strong> {str(e)}
                    </div>
                    ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 4: Import Budgets CSV
    with tab4:
        st.markdown('''
        <div class="section-container">
            <div class="section-header">
                Import Budgets from CSV
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="alert-box alert-low">
            <strong>CSV FORMAT:</strong> Your CSV should include columns: department, category, period_start, period_end, allocated_amount, currency<br>
            <strong>EXAMPLE:</strong> Engineering, IT Infrastructure, 2024-01-01, 2024-01-31, 50000.00, USD
        </div>
        ''', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            budget_file = st.file_uploader("Choose CSV file", type="csv", key="budget_csv")
        
        with col2:
            default_budget_currency = st.selectbox("Default Currency", 
                                                  options=list(currency_options.keys()),
                                                  format_func=lambda x: currency_options[x],
                                                  key="default_bud_currency")
        
        if budget_file is not None and st.button("Import Budgets", use_container_width=True):
            with st.spinner("Importing budgets..."):
                files = {"file": budget_file}
                data = {"default_currency": default_budget_currency}
                
                try:
                    import requests
                    response = requests.post(f"{API_BASE_URL}/budgets/import", files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            st.markdown(f'''
                            <div class="success-box">
                                <strong>SUCCESS:</strong> {result.get("message", "Import completed")}<br>
                                <strong>RECORDS PROCESSED:</strong> {result.get("records_processed", 0)}
                            </div>
                            ''', unsafe_allow_html=True)
                            st.cache_data.clear()
                        else:
                            st.markdown(f'''
                            <div class="alert-box alert-high">
                                <strong>ERROR:</strong> {result.get("message", "Import failed")}
                            </div>
                            ''', unsafe_allow_html=True)
                            if result.get("errors"):
                                with st.expander("View Errors"):
                                    for error in result["errors"]:
                                        st.write(f"• {error}")
                    else:
                        st.markdown('''
                        <div class="alert-box alert-high">
                            <strong>ERROR:</strong> Failed to upload file
                        </div>
                        ''', unsafe_allow_html=True)
                        
                except Exception as e:
                    st.markdown(f'''
                    <div class="alert-box alert-high">
                        <strong>ERROR:</strong> {str(e)}
                    </div>
                    ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_download_data_page():
    """Display comprehensive data download features with filtering and preview."""
    st.markdown('''
    <div class="main-header">
        <h1>Download Data</h1>
        <p>Export your financial data with advanced filtering options</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize session state for filters
    if 'download_filters' not in st.session_state:
        st.session_state.download_filters = {}
    
    # Main container
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">DOWNLOAD</span>Data Export Center
        </div>
    ''', unsafe_allow_html=True)
    
    # Step 1: Data Type Selection
    st.markdown("### Step 1: Select Data Type")
    data_type = st.radio(
        "What data would you like to download?",
        ["Expenses Only", "Budgets Only", "Combined Report"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Step 2: Filter Options
    st.markdown("### Step 2: Filter Your Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Date Filters**")
        date_filter_type = st.selectbox(
            "Date Range",
            ["All Time", "Last 30 Days", "Last 3 Months", "This Year", "Custom Range"]
        )
        
        start_date = None
        end_date = None
        if date_filter_type == "Custom Range":
            start_date = st.date_input("From Date")
            end_date = st.date_input("To Date")
        elif date_filter_type == "Last 30 Days":
            from datetime import datetime, timedelta
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        elif date_filter_type == "Last 3 Months":
            from datetime import datetime, timedelta
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=90)
        elif date_filter_type == "This Year":
            from datetime import datetime
            end_date = datetime.now().date()
            start_date = datetime(datetime.now().year, 1, 1).date()
    
    with col2:
        st.markdown("**Currency & Location**")
        
        # Currency filter
        currency_options = {
            "ALL": "All Currencies",
            "USD": "US Dollar (USD)",
            "INR": "Indian Rupee (INR)", 
            "CAD": "Canadian Dollar (CAD)",
            "TRY": "Turkish Lira (TRY)"
        }
        
        selected_currencies = st.multiselect(
            "Currencies",
            options=list(currency_options.keys()),
            default=["ALL"],
            format_func=lambda x: currency_options[x]
        )
        
        # Department filter
        departments = [
            "All Departments", "Engineering", "Marketing", "Sales", 
            "Operations", "HR", "Finance", "Legal"
        ]
        selected_departments = st.multiselect(
            "Departments",
            options=departments,
            default=["All Departments"]
        )
        
        # Category filter
        categories = [
            "All Categories", "Software & Tools", "Marketing & Advertising",
            "Travel & Transport", "Office Supplies", "Equipment & Hardware",
            "Professional Services", "Utilities & Internet", "Training & Education",
            "Entertainment & Events", "Other"
        ]
        selected_categories = st.multiselect(
            "Categories", 
            options=categories,
            default=["All Categories"]
        )
    
    with col3:
        st.markdown("**Amount & Advanced**")
        
        # Amount range
        use_amount_filter = st.checkbox("Filter by Amount Range")
        min_amount = None
        max_amount = None
        
        if use_amount_filter:
            amount_range = st.slider(
                "Amount Range",
                min_value=0,
                max_value=10000,
                value=(0, 10000),
                step=50
            )
            min_amount = amount_range[0] if amount_range[0] > 0 else None
            max_amount = amount_range[1] if amount_range[1] < 10000 else None
        
        # Vendor filter
        vendor_filter = st.text_input("Vendor Contains (optional)", placeholder="e.g., Microsoft, Amazon")
        
        # Recurring filter (for expenses)
        if data_type == "Expenses Only":
            recurring_filter = st.selectbox(
                "Expense Type",
                ["All Expenses", "Recurring Only", "One-time Only"]
            )
    
    st.markdown("---")
    
    # Step 3: Preview & Format Selection
    st.markdown("### Step 3: Preview & Download")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Preview button
        if st.button("Preview Data", use_container_width=True):
            with st.spinner("Loading preview..."):
                try:
                    # Build API parameters
                    params = {}
                    
                    # Add currency filter
                    if "ALL" not in selected_currencies and selected_currencies:
                        if len(selected_currencies) == 1:
                            params['currency'] = selected_currencies[0]
                    
                    # Add department filter
                    if "All Departments" not in selected_departments and selected_departments:
                        if len(selected_departments) == 1:
                            params['department'] = selected_departments[0]
                    
                    # Add category filter  
                    if "All Categories" not in selected_categories and selected_categories:
                        if len(selected_categories) == 1:
                            params['category'] = selected_categories[0]
                    
                    # Add date filters
                    if start_date:
                        params['start_date'] = start_date.strftime('%Y-%m-%d')
                    if end_date:
                        params['end_date'] = end_date.strftime('%Y-%m-%d')
                    
                    # Add amount filters
                    if min_amount:
                        params['min_amount'] = min_amount
                    if max_amount:
                        params['max_amount'] = max_amount
                    
                    # Add vendor filter
                    if vendor_filter:
                        params['vendor'] = vendor_filter
                    
                    # Add recurring filter
                    if data_type == "Expenses Only" and recurring_filter != "All Expenses":
                        params['is_recurring'] = recurring_filter == "Recurring Only"
                    
                    # Make API call for preview
                    if data_type == "Expenses Only":
                        response = requests.get(f"{API_BASE_URL}/expenses", 
                                              params={**params, 'limit': 10})
                    elif data_type == "Budgets Only":
                        response = requests.get(f"{API_BASE_URL}/budgets", 
                                              params={**params, 'limit': 10})
                    else:  # Combined
                        # For combined, we'll get both
                        exp_response = requests.get(f"{API_BASE_URL}/expenses", 
                                                  params={**params, 'limit': 5})
                        bud_response = requests.get(f"{API_BASE_URL}/budgets", 
                                                  params={**params, 'limit': 5})
                    
                    if data_type != "Combined Report":
                        if response.status_code == 200:
                            data = response.json()
                            if data:
                                st.success(f"Found {len(data)} records matching your criteria")
                                
                                # Show preview table
                                st.markdown("**Preview (First 10 records):**")
                                df = pd.DataFrame(data)
                                st.dataframe(df, use_container_width=True)
                                
                                # Store preview data for download
                                st.session_state.preview_data = data
                                st.session_state.preview_params = params
                                
                            else:
                                st.warning("No data found matching your criteria. Try adjusting your filters.")
                        else:
                            st.error(f"Failed to load preview: {response.status_code}")
                    else:
                        # Handle combined preview
                        if exp_response.status_code == 200 and bud_response.status_code == 200:
                            exp_data = exp_response.json()
                            bud_data = bud_response.json()
                            
                            st.success(f"Found {len(exp_data)} expenses and {len(bud_data)} budgets")
                            
                            if exp_data:
                                st.markdown("**Expenses Preview:**")
                                df_exp = pd.DataFrame(exp_data)
                                st.dataframe(df_exp, use_container_width=True)
                            
                            if bud_data:
                                st.markdown("**Budgets Preview:**")
                                df_bud = pd.DataFrame(bud_data)
                                st.dataframe(df_bud, use_container_width=True)
                            
                            st.session_state.preview_params = params
                        
                except Exception as e:
                    st.error(f"Preview error: {str(e)}")
    
    with col2:
        st.markdown("**Export Format**")
        export_format = st.selectbox(
            "File Format",
            ["CSV", "Excel", "JSON"],
            help="CSV: Universal compatibility, Excel: Formatted sheets, JSON: API/Development use"
        )
        
        # Custom filename
        custom_filename = st.text_input(
            "Custom Filename (optional)",
            placeholder="my_budget_data"
        )
    
    # Download button
    st.markdown("---")
    
    download_col1, download_col2, download_col3 = st.columns([1, 2, 1])
    
    with download_col2:
        if st.button("Download Data", use_container_width=True, type="primary"):
            with st.spinner("Preparing your download..."):
                try:
                    # Build download parameters
                    download_params = st.session_state.get('preview_params', {})
                    download_params['format'] = export_format.lower()
                    
                    # Generate filename
                    if custom_filename:
                        filename_base = custom_filename
                    else:
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename_base = f"{data_type.lower().replace(' ', '_')}_{timestamp}"
                    
                    # Make download API call
                    if data_type == "Expenses Only":
                        download_url = f"{API_BASE_URL}/export/expenses"
                    elif data_type == "Budgets Only":
                        download_url = f"{API_BASE_URL}/export/budgets"
                    else:
                        download_url = f"{API_BASE_URL}/export/combined"
                    
                    download_response = requests.get(download_url, params=download_params)
                    
                    if download_response.status_code == 200:
                        # Set MIME type based on format
                        if export_format == "CSV":
                            mime_type = "text/csv"
                            file_ext = ".csv"
                        elif export_format == "Excel":
                            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            file_ext = ".xlsx"
                        else:  # JSON
                            mime_type = "application/json"
                            file_ext = ".json"
                        
                        # Provide download
                        st.download_button(
                            label=f"Click to Download {export_format} File",
                            data=download_response.content,
                            file_name=f"{filename_base}{file_ext}",
                            mime=mime_type,
                            use_container_width=True
                        )
                        
                        st.success(f"{export_format} file prepared successfully!")
                        
                        # Show download info
                        file_size = len(download_response.content)
                        if file_size > 1024*1024:
                            size_str = f"{file_size/(1024*1024):.1f} MB"
                        elif file_size > 1024:
                            size_str = f"{file_size/1024:.1f} KB"
                        else:
                            size_str = f"{file_size} bytes"
                        
                        st.info(f"File size: {size_str}")
                        
                    else:
                        st.error(f"Download failed: {download_response.status_code}")
                        if download_response.text:
                            st.error(f"Error details: {download_response.text}")
                        
                except Exception as e:
                    st.error(f"Download error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tips section
    st.markdown('''
    <div class="section-container">
        <div class="section-header">
            <span class="icon">TIP</span>Download Tips
        </div>
        <div class="alert-box alert-low">
            <strong>Pro Tips:</strong><br>
            • Use <strong>CSV</strong> for universal compatibility with Excel, Google Sheets<br>
            • Use <strong>Excel</strong> for formatted reports with multiple sheets (Combined Report)<br>
            • Use <strong>JSON</strong> for API integration or custom data processing<br>
            • Filter by currency to get region-specific reports<br>
            • Use date ranges for quarterly or annual reports<br>
            • Custom filenames help organize your downloads
        </div>
    </div>
    ''', unsafe_allow_html=True)

# Main App
def main():
    """Main dashboard application."""
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Overview"
    
    # Professional Sidebar navigation
    st.sidebar.markdown('''
    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); 
                padding: 1.5rem; margin: -1rem -1rem 2rem -1rem; border-radius: 0 0 12px 12px;">
        <h2 style="color: white; margin: 0; text-align: center; font-size: 1.4rem;">NAVIGATION</h2>
    </div>
    ''', unsafe_allow_html=True)
    
    pages = {
        "Overview": "Dashboard Overview",
        "Analytics": "Analytics & Charts", 
        "Expense Classification": "Expense Classification",
        "Forecasting": "Budget Forecasting",
        "Anomaly Detection": "Anomaly Alerts",
        "Data Management": "Data Management",
        "Download Data": "Download Data"
    }
    
    # Page selection
    for page_key, page_name in pages.items():
        if st.sidebar.button(page_name, use_container_width=True):
            st.session_state.page = page_key
            st.rerun()
    
    # API Status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown('''
    <div style="background: rgba(30, 41, 59, 0.8); padding: 1rem; border-radius: 8px; margin: 1rem 0; 
                border: 1px solid rgba(59, 130, 246, 0.2); box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h4 style="color: #e2e8f0; margin: 0 0 0.5rem 0;">SYSTEM STATUS</h4>
    </div>
    ''', unsafe_allow_html=True)
    
    if check_api_health():
        st.sidebar.markdown('''
        <div style="background: rgba(16, 185, 129, 0.1); padding: 0.75rem; border-radius: 6px; 
                    border: 1px solid #10b981; color: #6ee7b7; font-weight: 500;">
            STATUS: API Backend Online
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('''
        <div style="background: rgba(239, 68, 68, 0.1); padding: 0.75rem; border-radius: 6px; 
                    border: 1px solid #ef4444; color: #fca5a5; font-weight: 500;">
            STATUS: API Backend Offline<br>
            <small>Start with: py -m uvicorn src.api.main:app --reload --port 8000</small>
        </div>
        ''', unsafe_allow_html=True)
    
    # Display selected page
    if st.session_state.page == "Overview":
        show_overview_page()
    elif st.session_state.page == "Analytics":
        show_analytics_page()
    elif st.session_state.page == "Expense Classification":
        show_ml_features_page()
    elif st.session_state.page == "Forecasting":
        show_forecasting_page()
    elif st.session_state.page == "Anomaly Detection":
        show_anomaly_detection_page()
    elif st.session_state.page == "Data Management":
        show_data_management_page()
    elif st.session_state.page == "Download Data":
        show_download_data_page()

if __name__ == "__main__":
    main() 