import streamlit as st
import requests as rq
import numpy as np

pageTitle = "TEMP"
st.set_page_config(
    page_title=pageTitle,
    menu_items={
        "About": "HCI Project 2"
    }
)

st.title(pageTitle)
