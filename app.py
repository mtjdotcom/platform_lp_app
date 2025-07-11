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
    # Header
    st.title("🏢 Co-Investment Portal")
    st.markdown("Explore exclusive investment opportunities tailored for our valued partners.")
    
    # Initialize session state for data
    if 'deals_data' not in st.session_state:
        st.session_state.deals_data = None
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🔧 Controls")
        
        # Refresh button
        if st.button("🔄 Refresh Data", type="primary"):
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
                    st.success("✅ Data loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Error loading data: {str(e)}")
                    st.info("Please check your Google Sheets connection and permissions.")
                    # Create empty DataFrame to prevent slider errors
                    st.session_state.deals_data = pd.DataFrame()
        
        deals_df = st.session_state.deals_data
        
        if deals_df is None or deals_df.empty:
            st.warning("No deals data available. Please check your Google Sheet connection.")
            st.info("Make sure your Google Sheet has the following columns: Title, Description, Industry, Target Amount, Raised Amount, Status, Min Investment, Due Date, Documents Link")
            
            # Show sample data structure
            with st.expander("📋 Expected Google Sheet Structure"):
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
        st.header("🔍 Filters")
        
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
    st.header("📋 Investment Deals")
    
    # Display deals in a grid layout
    for i in range(0, len(filtered_df), 2):
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j < len(filtered_df):
                deal = filtered_df.iloc[i + j]
                with col:
                    display_deal_card(deal)

def display_deal_card(deal):
    """Display a single deal card"""
    # Calculate progress
    progress = (deal['raised_amount'] / deal['target_amount']) * 100 if deal['target_amount'] > 0 else 0
    
    # Create unique identifier for this deal card
    deal_id = f"{deal.name}_{hash(deal['title'])}" if 'title' in deal.index else f"{deal.name}_{hash(str(deal))}"
    
    # Create the card container
    with st.container():
        st.markdown(f"""
        <div style="
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
        """, unsafe_allow_html=True)
        
        # Title and status
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(deal['title'])
        with col2:
            status_color = get_status_color(deal['status'])
            st.markdown(f"""
            <div style="
                background-color: {status_color};
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                text-align: center;
                font-size: 12px;
                font-weight: bold;
            ">{deal['status']}</div>
            """, unsafe_allow_html=True)
        
        # Description
        st.write(deal['description'])
        
        # Details
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Industry:** {deal['industry']}")
            st.write(f"**Target Amount:** {format_currency(deal['target_amount'])}")
            st.write(f"**Raised Amount:** {format_currency(deal['raised_amount'])}")
        
        with col2:
            # Handle missing columns gracefully
            if 'min_investment' in deal.index:
                st.write(f"**Min Investment:** {format_currency(deal['min_investment'])}")
            
            if 'due_date' in deal.index and pd.notna(deal['due_date']):
                try:
                    due_date = pd.to_datetime(deal['due_date']).strftime('%B %d, %Y')
                    st.write(f"**Due Date:** {due_date}")
                except:
                    st.write(f"**Due Date:** {deal['due_date']}")
        
        # Progress bar (only for non-closed deals)
        if deal['status'] != 'Closed':
            st.write(f"**Progress:** {progress:.1f}% raised")
            st.progress(min(progress / 100, 1.0))
        
        # Action button
        if 'documents_link' in deal.index and pd.notna(deal['documents_link']) and deal['documents_link'] != '#':
            st.link_button("📄 View Details", deal['documents_link'], key=f"link_{deal_id}")
        else:
            st.button("📄 View Details", disabled=True, help="Document link not available", key=f"btn_{deal_id}")
        
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
