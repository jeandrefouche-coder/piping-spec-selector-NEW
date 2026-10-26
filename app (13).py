import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Amplats Piping Spec Selector", layout="wide")

st.title("Amplats Piping Specification Selector")
st.markdown("Filter by commodity, material, and other criteria to find the required specification.")

# Load data
@st.cache_data
def load_data():
    base = "/workspace/artifacts"
    headers = pd.read_excel(os.path.join(base, "Amplats_Headers_All_Specs.xlsx"))
    # Load other sheets if needed
    try:
        valves = pd.read_excel(os.path.join(base, "All_Specs_Valves_Complete.xlsx"))
    except:
        valves = pd.DataFrame()
    try:
        pipes = pd.read_excel(os.path.join(base, "Amplats_Pipes_Expanded.xlsx"))
    except:
        pipes = pd.DataFrame()
    return headers, valves, pipes

headers, valves, pipes = load_data()

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
