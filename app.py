import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io

# Configure the page
st.set_page_config(
    page_title="Hotel Booking Analyzer",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 1rem;
        text-align: center;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #374151;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        color: white;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .upload-section {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 12px;
        border: 2px dashed #cbd5e1;
        margin: 2rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #0ea5e9;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def analyze_booking_data(df):
    """Analyze booking data and return comprehensive statistics"""
    # Group by country and calculate metrics
    country_analysis = df.groupby('Hotel Country Name').agg({
        'Guests': ['count', 'mean', 'sum'],
        'Room Nights': ['mean', 'sum']
    }).round(2)
    
    # Flatten column names
    country_analysis.columns = ['Total_Bookings', 'Avg_Guests', 'Total_Guests', 'Avg_Stay_Nights', 'Total_Nights']
    country_analysis = country_analysis.reset_index()
    
    # Sort by total bookings for ranking
    country_analysis = country_analysis.sort_values('Total_Bookings', ascending=False)
    
    analysis = {
        'total_bookings': len(df),
        'total_countries': len(country_analysis),
        'total_guests': df['Guests'].sum(),
        'avg_stay': df['Room Nights'].mean(),
        'country_data': country_analysis,
        'top_country': country_analysis.iloc[0]['Hotel Country Name'] if not country_analysis.empty else 'N/A'
    }
    
    return analysis

def create_interactive_map(analysis):
    """Create modern interactive choropleth map with improved styling"""
    country_data = analysis['country_data']
    
    # Create the choropleth map with modern color scheme
    fig = go.Figure(data=go.Choropleth(
        locations=country_data['Hotel Country Name'],
        z=country_data['Total_Bookings'],
        locationmode='country names',
        colorscale=[
            [0, '#f8fafc'],
            [0.2, '#e2e8f0'],
            [0.4, '#94a3b8'],
            [0.6, '#64748b'],
            [0.8, '#475569'],
            [1, '#1e293b']
        ],
        autocolorscale=False,
        text=country_data['Hotel Country Name'],
        hovertemplate=
        '<b>%{text}</b><br>' +
        'Total Bookings: %{z:,}<br>' +
        'Average Guests: ' + country_data['Avg_Guests'].astype(str) + '<br>' +
        'Average Stay: ' + country_data['Avg_Stay_Nights'].astype(str) + ' nights<br>' +
        'Total Guests: ' + country_data['Total_Guests'].astype(str) +
        '<extra></extra>',
        colorbar=dict(
            title=dict(
                text="Total Bookings",
                font=dict(size=14, color='#374151')
            ),
            tickfont=dict(size=12, color='#6b7280'),
            thickness=15,
            len=0.8
        )
    ))

    fig.update_layout(
        title={
            'text': 'Global Hotel Booking Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#1f2937', 'family': 'Arial, sans-serif'}
        },
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='#e5e7eb',
            showland=True,
            landcolor='#f9fafb',
            showocean=True,
            oceancolor='#f0f9ff',
            projection_type='natural earth',
            showlakes=True,
            lakecolor='#dbeafe'
        ),
        height=650,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig

