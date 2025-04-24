import streamlit as st
import datetime
import pandas as pd
import uuid
from supabase import create_client, Client

# --- Supabase Config ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Insert Data to Supabase ---
def insert_adherence_data_supa(patient_id, glucose, state, meal_taken, activity,
                                meal_time, reading_time, recommendation,
                                adherence, activity_done, meal_taken_feedback):
    supabase.table("adherence").insert({
        "patient_id": patient_id,
        "glucose": glucose,
        "state": state,
        "meal_taken": meal_taken,
        "activity": activity,
        "meal_time": str(meal_time),
        "reading_time": str(reading_time),
        "recommendation": recommendation,
        "adherence": adherence,
        "activity_done": activity_done,
        "meal_taken_feedback": meal_taken_feedback
    }).execute()

# --- Export Data from Supabase ---
def export_adherence_data_supa(patient_id):
    response = supabase.table("adherence").select("*").eq("patient_id", patient_id).execute()
    return pd.DataFrame(response.data)

# --- Generate Recommendation ---
def generate_recommendation(glucose, state, activity, meal_taken, meal_time, reading_time):
    try:
        meal_time_obj = meal_time if isinstance(meal_time, datetime.time) else datetime.datetime.strptime(meal_time, "%H:%M").time()
        reading_time_obj = reading_time if isinstance(reading_time, datetime.time) else datetime.datetime.strptime(reading_time, "%H:%M").time()
        meal_dt = datetime.datetime.combine(datetime.date.today(), meal_time_obj)
        reading_dt = datetime.datetime.combine(datetime.date.today(), reading_time_obj)
        diff_minutes = (reading_dt - meal_dt).total_seconds() / 60.0
    except Exception:
        diff_minutes = None

    if state == "Fasting":
        if glucose < 70:
            return "Low blood sugar – consider eating something."
        elif glucose > 130:
            return "High fasting glucose – consult your physician."
        else:
            return "Glucose level is normal for fasting."
    elif state == "Post-meal":
        if diff_minutes is not None:
            if diff_minutes < 120:
                return "High post-meal glucose – try light exercise or consult doctor." if glucose > 180 else "Glucose is acceptable post meal."
            else:
                return "Reading taken long after meal – interpret cautiously."
        else:
            return "Could not determine time difference. Please check inputs."
    else:
        return "General advice: monitor regularly and maintain healthy lifestyle."

# --- Generate or Retrieve Patient ID ---
def get_patient_id():
    if 'patient_id' not in st.session_state:
        st.session_state['patient_id'] = str(uuid.uuid4())[:8]
    return st.session_state['patient_id']

# --- Streamlit App ---
def main():
    st.set_page_config(page_title="Glucose Tracker", layout="centered")
    st.title("🩸 Glucose Reading & Adherence Tracker")

    # Patient ID Section
    st.sidebar.header("🔐 Patient Info")
    use_existing = st.sidebar.checkbox("Enter Existing Patient ID")
    if use_existing:
        patient_id = st.sidebar.text_input("Enter your Patient ID")
        if patient_id:
            st.session_state['patient_id'] = patient_id
    else:
        patient_id = get_patient_id()
        st.sidebar.success(f"Your Patient ID: {patient_id}")

    with st.form("glucose_form"):
        glucose = st.number_input("Enter your glucose reading (mg/dL)", min_value=40, max_value=500)
        state = st.selectbox("What is your state?", ["Fasting", "Post-meal"])
        reading_time = st.time_input("Time of glucose reading")
        meal_taken = st.radio("Did you take a meal?", ["Yes", "No"])

        if meal_taken == "Yes":
            meal_time = st.time_input("What time did you take the meal?")
        else:
            meal_time = reading_time

        activity = st.radio("Did you do any physical activity?", ["Yes", "No"])

        submitted = st.form_submit_button("Submit and Get Recommendation")
        if submitted:
            recommendation = generate_recommendation(glucose, state, activity, meal_taken, meal_time, reading_time)
            st.success(f"💡 Recommendation: {recommendation}")

            st.write("---")
            st.subheader("📋 Adherence Feedback")
            adherence = st.radio("Did you follow the recommendation?", ["Yes", "No"])
            activity_done = st.radio("Did you perform physical activity if suggested?", ["Yes", "No"])
            meal_taken_feedback = st.text_input("Any comment on the meal you took?")

            insert_adherence_data_supa(
                patient_id, glucose, state, meal_taken, activity,
                meal_time, reading_time, recommendation,
                adherence, activity_done, meal_taken_feedback
            )

            st.success("✅ Your response has been saved!")

    st.write("---")
    st.subheader("📤 Export Your Records")
    if st.button("Download My CSV"):
        csv_data = export_adherence_data_supa(get_patient_id())
        if csv_data.empty:
            st.warning("No data found for your Patient ID.")
        else:
            st.download_button("Download CSV", data=csv_data.to_csv(index=False), file_name=f"adherence_{get_patient_id()}.csv", mime="text/csv")

if __name__ == "__main__":
    main()
