import sys
import os
import uuid
import streamlit as st
from langchain_core.messages import HumanMessage

# Add this BEFORE the import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent import Agent

# Rest of the code remains the same


# Set page configuration
st.set_page_config(
    page_title="AI Travel Companion",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def populate_envs(receiver_email, subject):
    # Use a specific sender email, and set the other email-related environment variables
    os.environ['FROM_EMAIL'] = "your_fixed_sender_email@example.com"  # Replace with your desired sender email
    os.environ['TO_EMAIL'] = receiver_email
    os.environ['EMAIL_SUBJECT'] = subject

def send_email(receiver_email, subject, thread_id):
    try:
        populate_envs(receiver_email, subject)
        config = {'configurable': {'thread_id': thread_id}}
        st.session_state.agent.graph.invoke(None, config=config)
        st.success('Email sent successfully!')
        for key in ['travel_info', 'thread_id']:
            st.session_state.pop(key, None)
    except Exception as e:
        st.error(f'Error sending email: {e}')

def render_email_form():
    send_email_option = st.radio('Share Your Travel Plan', ('Keep to Myself', 'Send via Email'))
    if send_email_option == 'Send via Email':
        with st.form(key='email_form'):
            receiver_email = st.text_input('Recipient Email', help='Enter the email address of the recipient.')
            subject = st.text_input('Email Subject', 'My AI Travel Plan')
            submit_button = st.form_submit_button(label='Send Travel Plan')

        if submit_button:
            if receiver_email and subject:
                # Fix: Ensure thread_id is provided as the third argument
                if 'thread_id' in st.session_state:
                    send_email(receiver_email, subject, st.session_state.thread_id)
                else:
                    st.error('Thread ID is missing. Please try generating your travel plan again.')
            else:
                st.error('Please complete all email fields.')


def initialize_agent():
    if 'agent' not in st.session_state:
        with st.spinner('Initializing AI Travel Assistant...'):
            st.session_state.agent = Agent()

def render_custom_css():
    st.markdown('''
        <style>
        /* Reset and Global Styles */
        :root {
            --primary-color: #4158D0;
            --secondary-color: #C850C0;
            --background-color: #f4f6f9;
            --text-color: #333; /* Dark gray text for readability */
            --light-background: #ffffff; /* Pure white for text areas and cards */
            --dark-background: #1e1e2f; /* Dark background for contrast */
            --highlight-color: #666; /* Mid-gray for less prominent text */
        }
                
        p {
            color: black
        }
                
        button {
            background-color: white;
            border: 1px solid black;
                }
                
        div[data-baseweb="radio"] > label {
            color: black !important; /* Explicitly set text color to black */
        }

        /* Global Background and Text */
        body, .stApp {
            background-color: var(--background-color) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: var(--text-color) !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: var(--light-background) !important;
            border-right: 1px solid #d0d7de !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            color: var(--text-color) !important;
        }

        /* Radio Button Text Color */
        .stRadio label {
            color: var(--text-color) !important;
        }

        /* Container Styling */
        .stApp > div:first-child {
            background-color: var(--background-color) !important;
        }

        /* Text Styling */
        .stMarkdown, .stText, .stTextArea {
            color: var(--text-color) !important;
        }

        /* Text Area Styling */
        .stTextArea textarea {
            background-color: var(--light-background) !important;
            color: var(--text-color) !important;
            border: 1px solid #d0d7de !important;
            border-radius: 12px !important;
            padding: 12px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }

        /* Highlighted Text for Less Important Elements */
        .stMarkdown p, .stText small {
            color: var(--highlight-color) !important;
        }

        /* Button Styling */
        .stButton > button {
            background-color: var(--primary-color) !important;
            color: #ffffff !important;
            border-radius: 20px !important;
            border: none !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase !important;
        }

        .stButton > button:hover {
            background-color: var(--secondary-color) !important;
            transform: scale(1.05) !important;
            box-shadow: 0 6px 8px rgba(0,0,0,0.2) !important;
        }

        /* Scrollbar Styling */
        ::-webkit-scrollbar {
            width: 10px !important;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1 !important;
        }
        ::-webkit-scrollbar-thumb {
            background: #888 !important;
            border-radius: 5px !important;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555 !important;
        }

        /* Title Styling */
        .main-title {
            font-size: 3em !important;
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color)) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            text-align: center !important;
            margin-bottom: 30px !important;
            font-weight: 800 !important;
        }

        /* Responsive Typography */
        @media (max-width: 600px) {
            .main-title {
                font-size: 2em !important;
            }
        }

        /* Branding Removal (Minimal) */
        #MainMenu, footer, header, [data-testid="stToolbar"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Card-like Container */
        .stContainer {
            background-color: var(--light-background) !important;
            color: var(--text-color) !important;
            border-radius: 15px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            padding: 20px !important;
            margin-bottom: 20px !important;
        }

        /* Descriptive Text in Centered Section */
        .center-container p {
            color: var(--highlight-color) !important;
            font-size: 1.1em !important;
            text-align: center !important;
        }
        </style>
        ''', unsafe_allow_html=True)

def render_ui():
    # Custom sidebar with logo
    with st.sidebar:
        st.image('images/ai-travel.png', use_column_width=True)
        st.markdown("### AI Travel Companion")
        st.markdown("Your intelligent travel planning assistant")
        st.markdown('''
    <style>
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(65,88,208,0.1) 0%, rgba(200,80,192,0.1) 100%);
        z-index: -1;
        pointer-events: none;
    }
    </style>
    ''', unsafe_allow_html=True)

    # Main content
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    
    # Animated title
    st.markdown('''
    <div class="main-title">
    <span style="display:inline-block; animation: float 2s ease-in-out infinite;">✈️</span> 
    AI Travel Companion 
    <span style="display:inline-block; animation: float 2s ease-in-out infinite;">🌍</span>
    </div>
    ''', unsafe_allow_html=True)
    
    # Descriptive text
    st.markdown("""
    <div style="text-align:center; color:#666; margin-bottom:20px; font-size:1.1em;">
    Discover personalized travel experiences with our AI-powered assistant. 
    Simply describe your dream trip, and we'll find the perfect flights and hotels.
    </div>
    """, unsafe_allow_html=True)

    # Travel query input
    user_input = st.text_area(
        'Describe Your Dream Trip',
        height=200,
        key='query',
        placeholder='E.g., "I want to visit Italy for a week in June, focusing on historical sites and coastal towns. Budget-friendly options preferred."',
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

    return user_input

def process_query(user_input):
    if user_input:
        try:
            # Generate unique thread ID
            thread_id = str(uuid.uuid4())
            st.session_state.thread_id = thread_id

            # Prepare and process query
            messages = [HumanMessage(content=user_input)]
            config = {'configurable': {'thread_id': thread_id}}

            with st.spinner('Analyzing your travel request...'):
                result = st.session_state.agent.graph.invoke({'messages': messages}, config=config)

            # Display results
            st.subheader('Your Personalized Travel Plan')
            st.write(result['messages'][-1].content)

            # Store result in session state
            st.session_state.travel_info = result['messages'][-1].content

        except Exception as e:
            st.error(f'Error processing your request: {e}')
    else:
        st.error('Please enter a detailed travel query.')

def render_email_form():
    send_email_option = st.radio('Share Your Travel Plan', ('Keep to Myself', 'Send via Email'))
    if send_email_option == 'Send via Email':
        with st.form(key='email_form'):
            receiver_email = st.text_input('Recipient Email', help='Enter the email address of the recipient.')
            subject = st.text_input('Email Subject', 'My AI Travel Plan')
            submit_button = st.form_submit_button(label='Send Travel Plan')

        if submit_button:
            if receiver_email and subject:
                send_email(receiver_email, subject, st.session_state.thread_id)
            else:
                st.error('Please complete all email fields.')

def main():
    initialize_agent()
    render_custom_css()
    user_input = render_ui()

    if st.button('Generate My Travel Plan'):
        process_query(user_input)

    if 'travel_info' in st.session_state:
        render_email_form()

if __name__ == '__main__':
    main()