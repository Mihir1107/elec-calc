import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="Electricity Usage Calculator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'usage_data' not in st.session_state:
    st.session_state.usage_data = []

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}

def calculate_base_energy(facility):
    """Calculate base energy consumption based on facility type"""
    base_consumption = {
        "1bhk": 2 * 0.4 + 2 * 0.8,  # 2.4 kWh
        "2bhk": 3 * 0.4 + 3 * 0.8,  # 3.6 kWh
        "3bhk": 4 * 0.4 + 4 * 0.8   # 4.8 kWh
    }
    return base_consumption.get(facility.lower(), 0)

def calculate_appliance_energy(ac, fridge, washing_machine, tv, microwave, water_heater):
    """Calculate energy consumption from appliances"""
    appliance_consumption = 0
    
    # AC: 1.5 kWh per hour, assuming 8 hours usage
    if ac:
        appliance_consumption += 1.5 * 8
    
    # Fridge: 0.15 kWh per hour, 24 hours
    if fridge:
        appliance_consumption += 0.15 * 24
    
    # Washing Machine: 2 kWh per cycle, assuming 1 cycle
    if washing_machine:
        appliance_consumption += 2
    
    # TV: 0.15 kWh per hour, assuming 6 hours
    if tv:
        appliance_consumption += 0.15 * 6
    
    # Microwave: 1.2 kWh per hour, assuming 0.5 hours
    if microwave:
        appliance_consumption += 1.2 * 0.5
    
    # Water Heater: 2 kWh per hour, assuming 2 hours
    if water_heater:
        appliance_consumption += 2 * 2
    
    return appliance_consumption

