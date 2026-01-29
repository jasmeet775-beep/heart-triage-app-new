import pandas as pd
import folium
import matplotlib.pyplot as plt
import googlemaps
import ast
import random
import os
import webbrowser

# --- 1. SETUP & CONFIGURATION ---

API_KEY = "AIzaSyCgD-9bS0ECQEgvUHio6DCLITQmQm1FLzA"

# Initialize Google Maps Client
try:
    gmaps = googlemaps.Client(key=API_KEY)
except ValueError:
    gmaps = None
    print("⚠️ API Key missing or invalid. Map features will be disabled.")

# File Names
PATIENT_DB_FILE = "patient_database.csv"
MED_DB_FILE = "heart_medication_detailed.csv"

# --- 2. AUTOMATIC DATABASE GENERATION (If files are missing) ---

def generate_databases_if_missing():
    """Checks if CSV files exist. If not, creates them automatically."""
    
    # A. Generate Medication Database
    if not os.path.exists(MED_DB_FILE):
        print("⚙️ Generating Medication Database...")
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
        print("⚙️ Generating Patient Database...")
        
        def get_trace(base):
            trace = []
            curr = base
            for _ in range(60):
                curr += random.randint(-3, 3)
                if curr > base + 10:
                    curr -= 2
                if curr < base - 10:
                    curr += 2
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

