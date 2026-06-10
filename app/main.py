"""Streamlit application entrypoint."""

import sys
import os

# Ensure project root is on PYTHONPATH so all packages resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="AI Code Review Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.dashboard import render_dashboard

render_dashboard()