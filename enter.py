import streamlit as st
from Admin import login
from Student import studentPortal
from streamlit_option_menu import option_menu

Roles = {"Admin" : login, "Student": studentPortal}

with st.sidebar:
    role = option_menu(
        menu_title = "Main Menu",
        options = ["Admin","Student"],
        icons = ["house","person-workspace"],
        menu_icon="cast",
        default_index = 0,
        orientation = "horizontal"
    )
    
def homepage():
    st.title("AI Recruiter")
    st.write("Welcome to the AI Recruitment Portal")
    

if role in Roles:
    Roles[role].page()
else:
    homepage()
    
