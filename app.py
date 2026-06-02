import os
import streamlit as st
import folium
from streamlit_folium import st_folium
from google import genai
from dotenv import load_dotenv  # <-- ADD THIS LINE

# Load local secrets from the .env file immediately on startup
load_dotenv()  # <-- ADD THIS LINE

# 1. Page Configuration & Title
st.set_page_config(page_title="India Wildlife AI Explorer", layout="wide")
st.title("🗺️ India Wildlife Sanctuary AI Explorer")

st.write("Click on any marker on the map of India to instantly discover its key wildlife sanctuaries via AI.")

# =====================================================================
# SECURE ENVIRONMENT VARIABLE FETCH
API_KEY = os.environ.get("GEMINI_API_KEY") 
# =====================================================================

if not API_KEY:
    st.error("⚠️ Gemini API Key not found! Please add GEMINI_API_KEY to your Codespaces Secrets.")
    st.stop()

# Initialize the new modern client
client = genai.Client(api_key=API_KEY)

# State Data: Map Coordinates (Latitude & Longitude)
state_coordinates = {
    "Assam": [26.2006, 92.9376],
    "Gujarat": [22.2587, 71.1924],
    "Karnataka": [15.3173, 75.7139],
    "Madhya Pradesh": [22.9734, 78.6569],
    "Kerala": [10.8505, 76.2711],
    "Rajasthan": [27.0238, 74.2179],
    "West Bengal": [22.9868, 87.8550],
    "Andhra Pradesh": [15.9129, 79.7400],
    "Uttarakhand": [30.0668, 79.0193],
    "Tamil Nadu": [11.1271, 78.6569]
}

import time  # <-- Make sure this is imported at the very top of app.py

def get_ai_wildlife_info(state_name):
    prompt = f"""
    Act as an expert Indian wildlife zoologist. Provide a neat, structured guide for the major wildlife sanctuaries and national parks in '{state_name}'.
    Format the response strictly with clear bold headers:
    - **Name of Sanctuary / National Park**
    - **Ecological Importance**
    - **Key Species / Famous Animals found there** (Use clean bullet points)
    Keep the layout compact and highly engaging.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        # Catching the exact 429 quota error to show a user-friendly message
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return (
                "⚠️ **The AI is taking a quick breath!** \n\n"
                "We are using Google's free API tier which limits map clicks to 20 requests per minute. "
                "Please wait a few seconds and try clicking the state pin again."
            )
        return f"Error connecting to AI: {e}"

# Create the Interactive Layout (Columns)
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Select a State on the Map")
    india_map = folium.Map(location=[21.7679, 78.8718], zoom_start=5, tiles="OpenStreetMap")
    
    for state, coords in state_coordinates.items():
        folium.Marker(
            location=coords,
            popup=state,
            tooltip=f"Click to explore {state}",
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(india_map)
    
    map_data = st_folium(india_map, width=650, height=500)

selected_state = None
if map_data and map_data.get("last_object_clicked_popup"):
    selected_state = map_data["last_object_clicked_popup"]

with col2:
    st.subheader("🌿 Wildlife Sanctuary Details")
    if selected_state:
        st.success(f"Displaying results for: **{selected_state}**")
        with st.spinner("Fetching ecological data from Gemini AI..."):
            ai_report = get_ai_wildlife_info(selected_state)
            st.markdown(ai_report)
    else:
        st.info("👈 Please click a green leaf marker pin on the map to display real-time AI sanctuary insights.")
