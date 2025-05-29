import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.backends.backend_pdf import PdfPages

# Configure page
st.set_page_config(
    page_title="Booking Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

def process_data(df, time_period):
    time_column = 'Booking Week' if time_period == 'Week' else 'Booking Month'
    
    # Convert to datetime for proper sorting
    if time_period == 'Week':
        # Handle week format: "Week XX 20XX"
        def parse_week(week_str):
            try:
                if pd.isna(week_str):
                    return pd.NaT
                # Extract week number and year from "Week XX 20XX" format
                import re
                match = re.match(r'Week\s+(\d+)\s+(\d{4})', str(week_str).strip())
                if match:
                    week_num = int(match.group(1))
                    year = int(match.group(2))
                    # Create datetime from year and week number
                    return pd.to_datetime(f'{year}-W{week_num:02d}-1', format='%Y-W%W-%w')
                else:
                    return pd.NaT
            except:
                return pd.NaT
        
        df['Time_Date'] = df[time_column].apply(parse_week)
    else:
        df['Time_Date'] = pd.to_datetime(df[time_column], format='%b %Y', errors='coerce')
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['Time_Date'])
    
    if df.empty:
        # Return empty pivot table with proper structure if no valid dates
        return pd.DataFrame(), df, time_column
        
    df_sorted = df.sort_values('Time_Date')

    # Calculate bookings by time period and status with sorted data
    bookings_summary = df_sorted.groupby([time_column, 'Booking Status']).size().reset_index(name='Count')

    # Create a pivot table with properly sorted time periods
    pivot_table = bookings_summary.pivot(index=time_column, columns='Booking Status', values='Count').fillna(0)

    # Sort the pivot table by the original time order
    if not pivot_table.empty:
        time_sorted_df = df_sorted.drop_duplicates(subset=[time_column]).sort_values('Time_Date')
        sorted_periods = time_sorted_df[time_column].tolist()
        pivot_table = pivot_table.reindex(sorted_periods, fill_value=0)

    return pivot_table, df_sorted, time_column

