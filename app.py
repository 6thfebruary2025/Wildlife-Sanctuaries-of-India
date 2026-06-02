import os
import streamlit as st
import folium
from streamlit_folium import st_folium
from google import genai
from dotenv import load_dotenv

# Import our comprehensive data dictionary directly from our new database module
from states_data import INDIA_STATES

load_dotenv()

st.set_page_config(page_title="India Wildlife Production Dashboard", layout="wide")

# App Header Styling
st.markdown("""
    <h1 style='text-align: center; color: #1E4620;'>🌿 Enterprise India Wildlife Sanctuary Analytics Dashboard</h1>
    <p style='text-align: center; font-size: 16px; color: #4A5D4E;'>
        An advanced geospatial explorer mapping regional ecosystems, area metrics, indigenous species, and live AI zoological data.
    </p>
    <hr style='border: 1px solid #E1E8E2;'/>
""", allow_html=True)

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
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return "⚠️ **Rate Limit Reached.** Cached state metadata remains fully operational. AI text layer will refresh momentarily."
        return f"Database Stream Interrupted: {e}"

# Layout Construction
col1, col2 = st.columns([1.1, 1])

with col1:
    st.subheader("🗺️ Regional Geospatial Selection")
    
    # Render modern dark/terrain balanced baseline map center point
    india_map = folium.Map(location=[21.7679, 78.8718], zoom_start=5, tiles="OpenStreetMap")
    
    # Loop over database dictionary values to dynamically generate all map leaf components
    for state, details in INDIA_STATES.items():
        folium.Marker(
            location=details["coords"],
            popup=state,
            tooltip=f"Analyze {state} Ecosystem",
            icon=folium.Icon(color="darkgreen", icon="tree", prefix="fa")
        ).add_to(india_map)
    
    map_data = st_folium(india_map, width=680, height=520, key="main_map")

selected_state = None
if map_data and map_data.get("last_object_clicked_popup"):
    selected_state = map_data["last_object_clicked_popup"]

with col2:
    if selected_state and selected_state in INDIA_STATES:
        state_info = INDIA_STATES[selected_state]
        
        st.markdown(f"<h2 style='color: #2E6F40;'>📊 {selected_state} Ecological Profile</h2>", unsafe_with_html=True)
        
        # Professional Analytics Metrics Row
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="Protected Area Coverage", value=f"{state_info['area_sq_km']} km²", delta="Official Data")
        with m_col2:
            st.metric(label="Major Sanctuaries Tracked", value=state_info['total_sanctuaries'])
            
        # Key Target Species Badges Display Section
        st.write("### 🐾 Flagship Indigenous Species")
        badge_html = "".join([f"<span style='background-color:#EBF5FB; color:#1F618D; padding:5px 12px; margin:4px; border-radius:15px; font-weight:bold; display:inline-block; border:1px solid #AED6F1;'>{species}</span>" for species in state_info["key_species"]])
        st.markdown(badge_html, unsafe_with_html=True)
        
        # High-Fidelity Visual Asset Layer Showcase Placeholder
        st.write("### 🖼️ Key Ecosystem Habitats")
        
        # Professional systems use dynamic search strings. We render an organized container layout:
        img_col1, img_col2 = st.columns(2)
        with img_col1:
            st.image("https://unsplash.com", caption=f"Primary Habitat: {state_info['key_species'][0]}", use_container_width=True)
        with img_col2:
            st.image("https://unsplash.com", caption="Protected Reserve Core Zone", use_container_width=True)
            
        # Deep Analytics Live AI Text Delivery 
        st.write("---")
        with st.spinner("Synthesizing live environmental data..."):
            ai_report = get_ai_wildlife_info(selected_state)
            st.markdown(ai_report)
            
    else:
        st.markdown("""
            <div style='background-color: #F4F6F4; border-left: 5px solid #2E6F40; padding: 20px; border-radius: 4px; margin-top: 50px;'>
                <h4 style='margin-top:0; color: #2E6F40;'>👈 Awaiting System Selection</h4>
                <p style='margin-bottom:0; color: #555;'>Please select an active geospatial green leaf node on the interactive tracking map to compute and stream deep analytics, metadata, and live AI environmental reports.</p>
            </div>
        """, unsafe_with_html=True)
