import os
import streamlit as st
import webbrowser
import subprocess
import time

flask_start= None
testDone=False
startFlag=False

# Simple hardcoded username and password for demo purposes
VALID_USERNAME = "a"
VALID_PASSWORD = "b"

def open_flask_app():
    try:
        app_dir = "Student/INTERVIEWER"  # Replace this with the actual path to your Flask app directory
        global flask_start,testDone
        # Change directory to the Flask app directory
        os.chdir(app_dir)
        # Replace the command with the appropriate command to run your Flask app
        flask_start = subprocess.Popen(["python", "test.py"])
        testDone=True
    except Exception as e:
        st.error(f"An error occurred: {e}")



def open_url(url):
    # Open the URL in a new tab/window
    webbrowser.open_new_tab(url)
        
def stop_flask_subprocess():
    # global flask_start
    flask_start.terminate()



def login():
    st.title("Login")
    

    username = st.text_input("Enter UID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
        
                    st.session_state.logged_in = True
                
        else:
            st.error("Invalid credentials. Please try again.")


def page():
    global startFlag
    # Check if the 'logged_in' session state variable exists and is True
    if hasattr(st.session_state, "logged_in") and st.session_state.logged_in:
        st.title("AI Proctored Screening/Interview")
        st.title("Test Instructions")  
        st.markdown('''
                    Instructions for AI Proctored Interview:

Welcome to the AI proctored interview! Please read the following instructions carefully before proceeding:

1. Click on "Start Test" to begin the interview. Once you start the test, you cannot go back or restart.

2. Make sure You have opened this window in your default browser.

3. During the interview, the AI will present each question. The question will be displayed as written text on the screen and will be read out loud by the AI.

4. You are required to answer each question strictly in the English language. Speak clearly and confidently.

5. After you finish recording your answer, the transcript of your spoken response will be shown on the screen. You will have one chance to re-record your answer if needed.

6. Use the "Next Question" button to proceed to the next question after completing your response. Once you move to the next question, you cannot go back.

7. There is no option to clear your answer. Pre-emptive decision-making is vital in any role and company.

8. On the left-hand side, you can navigate between questions using the provided pane.

9. On the right side, your camera feed will be shown. Violations will be recorded if you look away from the screen or if there is more than one face in the camera view.

10. Exiting full-screen mode during the interview will also be considered a violation.

11. If you receive more than 5 violations, you will receive a message indicating disqualification. However, you can still complete the test if you wish to do so or finish as it is. Once you receive the disqualification message, you are by default out of the selection process.

12. Click on "Start Test" if you have read these instructions clearly and agree to follow them.

Remember, the AI proctored interview aims to assess your honesty, skills and determination. Good luck with your interview!
                    
                     ''')
        
        if st.button("Start Test"):
        # Open the webpage in a new tab/window
            open_flask_app()
            time.sleep(2)
            open_url("http://127.0.0.1:5000")
        
        if testDone:
            if st.button("Test Completed"):
                startFlag=True
                stop_flask_subprocess()
                st.session_state.logged_in = False
                login()
                

    else:
        login()



