import os
import json
from flask import Flask, render_template, jsonify, request,redirect,send_file
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
# Initialize Text to Speech service
authenticator = IAMAuthenticator(os.getenv("IBM_WATSON_API_KEY"))
tts = TextToSpeechV1(authenticator=authenticator)
tts.set_service_url('https://api.jp-tok.text-to-speech.watson.cloud.ibm.com/instances/4b6f63a0-8daa-4dcc-82ea-877d8b7e04c6')

# Create or load the transcript data JSON file
TRANSCRIPT_FILE = 'uploads//answers.json'
if not os.path.exists(TRANSCRIPT_FILE):
    with open(TRANSCRIPT_FILE, 'w') as f:
        json.dump([], f)

if not os.path.exists('conversation_history.json'):
    with open('conversation_history.json', 'w') as f:
        json.dump([], f)

############################################VARIABLES/END POINTS#######################
ID=1032201777
firstChk = -1
jd=[
    "Machine Learning Engineer",
    "AI",
    "machine learning",
    "recent graduates",
    "dynamic",
    "supportive environment",
    "data scientists",
    "develop",
    "implement",
    "algorithms",
    "models",
    "cross-functional teams",
    "data analysis",
    "model performance",
    "machine learning pipelines",
    "data quality",
    "model scalability",
    "deployment",
    "web applications",
    "Flask",
    "front-end components",
    "HTML",
    "CSS",
    "JavaScript",
    "user interfaces",
    "code reviews",
    "code quality",
    "Python programming",
    "TensorFlow",
    "scikit-learn",
    "communication",
    "fast-paced",
    "innovative environment",
    "problem-solving",
    "Git",
    "data preprocessing",
    "feature engineering",
    "data visualization",
    "version control systems",
    "front-end frameworks",
    "entry-level salary",
    "growth opportunities",
    "health insurance",
    "dental insurance",
    "vision insurance",
    "flexible work arrangements",
    "remote work",
    "mentorship",
    "continuous learning",
    "workshops",
    "conferences",
    "company culture",
    "collaboration",
    "innovation",
    "recent graduate",
    "web development",
    "apply",
    "first steps",
    "career",
    "application",
    "resume",
    "cover letter",
    "portfolios"]
student_skills=["Python-StreamLit",
            "Python Data Science",
            "Python",
            "Machine Learning",
            "C++",
            "OOP",
            "Communication",
            "Android Studio",
            "Java",
            "NLP",
            "MySQL"]
# questions=["Who are you", "How are you", "Where Are you"]
firstPrompt=f'''You are an interviewer from a company. You are taking an interview of a candidate i.e. the User.
                STRICTLY ADHERE TO EACH AND EVERY INSTRUCTION LISTED BELOW WHILE GENERATING EACH RESPONSE.
                1. You have following arrays, job description(JD) keywords:\n {jd} and candidate/student skills: \n{student_skills}. 
                2. Ask only one question at a time. 
                3. Make sure give priority to keywords that are common in both the arrays while asking questions. 
                4. If there are any soft skills like character hobbies etc in student skills Make sure to ask questions based on them towards the end of the interview.
                5. Your goal is to simulate a real interview experience by asking the candidate a series of questions related to the job requirements. 
                6. Your interview should consist of about 8-10 questions. 
                7. After each question, you should wait for the candidate's response and use their responses, as well as the information provided earlier, to determine the follow-up questions.  
                8. Remember to focus on the skills and keywords mentioned in the job description. 
                9. Feel free to adapt your questions based on the candidate's previous answers, just like an actual interviewer would. 
                10. Your aim is to assess the candidate's suitability for the role and their compatibility with the job description. 
                11. DO NOT ANSWER THE QUESTIONS AT ALL.  **THIS IS THE MOST IMPORTANT INSTRUCTION.**
                12. If user response is blank just move on to the next question. 
                13. At end of interview just say \"911-EOI\" 
                Please begin the interview:'''
#############################################VARIABLES#######################

app = Flask(__name__)
question=''

@app.route('/')
def index():
    global question
    initial_response=getQuestion(firstPrompt)
    question=initial_response
    return render_template('interview.html', initial_response=initial_response)

################################################# OPENAI QUESTIONS GENERTION ###########################
def fire_Request(data):
    conversation = [
        {"role": "user", "content": data}
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=conversation
    )

    response = completion.choices[0].message['content']
    return response

    
def getQuestion(user_input):
    # Load conversation history from a JSON file (if it exists)
    try:
        with open('conversation_history.json', 'r') as f:
            conversation_history = json.load(f)
    except FileNotFoundError:
        conversation_history = []
    # Add user input to conversation history
    conversation_history.append({"role": "user", "content": user_input})

    # Get assistant's response using the entire conversation history as context
    assistant_response = fire_Request("\n".join('\n'+item["role"] + ": " + item["content"] for item in conversation_history))

    # Display assistant's response
    # print("AI:", assistant_response)
    parts=assistant_response.split('user:',1)
    final_response=parts[0]
    # Add assistant's response to conversation history
    conversation_history.append({"role": "assistant", "content": final_response})
    
    # Save updated conversation history to JSON file
    with open('conversation_history.json', 'w') as f:
        json.dump(conversation_history, f)
    
        
    return(final_response)



######################Next Question Method#################################