def create_visualizations(pivot_table, df, time_period):
    # Modern color palette
    colors = {
        'Cancelled': '#FF8A95',
        'Confirmed': '#81C784',
        'Rejected': '#90CAF9'
    }

    # Set modern styling
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except OSError:
        plt.style.use('default')
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.size'] = 11

    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.patch.set_facecolor('#FAFBFC')

    period_label = time_period.title()

    # 1. Stacked bar chart
    pivot_table.plot(kind='bar', stacked=True, ax=axes[0,0], 
                    color=[colors.get(col, '#CCCCCC') for col in pivot_table.columns], 
                    alpha=0.85, edgecolor='white', linewidth=1.5)
    axes[0,0].set_title(f'{period_label}ly Bookings Distribution', fontsize=14, fontweight='bold', pad=20, color='#2C3E50')
    axes[0,0].set_xlabel(period_label, fontsize=12, color='#34495E')
    axes[0,0].set_ylabel('Number of Bookings', fontsize=12, color='#34495E')
    axes[0,0].tick_params(axis='x', rotation=45, colors='#34495E')
    axes[0,0].tick_params(axis='y', colors='#34495E')
    axes[0,0].set_facecolor('#FAFBFC')
    axes[0,0].grid(True, alpha=0.3, color='#BDC3C7')
    axes[0,0].legend(frameon=True, fancybox=True, shadow=True, framealpha=0.9)

    # 2. Grouped bar chart
    pivot_table.plot(kind='bar', ax=axes[0,1], 
                    color=[colors.get(col, '#CCCCCC') for col in pivot_table.columns], 
                    alpha=0.85, edgecolor='white', linewidth=1.5)
    axes[0,1].set_title(f'{period_label}ly Booking Comparison', fontsize=14, fontweight='bold', pad=20, color='#2C3E50')
    axes[0,1].set_xlabel(period_label, fontsize=12, color='#34495E')
    axes[0,1].set_ylabel('Number of Bookings', fontsize=12, color='#34495E')
    axes[0,1].tick_params(axis='x', rotation=45, colors='#34495E')
    axes[0,1].tick_params(axis='y', colors='#34495E')
    axes[0,1].set_facecolor('#FAFBFC')
    axes[0,1].grid(True, alpha=0.3, color='#BDC3C7')
    axes[0,1].legend(frameon=True, fancybox=True, shadow=True, framealpha=0.9)

    # 3. Line plot
    pivot_table.plot(kind='line', ax=axes[1,0], marker='o', markersize=8, linewidth=3,
                    color=[colors.get(col, '#CCCCCC') for col in pivot_table.columns], 
                    alpha=0.9)
    axes[1,0].set_title('Booking Trends Over Time', fontsize=14, fontweight='bold', pad=20, color='#2C3E50')
    axes[1,0].set_xlabel(period_label, fontsize=12, color='#34495E')
    axes[1,0].set_ylabel('Number of Bookings', fontsize=12, color='#34495E')
    axes[1,0].tick_params(axis='x', rotation=45, colors='#34495E')
    axes[1,0].tick_params(axis='y', colors='#34495E')
    axes[1,0].set_facecolor('#FAFBFC')
    axes[1,0].grid(True, alpha=0.3, color='#BDC3C7')
    axes[1,0].legend(frameon=True, fancybox=True, shadow=True, framealpha=0.9)

    # 4. Donut chart
    status_totals = df['Booking Status'].value_counts()
    # 4. Donut chart
    status_totals = df['Booking Status'].value_counts()
    pie_colors = [colors.get(status, '#CCCCCC') for status in status_totals.index]

    _, _, autotexts = axes[1,1].pie(status_totals.values, labels=status_totals.index, 
                                             autopct='%1.1f%%', colors=pie_colors,
                                             wedgeprops=dict(width=0.5, alpha=0.85, edgecolor='white', linewidth=2),
                                             textprops={'fontsize': 11, 'color': '#2C3E50'},
                                             pctdistance=0.75, startangle=90)

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)

    # Add center circle for donut effect
    centre_circle = plt.Circle((0,0), 0.3, fc='#FAFBFC', linewidth=2, edgecolor='#ECF0F1')
    axes[1,1].add_artist(centre_circle)

    total_bookings = len(df)
    axes[1,1].text(0, 0, f'{total_bookings}\nTotal\nBookings', 
                   horizontalalignment='center', verticalalignment='center',
                   fontsize=12, fontweight='bold', color='#2C3E50')

    plt.tight_layout(pad=3.0)
    
    return fig

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string for copying"""
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    return img_str

def create_pdf_download(fig):
    """Create PDF download button"""
    pdf_buffer = io.BytesIO()
    with PdfPages(pdf_buffer) as pdf:
        pdf.savefig(fig, bbox_inches='tight', dpi=300)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
st.title("📊 Booking Analysis Dashboard")
st.markdown("Upload your CSV file to analyze booking data")

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read CSV file
        df = pd.read_csv(uploaded_file)
        
        # Validate required columns
        required_columns = ['Booking Week', 'Booking Month', 'Booking Status']
        if not all(col in df.columns for col in required_columns):
            st.error(f'CSV file must contain columns: {", ".join(required_columns)}')
        else:
            # Time period selection
            st.header("⚙️ Analysis Settings")
            time_period = st.selectbox(
                "Select time period for analysis:",
                options=['Month', 'Week'],
                index=0
            )
            
            # Process data
            pivot_table, df_processed, time_column = process_data(df, time_period)
            
            if pivot_table.empty:
                st.warning(f"No valid data found for {time_period.lower()} analysis. Please check your {time_column} column format.")
                st.info(f"Expected format for {time_column}: {'Week format like \"Week 1 2024\"' if time_period == 'Week' else 'Month format like \"Jan 2024\"'}")
            else:
                # Calculate summary statistics
                status_totals = df['Booking Status'].value_counts()
                total_bookings = len(df)
                
                # Display summary statistics
                st.header("📈 Summary Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Bookings", total_bookings)
                with col2:
                    confirmed = status_totals.get('Confirmed', 0)
                    confirmed_pct = (confirmed/total_bookings*100) if total_bookings > 0 else 0
                    st.metric("Confirmed", f"{confirmed}", f"{confirmed_pct:.1f}%")
                with col3:
                    cancelled = status_totals.get('Cancelled', 0)
                    cancelled_pct = (cancelled/total_bookings*100) if total_bookings > 0 else 0
                    st.metric("Cancelled", f"{cancelled}", f"{cancelled_pct:.1f}%")
                with col4:
                    rejected = status_totals.get('Rejected', 0)
                    rejected_pct = (rejected/total_bookings*100) if total_bookings > 0 else 0
                    st.metric("Rejected", f"{rejected}", f"{rejected_pct:.1f}%")
                
                # Create and display visualizations
                st.header("📊 Visualizations")
                fig = create_visualizations(pivot_table, df_processed, time_period)
                st.pyplot(fig)
                
                # Download Options
                st.header("💾 Download Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Copy image button
                    img_base64 = fig_to_base64(fig)
                    st.markdown(
                        f"""
                        <button onclick="navigator.clipboard.writeText('data:image/png;base64,{img_base64}')">
                            📋 Copy Image to Clipboard
                        </button>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Alternative: Display copyable base64 string
                    with st.expander("📋 Copy Image Data"):
                        st.text_area("Base64 Image Data (copy this):", 
                                   value=f"data:image/png;base64,{img_base64}", 
                                   height=100)
                
                with col2:
                    # PDF download button
                    pdf_data = create_pdf_download(fig)
                    st.download_button(
                        label="📄 Download as PDF",
                        data=pdf_data,
                        file_name=f"booking_analysis_{time_period.lower()}.pdf",
                        mime="application/pdf"
                    )
                
                # Display data table
                st.header("📋 Data Summary")
                st.dataframe(pivot_table, use_container_width=True)
                                    
    except Exception as e:
            st.error(f"An error occurred while processing the file: {str(e)}")
    else:
        st.info("Please upload a CSV file to get started")