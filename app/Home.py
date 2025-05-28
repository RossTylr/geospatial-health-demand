import streamlit as st

st.set_page_config(
    page_title="Geospatial Health Demand",
    page_icon="🌍",
    layout="wide"
)

st.title("Welcome to the Geospatial Health Demand App!")
st.sidebar.success("Select a page above.")

st.markdown(
    """
    This application provides insights into geospatial health demand.
    Navigate through the different pages using the sidebar to explore various analyses and visualizations.

    **👈 Select a page from the sidebar** to get started!

    ### Project Structure
    This app is built within the `geospatial-health-demand` project, leveraging its existing data processing
    and analytical capabilities.
    """
)