def save_daily_usage(total_energy, user_data):
    """Save daily usage data"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    usage_entry = {
        "date": today,
        "total_energy": total_energy,
        "user_data": user_data,
        "timestamp": datetime.now().isoformat()
    }
    
    # Check if today's data already exists
    existing_index = None
    for i, entry in enumerate(st.session_state.usage_data):
        if entry["date"] == today:
            existing_index = i
            break
    
    if existing_index is not None:
        st.session_state.usage_data[existing_index] = usage_entry
    else:
        st.session_state.usage_data.append(usage_entry)

def get_weekly_data():
    """Get data for the last 7 days"""
    if not st.session_state.usage_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(st.session_state.usage_data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Get last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    weekly_data = df[df['date'] >= start_date].sort_values('date')
    return weekly_data

# Main UI
st.title("⚡ Electricity Usage Calculator")
st.markdown("Calculate and track your daily electricity consumption")

# Sidebar for user profile
st.sidebar.header("👤 User Profile")

with st.sidebar:
    name = st.text_input("Enter your name:", value=st.session_state.user_profile.get('name', ''))
    age = st.number_input("Enter your age:", min_value=1, max_value=120, value=st.session_state.user_profile.get('age', 25))
    city = st.text_input("Enter your city:", value=st.session_state.user_profile.get('city', ''))
    area = st.text_input("Enter your area name:", value=st.session_state.user_profile.get('area', ''))
    
    st.subheader("🏠 Housing Details")
    flat_tenement = st.selectbox("Are you living in:", 
                                ["Flat", "Tenement"], 
                                index=0 if st.session_state.user_profile.get('flat_tenement', 'Flat') == 'Flat' else 1)
    
    facility = st.selectbox("Select your housing type:", 
                           ["1BHK", "2BHK", "3BHK"],
                           index=["1BHK", "2BHK", "3BHK"].index(st.session_state.user_profile.get('facility', '1BHK')))

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🔌 Appliances Usage")
    
    # Appliances input
    ac = st.checkbox("Air Conditioner (AC)", value=st.session_state.user_profile.get('ac', False))
    fridge = st.checkbox("Refrigerator", value=st.session_state.user_profile.get('fridge', False))
    washing_machine = st.checkbox("Washing Machine", value=st.session_state.user_profile.get('washing_machine', False))
    tv = st.checkbox("Television", value=st.session_state.user_profile.get('tv', False))
    microwave = st.checkbox("Microwave", value=st.session_state.user_profile.get('microwave', False))
    water_heater = st.checkbox("Water Heater", value=st.session_state.user_profile.get('water_heater', False))

with col2:
    st.subheader("📊 Today's Calculation")
    
    # Calculate energy consumption
    base_energy = calculate_base_energy(facility)
    appliance_energy = calculate_appliance_energy(ac, fridge, washing_machine, tv, microwave, water_heater)
    total_energy = base_energy + appliance_energy
    
    # Display breakdown
    st.metric("Base Consumption (Lighting & Fans)", f"{base_energy:.2f} kWh")
    st.metric("Appliances Consumption", f"{appliance_energy:.2f} kWh")
    st.metric("Total Daily Consumption", f"{total_energy:.2f} kWh", delta=f"₹{total_energy * 6:.2f}")
    
    # Estimated monthly cost (assuming ₹6 per kWh)
    monthly_cost = total_energy * 30 * 6
    st.info(f"💰 Estimated Monthly Cost: ₹{monthly_cost:.2f}")

# Save button
if st.button("💾 Save Today's Usage", type="primary"):
    if name:
        user_data = {
            'name': name,
            'age': age,
            'city': city,
            'area': area,
            'flat_tenement': flat_tenement,
            'facility': facility,
            'ac': ac,
            'fridge': fridge,
            'washing_machine': washing_machine,
            'tv': tv,
            'microwave': microwave,
            'water_heater': water_heater
        }
        
        # Update session state
        st.session_state.user_profile = user_data
        
        # Save usage data
        save_daily_usage(total_energy, user_data)
        st.success("✅ Usage data saved successfully!")
    else:
        st.error("❌ Please enter your name first!")

# Analytics section
st.header("📈 Usage Analytics")

# Get weekly data
weekly_data = get_weekly_data()

if not weekly_data.empty:
    tab1, tab2, tab3 = st.tabs(["📅 Daily Usage", "📊 Weekly Trend", "🔍 Detailed Analysis"])
    
    with tab1:
        st.subheader("Last 7 Days Usage")
        
        # Create daily usage chart
        fig_daily = px.bar(
            weekly_data, 
            x='date', 
            y='total_energy',
            title='Daily Electricity Consumption',
            labels={'total_energy': 'Energy (kWh)', 'date': 'Date'},
            color='total_energy',
            color_continuous_scale='Blues'
        )
        fig_daily.update_layout(height=400)
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Display data table
        display_data = weekly_data[['date', 'total_energy']].copy()
        display_data['date'] = display_data['date'].dt.strftime('%Y-%m-%d')
        display_data['cost'] = display_data['total_energy'] * 6
        display_data.columns = ['Date', 'Energy (kWh)', 'Cost (₹)']
        st.dataframe(display_data, use_container_width=True)
    
    with tab2:
        st.subheader("Weekly Consumption Trend")
        
        # Line chart for trend
        fig_trend = px.line(
            weekly_data, 
            x='date', 
            y='total_energy',
            title='Weekly Electricity Consumption Trend',
            labels={'total_energy': 'Energy (kWh)', 'date': 'Date'},
            markers=True
        )
        fig_trend.update_layout(height=400)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Weekly statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Week", f"{weekly_data['total_energy'].sum():.2f} kWh")
        with col2:
            st.metric("Average Daily", f"{weekly_data['total_energy'].mean():.2f} kWh")
        with col3:
            st.metric("Highest Day", f"{weekly_data['total_energy'].max():.2f} kWh")
        with col4:
            st.metric("Lowest Day", f"{weekly_data['total_energy'].min():.2f} kWh")
    
    with tab3:
        st.subheader("Detailed Analysis")
        
        # Appliance-wise breakdown (for latest entry)
        if not weekly_data.empty:
            latest_data = weekly_data.iloc[-1]['user_data']
            
            # Create appliance breakdown
            appliances = {
                'AC': 12.0 if latest_data.get('ac', False) else 0,
                'Fridge': 3.6 if latest_data.get('fridge', False) else 0,
                'Washing Machine': 2.0 if latest_data.get('washing_machine', False) else 0,
                'TV': 0.9 if latest_data.get('tv', False) else 0,
                'Microwave': 0.6 if latest_data.get('microwave', False) else 0,
                'Water Heater': 4.0 if latest_data.get('water_heater', False) else 0,
                'Base (Lights & Fans)': calculate_base_energy(latest_data.get('facility', '1BHK'))
            }
            
            # Filter out zero values
            active_appliances = {k: v for k, v in appliances.items() if v > 0}
            
            if active_appliances:
                fig_pie = px.pie(
                    values=list(active_appliances.values()),
                    names=list(active_appliances.keys()),
                    title='Energy Consumption Breakdown (Latest Day)'
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        # Energy efficiency tips
        st.subheader("💡 Energy Efficiency Tips")
        st.markdown("""
        - **AC Usage**: Set temperature to 24°C or higher to save up to 20% energy
        - **Fridge**: Keep it at optimal temperature (3-4°C) and avoid frequent door opening
        - **Washing Machine**: Use cold water and full loads to maximize efficiency
        - **Lighting**: Switch to LED bulbs to reduce consumption by 75%
        - **Water Heater**: Use timer switches and insulate the tank
        """)

else:
    st.info("📝 No usage data available yet. Save your first entry to see analytics!")

# Export data feature
if st.session_state.usage_data:
    st.subheader("📤 Export Data")
    
    # Prepare data for export
    export_data = []
    for entry in st.session_state.usage_data:
        export_entry = {
            'Date': entry['date'],
            'Total Energy (kWh)': entry['total_energy'],
            'Cost (₹)': entry['total_energy'] * 6,
            'Name': entry['user_data']['name'],
            'City': entry['user_data']['city'],
            'Housing Type': entry['user_data']['facility'],
            'AC': entry['user_data']['ac'],
            'Fridge': entry['user_data']['fridge'],
            'Washing Machine': entry['user_data']['washing_machine'],
            'TV': entry['user_data']['tv'],
            'Microwave': entry['user_data']['microwave'],
            'Water Heater': entry['user_data']['water_heater']
        }
        export_data.append(export_entry)
    
    export_df = pd.DataFrame(export_data)
    
    col1, col2 = st.columns(2)
    with col1:
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"electricity_usage_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = json.dumps(st.session_state.usage_data, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"electricity_usage_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown("⚡ **Electricity Usage Calculator** - Track your energy consumption and save money!")