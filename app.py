import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from google_sheets_service import GoogleSheetsService
from deal_components import DealCard

# Page configuration
st.set_page_config(
    page_title="Co-Investment Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Google Sheets service
@st.cache_resource
def get_sheets_service():
    """Initialize and return Google Sheets service"""
    return GoogleSheetsService()

def format_currency(amount):
    """Format currency values"""
    if pd.isna(amount) or amount == 0:
        return "$0"
    return f"${amount:,.0f}"

def get_status_color(status):
    """Get color for status badges"""
    colors = {
        'Open': '#28a745',
        'Due Diligence': '#ffc107',
        'Closed': '#dc3545'
    }
    return colors.get(status, '#6c757d')

def main():
    # Custom CSS for Isomer Capital-inspired design
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #fafafa;
        color: #1a1a1a;
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 3rem 0;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.025em;
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 1rem 0 0 0;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* Sidebar Styles */
    .stSidebar {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    
    .stSidebar .stSelectbox > div > div {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
    
    .stSidebar .stTextInput > div > div {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
    
    /* Metrics Cards */
    .stMetric {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
    }
    
    .stMetric > div {
        color: #1f2937;
    }
    
    .stMetric [data-testid="metric-value"] {
        color: #1e40af;
        font-weight: 600;
    }
    
    /* Deal Cards */
    .deal-card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .deal-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .deal-title {
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        line-height: 1.3;
    }
    
    .deal-description {
        color: #6b7280;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    .deal-details {
        color: #374151;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .deal-details strong {
        color: #1f2937;
        font-weight: 600;
    }
    
    /* Status Badge */
    .status-open {
        background-color: #10b981;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        text-align: center;
        display: inline-block;
    }
    
    .status-due-diligence {
        background-color: #f59e0b;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        text-align: center;
        display: inline-block;
    }
    
    .status-closed {
        background-color: #ef4444;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        text-align: center;
        display: inline-block;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    
    .stLinkButton > a {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: inline-block;
    }
    
    .stLinkButton > a:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #1e40af 100%);
        border-radius: 10px;
        height: 8px;
    }
    
    .stProgress > div {
        background-color: #e5e7eb;
        border-radius: 10px;
        height: 8px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom spacing */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Section dividers */
    .stDivider {
        margin: 2rem 0;
        border-color: #e5e7eb;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .deal-card {
            padding: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Co-Investment Portal</h1>
        <p>Explore exclusive investment opportunities tailored for our valued partners</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for data
    if 'deals_data' not in st.session_state:
        st.session_state.deals_data = None
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None
    
    # Sidebar for controls
    with st.sidebar:
        st.markdown("### Portfolio Controls")
        
        # Refresh button
        if st.button("Refresh Data", type="primary"):
            st.session_state.deals_data = None
            st.session_state.last_refresh = datetime.now()
            st.rerun()
        
        if st.session_state.last_refresh:
            st.caption(f"Last refreshed: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        st.divider()
        
        # Load data
        if st.session_state.deals_data is None:
            with st.spinner("Loading deals from Google Sheets..."):
                try:
                    sheets_service = get_sheets_service()
                    st.session_state.deals_data = sheets_service.get_deals()
                    st.success("Data loaded successfully!")
                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")
                    st.info("Please check your Google Sheets connection and permissions.")
                    # Create empty DataFrame to prevent slider errors
                    st.session_state.deals_data = pd.DataFrame()
        
        deals_df = st.session_state.deals_data
        
        if deals_df is None or deals_df.empty:
            st.warning("No deals data available. Please check your Google Sheet connection.")
            st.info("Make sure your Google Sheet has the following columns: Title, Description, Industry, Target Amount, Raised Amount, Status, Min Investment, Due Date, Documents Link")
            
            # Show sample data structure
            with st.expander("Expected Google Sheet Structure"):
                st.markdown("""
                **Column Headers (first row of your Google Sheet):**
                - **Title**: Name of the investment deal
                - **Description**: Detailed description of the opportunity
                - **Industry**: Industry category (e.g., Technology, Real Estate, Healthcare)
                - **Target Amount**: Target funding amount (numbers only, e.g., 5000000)
                - **Raised Amount**: Amount already raised (numbers only, e.g., 3500000)
                - **Status**: Deal status (Open, Due Diligence, Closed)
                - **Min Investment**: Minimum investment amount (numbers only, e.g., 50000)
                - **Due Date**: Investment deadline (e.g., 2025-08-15)
                - **Documents Link**: Link to deal documents (optional)
                """)
            
            st.stop()
        
        # Filters
        st.markdown("### Investment Filters")
        
        # Search
        search_term = st.text_input("Search deals:", placeholder="Enter title or description...")
        
        # Industry filter
        industries = ['All'] + sorted(deals_df['industry'].unique().tolist())
        selected_industry = st.selectbox("Industry:", industries)
        
        # Status filter
        statuses = ['All'] + sorted(deals_df['status'].unique().tolist())
        selected_status = st.selectbox("Status:", statuses)
        
        # Amount range filter
        if not deals_df['target_amount'].isna().all() and deals_df['target_amount'].max() > 0:
            min_amount = int(deals_df['target_amount'].min())
            max_amount = int(deals_df['target_amount'].max())
            
            # Ensure min_amount is less than max_amount
            if min_amount >= max_amount:
                max_amount = min_amount + 1000000  # Add 1M as buffer
            
            amount_range = st.slider(
                "Target Amount Range:",
                min_value=min_amount,
                max_value=max_amount,
                value=(min_amount, max_amount),
                format="$%d"
            )
        else:
            amount_range = None
    
    # Apply filters
    filtered_df = deals_df.copy()
    
    # Search filter
    if search_term:
        mask = (
            filtered_df['title'].str.contains(search_term, case=False, na=False) |
            filtered_df['description'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Industry filter
    if selected_industry != 'All':
        filtered_df = filtered_df[filtered_df['industry'] == selected_industry]
    
    # Status filter
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    
    # Amount range filter
    if amount_range:
        filtered_df = filtered_df[
            (filtered_df['target_amount'] >= amount_range[0]) &
            (filtered_df['target_amount'] <= amount_range[1])
        ]
    
    # Main content area
    if filtered_df.empty:
        st.info("🔍 No deals found matching your criteria. Try adjusting your filters.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Deals", len(filtered_df))
    
    with col2:
        total_target = filtered_df['target_amount'].sum()
        st.metric("Total Target", format_currency(total_target))
    
    with col3:
        total_raised = filtered_df['raised_amount'].sum()
        st.metric("Total Raised", format_currency(total_raised))
    
    with col4:
        open_deals = len(filtered_df[filtered_df['status'] == 'Open'])
        st.metric("Open Deals", open_deals)
    
    st.divider()
    
    # Deal cards
    st.markdown("### Investment Opportunities")
    
    # Display deals in a single column layout for better readability
    for i in range(len(filtered_df)):
        deal = filtered_df.iloc[i]
        display_deal_card(deal)

def display_deal_card(deal):
    """Display a single deal card"""
    # Calculate progress
    progress = (deal['raised_amount'] / deal['target_amount']) * 100 if deal['target_amount'] > 0 else 0
    
    # Create unique identifier for this deal card
    deal_id = f"{deal.name}_{hash(deal['title'])}" if 'title' in deal.index else f"{deal.name}_{hash(str(deal))}"
    
    # Create the card container with custom styling
    st.markdown('<div class="deal-card">', unsafe_allow_html=True)
    
    # Status badge CSS class
    status_class = f"status-{deal['status'].lower().replace(' ', '-')}"
    
    # Deal card HTML with custom styling
    min_investment_html = ""
    if 'min_investment' in deal.index:
        min_investment_html = f"<div class='deal-details'><strong>Min Investment:</strong> {format_currency(deal['min_investment'])}</div>"
    
    due_date_html = ""
    if 'due_date' in deal.index and pd.notna(deal['due_date']):
        try:
            due_date = pd.to_datetime(deal['due_date']).strftime('%B %d, %Y')
            due_date_html = f"<div class='deal-details'><strong>Due Date:</strong> {due_date}</div>"
        except:
            due_date_html = f"<div class='deal-details'><strong>Due Date:</strong> {deal['due_date']}</div>"
    
    progress_html = ""
    if deal['status'] != 'Closed':
        progress_html = f"<div class='deal-details'><strong>Progress:</strong> {progress:.1f}% raised</div>"
    
    # Title and status row
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f'<h3 class="deal-title">{deal["title"]}</h3>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<span class="{status_class}">{deal["status"]}</span>', unsafe_allow_html=True)
    
    # Description
    st.markdown(f'<div class="deal-description">{deal["description"]}</div>', unsafe_allow_html=True)
    
    # Details in two columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="deal-details"><strong>Industry:</strong> {deal["industry"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="deal-details"><strong>Target Amount:</strong> {format_currency(deal["target_amount"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="deal-details"><strong>Raised Amount:</strong> {format_currency(deal["raised_amount"])}</div>', unsafe_allow_html=True)
    
    with col2:
        if min_investment_html:
            st.markdown(min_investment_html, unsafe_allow_html=True)
        if due_date_html:
            st.markdown(due_date_html, unsafe_allow_html=True)
        if progress_html:
            st.markdown(progress_html, unsafe_allow_html=True)
    
    # Progress bar (only for non-closed deals)
    if deal['status'] != 'Closed':
        st.progress(min(progress / 100, 1.0))
    
    # Action button
    if 'documents_link' in deal.index and pd.notna(deal['documents_link']) and deal['documents_link'] != '#':
        st.link_button("View Details", deal['documents_link'], key=f"link_{deal_id}")
    else:
        st.button("View Details", disabled=True, help="Document link not available", key=f"btn_{deal_id}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

if __name__ == "__main__":
    main()
