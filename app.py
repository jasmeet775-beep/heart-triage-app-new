import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import googlemaps
import ast
import random
import os

# --- 1. SETUP & CONFIGURATION ---

# 🛑 PASTE YOUR API KEY HERE
API_KEY = "AIzaSyCgD-9bS0ECQEgvUHio6DCLITQmQm1FLzA"

# Initialize Google Maps Client
gmaps = None
if API_KEY and API_KEY != "AIzaSyCgD-9bS0ECQEgvUHio6DCLITQmQm1FLzA":
    try:
        gmaps = googlemaps.Client(key=API_KEY)
    except ValueError:
        st.error("⚠️ API Key invalid.")

# File Names
PATIENT_DB_FILE = "patient_database.csv"
MED_DB_FILE = "heart_medication_detailed.csv"

# --- 2. AUTOMATIC DATABASE GENERATION ---
@st.cache_data
def generate_databases_if_missing():
    # A. Generate Medication Database
    if not os.path.exists(MED_DB_FILE):
        med_data = [
            {"Condition_Key": "Normal", "Medicine_Name": "Multivitamin", "Brand_Name": "Centrum", "Dosage": "1 Tablet", "Frequency": "Once Daily", "Duration": "Continuous", "Best_Time": "After Breakfast", "Instructions": "Take with water.", "Risk_Warning": "None"},
            {"Condition_Key": "Bradycardia", "Medicine_Name": "Levothyroxine", "Brand_Name": "Synthroid", "Dosage": "50 mcg", "Frequency": "Once Daily", "Duration": "Life-long", "Best_Time": "Empty Stomach", "Instructions": "No calcium/iron with this.", "Risk_Warning": "Check TSH levels."},
            {"Condition_Key": "Severe Bradycardia", "Medicine_Name": "Atropine", "Brand_Name": "AtroPen", "Dosage": "0.5 mg IV", "Frequency": "Emergency Single Dose", "Duration": "Until Stable", "Best_Time": "IMMEDIATE", "Instructions": "Medical pro only.", "Risk_Warning": "Dry mouth, blurred vision."},
            {"Condition_Key": "Moderate Tachycardia", "Medicine_Name": "Metoprolol", "Brand_Name": "Lopressor", "Dosage": "25 mg", "Frequency": "Twice Daily", "Duration": "Continuous", "Best_Time": "8 AM / 8 PM", "Instructions": "Take with food.", "Risk_Warning": "AVOID IF ASTHMATIC."},
            {"Condition_Key": "SVT_AFib", "Medicine_Name": "Adenosine", "Brand_Name": "Adenocard", "Dosage": "6 mg IV Push", "Frequency": "Single Dose", "Duration": "Immediate", "Best_Time": "IMMEDIATE", "Instructions": "Continuous ECG monitoring.", "Risk_Warning": "Causes temporary asystole."},
            {"Condition_Key": "Emergency_Symptomatic", "Medicine_Name": "Aspirin", "Brand_Name": "Disprin", "Dosage": "300 mg", "Frequency": "One-time", "Duration": "Emergency", "Best_Time": "IMMEDIATE", "Instructions": "Chew fully.", "Risk_Warning": "Check for allergies."}
        ]
        pd.DataFrame(med_data).to_csv(MED_DB_FILE, index=False)

    # B. Generate Patient Database
    if not os.path.exists(PATIENT_DB_FILE):
        def get_trace(base):
            trace = []
            curr = base
            for _ in range(60):
                curr += random.randint(-3, 3)
                if curr > base + 10: curr -= 2
                if curr < base - 10: curr += 2
                trace.append(curr)
            return str(trace)

        patients = [
            {"Name": "John Doe", "Age": 30, "Symptoms": "n", "Status": "resting", "Athlete": "n", "Pregnant": "n", "Location": "New York, USA", "Base_BPM": 72},
            {"Name": "Sarah Connor", "Age": 29, "Symptoms": "n", "Status": "resting", "Athlete": "n", "Pregnant": "y", "Location": "Los Angeles, USA", "Base_BPM": 105},
            {"Name": "Usain Bolt", "Age": 35, "Symptoms": "n", "Status": "resting", "Athlete": "y", "Pregnant": "n", "Location": "London, UK", "Base_BPM": 42},
            {"Name": "Walter White", "Age": 52, "Symptoms": "n", "Status": "resting", "Athlete": "n", "Pregnant": "n", "Location": "Albuquerque, USA", "Base_BPM": 175},
            {"Name": "Grandpa Joe", "Age": 78, "Symptoms": "y", "Status": "resting", "Athlete": "n", "Pregnant": "n", "Location": "Chicago, USA", "Base_BPM": 38},
            {"Name": "Rahul Sharma", "Age": 24, "Symptoms": "n", "Status": "resting", "Athlete": "n", "Pregnant": "n", "Location": "Mumbai, India", "Base_BPM": 70},
            {"Name": "Priya Patel", "Age": 45, "Symptoms": "n", "Status": "resting", "Athlete": "n", "Pregnant": "n", "Location": "Delhi, India", "Base_BPM": 115},
            {"Name": "Amit Singh", "Age": 60, "Symptoms": "y", "Status": "resting", "Athlete": "n", "Pregnant": "n", "Location": "Bangalore, India", "Base_BPM": 140},
            {"Name": "Kenji Sato", "Age": 8, "Symptoms": "n", "Status": "resting", "Athlete": "n", "Pregnant": "n", "Location": "Tokyo, Japan", "Base_BPM": 95},
            {"Name": "Camille", "Age": 28, "Symptoms": "n", "Status": "resting", "Athlete": "y", "Pregnant": "n", "Location": "Paris, France", "Base_BPM": 48}
        ]
        df = pd.DataFrame(patients)
        df["BPM_Trace"] = df["Base_BPM"].apply(get_trace)
        df.to_csv(PATIENT_DB_FILE, index=False)

