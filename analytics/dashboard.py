import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import get_all_violations, get_safety_index

st.set_page_config(
    page_title="VioSense - AI Traffic Enforcement",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #CC0000;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    conn = sqlite3.connect("database/viosense.db")
    try:
        df = pd.read_sql_query("SELECT * FROM violations ORDER BY timestamp DESC", conn)
    except:
        df = pd.DataFrame()
    try:
        locations_df = pd.read_sql_query("SELECT * FROM locations ORDER BY safety_score ASC", conn)
    except:
        locations_df = pd.DataFrame()
    try:
        vehicles_df = pd.read_sql_query("SELECT * FROM vehicles ORDER BY total_violations DESC", conn)
    except:
        vehicles_df = pd.DataFrame()
    conn.close()
    return df, locations_df, vehicles_df

def add_demo_data():
    sys.path.append('.')
    from database.models import save_violation, update_location_safety
    import random
    locations = ["MG Road", "Silk Board", "Whitefield", "Koramangala", "Brigade Road", "Hebbal"]
    violations = [
        ("No Helmet", 7.2, "HIGH", "motorcycle"),
        ("Triple Riding", 6.5, "HIGH", "motorcycle"),
        ("Wrong Side Driving", 9.4, "CRITICAL", "car"),
        ("Red Light Jump", 8.5, "CRITICAL", "car"),
        ("Illegal Parking", 4.1, "MEDIUM", "car"),
        ("No Seatbelt", 6.8, "HIGH", "car"),
        ("Stop Line Violation", 6.0, "MEDIUM", "motorcycle"),
    ]
    plates = ["KA01AB1234", "MH02CD5678", "DL03EF9012", "TN04GH3456", "UP05IJ7890", "KA06KL2345"]
    for _ in range(30):
        v = random.choice(violations)
        loc = random.choice(locations)
        plate = random.choice(plates)
        save_violation({
            'vehicle_type': v[3],
            'plate_number': plate,
            'violation_type': v[0],
            'severity': v[1],
            'risk_level': v[2],
            'confidence': round(random.uniform(85, 99), 1),
            'location': loc
        })
        update_location_safety(loc, v[1])
    st.success("Demo data loaded successfully!")
    st.rerun()

st.markdown('<div class="main-header">VioSense AI Traffic Enforcement Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Violation Detection | Evidence Generation | Predictive Analytics</div>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/color/96/traffic-light.png", width=80)
    st.title("VioSense")
    st.markdown("---")
    page = st.radio("Navigation", [
        "Live Dashboard",
        "Violation Records",
        "Safety Index",
        "Repeat Offenders",
        "Officer Deployment Planner",
        "Hotspot Prediction",
        "Upload & Detect"
    ])
    st.markdown("---")
    if st.button("Load Demo Data", type="primary"):
        add_demo_data()
    st.markdown("---")
    st.caption("Gridlock Hackathon 2.0")
    st.caption("Theme 3: Computer Vision")

df, locations_df, vehicles_df = load_data()

# PAGE 1: Live Dashboard
if page == "Live Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    total = len(df)
    critical = len(df[df['risk_level'] == 'CRITICAL']) if not df.empty else 0
    high = len(df[df['risk_level'] == 'HIGH']) if not df.empty else 0
    avg_conf = round(df['confidence'].mean(), 1) if not df.empty else 0
    col1.metric("Total Violations", total, "+5 today")
    col2.metric("Critical Risk", critical, delta_color="inverse")
    col3.metric("High Risk", high, delta_color="inverse")
    col4.metric("Avg AI Confidence", f"{avg_conf}%")
    st.markdown("---")
    if df.empty:
        st.warning("No data yet! Click 'Load Demo Data' in sidebar.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Violations by Type")
            v_counts = df['violation_type'].value_counts().reset_index()
            v_counts.columns = ['Violation', 'Count']
            fig = px.bar(v_counts, x='Count', y='Violation', orientation='h',
                        color='Count', color_continuous_scale='Reds', title="Most Common Violations")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Violations by Location")
            if not locations_df.empty:
                fig2 = px.pie(locations_df, values='total_violations', names='location_name',
                             title="Hotspot Distribution", color_discrete_sequence=px.colors.sequential.Reds_r)
                st.plotly_chart(fig2, use_container_width=True)
        st.subheader("Risk Level Distribution")
        if 'risk_level' in df.columns:
            risk_counts = df['risk_level'].value_counts().reset_index()
            risk_counts.columns = ['Risk', 'Count']
            colors_map = {'CRITICAL': '#FF0000', 'HIGH': '#FF8C00', 'MEDIUM': '#FFD700', 'LOW': '#00FF00'}
            fig3 = px.bar(risk_counts, x='Risk', y='Count', color='Risk',
                         color_discrete_map=colors_map, title="Violations by Risk Level")
            st.plotly_chart(fig3, use_container_width=True)

# PAGE 2: Violation Records
elif page == "Violation Records":
    st.subheader("Searchable Violation Database")
    if df.empty:
        st.warning("No records found. Click 'Load Demo Data' in sidebar.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            search_plate = st.text_input("Search by Plate Number", placeholder="e.g. KA01AB1234")
        with col2:
            violation_filter = st.selectbox("Filter by Violation", ["All"] + list(df['violation_type'].unique()))
        with col3:
            risk_filter = st.selectbox("Filter by Risk", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        filtered = df.copy()
        if search_plate:
            filtered = filtered[filtered['plate_number'].str.contains(search_plate.upper(), na=False)]
        if violation_filter != "All":
            filtered = filtered[filtered['violation_type'] == violation_filter]
        if risk_filter != "All":
            filtered = filtered[filtered['risk_level'] == risk_filter]
        st.markdown(f"**{len(filtered)} records found**")
        display_cols = ['violation_id', 'plate_number', 'vehicle_type', 'violation_type',
                       'severity', 'risk_level', 'confidence', 'location', 'timestamp']
        available = [c for c in display_cols if c in filtered.columns]
        st.dataframe(filtered[available], use_container_width=True, height=400)
        csv = filtered.to_csv(index=False)
        st.download_button("Download Records as CSV", csv, "violations.csv", "text/csv")

# PAGE 3: Safety Index
elif page == "Safety Index":
    st.subheader("City Safety Index — Bengaluru")
    st.caption("Areas ranked by AI-computed safety score (0-100)")
    if locations_df.empty:
        st.warning("No location data. Click 'Load Demo Data' in sidebar.")
    else:
        for _, row in locations_df.iterrows():
            score = row['safety_score']
            name = row['location_name']
            total_v = row['total_violations']
            if score >= 70:
                emoji = "🟢"
            elif score >= 40:
                emoji = "🟠"
            else:
                emoji = "🔴"
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"{emoji} **{name}**")
                st.progress(int(score) / 100)
            with col2:
                st.metric("Safety Score", f"{score:.0f}/100")
            with col3:
                st.metric("Violations", total_v)
            st.markdown("---")

# PAGE 4: Repeat Offenders
elif page == "Repeat Offenders":
    st.subheader("Repeat Offender Tracking System")
    if vehicles_df.empty:
        st.warning("No vehicle data. Click 'Load Demo Data' in sidebar.")
    else:
        repeat = vehicles_df[vehicles_df['total_violations'] >= 2]
        st.markdown(f"**{len(repeat)} repeat offenders identified**")
        for _, row in repeat.iterrows():
            risk = row['risk_score']
            if risk >= 7:
                status = "HABITUAL OFFENDER"
            elif risk >= 4:
                status = "FREQUENT OFFENDER"
            else:
                status = "REPEAT OFFENDER"
            with st.expander(f"Plate: {row['plate_number']} | Violations: {row['total_violations']} | {status}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Violations", row['total_violations'])
                col2.metric("Risk Score", f"{row['risk_score']:.1f}/10")
                col3.metric("Status", status)
                st.caption(f"First seen: {row['first_seen']}")
                st.caption(f"Last seen: {row['last_seen']}")

# PAGE 5: Officer Deployment Planner
elif page == "Officer Deployment Planner":
    st.subheader("AI Enforcement Recommendation Engine")
    st.caption("AI suggests optimal officer deployment based on violation patterns")
    if locations_df.empty:
        st.warning("No data. Click 'Load Demo Data' in sidebar.")
    else:
        deployment_data = []
        for _, row in locations_df.iterrows():
            score = row['safety_score']
            violations = row['total_violations']
            name = row['location_name']
            if score <= 20:
                risk = "CRITICAL"
                officers = 5
                time = "6PM - 9PM"
                action = "Immediate deployment required"
                emoji = "🔴"
            elif score <= 40:
                risk = "HIGH"
                officers = 3
                time = "5PM - 8PM"
                action = "Increase patrol frequency"
                emoji = "🟠"
            elif score <= 60:
                risk = "MEDIUM"
                officers = 2
                time = "8AM - 10AM"
                action = "Standard monitoring"
                emoji = "🟡"
            else:
                risk = "LOW"
                officers = 1
                time = "Peak hours only"
                action = "Regular patrol"
                emoji = "🟢"
            deployment_data.append({
                'Location': f"{emoji} {name}",
                'Risk Level': risk,
                'Officers Needed': officers,
                'Peak Time': time,
                'Violations': violations,
                'Recommended Action': action
            })
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Officers Needed", sum([d['Officers Needed'] for d in deployment_data]))
        col2.metric("Critical Zones", len([d for d in deployment_data if d['Risk Level'] == 'CRITICAL']))
        col3.metric("High Risk Zones", len([d for d in deployment_data if d['Risk Level'] == 'HIGH']))
        st.markdown("---")
        st.markdown("### Deployment Plan")
        deploy_df = pd.DataFrame(deployment_data)
        st.dataframe(deploy_df, use_container_width=True, height=300)
        st.markdown("---")
        st.markdown("### Critical & High Risk Zones")
        for data in deployment_data:
            if data['Risk Level'] in ['CRITICAL', 'HIGH']:
                with st.expander(f"{data['Location']} | Officers: {data['Officers Needed']} | {data['Risk Level']}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Officers", data['Officers Needed'])
                    col2.metric("Peak Time", data['Peak Time'])
                    col3.metric("Violations", data['Violations'])
                    st.error(f"Action: {data['Recommended Action']}")
        csv = deploy_df.to_csv(index=False)
        st.download_button("Download Deployment Plan", csv, "deployment_plan.csv", "text/csv")

# PAGE 6: Hotspot Prediction
elif page == "Hotspot Prediction":
    st.subheader("Tomorrow's Predicted Violation Hotspots")
    st.caption("AI predicts where violations will occur tomorrow based on historical patterns")
    sys.path.append('.')
    from analytics.hotspot_predictor import predict_hotspots
    from genai.summary import generate_ai_summary
    predictions = predict_hotspots()
    col1, col2, col3 = st.columns(3)
    critical = len([p for p in predictions if p['risk_level'] == 'CRITICAL'])
    high = len([p for p in predictions if p['risk_level'] == 'HIGH'])
    total_officers = sum([p['officers_needed'] for p in predictions])
    col1.metric("Critical Zones Tomorrow", critical)
    col2.metric("High Risk Zones", high)
    col3.metric("Total Officers Needed", total_officers)
    st.markdown("---")
    st.markdown("### Zone-wise Predictions")
    for p in predictions:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            st.markdown(f"{p['emoji']} **{p['location']}**")
        with col2:
            st.metric("Risk", p['risk_level'])
        with col3:
            st.metric("Expected Violations", p['predicted_violations'])
        with col4:
            st.metric("Officers Needed", p['officers_needed'])
        st.progress(min(p['risk_score'] / 10, 1.0))
        st.markdown("---")
    st.markdown("### AI Generated Weekly Report")
    if st.button("Generate AI Report", type="primary"):
        with st.spinner("AI analyzing violation patterns..."):
            summary = generate_ai_summary()
        st.code(summary)

# PAGE 7: Upload & Detect
elif page == "Upload & Detect":
    st.subheader("Upload Traffic Image for Analysis")
    location = st.selectbox("Select Location", [
        "MG Road", "Silk Board", "Whitefield",
        "Koramangala", "Brigade Road", "Hebbal",
        "Electronic City", "Indiranagar"
    ])
    uploaded_file = st.file_uploader("Upload Traffic Image", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        import cv2
        from main_pipeline import process_image
        img_path = f"static/{uploaded_file.name}"
        os.makedirs("static", exist_ok=True)
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.image(uploaded_file, caption="Uploaded Image", width=400)
        if st.button("Analyze Image", type="primary"):
            with st.spinner("VioSense AI analyzing image..."):
                results = process_image(img_path, location)
            if results:
                st.success(f"{len(results)} violation(s) detected!")
                annotated_path = "static/annotated_result.jpg"
                if os.path.exists(annotated_path):
                    st.image(annotated_path, caption="AI Annotated Result", use_column_width=True)
                for r in results:
                    st.error(f"Violation: {r['violation']}")
                    st.info(f"Plate: {r['plate']}")
                    st.info(f"Evidence ID: {r['violation_id']}")
                    if os.path.exists(r['pdf']):
                        with open(r['pdf'], 'rb') as f:
                            st.download_button(
                                "Download Evidence PDF",
                                f.read(),
                                f"{r['violation_id']}.pdf",
                                "application/pdf"
                            )

if __name__ == "__main__":
    pass