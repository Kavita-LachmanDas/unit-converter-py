import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# Set page configuration
st.set_page_config(
    page_title="Advanced Unit Converter",
    page_icon="🔄",
    layout="wide",
)

# Apply custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 2rem;
    }
    .card {
        background-color: #f8f9fa;
         color: #0D47A1;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown("<h1 class='main-header'>Advanced Unit Converter</h1>", unsafe_allow_html=True)
st.markdown("<div class='card'>This application allows you to convert between various units across different categories with real-time visualization of the conversion ratios.</div>", unsafe_allow_html=True)

# Initialize session state for animation
if 'animation_progress' not in st.session_state:
    st.session_state.animation_progress = 0

if 'convert_clicked' not in st.session_state:
    st.session_state.convert_clicked = False

if 'conversion_values' not in st.session_state:
    st.session_state.conversion_values = []

# Define unit conversion dictionaries
length_units = {
    "Meters": 1,
    "Kilometers": 0.001,
    "Centimeters": 100,
    "Millimeters": 1000,
    "Miles": 0.000621371,
    "Yards": 1.09361,
    "Feet": 3.28084,
    "Inches": 39.3701
}

weight_units = {
    "Kilograms": 1,
    "Grams": 1000,
    "Milligrams": 1000000,
    "Metric Tons": 0.001,
    "Pounds": 2.20462,
    "Ounces": 35.274,
    "Stone": 0.157473
}

volume_units = {
    "Liters": 1,
    "Milliliters": 1000,
    "Cubic Meters": 0.001,
    "Gallons (US)": 0.264172,
    "Quarts (US)": 1.05669,
    "Pints (US)": 2.11338,
    "Fluid Ounces (US)": 33.814,
    "Cups": 4.22675
}

temperature_units = {
    "Celsius": "C",
    "Fahrenheit": "F",
    "Kelvin": "K"
}

area_units = {
    "Square Meters": 1,
    "Square Kilometers": 0.000001,
    "Square Centimeters": 10000,
    "Square Millimeters": 1000000,
    "Square Miles": 3.861e-7,
    "Square Yards": 1.19599,
    "Square Feet": 10.7639,
    "Square Inches": 1550,
    "Hectares": 0.0001,
    "Acres": 0.000247105
}

speed_units = {
    "Meters per Second": 1,
    "Kilometers per Hour": 3.6,
    "Miles per Hour": 2.23694,
    "Knots": 1.94384,
    "Feet per Second": 3.28084
}

time_units = {
    "Seconds": 1,
    "Minutes": 1/60,
    "Hours": 1/3600,
    "Days": 1/86400,
    "Weeks": 1/604800,
    "Months (30 days)": 1/2592000,
    "Years (365 days)": 1/31536000
}

data_units = {
    "Bytes": 1,
    "Kilobytes": 1/1024,
    "Megabytes": 1/(1024**2),
    "Gigabytes": 1/(1024**3),
    "Terabytes": 1/(1024**4),
    "Petabytes": 1/(1024**5),
    "Bits": 8,
    "Kilobits": 8/1024,
    "Megabits": 8/(1024**2),
    "Gigabits": 8/(1024**3)
}

energy_units = {
    "Joules": 1,
    "Kilojoules": 0.001,
    "Calories": 0.239006,
    "Kilocalories": 0.000239006,
    "Watt-hours": 0.000277778,
    "Kilowatt-hours": 2.77778e-7,
    "Electron-volts": 6.242e+18,
    "British Thermal Units": 0.000947817
}

pressure_units = {
    "Pascal": 1,
    "Kilopascal": 0.001,
    "Megapascal": 0.000001,
    "Bar": 0.00001,
    "Atmosphere": 9.86923e-6,
    "Torr": 0.00750062,
    "Pounds per Square Inch": 0.000145038
}

# Function to convert temperature
def convert_temperature(value, from_unit, to_unit):
    # Convert from the source unit to Celsius
    if from_unit == "Celsius":
        celsius = value
    elif from_unit == "Fahrenheit":
        celsius = (value - 32) * 5/9
    elif from_unit == "Kelvin":
        celsius = value - 273.15
    
    # Convert from Celsius to the target unit
    if to_unit == "Celsius":
        return celsius
    elif to_unit == "Fahrenheit":
        return celsius * 9/5 + 32
    elif to_unit == "Kelvin":
        return celsius + 273.15

# Function to convert units
def convert_units(value, from_unit, to_unit, unit_dict):
    if unit_dict == temperature_units:
        return convert_temperature(value, from_unit, to_unit)
    else:
        # For all other units, convert to base unit first then to target unit
        base_value = value / unit_dict[from_unit]
        return base_value * unit_dict[to_unit]

# Function to create animated pie chart
def create_animated_pie_chart(input_value, output_value, from_unit, to_unit, progress):
    # Create figure
    fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
    
    # Calculate the proportion for animation
    actual_proportion = output_value / (input_value + output_value) if input_value + output_value > 0 else 0.5
    current_proportion = min(progress, actual_proportion) if progress <= actual_proportion else actual_proportion
    
    if progress <= actual_proportion:
        proportions = [1 - current_proportion, current_proportion]
    else:
        proportions = [1 - actual_proportion, actual_proportion]
    
    # Create the pie chart
    fig.add_trace(
        go.Pie(
            labels=[from_unit, to_unit],
            values=proportions,
            textinfo='label+percent',
            insidetextorientation='radial',
            hole=0.4,
            marker=dict(
                colors=['#1E88E5', '#4CAF50'],
                line=dict(color='#FFFFFF', width=2)
            ),
        )
    )
    
    # Update layout
    fig.update_layout(
        title=f"Conversion Ratio: {from_unit} to {to_unit}",
        annotations=[
            dict(
                text=f"{input_value:.4g} → {output_value:.4g}",
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )
        ],
        showlegend=False,
        height=400,
        width=600,
        margin=dict(t=80, b=20, l=20, r=20)
    )
    
    return fig

# Create tabs for different unit categories
unit_categories = {
    "Length": length_units,
    "Weight": weight_units,
    "Volume": volume_units,
    "Temperature": temperature_units,
    "Area": area_units,
    "Speed": speed_units,
    "Time": time_units,
    "Data": data_units,
    "Energy": energy_units,
    "Pressure": pressure_units
}

# Create layout with columns
col1, col2 = st.columns([2, 3])

with col1:
    # st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # Unit category selection
    category = st.selectbox("Select Category", list(unit_categories.keys()))
    current_units = unit_categories[category]
    
    # Input and output unit selection
    from_unit = st.selectbox("From Unit", list(current_units.keys()), key="from_unit")
    to_unit = st.selectbox("To Unit", list(current_units.keys()), key="to_unit")
    
    # Input value
    input_value = st.number_input("Enter Value", value=1.0, step=0.1)
    
    # Convert button
    if st.button("Convert"):
        st.session_state.convert_clicked = True
        st.session_state.animation_progress = 0
        
        # Calculate the conversion
        if category == "Temperature":
            output_value = convert_temperature(input_value, from_unit, to_unit)
        else:
            output_value = convert_units(input_value, from_unit, to_unit, current_units)
        
        # Store values for animation and display
        st.session_state.conversion_values = [input_value, output_value, from_unit, to_unit]
    
    # Display the result
    if st.session_state.convert_clicked and len(st.session_state.conversion_values) > 0:
        input_val, output_val, from_unit_val, to_unit_val = st.session_state.conversion_values
        
        st.markdown(f"""
        <div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin-top: 20px;'>
            <h3 style='color: #2e7d32; margin: 0;'>Conversion Result</h3>
            <p style='font-size: 1.2rem; margin-top: 10px;'>{input_val} {from_unit_val} = <span style='font-weight: bold; color: #1b5e20;'>{output_val:.6g} {to_unit_val}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Formula or conversion factor
        if category == "Temperature":
            if from_unit_val == "Celsius" and to_unit_val == "Fahrenheit":
                formula = "°F = °C × 9/5 + 32"
            elif from_unit_val == "Fahrenheit" and to_unit_val == "Celsius":
                formula = "°C = (°F - 32) × 5/9"
            elif from_unit_val == "Celsius" and to_unit_val == "Kelvin":
                formula = "K = °C + 273.15"
            elif from_unit_val == "Kelvin" and to_unit_val == "Celsius":
                formula = "°C = K - 273.15"
            elif from_unit_val == "Fahrenheit" and to_unit_val == "Kelvin":
                formula = "K = (°F - 32) × 5/9 + 273.15"
            elif from_unit_val == "Kelvin" and to_unit_val == "Fahrenheit":
                formula = "°F = (K - 273.15) × 9/5 + 32"
            else:
                formula = "Same unit, no conversion needed"
        else:
            if from_unit_val == to_unit_val:
                formula = "Same unit, no conversion needed"
            else:
                from_factor = current_units[from_unit_val]
                to_factor = current_units[to_unit_val]
                conversion_factor = from_factor / to_factor
                if conversion_factor < 0.0001 or conversion_factor > 10000:
                    formula = f"Conversion Factor: {conversion_factor:.6e}"
                else:
                    formula = f"Conversion Factor: {conversion_factor:.6g}"
        
        st.markdown(f"""
        <div style='background-color:rgb(174, 113, 22); padding: 15px; border-radius: 10px; margin-top: 20px;'>
            <h3 style='color: #1565c0; margin: 0;'>Conversion Formula</h3>
            <p style='font-size: 1.1rem; margin-top: 10px; font-family: monospace;'>{formula}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Additional unit information
    st.markdown("<div class='card' style='margin-top: 20px;'>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-header' style='margin-top: 0;  '>Unit Information</h3>", unsafe_allow_html=True)
    
    if category == "Length":
        st.markdown("""
        - **Meter (m)**: The base unit of length in the International System of Units (SI)
        - **Kilometer (km)**: Equal to 1,000 meters
        - **Mile**: Approximately 1,609 meters
        - **Foot**: Exactly 0.3048 meters
        """)
    elif category == "Weight":
        st.markdown("""
        - **Kilogram (kg)**: The base unit of mass in the SI system
        - **Gram (g)**: Equal to 1/1000 of a kilogram
        - **Pound (lb)**: Approximately 0.45359237 kilograms
        - **Ounce (oz)**: Equal to 1/16 of a pound
        """)
    elif category == "Temperature":
        st.markdown("""
        - **Celsius (°C)**: Water freezes at 0°C and boils at 100°C at standard pressure
        - **Fahrenheit (°F)**: Water freezes at 32°F and boils at 212°F at standard pressure
        - **Kelvin (K)**: The SI unit of temperature. 0K = -273.15°C (absolute zero)
        """)
    else:
        st.markdown("""
        Unit conversion is based on established standards and conversion factors.
        For more precise conversions in scientific or engineering applications, 
        consider the context and required precision.
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # Auto-refresh component for animation
    if st.session_state.convert_clicked:
        st_autorefresh(interval=100, limit=20, key="refresh")
        
        # Increment animation progress
        if st.session_state.animation_progress < 1.0:
            st.session_state.animation_progress += 0.05
        
        # Get the conversion values
        if len(st.session_state.conversion_values) > 0:
            input_val, output_val, from_unit_val, to_unit_val = st.session_state.conversion_values
            
            # Create the animated pie chart
            fig = create_animated_pie_chart(
                input_val, output_val, 
                from_unit_val, to_unit_val, 
                st.session_state.animation_progress
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add a progress indicator for animation
            progress_text = f"Animation progress: {int(st.session_state.animation_progress * 100)}%"
            st.progress(st.session_state.animation_progress)
    else:
        st.markdown("""
            <div style='text-align: center; padding: 50px;'>
                <h3>Select units and click 'Convert' to see the animated visualization</h3>
                <p>The animation will show the proportion between input and output values</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent conversions history
    if 'conversion_history' not in st.session_state:
        st.session_state.conversion_history = []
    
    # Add current conversion to history
    if st.session_state.convert_clicked and len(st.session_state.conversion_values) > 0:
        input_val, output_val, from_unit_val, to_unit_val = st.session_state.conversion_values
        
        # Add to history if it's a new conversion
        if len(st.session_state.conversion_history) == 0 or \
           st.session_state.conversion_history[0] != [input_val, output_val, from_unit_val, to_unit_val, category]:
            st.session_state.conversion_history.insert(0, [input_val, output_val, from_unit_val, to_unit_val, category])
            
        # Keep only the last 5 conversions
        if len(st.session_state.conversion_history) > 5:
            st.session_state.conversion_history = st.session_state.conversion_history[:5]
    
    # Display conversion history
    if len(st.session_state.conversion_history) > 0:
        st.markdown("<div class='card' style='margin-top: 20px;  color: #0D47A1;'>", unsafe_allow_html=True)
        st.markdown("<h3 class='sub-header' style='margin-top: 0;'>Recent Conversions</h3>", unsafe_allow_html=True)
        
        for i, (in_val, out_val, f_unit, t_unit, cat) in enumerate(st.session_state.conversion_history):
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; padding: 8px 0; 
                       border-bottom: {'' if i == len(st.session_state.conversion_history)-1 else '1px solid #e0e0e0'}'>
                <span><strong>{cat}:</strong> {in_val} {f_unit}</span>
                <span>→</span>
                <span>{out_val:.6g} {t_unit}</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

# Information section at the bottom
st.markdown("<div class='card' style='margin-top: 30px;'>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-header' style='margin-top: 0;'>About This Unit Converter</h3>", unsafe_allow_html=True)

st.markdown("""
This advanced unit converter app is built with Streamlit and provides:

- Conversions across 10 different categories
- Real-time animated visualizations using Plotly
- Detailed conversion information and formulas
- Conversion history tracking
- Responsive design for various screen sizes

The pie chart visualization dynamically shows the proportion between input and output values with smooth animations.
""")

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""

""", unsafe_allow_html=True)