def check_heart_health():
    # Ensure databases exist before running
    generate_databases_if_missing()
    
    # Load Data
    df_patients = pd.read_csv(PATIENT_DB_FILE)
    df_meds = pd.read_csv(MED_DB_FILE)

    print("\n" + "="*50)
    print("       ❤️ CARDIAC TRIAGE SYSTEM (VS CODE EDITION)")
    print("="*50)
    
    mode = input("Select Mode: \n1. Manual Entry \n2. Load Patient from Database\n>>> Enter 1 or 2: ").strip()

    # Variables
    bpm_avg = 75
    patient_name = "Manual User"
    location = ""
    age = 0
    symptoms = False
    status = "resting"
    is_athlete = False
    is_pregnant = False
    bpm_trace = [75] * 60
    
    # --- INPUT LOGIC ---
    if mode == '2':
        print(f"\n--- AVAILABLE PATIENT PROFILES ---")
        print(df_patients[["Name", "Location"]].to_string())
        try:
            p_idx = int(input("\n>>> Enter Patient ID (0-9): "))
            if 0 <= p_idx < len(df_patients):
                patient = df_patients.iloc[p_idx]
                
                bpm_trace = ast.literal_eval(patient["BPM_Trace"])
                bpm_avg = sum(bpm_trace) / len(bpm_trace)
                age = int(patient["Age"])
                symptoms = patient["Symptoms"].lower() == 'y'
                status = patient["Status"]
                is_athlete = patient["Athlete"].lower() == 'y'
                is_pregnant = patient["Pregnant"].lower() == 'y'
                location = patient["Location"]
                patient_name = patient["Name"]
            else:
                print("❌ Invalid ID. Using default values.")
        except Exception as e:
            print(f"❌ Error loading patient: {e}")
            return
    else:
        # Manual
        try:
            bpm_avg = int(input("Enter BPM: "))
            bpm_trace = [bpm_avg] * 60
            age = int(input("Age: "))
            symptoms = input("Symptoms (y/n): ").lower() == 'y'
            location = input("Location (City, Country): ").strip()
            status, is_athlete, is_pregnant = "resting", False, False
        except ValueError:
            print("❌ Invalid input data.")
            return

    # --- 1. PLOT GRAPH (Opens in a pop-up window in VS Code) ---
    print("\n📊 Generating Heart Rate Graph...")
    try:
        plt.figure(figsize=(10, 4))
        color = 'red' if bpm_avg > 100 or bpm_avg < 60 else 'green'
        plt.plot(bpm_trace, color=color, linewidth=2, label=f'Avg BPM: {bpm_avg:.0f}')
        plt.title(f'Live Telemetry: {patient_name}')
        plt.xlabel('Time (seconds)')
        plt.ylabel('BPM')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"❌ Graph Error: {e}")

    # --- 2. DIAGNOSIS ENGINE ---
    upper_limit = 110 if is_pregnant else 100
    cond_key = "Normal"
    condition = "Normal Sinus Rhythm"
    urgency = "Safe"
    
    if symptoms:
        condition = "SYMPTOMATIC EMERGENCY"
        urgency = "CRITICAL (CODE RED)"
        cond_key = "Emergency_Symptomatic"
    elif status == 'resting' and bpm_avg > 150:
        condition = "Supraventricular Tachycardia (SVT)"
        urgency = "HIGH"
        cond_key = "SVT_AFib"
    elif status == 'resting' and bpm_avg > upper_limit:
        condition = "Tachycardia (Elevated)"
        urgency = "Medium"
        cond_key = "Moderate Tachycardia"
    elif bpm_avg < 40:
        condition = "Severe Bradycardia"
        urgency = "HIGH"
        cond_key = "Severe Bradycardia"
    elif bpm_avg < 60 and not is_athlete:
        condition = "Bradycardia"
        urgency = "Low-Medium"
        cond_key = "Bradycardia"

    # --- 3. MEDICINE LOOKUP ---
    med_info = {"Name": "Consult Doctor", "Brand": "-", "Dose": "-", "Freq": "-", "Time": "-", "Instr": "-", "Risk": "-"}
    try:
        med_rows = df_meds[df_meds['Condition_Key'] == cond_key]
        if not med_rows.empty:
            row = med_rows.iloc[0]
            med_info = {
                "Name": row['Medicine_Name'], "Brand": row['Brand_Name'],
                "Dose": row['Dosage'], "Freq": row['Frequency'],
                "Time": row['Best_Time'], "Instr": row['Instructions'],
                "Risk": row['Risk_Warning']
            }
    except Exception as e:
        print(f"⚠️ Medicine lookup error: {e}")

    # --- 4. MAP GENERATION (Saves to HTML & Opens Browser) ---
    if location and gmaps:
        try:
            print(f"🌍 Locating {location} and finding nearby services...")
            geo = gmaps.geocode(location)
            if geo:
                lat = geo[0]['geometry']['location']['lat']
                lng = geo[0]['geometry']['location']['lng']
                
                # Create Map
                m = folium.Map(location=[lat, lng], zoom_start=14)
                folium.Marker([lat, lng], popup="<b>Patient Location</b>", icon=folium.Icon(color='blue', icon='user')).add_to(m)

                # Add Hospitals (Red)
                try:
                    hosp = gmaps.places_nearby(location=(lat, lng), rank_by='distance', type='hospital')
                    for p in hosp.get('results', [])[:3]:
                        loc = p['geometry']['location']
                        link = f"https://www.google.com/maps/search/?api=1&query={loc['lat']},{loc['lng']}"
                        folium.Marker([loc['lat'], loc['lng']], popup=f"🏥 <b>{p['name']}</b><br><a href='{link}' target='_blank'>Navigate</a>", icon=folium.Icon(color='red', icon='plus')).add_to(m)
                except Exception as e:
                    print(f"⚠️ Could not fetch hospitals: {e}")

                # Add Pharmacies (Green)
                try:
                    pharm = gmaps.places_nearby(location=(lat, lng), rank_by='distance', type='pharmacy')
                    for p in pharm.get('results', [])[:3]:
                        loc = p['geometry']['location']
                        link = f"https://www.google.com/maps/search/?api=1&query={loc['lat']},{loc['lng']}"
                        folium.Marker([loc['lat'], loc['lng']], popup=f"💊 <b>{p['name']}</b><br><a href='{link}' target='_blank'>Navigate</a>", icon=folium.Icon(color='green', icon='medkit', prefix='fa')).add_to(m)
                except Exception as e:
                    print(f"⚠️ Could not fetch pharmacies: {e}")

                # SAVE AND OPEN
                map_filename = "medical_map.html"
                m.save(map_filename)
                webbrowser.open(map_filename)
                print(f"✅ Map generated and opened in browser: {map_filename}")

        except Exception as e:
            print(f"❌ Map Error: {e}")
    elif not gmaps:
        print("⚠️ Map skipped (API Key missing).")

    # --- 5. FINAL REPORT ---
    print("\n" + "="*60)
    print(f"📄 DETAILED MEDICAL REPORT | Patient: {patient_name}")
    print("="*60)
    print(f"DIAGNOSIS  : {condition}")
    print(f"URGENCY    : {urgency}")
    print("-" * 60)
    print(f"💊 MEDICATION PROTOCOL")
    print(f"Medicine   : {med_info['Name']} ({med_info['Brand']})")
    print(f"Dosage     : {med_info['Dose']}")
    print(f"Frequency  : {med_info['Freq']}")
    print(f"Best Time  : {med_info['Time']}")
    print("-" * 60)
    print(f"📝 INSTRUCTIONS: {med_info['Instr']}")
    print(f"⚠️ WARNING: {med_info['Risk']}")
    print("="*60 + "\n")

# --- RUN APPLICATION ---
if __name__ == "__main__":
    check_heart_health()