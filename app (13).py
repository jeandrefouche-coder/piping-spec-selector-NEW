import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Amplats Piping Spec Selector", layout="wide")

st.title("Amplats Piping Specification Selector")
st.markdown("Filter by commodity, material, and other criteria to find the required specification.")

# Load data
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    
    # User's file names
    headers_path = os.path.join(base, "Headers.xlsx")
    fittings_path = os.path.join(base, "Fittings.xlsx")
    piping_path = os.path.join(base, "Piping.xlsx")
    bends_path = os.path.join(base, "Bends.xlsx")
    joints_path = os.path.join(base, "Joints.xlsx")
    bolting_path = os.path.join(base, "Bolting.xlsx")
    gaskets_path = os.path.join(base, "Gaskets.xlsx")
    valves_path = os.path.join(base, "Equipment & Valve.xlsx")
    
    if not os.path.exists(headers_path):
        st.error("Data file not found: Headers.xlsx\n\nPlease place the Excel files in the same folder as app.py.")
        st.stop()
    
    headers = pd.read_excel(headers_path)
    
    # Load others if they exist
    fittings = pd.read_excel(fittings_path) if os.path.exists(fittings_path) else pd.DataFrame()
    piping = pd.read_excel(piping_path) if os.path.exists(piping_path) else pd.DataFrame()
    bends = pd.read_excel(bends_path) if os.path.exists(bends_path) else pd.DataFrame()
    joints = pd.read_excel(joints_path) if os.path.exists(joints_path) else pd.DataFrame()
    bolting = pd.read_excel(bolting_path) if os.path.exists(bolting_path) else pd.DataFrame()
    gaskets = pd.read_excel(gaskets_path) if os.path.exists(gaskets_path) else pd.DataFrame()
    valves = pd.read_excel(valves_path) if os.path.exists(valves_path) else pd.DataFrame()
    
    return headers, fittings, piping, bends, joints, bolting, gaskets, valves

headers, fittings, piping, bends, joints, bolting, gaskets, valves = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Commodity filter
commodities = []
for c in headers['Commodity / Line Service'].dropna().unique():
    commodities.extend([x.strip() for x in str(c).split(',')])
commodities = sorted(set(commodities))
selected_commodity = st.sidebar.selectbox("Commodity / Service", ["All"] + commodities)

# Material filter
materials = sorted(headers['General Material'].dropna().unique())
selected_material = st.sidebar.selectbox("General Material", ["All"] + materials)

# Design Code filter
codes = sorted(headers['Design Code'].dropna().unique())
selected_code = st.sidebar.selectbox("Design Code", ["All"] + codes)

# Apply filters
filtered = headers.copy()
if selected_commodity != "All":
    filtered = filtered[filtered['Commodity / Line Service'].str.contains(selected_commodity, case=False, na=False)]
if selected_material != "All":
    filtered = filtered[filtered['General Material'].str.contains(selected_material, case=False, na=False)]
if selected_code != "All":
    filtered = filtered[filtered['Design Code'] == selected_code]

st.subheader(f"Matching Specifications ({len(filtered)} found)")

if len(filtered) > 0:
    st.dataframe(filtered, use_container_width=True, height=400)
    
    # Detail view
    if len(filtered) > 0:
        selected_spec = st.selectbox("Select a spec for more details", filtered['Spec'].tolist())
        detail = filtered[filtered['Spec'] == selected_spec].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Header Details")
            for col in detail.index:
                if pd.notna(detail[col]) and str(detail[col]).strip():
                    st.write(f"**{col}:** {detail[col]}")
        
        with col2:
            st.markdown("### Related Data")
            if not valves.empty:
                v = valves[valves['Spec Code'] == selected_spec]
                if not v.empty:
                    st.write("**Valves / Equipment:**")
                    st.dataframe(v[['Valve Type', 'Size Range', 'Description', 'Item Code']], use_container_width=True)
else:
    st.info("No specifications match the selected filters. Try broadening your search.")

st.sidebar.markdown("---")
st.sidebar.caption("Data extracted from Amplats APP001 piping material specifications.")