@app.route('/get_next_question', methods=['POST'])
def get_next_question():
    global question
    trans=request.json
    user_input=trans.get('transcript')
    if user_input=='':
        emptyResp=question+'\nPLEASE DO NOT GIVE AN EMPTY RESPONSE'
        return jsonify({'next_question': emptyResp, 'completed': False})
    question_half=getQuestion(user_input)
    parts=question_half.split('(Note:',1)
    question_half2=parts[0]
    parts2=question_half2.split('Note:',1)
    question=parts2[0]  
    question=question.replace('Interviewer:',' ')
    print(question)
    question=question.replace('interviewer:',' ')
    question=question.replace('Assistant:',' ')
    question=question.replace('assistant:',' ')
    question=question.replace('user\'s',' ')
    # append_transcript(question,user_input)
    if "911-EOI" in question:
        question="Thank you for taking this Interview. \n You may exit the Test using the \'Exit Test\' button in the Bottom Right corner"
        return jsonify({'next_question': question, 'completed': True})  # Interview completed
    else:
        return jsonify({'next_question': question, 'completed': False})

@app.route('/over')
def over():
    return app.send_static_file('over.html')


################### TEXT TO SPEECH #########################################
@app.route('/synthesize', methods=['POST'])
def synthesize():
    print('test1')
    request_data = request.json
    toConv = request_data.get('text')
    print(toConv)
    output_file = 'uploads/output.wav'
    print('test2')
    with open(output_file, 'wb') as audio_file:
        response = tts.synthesize(toConv, voice='en-US_KevinV3Voice', accept='audio/wav').get_result()
        audio_file.write(response.content)

    return send_file(output_file, mimetype='audio/wav') 


####################AUDIO PROCESS###########################################
@app.route('/upload', methods=['POST'])
def upload():
    audio_data = request.data  # Get the raw audio data

    if audio_data:
        # Save the audio data as a file
        audio_filename='uploads/answer.wav'
        with open(audio_filename, 'wb') as audio_file:
            audio_file.write(audio_data)

        # Call OpenAI's ASR API~
        transcript = transcribe_audio(audio_filename)
        
        # Append the transcript to the JSON file
        append_transcript(transcript)

        return jsonify({"message": "Answer transcribed and stored successfully.", "transcript": transcript})

    return jsonify({"message": "Upload failed."})

def transcribe_audio(audio_filename):
    try:
        audio_file = open(audio_filename, "rb")
        response = openai.Audio.transcribe("whisper-1", audio_file,language='en')
        transcript = response['text']
        return transcript
    except Exception as e:
        print("Error transcribing audio:", e)
        return "Transcription error."
    
def append_transcript(transcript):
    with open(TRANSCRIPT_FILE, 'r') as f:
        transcripts = json.load(f)
    
    
    new_entry = {
        "ID": ID,  # Replace with the actual ID
        "Question": question,
        "Answer": transcript
    }
    
    transcripts.append(new_entry)
    
    with open(TRANSCRIPT_FILE, 'w') as f:
        json.dump(transcripts, f, indent=4)
        
        
#######################################Calculating Scores############################################

def calculateScore(qna_data,noFace):
    query=f'''{qna_data}\n\n The above dictionary is a set of question and answer pairs from a transcribed interview. 
            Give the score based on the question and answer pair's relevance to the job description.
            Evaluate stricty for each and every pair of question and answer.
            Take the average at the end to get the final score out of 100.
            The Job Description keywords are as follows:
            {jd}
            The response should be in format: Score: 0-100
            '''
    score = fire_Request(query)
    print(score)
    parts=score.split(':')
    finalScore=float(parts[1])
    finalScore=finalScore-0.001*noFace
    return finalScore
        
#######################################END SEQUENCE##############################

@app.route('/transfer_data', methods=['POST'])
def transfer_data():
    data = request.json
    number = data.get("number")
    # Read the existing data from transfer.json (if it exists)
    existing_data = {}
    # Append noFaceDetected count to json
    noFace=number
    with open('finals/cheatCaught.json', 'r') as f:
            alred = json.load(f)
    alred[ID]=noFace
    with open('finals/cheatCaught.json', 'w') as f:
        json.dump(alred, f, indent=4) 
        
        
    ##############   
    if os.path.exists('finals//transfer.json'):
        with open('finals//transfer.json', 'r') as f:
            existing_data = json.load(f)
    
    # Read the data from answers.json
    with open(TRANSCRIPT_FILE, 'r') as f:
        answers_data = json.load(f)
     

    # Append the new entry to the existing data
    existing_data[ID] = answers_data
    
    # Write the updated data back to transfer.json
    with open('finals//transfer.json', 'w') as f:
        json.dump(existing_data, f, indent=4)
    
    ###############
    
    score=calculateScore(answers_data,noFace)
    if os.path.exists('finals//finalScores.json'):
        with open('finals//finalScores.json', 'r') as f:
            existing_scores = json.load(f)
    existing_scores[ID]=score
    with open('finals//finalScores.json', 'w') as f:
        json.dump(existing_scores, f, indent=4) 

    
    # Delete conversation_history.json
    os.remove("conversation_history.json")
    
    return jsonify({"message": "Data transferred and answers.json deleted."})

@app.route('/exit_test', methods=['POST'])
def exit_test():
    return jsonify({'completed': True})

@app.route('/terminate')
def terminate():
    # Perform any necessary actions
    # Redirect to the Streamlit login URL
    return redirect("http://localhost:8501/studentPortal")
    



if __name__ == '__main__':
    app.run(debug=True)