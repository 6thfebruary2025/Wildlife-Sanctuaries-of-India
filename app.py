import os
import streamlit as st
import folium
from streamlit_folium import st_folium
from google import genai
from dotenv import load_dotenv

# Import our comprehensive data dictionary directly from our states database module
from states_data import INDIA_STATES

load_dotenv()

# 1. ALWAYS PLACE PAGE CONFIG FIRST
st.set_page_config(page_title="India Wildlife Production Dashboard", layout="wide")

# 2. RUN HEADER FIXED ONCE (No duplicates)
st.markdown("""
    <h1 style='text-align: center; color: #4AF273; text-shadow: 2px 2px 4px rgba(0,0,0,0.6); font-weight: 800; font-family: sans-serif; padding-top: 10px;'>
        🌿 Enterprise India Wildlife Sanctuary Analytics Dashboard
    </h1>
    <p style='text-align: center; font-size: 16px; color: #A4C2A9; font-weight: 500;'>
        An advanced geospatial explorer mapping regional ecosystems, area metrics, indigenous species, and live AI zoological data.
    </p>
    <hr style='border: 1px solid #2A4830;'/>
""", unsafe_allow_html=True)

API_KEY = os.environ.get("GEMINI_API_KEY") 
if not API_KEY:
    st.error("⚠️ Gemini API Key configuration missing from deployment environment properties.")
    st.stop()

client = genai.Client(api_key=API_KEY)

@st.cache_data(show_spinner=False)
def get_ai_wildlife_info(state_name):
    prompt = f"""
    Act as an elite senior Indian wildlife conservationist. 
    Provide a highly technical, executive summary of the wildlife management strategies, current environmental threats, and top 3 national parks within '{state_name}'.
    Format strictly using markdown headers:
    ### 🏗️ Primary National Parks & Reserves
    ### ⚡ Key Conservation/Ecological Threats
    ### 🛡️ Ongoing Wildlife Protection Initiatives
    Keep descriptions dense, informative, professional, and omit introductory conversational filler.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return (
                "⚠️ **The AI is taking a quick breath!** \n\n"
                "We are using Google's free API tier which limits map clicks to 20 requests per minute. "
                "Please wait a few seconds and try clicking the state pin again."
            )
        return f"Database Stream Interrupted: {e}"

# 3. CONSTRUCT SIDE-BY-SIDE GRID
col1, col2 = st.columns([1.1, 1])

with col1:
    st.subheader("🗺️ Regional Geospatial Selection")
    india_map = folium.Map(location=[21.7679, 78.8718], zoom_start=5, tiles="OpenStreetMap")
    
    for state, details in INDIA_STATES.items():
        folium.Marker(
            location=details["coords"],
            popup=state,
            tooltip=f"Analyze {state} Ecosystem",
            icon=folium.Icon(color="darkgreen", icon="tree", prefix="fa")
        ).add_to(india_map)
    
    map_data = st_folium(india_map, width=650, height=500, key="main_map")

# 4. PARSE INTERACTION MAP PAYLOADS CLEANLY
selected_state = None
if map_data:
    if map_data.get("last_object_clicked_tooltip"):
        raw_tooltip = map_data["last_object_clicked_tooltip"].strip()
        for state in INDIA_STATES.keys():
            if state in raw_tooltip:
                selected_state = state
                break
                
    if not selected_state and map_data.get("last_object_clicked_popup"):
        selected_state = map_data["last_object_clicked_popup"].strip()
        
    if not selected_state and map_data.get("last_object_clicked"):
        last_obj = map_data["last_object_clicked"]
        if isinstance(last_obj, dict) and last_obj.get("value"):
            selected_state = last_obj["value"].strip()

# 5. STREAM DATA INSIDE PROFILE PANEL EXCLUSIVELY
with col2:
    if selected_state and selected_state in INDIA_STATES:
        state_info = INDIA_STATES[selected_state]
        
        st.markdown(f"<h2 style='color: #4AF273; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>📊 {selected_state} Ecological Profile</h2>", unsafe_allow_html=True)
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="Protected Area Coverage", value=f"{state_info['area_sq_km']} km²", delta="Official Data")
        with m_col2:
            st.metric(label="Major Sanctuaries Tracked", value=state_info['total_sanctuaries'])
            
        #st.write("### 🐾 Flagship Indigenous Species")
        #badge_html = "".join([f"<span style='background-color:#1E3A24; color:#4AF273; padding:6px 14px; margin:5px; border-radius:15px; font-weight:bold; display:inline-block; border:1px solid #2A5C34;'>{species}</span>" for species in state_info["key_species"]])
        #st.markdown(badge_html, unsafe_allow_html=True)
        
        #st.write("### 🖼️ Flagship Species Visual Habitat")
        
        # High-performance direct Unsplash visual links configured to bypass direct hotlink blocks
        #animal_keyword = state_info["key_species"][0].lower() if state_info["key_species"] else "wildlife"
        #fallback_source_url = "https://unsplash.com"
        
        #if "tiger" in animal_keyword:
            #fallback_source_url = "https://unsplash.com"
        #elif "elephant" in animal_keyword:
           # fallback_source_url = "https://unsplash.com"
        #elif "rhino" in animal_keyword:
           # fallback_source_url = "https://unsplash.com"
        #elif "leopard" in animal_keyword:
           # fallback_source_url = "https://unsplash.com"
        #elif any(k in animal_keyword for k in ["deer", "blackbuck", "tahr", "stag", "antelope", "chital"]):
         #   fallback_source_url = "https://unsplash.com"
            
        
        #st.image(
         #   fallback_source_url, 
          #  caption=f"Photographic analysis matching flagship native regional wildlife.", 
           # width="stretch"  # Updated to modern Streamlit dark-mode responsive width settings
        #)*/
            
        st.write("---")
        with st.spinner("Synthesizing live environmental data..."):
            ai_report = get_ai_wildlife_info(selected_state)
            st.markdown(ai_report)
            
    else:
        st.markdown("""
            <div style='background-color: #152918; border-left: 5px solid #4AF273; padding: 20px; border-radius: 4px; margin-top: 50px; border-top: 1px solid #233D27; border-right: 1px solid #233D27; border-bottom: 1px solid #233D27;'>
                <h4 style='margin-top:0; color: #4AF273;'>👈 Awaiting System Selection</h4>
                <p style='margin-bottom:0; color: #A4C2A9;'>Please select an active geospatial green leaf node on the interactive tracking map to compute and stream deep analytics, metadata, and live AI environmental reports.</p>
            </div>
        """, unsafe_allow_html=True)
