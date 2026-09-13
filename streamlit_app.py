import streamlit as st

st.set_page_config(
    page_title="Your App Title",
    initial_sidebar_state="collapsed"
)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Main Title")
st.header("Section Header")
st.subheader("Subsection")
st.markdown("### Custom Markdown Header")
st.text("Regular text content here")