# --- 3. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="Cardiac Triage", layout="wide")
    
    # Initialize Databases
    generate_databases_if_missing()
    
    st.title("Ř CARDIAC TRIAGE SYSTEM")
    st.markdown("### Intelligent Heart Health Analysis & Location Services")
    
    # Load Data
    try:
        df_patients = pd.read_csv(PATIENT_DB_FILE)
        df_meds = pd.read_csv(MED_DB_FILE)
    except:
        st.error("Database generation failed. Please refresh.")
        return

    # --- SIDEBAR INPUTS ---
    st.sidebar.header("Configuration")
    mode = st.sidebar.radio("Select Mode", ["Manual Entry", "Load Patient Database"])

    # Variables to populate
    bpm_avg = 75
    patient_name = "User"
    location = ""
    age = 30
    symptoms = False
    status = "resting"
    is_athlete = False
    is_pregnant = False
    bpm_trace = [75] * 60

    if mode == "Load Patient Database":
        patient_names = df_patients["Name"].tolist()
        selected_name = st.sidebar.selectbox("Select Patient Profile", patient_names)
        
        # Get patient data
        patient = df_patients[df_patients["Name"] == selected_name].iloc[0]
        patient_name = patient["Name"]
        bpm_trace = ast.literal_eval(patient["BPM_Trace"])
        bpm_avg = sum(bpm_trace) / len(bpm_trace)
        age = int(patient["Age"])
        symptoms = patient["Symptoms"] == 'y'
        status = patient["Status"]
        is_athlete = patient["Athlete"] == 'y'
        is_pregnant = patient["Pregnant"] == 'y'
        location = patient["Location"]
        
        st.success(f"Loaded Profile: **{patient_name}**")
        
    else:
        # Manual Inputs
        col1, col2 = st.columns(2)
        with col1:
            bpm_avg = st.number_input("Enter Heart Rate (BPM)", min_value=30, max_value=220, value=75)
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            location = st.text_input("Location (City, Country)", "New York, USA")
        with col2:
            symptoms = st.checkbox("Chest Pain / Shortness of Breath?")
            is_athlete = st.checkbox("Professional Athlete?")
            is_pregnant = st.checkbox("Pregnant?")
            status = "resting" # Simplified for manual
        
        bpm_trace = [bpm_avg] * 60

    # --- 1. VISUALIZATION ---
    st.markdown("---")
    st.subheader(f"❤️ Live Telemetry: {patient_name}")
    
    fig, ax = plt.subplots(figsize=(10, 3))
    color = 'red' if bpm_avg > 100 or bpm_avg < 60 else 'green'
    ax.plot(bpm_trace, color=color, linewidth=2, label=f'Avg BPM: {bpm_avg:.0f}')
    ax.set_ylabel('BPM')
    ax.set_xlabel('Time (seconds)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    # --- 2. DIAGNOSIS ENGINE ---
    upper_limit = 110 if is_pregnant else 100
    cond_key = "Normal"
    
    if symptoms:
        condition = "SYMPTOMATIC EMERGENCY"
        urgency = "CRITICAL (CODE RED)"
        cond_key = "Emergency_Symptomatic"
        st.error(f"## DIAGNOSIS: {condition}")
    elif status == 'resting' and bpm_avg > 150:
        condition = "Supraventricular Tachycardia (SVT)"
        urgency = "HIGH"
        cond_key = "SVT_AFib"
        st.warning(f"## DIAGNOSIS: {condition}")
    elif status == 'resting' and bpm_avg > upper_limit:
        condition = "Tachycardia (Elevated)"
        urgency = "Medium"
        cond_key = "Moderate Tachycardia"
        st.warning(f"## DIAGNOSIS: {condition}")
    elif bpm_avg < 40:
        condition = "Severe Bradycardia"
        urgency = "HIGH"
        cond_key = "Severe Bradycardia"
        st.warning(f"## DIAGNOSIS: {condition}")
    elif bpm_avg < 60 and not is_athlete:
        condition = "Bradycardia"
        urgency = "Low-Medium"
        cond_key = "Bradycardia"
        st.info(f"## DIAGNOSIS: {condition}")
    else:
        condition = "Normal Sinus Rhythm"
        urgency = "Safe"
        cond_key = "Normal"
        st.success(f"## DIAGNOSIS: {condition}")

    # --- 3. MEDICINE & REPORT ---
    try:
        row = df_meds[df_meds['Condition_Key'] == cond_key].iloc[0]
        med_info = row.to_dict()
    except:
        med_info = {"Medicine_Name": "Consult Doctor", "Brand_Name": "-", "Dosage": "-", "Frequency": "-", "Best_Time": "-", "Instructions": "-", "Risk_Warning": "-"}

    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**Urgency Level:** {urgency}")
        st.markdown(f"**Recommended Action:** {med_info['Instructions']}")
    with c2:
        st.write(f"**Medicine:** {med_info['Medicine_Name']} ({med_info['Brand_Name']})")
        st.write(f"**Dosage:** {med_info['Dosage']} | {med_info['Frequency']}")
        if med_info['Risk_Warning'] != "None":
            st.error(f"⚠️ {med_info['Risk_Warning']}")

    # --- 4. MAP GENERATION ---
    st.markdown("---")
    st.subheader("📍 Nearby Medical Services")
    
    if not API_KEY or API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
        st.warning("Please enter a valid Google Maps API Key in the code to view the map.")
    elif location and gmaps:
        try:
            with st.spinner(f"Locating {location}..."):
                geo = gmaps.geocode(location)
                if geo:
                    lat = geo[0]['geometry']['location']['lat']
                    lng = geo[0]['geometry']['location']['lng']
                    
                    # Create Map
                    m = folium.Map(location=[lat, lng], zoom_start=14)
                    folium.Marker([lat, lng], popup="Patient", icon=folium.Icon(color='blue', icon='user')).add_to(m)

                    # Add Hospitals
                    hosp = gmaps.places_nearby(location=(lat, lng), rank_by='distance', type='hospital')
                    for p in hosp.get('results', [])[:3]:
                        loc = p['geometry']['location']
                        folium.Marker(
                            [loc['lat'], loc['lng']], 
                            popup=f"🏥 {p['name']}", 
                            icon=folium.Icon(color='red', icon='plus')
                        ).add_to(m)

                    # Add Pharmacies
                    pharm = gmaps.places_nearby(location=(lat, lng), rank_by='distance', type='pharmacy')
                    for p in pharm.get('results', [])[:3]:
                        loc = p['geometry']['location']
                        folium.Marker(
                            [loc['lat'], loc['lng']], 
                            popup=f"💊 {p['name']}", 
                            icon=folium.Icon(color='green', icon='medkit', prefix='fa')
                        ).add_to(m)

                    # Render map in Streamlit
                    st_folium(m, width=700, height=500)
                else:
                    st.error("Location not found.")
        except Exception as e:
            st.error(f"Map Error: {e}")

if __name__ == "__main__":
    main()
