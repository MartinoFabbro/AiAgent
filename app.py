import os
import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from agents.agent import Agent

st.set_page_config(
    page_title="AI Travel Companion",
    page_icon="✈️",  # Use your preferred icon
    layout="wide"
)

def populate_envs(sender_email, receiver_email, subject):
    os.environ['FROM_EMAIL'] = sender_email
    os.environ['TO_EMAIL'] = receiver_email
    os.environ['EMAIL_SUBJECT'] = subject

def send_email(sender_email, receiver_email, subject, thread_id):
    try:
        populate_envs(sender_email, receiver_email, subject)
        config = {'configurable': {'thread_id': thread_id}}
        st.session_state.agent.graph.invoke(None, config=config)
        st.success('Email sent successfully!')
        for key in ['travel_info', 'thread_id']:
            st.session_state.pop(key, None)
    except Exception as e:
        st.error(f'Error sending email: {e}')

def initialize_agent():
    if 'agent' not in st.session_state:
        st.session_state.agent = Agent()

# In app.py, enhance the UI
def render_custom_css():
    st.markdown('''
        <style>
        /* Modern, sleek design */
        
        /* Hide Streamlit branding */
                
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Your custom styling */
        .stApp {
            background-color: #f0f2f6;
            font-family: 'Inter', sans-serif;
        }
        .stApp {
            background-color: #f0f2f6;
            font-family: 'Inter', sans-serif;
        }
        .main-title {
            font-size: 3em;
            background: linear-gradient(45deg, #4158D0, #C850C0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 30px;
            font-weight: 800;
        }
        .stTextArea {
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stButton>button {
            background-color: #4158D0;
            color: white;
            border-radius: 20px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #C850C0;
            transform: scale(1.05);
        }
        </style>
    ''', unsafe_allow_html=True)

def render_ui():
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    
    # Add a cool animated title
    st.markdown('''
    <div class="main-title">
    <span style="display:inline-block; animation: float 2s ease-in-out infinite;">✈️</span> 
    AI Travel Companion 
    <span style="display:inline-block; animation: float 2s ease-in-out infinite;">🌍</span>
    </div>
    ''', unsafe_allow_html=True)
    
    # Add a cool description
    st.markdown("""
    <div style="text-align:center; color:#666; margin-bottom:20px;">
    Your AI-powered travel assistant that finds the perfect flights and hotels 
    with just a simple description.
    </div>
    """, unsafe_allow_html=True)

    # Rest of your existing UI code...
    
    user_input = st.text_area(
        'Travel Query',
        height=200,
        key='query',
        placeholder='Type your travel query here...',
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.image('images/ai-travel.png', caption='AI Travel Assistant')

    return user_input

def process_query(user_input):
    if user_input:
        try:
            thread_id = str(uuid.uuid4())
            st.session_state.thread_id = thread_id

            messages = [HumanMessage(content=user_input)]
            config = {'configurable': {'thread_id': thread_id}}

            result = st.session_state.agent.graph.invoke({'messages': messages}, config=config)

            st.subheader('Travel Information')
            st.write(result['messages'][-1].content)

            st.session_state.travel_info = result['messages'][-1].content

        except Exception as e:
            st.error(f'Error: {e}')
    else:
        st.error('Please enter a travel query.')

def render_email_form():
    send_email_option = st.radio('Do you want to send this information via email?', ('No', 'Yes'))
    if send_email_option == 'Yes':
        with st.form(key='email_form'):
            sender_email = st.text_input('Sender Email')
            receiver_email = st.text_input('Receiver Email')
            subject = st.text_input('Email Subject', 'Travel Information')
            submit_button = st.form_submit_button(label='Send Email')

        if submit_button:
            if sender_email and receiver_email and subject:
                send_email(sender_email, receiver_email, subject, st.session_state.thread_id)
            else:
                st.error('Please fill out all email fields.')

def main():
    initialize_agent()
    render_custom_css()
    user_input = render_ui()

    if st.button('Get Travel Information'):
        process_query(user_input)

    if 'travel_info' in st.session_state:
        render_email_form()

if __name__ == '__main__':
    main()