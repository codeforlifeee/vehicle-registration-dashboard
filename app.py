
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date
import json

# Page configuration
st.set_page_config(
    page_title="Vehicle Registration Analytics Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

class VehicleDataProcessor:
    def __init__(self):
        self.data = self.generate_sample_data()

    def generate_sample_data(self):
        """Generate sample vehicle registration data"""
        np.random.seed(42)

        states = ['Maharashtra', 'Gujarat', 'Tamil Nadu', 'Karnataka', 'Delhi', 'Uttar Pradesh']
        categories = ['2-Wheeler', '3-Wheeler', '4-Wheeler', 'Commercial Vehicle']
        manufacturers = ['Hero MotoCorp', 'Honda Motorcycle', 'Maruti Suzuki', 'Bajaj Auto', 
                        'TVS Motor', 'Tata Motors', 'Hyundai', 'Mahindra']
        years = [2021, 2022, 2023, 2024]
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']

        data = []
        for year in years:
            for quarter in quarters:
                for state in states:
                    for category in categories:
                        for manufacturer in manufacturers:
                            if np.random.random() > 0.7:  # Not all combinations exist
                                continue

                            base_registrations = np.random.randint(10000, 200000)
                            yoy_growth = np.random.normal(8, 15)  # 8% average with 15% std dev
                            qoq_growth = np.random.normal(2, 8)   # 2% average with 8% std dev

                            data.append({
                                'year': year,
                                'quarter': quarter,
                                'state': state,
                                'category': category,
                                'manufacturer': manufacturer,
                                'registrations': base_registrations,
                                'yoy_growth': yoy_growth,
                                'qoq_growth': qoq_growth,
                                'date_period': f"{year}-{quarter}"
                            })

        return pd.DataFrame(data)

    def calculate_summary_metrics(self, df):
        """Calculate key summary metrics"""
        total_registrations = df['registrations'].sum()
        avg_yoy_growth = df['yoy_growth'].mean()
        avg_qoq_growth = df['qoq_growth'].mean()

        top_category = df.groupby('category')['registrations'].sum().idxmax()
        top_manufacturer = df.groupby('manufacturer')['registrations'].sum().idxmax()
        top_state = df.groupby('state')['registrations'].sum().idxmax()

        return {
            'total_registrations': total_registrations,
            'avg_yoy_growth': avg_yoy_growth,
            'avg_qoq_growth': avg_qoq_growth,
            'top_category': top_category,
            'top_manufacturer': top_manufacturer,
            'top_state': top_state
        }

@st.cache_data
def load_vehicle_data():
    """Load and cache vehicle data"""
    processor = VehicleDataProcessor()
    return processor.data

def create_sidebar_filters(df):
    """Create sidebar filters"""
    st.sidebar.header("🔍 Data Filters")

    # Year filter
    years = sorted(df['year'].unique())
    selected_years = st.sidebar.multiselect(
        "Select Years",
        options=years,
        default=years
    )

    # State filter
    states = sorted(df['state'].unique())
    selected_states = st.sidebar.multiselect(
        "Select States",
        options=states,
        default=states[:3]  # Default to first 3 states
    )

    # Category filter
    categories = sorted(df['category'].unique())
    selected_categories = st.sidebar.multiselect(
        "Select Vehicle Categories",
        options=categories,
        default=categories
    )

    # Manufacturer filter
    manufacturers = sorted(df['manufacturer'].unique())
    selected_manufacturers = st.sidebar.multiselect(
        "Select Manufacturers",
        options=manufacturers,
        default=manufacturers[:5]  # Default to first 5 manufacturers
    )

    return {
        'years': selected_years,
        'states': selected_states,
        'categories': selected_categories,
        'manufacturers': selected_manufacturers
    }

def filter_dataframe(df, filters):
    """Apply filters to dataframe"""
    filtered_df = df[
        (df['year'].isin(filters['years'])) &
        (df['state'].isin(filters['states'])) &
        (df['category'].isin(filters['categories'])) &
        (df['manufacturer'].isin(filters['manufacturers']))
    ]
    return filtered_df

def display_metrics(df):
    """Display key metrics"""
    processor = VehicleDataProcessor()
    metrics = processor.calculate_summary_metrics(df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_registrations']:,}</div>
            <div class="metric-label">Total Registrations</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['avg_yoy_growth']:.1f}%</div>
            <div class="metric-label">Avg YoY Growth</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['avg_qoq_growth']:.1f}%</div>
            <div class="metric-label">Avg QoQ Growth</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['top_category']}</div>
            <div class="metric-label">Top Category</div>
        </div>
        """, unsafe_allow_html=True)

def create_yoy_trend_chart(df):
    """Create YoY trend chart"""
    # Aggregate data by year and category
    yoy_data = df.groupby(['year', 'category'])['registrations'].sum().reset_index()

    fig = px.line(
        yoy_data,
        x='year',
        y='registrations',
        color='category',
        title="📈 Vehicle Registrations by Category (YoY Trend)",
        labels={'registrations': 'Number of Registrations', 'year': 'Year'},
        markers=True
    )

    fig.update_layout(
        height=500,
        title_font_size=18,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14
    )

    return fig

def create_qoq_growth_chart(df):
    """Create QoQ growth chart"""
    qoq_data = df.groupby(['year', 'quarter'])['qoq_growth'].mean().reset_index()
    qoq_data['period'] = qoq_data['year'].astype(str) + '-' + qoq_data['quarter']

    fig = px.bar(
        qoq_data,
        x='period',
        y='qoq_growth',
        title="📊 Quarter-over-Quarter Growth Rate",
        labels={'qoq_growth': 'QoQ Growth (%)', 'period': 'Period'},
        color='qoq_growth',
        color_continuous_scale='RdYlGn'
    )

    fig.update_layout(
        height=500,
        title_font_size=18,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14
    )

    return fig

def create_manufacturer_pie_chart(df):
    """Create manufacturer market share pie chart"""
    manufacturer_data = df.groupby('manufacturer')['registrations'].sum().sort_values(ascending=False)

    # Take top 8 manufacturers and group rest as 'Others'
    top_manufacturers = manufacturer_data.head(8)
    others_sum = manufacturer_data.tail(-8).sum()

    if others_sum > 0:
        top_manufacturers['Others'] = others_sum

    fig = px.pie(
        values=top_manufacturers.values,
        names=top_manufacturers.index,
        title="🏭 Market Share by Manufacturer",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=500,
        title_font_size=18
    )

    return fig

def create_state_wise_chart(df):
    """Create state-wise registration chart"""
    state_data = df.groupby('state')['registrations'].sum().sort_values(ascending=True)

    fig = px.bar(
        x=state_data.values,
        y=state_data.index,
        orientation='h',
        title="🗺️ State-wise Vehicle Registrations",
        labels={'x': 'Number of Registrations', 'y': 'State'},
        color=state_data.values,
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        height=500,
        title_font_size=18,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14
    )

    return fig

def main():
    """Main dashboard function"""
    # Header
    st.markdown('<h1 class="main-header">🚗 Vehicle Registration Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("**Comprehensive insights into vehicle registration trends across India**")
    st.markdown("---")

    # Load data
    df = load_vehicle_data()

    # Create filters
    filters = create_sidebar_filters(df)

    # Apply filters
    filtered_df = filter_dataframe(df, filters)

    if filtered_df.empty:
        st.error("No data available for the selected filters. Please adjust your selection.")
        return

    # Display metrics
    display_metrics(filtered_df)
    st.markdown("---")

    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 YoY Trends", "📉 QoQ Analysis", "🏭 Manufacturers", "📋 Data Table"])

    with tab1:
        st.subheader("Dashboard Overview")
        col1, col2 = st.columns(2)

        with col1:
            fig_pie = create_manufacturer_pie_chart(filtered_df)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            fig_state = create_state_wise_chart(filtered_df)
            st.plotly_chart(fig_state, use_container_width=True)

    with tab2:
        st.subheader("Year-over-Year Trends")
        fig_yoy = create_yoy_trend_chart(filtered_df)
        st.plotly_chart(fig_yoy, use_container_width=True)

        # YoY growth by category
        st.subheader("YoY Growth Rate by Category")
        category_yoy = filtered_df.groupby('category')['yoy_growth'].mean().sort_values(ascending=False)

        fig_yoy_cat = px.bar(
            x=category_yoy.index,
            y=category_yoy.values,
            title="Average YoY Growth Rate by Vehicle Category",
            labels={'x': 'Vehicle Category', 'y': 'YoY Growth Rate (%)'},
            color=category_yoy.values,
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_yoy_cat, use_container_width=True)

    with tab3:
        st.subheader("Quarter-over-Quarter Analysis")
        fig_qoq = create_qoq_growth_chart(filtered_df)
        st.plotly_chart(fig_qoq, use_container_width=True)

        # QoQ insights
        st.subheader("QoQ Growth Insights")
        qoq_stats = filtered_df['qoq_growth'].describe()

        insight_col1, insight_col2, insight_col3 = st.columns(3)
        with insight_col1:
            st.metric("Max QoQ Growth", f"{qoq_stats['max']:.1f}%")
        with insight_col2:
            st.metric("Min QoQ Growth", f"{qoq_stats['min']:.1f}%")
        with insight_col3:
            st.metric("Median QoQ Growth", f"{qoq_stats['50%']:.1f}%")

    with tab4:
        st.subheader("Manufacturer Analysis")

        # Top 10 manufacturers
        top_manufacturers = filtered_df.groupby('manufacturer')['registrations'].sum().sort_values(ascending=False).head(10)

        fig_top_mfg = px.bar(
            x=top_manufacturers.index,
            y=top_manufacturers.values,
            title="Top 10 Manufacturers by Registrations",
            labels={'x': 'Manufacturer', 'y': 'Total Registrations'},
            color=top_manufacturers.values,
            color_continuous_scale='Blues'
        )
        fig_top_mfg.update_xaxes(tickangle=45)
        st.plotly_chart(fig_top_mfg, use_container_width=True)

        # Manufacturer performance by category
        st.subheader("Manufacturer Performance by Category")
        mfg_category = filtered_df.groupby(['manufacturer', 'category'])['registrations'].sum().unstack(fill_value=0)

        fig_heatmap = px.imshow(
            mfg_category.values,
            labels=dict(x="Vehicle Category", y="Manufacturer", color="Registrations"),
            x=mfg_category.columns,
            y=mfg_category.index,
            aspect="auto",
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    with tab5:
        st.subheader("Detailed Data View")

        # Search and sort options
        search_term = st.text_input("Search manufacturers, states, or categories:", "")

        if search_term:
            mask = (
                filtered_df['manufacturer'].str.contains(search_term, case=False, na=False) |
                filtered_df['state'].str.contains(search_term, case=False, na=False) |
                filtered_df['category'].str.contains(search_term, case=False, na=False)
            )
            display_df = filtered_df[mask]
        else:
            display_df = filtered_df

        # Sort options
        sort_column = st.selectbox("Sort by:", 
                                 options=['registrations', 'yoy_growth', 'qoq_growth', 'year'])
        sort_order = st.radio("Sort order:", ['Descending', 'Ascending'])

        display_df = display_df.sort_values(
            by=sort_column, 
            ascending=(sort_order == 'Ascending')
        )

        # Display data
        st.dataframe(
            display_df[['year', 'quarter', 'state', 'category', 'manufacturer', 
                       'registrations', 'yoy_growth', 'qoq_growth']],
            use_container_width=True,
            height=400
        )

        # Export functionality
        if st.button("📥 Export Filtered Data as CSV"):
            csv_data = display_df.to_csv(index=False)
            st.download_button(
                label="Download CSV File",
                data=csv_data,
                file_name=f"vehicle_registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    # Sidebar information
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Dashboard Info")
    st.sidebar.info(f"""
    **Data Summary:**
    - Total Records: {len(filtered_df):,}
    - Date Range: {filtered_df['year'].min()} - {filtered_df['year'].max()}
    - States: {len(filtered_df['state'].unique())}
    - Categories: {len(filtered_df['category'].unique())}
    - Manufacturers: {len(filtered_df['manufacturer'].unique())}
    """)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Key Insights")

    insights = f"""
    1. **Market Leader**: {filtered_df.groupby('manufacturer')['registrations'].sum().idxmax()}
    2. **Top State**: {filtered_df.groupby('state')['registrations'].sum().idxmax()}
    3. **Growth Category**: {filtered_df.groupby('category')['yoy_growth'].mean().idxmax()}
    4. **Total Market**: {filtered_df['registrations'].sum():,} registrations
    """

    st.sidebar.markdown(insights)

if __name__ == "__main__":
    main()
