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
        with st.spinner('Initializing AI Travel Assistant...'):
            st.session_state.agent = Agent()

def render_custom_css():
    st.markdown('''
        <style>

        /* Complete removal of Streamlit branding */
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        header {visibility: hidden !important;}
        
        /* Comprehensive branding removal */
        [data-testid="stDecoration"] {
            visibility: hidden !important;
        }
        
        /* Global text and background styling */
        body {
            color: #333;
            background-color: #f4f6f9 !important;
        }
                
        button {
                color: white !important
                }
        
        .stApp {
            background-color: #f4f6f9 !important;
            color: #333 !important;
        }
        
        /* Enhanced sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #e6eaf3;
        }
        
        /* Text area improvements */
        .stTextArea textarea {
            background-color: white !important;
            color: #333 !important;
            border: 1px solid #d0d7de !important;
        }
        
        /* Button styling */
        .stButton>button {
            background-color: #4158D0 !important;
            color: white !important;
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #C850C0 !important;
            transform: scale(1.05);
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
        
        /* Typography */
        .main-title {
            color: #333 !important;
            font-size: 3em;
            text-align: center;
            margin-bottom: 30px;
            font-weight: 800;
        }
        
        /* Ensure readable text */
        * {
            color: #333 !important;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 5px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        
        /* Responsive adjustments */
        @media (max-width: 600px) {
            .main-title {
                font-size: 2em;
            }
        }
        
        /* Hide any remaining Streamlit specific elements */
        [data-testid="stToolbar"] {
            visibility: hidden !important;
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
            sender_email = st.text_input('Your Email')
            receiver_email = st.text_input('Recipient Email')
            subject = st.text_input('Email Subject', 'My AI Travel Plan')
            submit_button = st.form_submit_button(label='Send Travel Plan')

        if submit_button:
            if sender_email and receiver_email and subject:
                send_email(sender_email, receiver_email, subject, st.session_state.thread_id)
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