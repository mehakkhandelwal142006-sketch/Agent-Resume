#==========LOAD MODULES==========
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import langchain
from langchain.agents import create_agent

from tavily import TavilyClient
import pytesseract as pyt
import streamlit as st
import os
import time
from PIL import Image
import pandas as pd
import numpy as np

# To show web app: complete page layout
st.set_page_config(layout= "wide")

# To Give Title
st.title("AI RESUME GENERATOR")
st.write("""This app helps user to build customized Professional Resume with latest Job apply links""")

st.image("https://raw.githubusercontent.com/mehakkhandelwal142006-sketch/Agent-Resume/refs/heads/main/bg.png")

st.sidebar.title("Fill Important Details")
st.sidebar.image("https://raw.githubusercontent.com/mehakkhandelwal142006-sketch/Agent-Resume/refs/heads/main/bg.png")


#===========API KEYS=========
GOOGLE_API_KEY = st.sidebar.text_input("Gemini-API", type = "password")
GROQ_API_KEY = st.sidebar.text_input("Groq-API", type = "password")
TAVILY_API_KEY = st.sidebar.text_input("Tavily-API", type = "password")

all_API = [GOOGLE_API_KEY,GROQ_API_KEY,TAVILY_API_KEY]
if not all(all_API):
    st.error("Must give API keys")
    st.stop()
elif all(all_API):
    st.success("API KEYS LOADED SUCCESSFULLY")
    #============MODEL==============
    model = ChatGoogleGenerativeAI(
        model = 'gemini-3.5-flash-lite',
        google_api_key = GOOGLE_API_KEY
    )
    

else:
    st.info("PASS ALL API KEYS")

# multiselect option
options = ["Delhi", "Mumbai", "Pune", "Banglore", "Gurugram/Gurgaon"]
location= st.sidebar.multiselect("Select Location",
                                 options = options)
profile_op = ["Data Analysts", "AI Engineer", "Gen AI Developer", "Full=Stack Developer", "Data Scientist"]
profile = st.sidebar.multiselect("Select Job Profile",
                                 options = profile_op)

#===== GET USER INFO=======
st.markdown("""### GET USER INFO""")
user_info = st.text_area("""Write your resume description: """)

# response = model.invoke("Hello Buddy!")
# response.content[-1]['text']

#==========TOOLS=================
def search_latest_news_jobs(query):
  """This function helps to fetch latest
  nr=ews or jobs related article using
  tavily"""

  Client = TavilyClient(
      api_key= TAVILY_API_KEY
  )

  response = Client.search(query)
  return response

#================Agent Creation=====================
agent = create_agent(
    model= model,
    tools = [search_latest_news_jobs])

# agent

def main_agent(agent, query):
  """This is the main agent' or leader agent
  orchestrate sub agents"""

  #Giving prompt to create detailed prompt for code generation
  prompt = """You are AI Assistant and below given is a prompt, your task is to give detailed prompt for this.

You are a professional Resume Generator where the user will provide their personal information.
Create a detailed and professional resume suitable for both students/freshers and experienced professionals.

The resume must have a dynamic UI/UX with advanced CSS and a modern, premium design.

DESIGN:
Make the resume visually attractive, modern, premium, and professional.
Use a sophisticated dark theme with a colorful rainbow-inspired accent theme.
Use subtle gradients, clean typography, soft borders, and minimal glow effects.

IMPORTANT TEXT VISIBILITY REQUIREMENTS:
- All resume text MUST be clearly visible and highly readable.
- Use strong contrast between the background and text.
- Main body text must use a bright/light color such as #E5E7EB or #F1F5F9.
- Headings must use bright accent colors such as cyan, blue, purple, pink, or orange.
- Do NOT use dark gray, muted gray, or low-opacity colors for important text.
- Do NOT reduce text opacity below 85%.
- Secondary text should still have sufficient contrast and must remain clearly readable.
- Dates, company names, education details, descriptions, skills, contact information, and links must all be clearly visible.
- Ensure text does not blend into the dark background or colorful gradients.
- Use appropriate font sizes, font weights, line height, and letter spacing.
- Maintain clear visual hierarchy between headings, subheadings, and body text.
- Never sacrifice readability for visual effects.

COLOR:
Use multiple complementary accent colors while keeping the overall design professional.
Use rainbow colors mainly for borders, small highlights, icons, badges, and decorative gradients.
Do NOT apply rainbow colors directly behind important text.
Keep the resume background dark and consistent.

LAYOUT:
Use clean spacing, proper alignment, readable content widths, and responsive design.
Ensure all sections are completely visible and not clipped, hidden, or overlapped.
The resume should look polished both on screen and when printed/saved as PDF.

Make sure to give output in HTML format only.
Use embedded CSS and JavaScript where required.
No Markdown.
No explanations outside the HTML.
"""

  response = agent.invoke({"messages":[{'role':'user','content':prompt}]})
  detailed_prompt= response['messages'][-1].content[-1]['text']

  # save prompt using file handling
  with open("prompt.txt","w") as f:
    f.write(detailed_prompt)

  user_details = f"""Below given is a user details generate Resume based on that,if not given keep: Default Resume: Python Developer user details: {query}"""

  final_prompt = prompt + detailed_prompt + user_details

  # CODE GENERATION
  response = agent.invoke({"messages":[{'role':'user','content':final_prompt}]})
  code = response['messages'][-1].content[-1]['text']



  return code

# code = main_agent(agent, "ALAN TURING, GEN AI EXPERT")
# from IPython import display as DISPLAY
# DISPLAY.HTML(code)


#==========Fetch latest domain related jobs using tavily===========

def get_jobs(agent,
             Location = "Noida,Delhi",
             Profile =  "Data Analyst, AI Engineer"):

  Location = "Noida,Delhi"
  Profile =  "Data Analyst, AI Engineer"

  prompt = f"""Based on user given job profile, fetch latest jobs or job apply article using Naukri, Linkedin, Indeed, or all popular Job apply platforms, show results with JOB PROFILE NAME, LOCATION , SALARY, COMPANY NAME, SHOW jobs only related to given {Location} and {Profile} output must be in Professional HTML Naukri theme cards with Dynamic Design show atleast top 10-20 results with direct apply link"""

  response = agent.invoke({"messages":[{'role':'user','content':prompt}]})
  code = response['messages'][-1].content[-1]['text']
  return code

# code = get_jobs(agent)
# DISPLAY.HTML(code)

if st.button("Generate Resume"):
    with st.spinner("Agent Running"):
        code = main_agent(agent,user_info)
        st.html(code, width="stretch" , unsafe_allow_javascript=True)
        st.divider()
        job_code = get_jobs(agent,location,profile)
        st.html(job_code, width="stretch" , unsafe_allow_javascript=True)
