import datetime
import operator
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from mailersend import emails

from agents.tools.flights_finder import flights_finder
from agents.tools.hotels_finder import hotels_finder

_ = load_dotenv()

CURRENT_YEAR = datetime.datetime.now().year

TOOLS_SYSTEM_PROMPT = f"""You are a smart travel agency. Use the tools to look up information.
    You are allowed to make multiple calls (either together or in sequence).
    Only look up information when you are sure of what you want.
    The current year is {CURRENT_YEAR}.
    If you need to look up some information before asking a follow up question, you are allowed to do that!
    I want to have in your output links to hotels websites and flights websites (if possible).
    I want to have as well the logo of the hotel and the logo of the airline company (if possible).
    In your output always include the price of the flight and the price of the hotel and the currency as well (if possible).
    """

EMAILS_SYSTEM_PROMPT = """Your task is to convert structured markdown-like text into a valid HTML email body.
Do not include a ```html preamble in your response.
The output should be in proper HTML format, ready to be used as the body of an email.
"""

TOOLS = [flights_finder, hotels_finder]

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:
    def __init__(self):
        self._tools = {t.name: t for t in TOOLS}
        self._tools_llm = ChatOpenAI(model='gpt-3.5-turbo').bind_tools(TOOLS)

        builder = StateGraph(AgentState)
        builder.add_node('call_tools_llm', self.call_tools_llm)
        builder.add_node('invoke_tools', self.invoke_tools)
        builder.add_node('email_sender', self.email_sender)
        builder.set_entry_point('call_tools_llm')

        builder.add_conditional_edges('call_tools_llm', Agent.exists_action, 
            {'more_tools': 'invoke_tools', 'email_sender': 'email_sender'}
        )
        builder.add_edge('invoke_tools', 'call_tools_llm')
        builder.add_edge('email_sender', END)
        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory, interrupt_before=['email_sender'])

    @staticmethod
    def exists_action(state: AgentState):
        result = state['messages'][-1]
        if len(result.tool_calls) == 0:
            return 'email_sender'
        return 'more_tools'

    def email_sender(self, state: AgentState):
        print('Sending email')
        email_llm = ChatOpenAI(model='gpt-4o', temperature=0.1)
        email_message = [
            SystemMessage(content=EMAILS_SYSTEM_PROMPT), 
            HumanMessage(content=state['messages'][-1].content)
        ]
        email_response = email_llm.invoke(email_message)
        print('Email content:', email_response.content)

        try:
            mailer = emails.NewEmail(os.environ.get('MAILERSEND_API_KEY'))
            mail_body = {
                "from": {
                    "email": os.environ['FROM_EMAIL'],
                    "name": "AI Travel Assistant"
                },
                "to": [
                    {
                        "email": os.environ['TO_EMAIL'],
                        "name": "Traveler"
                    }
                ],
                "subject": os.environ['EMAIL_SUBJECT'],
                "html": email_response.content
            }

            response = mailer.send(mail_body)
            print("Email sent successfully")
            print(response)
        except Exception as e:
            print(f"Error sending email: {str(e)}")

    def call_tools_llm(self, state: AgentState):
        messages = state['messages']
        messages = [SystemMessage(content=TOOLS_SYSTEM_PROMPT)] + messages
        message = self._tools_llm.invoke(messages)
        return {'messages': [message]}

    def invoke_tools(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f'Calling: {t}')
            if not t['name'] in self._tools:
                print('\n ....bad tool name....')
                result = 'bad tool name, retry'
            else:
                result = self._tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        print('Back to the model!')
        return {'messages': results}