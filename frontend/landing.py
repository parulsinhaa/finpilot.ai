"""
FinPilot AI — Landing page redirect wrapper.
The full .com landing page is index.html (served separately).
This shows a Streamlit pre-login page.
"""

import streamlit as st

def render_landing():
    from frontend.login import render_landing as _render
    _render()