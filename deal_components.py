import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

class DealCard:
    """Component for displaying individual deal cards"""
    
    @staticmethod
    def format_currency(amount):
        """Format currency values"""
        if pd.isna(amount) or amount == 0:
            return "$0"
        return f"${amount:,.0f}"
    
    @staticmethod
    def get_status_color(status):
        """Get color for status badges"""
        colors = {
            'Open': '#28a745',
            'Due Diligence': '#ffc107',
            'Closed': '#dc3545'
        }
        return colors.get(status, '#6c757d')
    
    @staticmethod
    def create_progress_chart(raised, target):
        """Create a progress chart using Plotly"""
        progress = (raised / target) * 100 if target > 0 else 0
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = progress,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Funding Progress"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 100], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=200,
            margin=dict(l=0, r=0, t=30, b=0),
            font={'size': 12}
        )
        
        return fig
    
    @classmethod
    def render(cls, deal, show_progress_chart=False):
        """Render a deal card"""
        # Calculate progress
        progress = (deal['raised_amount'] / deal['target_amount']) * 100 if deal['target_amount'] > 0 else 0
        
        # Create container with custom styling
        with st.container():
            # Card header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {deal['title']}")
            with col2:
                status_color = cls.get_status_color(deal['status'])
                st.markdown(f"""
                <div style="
                    background-color: {status_color};
                    color: white;
                    padding: 5px 10px;
                    border-radius: 15px;
                    text-align: center;
                    font-size: 12px;
                    font-weight: bold;
                    margin-top: 10px;
                ">{deal['status']}</div>
                """, unsafe_allow_html=True)
            
            # Description
            st.write(deal['description'])
            
            # Deal details in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Financial Details**")
                st.write(f"• **Industry:** {deal['industry']}")
                st.write(f"• **Target:** {cls.format_currency(deal['target_amount'])}")
                st.write(f"• **Raised:** {cls.format_currency(deal['raised_amount'])}")
            
            with col2:
                st.markdown("**💰 Investment Info**")
                st.write(f"• **Min Investment:** {cls.format_currency(deal['min_investment'])}")
                
                if pd.notna(deal['due_date']):
                    try:
                        due_date = pd.to_datetime(deal['due_date']).strftime('%B %d, %Y')
                        st.write(f"• **Due Date:** {due_date}")
                    except:
                        st.write(f"• **Due Date:** {deal['due_date']}")
                
                # Progress percentage
                st.write(f"• **Progress:** {progress:.1f}% raised")
            
            # Progress visualization
            if deal['status'] != 'Closed':
                if show_progress_chart:
                    # Show interactive chart
                    fig = cls.create_progress_chart(deal['raised_amount'], deal['target_amount'])
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Show simple progress bar
                    st.progress(min(progress / 100, 1.0))
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if pd.notna(deal['documents_link']) and deal['documents_link'] != '#':
                    st.link_button("📄 View Documents", deal['documents_link'], use_container_width=True)
                else:
                    st.button("📄 View Documents", disabled=True, help="Document link not available", use_container_width=True)
            
            with col2:
                if deal['status'] == 'Open':
                    if st.button("💼 Express Interest", key=f"interest_{deal.get('id', hash(deal['title']))}", use_container_width=True):
                        st.success("Interest registered! Someone will contact you soon.")
                else:
                    st.button("💼 Express Interest", disabled=True, help=f"Deal is {deal['status']}", use_container_width=True)
            
            # Add some spacing
            st.markdown("---")

class DealMetrics:
    """Component for displaying deal metrics and analytics"""
    
    @staticmethod
    def render_summary_metrics(deals_df):
        """Render summary metrics for deals"""
        if deals_df.empty:
            st.info("No deals available for metrics.")
            return
        
        # Calculate metrics
        total_deals = len(deals_df)
        total_target = deals_df['target_amount'].sum()
        total_raised = deals_df['raised_amount'].sum()
        avg_progress = ((deals_df['raised_amount'] / deals_df['target_amount']) * 100).mean()
        open_deals = len(deals_df[deals_df['status'] == 'Open'])
        
        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Deals", total_deals)
        
        with col2:
            st.metric("Total Target", f"${total_target:,.0f}")
        
        with col3:
            st.metric("Total Raised", f"${total_raised:,.0f}")
        
        with col4:
            st.metric("Avg Progress", f"{avg_progress:.1f}%")
        
        with col5:
            st.metric("Open Deals", open_deals)
    
    @staticmethod
    def render_industry_breakdown(deals_df):
        """Render industry breakdown chart"""
        if deals_df.empty:
            return
        
        industry_counts = deals_df['industry'].value_counts()
        
        fig = go.Figure(data=[
            go.Bar(
                x=industry_counts.values,
                y=industry_counts.index,
                orientation='h',
                marker_color='lightblue'
            )
        ])
        
        fig.update_layout(
            title="Deals by Industry",
            xaxis_title="Number of Deals",
            yaxis_title="Industry",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_status_distribution(deals_df):
        """Render status distribution pie chart"""
        if deals_df.empty:
            return
        
        status_counts = deals_df['status'].value_counts()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.3
            )
        ])
        
        fig.update_layout(
            title="Deal Status Distribution",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
