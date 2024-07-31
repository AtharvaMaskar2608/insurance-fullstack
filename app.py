import streamlit as st

st.title("Commission Calculator!")

# Input
with st.form("my-form"):
    st.text_input("Enter")

    st.form_submit_button("Calculate")