def create_metrics_cards(analysis):
    """Create modern metric cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{analysis['total_bookings']:,}</div>
            <div class="metric-label">Total Bookings</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{analysis['total_countries']}</div>
            <div class="metric-label">Countries</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{analysis['total_guests']:,}</div>
            <div class="metric-label">Total Guests</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{analysis['avg_stay']:.1f}</div>
            <div class="metric-label">Avg Stay (nights)</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Main header
    st.markdown('<h1 class="main-header">Hotel Booking Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Info section
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    **Data Requirements:** Your CSV file should contain exactly 3 columns:
    - **Hotel Country Name** - Country where booking was made
    - **Guests** - Number of guests for each booking  
    - **Room Nights** - Number of nights stayed
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">Data Upload</h3>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Select your booking data CSV file to begin analysis",
        type=['csv'],
        help="Upload a CSV file with your hotel booking data"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        try:
            # Read and validate data
            df = pd.read_csv(uploaded_file)
            
            # Validate CSV structure
            expected_columns = ['Hotel Country Name', 'Guests', 'Room Nights']
            if len(df.columns) != 3:
                st.error(f'Invalid file format: Expected 3 columns, found {len(df.columns)}')
                return
            
            # Rename columns to expected format
            df.columns = expected_columns
            
            # Validate and clean data
            try:
                df['Guests'] = pd.to_numeric(df['Guests'], errors='coerce')
                df['Room Nights'] = pd.to_numeric(df['Room Nights'], errors='coerce')
            except:
                st.error('Data validation failed: Guests and Room Nights must be numeric values')
                return
            
            # Remove invalid data
            df = df.dropna()
            
            if df.empty:
                st.error('No valid data found after processing')
                return
            
            # Analyze data
            analysis = analyze_booking_data(df)
            
            # Success message
            st.success(f"Successfully processed {uploaded_file.name}")
            
            # Display metrics
            st.markdown('<br>', unsafe_allow_html=True)
            create_metrics_cards(analysis)
            
            # Interactive map
            st.markdown('<h3 class="section-header">Geographic Distribution</h3>', unsafe_allow_html=True)
            fig = create_interactive_map(analysis)
            st.plotly_chart(fig, use_container_width=True)
            
            # Top countries chart
            st.markdown('<h3 class="section-header">Top 10 Countries by Bookings</h3>', unsafe_allow_html=True)
            top_10 = analysis['country_data'].head(10)
            
            bar_fig = px.bar(
                top_10, 
                x='Total_Bookings', 
                y='Hotel Country Name',
                orientation='h',
                color='Total_Bookings',
                color_continuous_scale=[
                    [0, '#f1f5f9'],
                    [0.5, '#64748b'],
                    [1, '#1e293b']
                ],
                labels={'Total_Bookings': 'Total Bookings', 'Hotel Country Name': 'Country'}
            )
            
            bar_fig.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#374151'),
                yaxis=dict(categoryorder='total ascending')
            )
            
            st.plotly_chart(bar_fig, use_container_width=True)
            
            # Detailed statistics table
            st.markdown('<h3 class="section-header">📊 Detailed Country Statistics</h3>', unsafe_allow_html=True)
            
            # Add filtering and sorting options
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                search_country = st.text_input("🔍 Search country", placeholder="Type country name...")
            with col2:
                sort_by = st.selectbox("Sort by", ["Total Bookings", "Total Guests", "Avg Guests", "Avg Stay (nights)", "Revenue Score"])
            with col3:
                sort_order = st.selectbox("Order", ["Descending", "Ascending"])
            
            # Filter and sort data with additional analysis columns
            filtered_df = analysis['country_data'].copy()
            
            # Add interesting analysis columns
            filtered_df['Booking_Percentage'] = (filtered_df['Total_Bookings'] / filtered_df['Total_Bookings'].sum() * 100).round(2)
            filtered_df['Guest_Percentage'] = (filtered_df['Total_Guests'] / filtered_df['Total_Guests'].sum() * 100).round(2)
            filtered_df['Revenue_Score'] = (filtered_df['Total_Bookings'] * filtered_df['Avg_Stay_Nights'] * filtered_df['Avg_Guests']).round(2)
            filtered_df['Occupancy_Intensity'] = (filtered_df['Total_Guests'] / filtered_df['Total_Nights']).round(2)
            
            if search_country:
                filtered_df = filtered_df[filtered_df['Hotel Country Name'].str.contains(search_country, case=False, na=False)]
            
            # Apply sorting
            sort_column_map = {
                "Total Bookings": "Total_Bookings",
                "Total Guests": "Total_Guests", 
                "Avg Guests": "Avg_Guests",
                "Avg Stay (nights)": "Avg_Stay_Nights",
                "Revenue Score": "Revenue_Score"
            }
            sort_ascending = sort_order == "Ascending"
            filtered_df = filtered_df.sort_values(sort_column_map[sort_by], ascending=sort_ascending)
            
            if filtered_df.empty:
                st.info("No countries match your search criteria.")
            else:
                st.info(f"Showing {len(filtered_df)} of {len(analysis['country_data'])} countries")
                
                # Create comprehensive display dataframe
                display_table_df = filtered_df.copy()
                display_table_df = display_table_df.rename(columns={
                    'Hotel Country Name': 'Country',
                    'Total_Bookings': 'Total Bookings',
                    'Avg_Guests': 'Avg Guests',
                    'Total_Guests': 'Total Guests',
                    'Avg_Stay_Nights': 'Avg Stay (nights)',
                    'Total_Nights': 'Total Nights',
                    'Booking_Percentage': 'Booking %',
                    'Guest_Percentage': 'Guest %',
                    'Revenue_Score': 'Revenue Score',
                    'Occupancy_Intensity': 'Guests/Night'
                })
                
                # Add ranking column
                display_table_df.insert(0, 'Rank', range(1, len(display_table_df) + 1))
                
                # Display the enhanced table
                st.dataframe(
                    display_table_df,
                    use_container_width=True,
                    height=400,
                    column_config={
                        "Rank": st.column_config.NumberColumn("Rank", format="%d"),
                        "Total Bookings": st.column_config.NumberColumn("Total Bookings", format="%,d"),
                        "Total Guests": st.column_config.NumberColumn("Total Guests", format="%,d"),
                        "Total Nights": st.column_config.NumberColumn("Total Nights", format="%,d"),
                        "Avg Guests": st.column_config.NumberColumn("Avg Guests", format="%.2f"),
                        "Avg Stay (nights)": st.column_config.NumberColumn("Avg Stay (nights)", format="%.2f"),
                        "Booking %": st.column_config.NumberColumn("Booking %", format="%.2f%%"),
                        "Guest %": st.column_config.NumberColumn("Guest %", format="%.2f%%"),
                        "Revenue Score": st.column_config.NumberColumn("Revenue Score", format="%.2f"),
                        "Guests/Night": st.column_config.NumberColumn("Guests/Night", format="%.2f")
                    }
                )
                
                # Additional insights
                st.markdown('<h4>📈 Key Insights</h4>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Top Performers:**")
                    top_revenue = display_table_df.nlargest(3, 'Revenue Score')
                    for idx, row in top_revenue.iterrows():
                        st.write(f"🏆 {row['Country']}: Revenue Score {row['Revenue Score']:,.0f}")
                
                with col2:
                    st.markdown("**Market Concentration:**")
                    top_5_booking_share = display_table_df.head(5)['Booking %'].sum()
                    st.write(f"📊 Top 5 countries: {top_5_booking_share:.1f}% of all bookings")
                    avg_guests_per_night = display_table_df['Guests/Night'].mean()
                    st.write(f"👥 Average occupancy: {avg_guests_per_night:.2f} guests per night")
            
            # Format the dataframe
            display_df = analysis['country_data'].copy()
            display_df = display_df.rename(columns={
                'Hotel Country Name': 'Country',
                'Total_Bookings': 'Total Bookings',
                'Avg_Guests': 'Avg Guests',
                'Total_Guests': 'Total Guests',
                'Avg_Stay_Nights': 'Avg Stay (nights)',
                'Total_Nights': 'Total Nights'
            })
            
            # Format numbers for better readability
            display_df['Total Bookings'] = display_df['Total Bookings'].apply(lambda x: f"{x:,}")
            display_df['Total Guests'] = display_df['Total Guests'].apply(lambda x: f"{x:,}")
            display_df['Total Nights'] = display_df['Total Nights'].apply(lambda x: f"{x:,}")
            
            # Download section
            _, col2, _ = st.columns([1, 1, 1])
            with col2:
                csv_buffer = io.StringIO()
                display_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="Download Analysis Results",
                    data=csv_buffer.getvalue(),
                    file_name=f"booking_analysis_{uploaded_file.name}",
                    mime="text/csv",
                    use_container_width=True
                )
            
        except Exception as e:
            st.error(f'Error processing file: {str(e)}')

if __name__ == '__main__':
    main()
