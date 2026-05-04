# ── ULTIMATE CAREER COCKPIT ──────────────────────────────────────────────────
# 
# 1. INSTALL LIBRARIES:
#    pip install streamlit pandas pyresparser fpdf2 google-generativeai 
#    pip install pdfminer.six pymysql streamlit-tags Pillow plotly nltk
#    python -m spacy download en_core_web_sm
#
# 2. SETUP:
#    - Create folders: 'Logo' and 'Uploaded_Resumes'
#    - Run: streamlit run App.py
#
# 3. DATABASE:
#    - Ensure MySQL is running with appropriate permissions.
# ──────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import base64,random
import time,datetime,os
#libraries to parse the resume pdf files
# (Moved to function scope to speed up load)
# from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
import hashlib
import urllib.request
import re
import plotly.express as px #to create visualisations at the admin session
import nltk

from fpdf import FPDF



# ── ULTIMATE DIAMOND PLATINUM ELITE TEMPLATE ENGINE (SINGLE COLUMN) ──────
def generate_elite_pdf(data, template_name=None):
    class ElitePDF(FPDF):
        def header(self):
            # Ultra-Premium Gradient Top Accent
            self.set_fill_color(15, 23, 42) # Deep Midnight
            self.rect(0, 0, 210, 10, 'F')
            self.set_fill_color(37, 99, 235) # Electric Blue
            self.rect(0, 10, 210, 1.5, 'F')
            self.set_fill_color(226, 232, 240) # Platinum
            self.rect(0, 11.5, 210, 0.5, 'F')
        def footer(self):
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.set_text_color(148, 163, 184)
            self.cell(0, 10, f"DIAMOND ELITE EXECUTIVE DOCUMENT  |  {data.get('name', '').upper()}  |  PAGE {self.page_no()}", align="C")

    pdf = ElitePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Constants
    PAGE_W = 210; MARGIN = 15; CONTENT_W = PAGE_W - (2 * MARGIN)
    F_BOLD = "helvetica"; F_REG = "helvetica"
    C_ACCENT = (37, 99, 235); C_DARK = (15, 23, 42); C_TEXT = (30, 41, 59); C_GRAY = (71, 85, 105)

    def safe(s): return str(s or '').strip()

    def draw_tag(x, y, text):
        pdf.set_font(F_BOLD, 'B', 8)
        text = text.upper()
        tw = pdf.get_string_width(text) + 10
        pdf.set_fill_color(248, 250, 252); pdf.set_draw_color(203, 213, 225); pdf.set_text_color(*C_ACCENT)
        pdf.rect(x, y, tw, 7, 'DF')
        pdf.set_xy(x + 5, y + 1.5)
        pdf.cell(tw-10, 4, text, align='C')
        return tw + 3

    def render_block(y, title, content, is_skills=False):
        if not safe(content): return y
        
        # Smart Page Break (Prevents orphaned headers)
        if y > 250:
            pdf.add_page()
            y = 25

        pdf.set_xy(MARGIN, y)
        # Refined Header with Underline
        pdf.set_font(F_BOLD, 'B', 13)
        pdf.set_text_color(*C_DARK)
        pdf.cell(CONTENT_W, 8, title.upper(), ln=True)
        
        pdf.set_draw_color(*C_ACCENT); pdf.set_line_width(0.6)
        pdf.line(MARGIN, pdf.get_y(), MARGIN + 25, pdf.get_y())
        pdf.set_draw_color(226, 232, 240); pdf.set_line_width(0.2)
        pdf.line(MARGIN + 25, pdf.get_y(), MARGIN + CONTENT_W, pdf.get_y())
        
        y = pdf.get_y() + 4
        
        if is_skills:
            items = [s.strip() for s in content.split(',') if s.strip()]
            pdf.set_xy(MARGIN, y); curr_x = MARGIN
            for s in items:
                if not s: continue
                tw = pdf.get_string_width(s.upper()) + 15
                if curr_x + tw > MARGIN + CONTENT_W: y += 10; curr_x = MARGIN; pdf.set_xy(curr_x, y)
                curr_x += draw_tag(curr_x, y, s)
            return y + 12
        else:
            lines = safe(content).split('\n')
            for bl in lines:
                if not bl.strip(): continue
                
                # Clean redundant hyphens/bullets
                clean_line = bl.strip()
                while clean_line and clean_line[0] in ('-', '•', '*', '>', '.'):
                    clean_line = clean_line[1:].strip()
                if not clean_line: continue

                pdf.set_xy(MARGIN, y)
                
                if '|' in bl:
                    parts = [p.strip() for p in bl.split('|')]
                    pdf.set_font(F_BOLD, 'B', 11.5); pdf.set_text_color(*C_DARK)
                    pdf.cell(CONTENT_W - 50, 6, parts[1] if len(parts)>1 else parts[0])
                    if len(parts) > 2:
                        pdf.set_x(MARGIN + CONTENT_W - 50); pdf.set_font(F_REG, 'I', 10); pdf.set_text_color(*C_GRAY)
                        pdf.cell(50, 6, parts[2], align='R', ln=True)
                    else: pdf.ln()
                    
                    pdf.set_x(MARGIN); pdf.set_font(F_BOLD, 'B', 10.5); pdf.set_text_color(*C_ACCENT)
                    pdf.cell(CONTENT_W, 5, parts[0], ln=True)
                    y = pdf.get_y() + 1
                else:
                    # Bullet Point Logic (Geometric)
                    pdf.set_fill_color(*C_ACCENT)
                    pdf.rect(MARGIN + 1, y + 2.2, 1.3, 1.3, 'F')
                    pdf.set_xy(MARGIN + 6, y)
                    pdf.set_font(F_REG, '', 10.5); pdf.set_text_color(*C_TEXT)
                    pdf.multi_cell(CONTENT_W - 6, 5.5, clean_line, align='J')
                    y = pdf.get_y()
            return y + 8

    # ── HEADER ───────────────────────────────────────────────────────────
    name = safe(data.get('name', 'YOUR NAME')).upper()
    pdf.set_xy(MARGIN, 25)
    pdf.set_font(F_BOLD, 'B', 38); pdf.set_text_color(*C_DARK)
    pdf.cell(CONTENT_W, 20, name, align='C', ln=True)
    
    # Role Subtitle
    pdf.set_font(F_BOLD, 'B', 15); pdf.set_text_color(*C_ACCENT)
    pdf.cell(CONTENT_W, 8, "EXECUTIVE TECHNOLOGY LEADER", align='C', ln=True)
    
    # Inline Contact Assets
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font(F_REG, '', 9.5); pdf.set_text_color(*C_GRAY)
    contact_str = f"{data.get('email')}  |  {data.get('phone')}  |  {data.get('address')}  |  LinkedIn/Portfolio"
    pdf.cell(CONTENT_W, 6, contact_str, align='C', ln=True)
    
    # ── CONTENT ──────────────────────────────────────────────────────────
    curr_y = pdf.get_y() + 12
    
    curr_y = render_block(curr_y, "Executive Narrative", data.get('summary') or data.get('objective'))
    
    # Impact Highlights (Top 0.1% Feature)
    impact_items = "Scale: Engineered architectures supporting 10M+ DAU with 99.99% uptime.\nEfficiency: Realized $2M+ annual cloud savings through serverless migration.\nGrowth: Built high-velocity engineering cultures from seed to Series D."
    curr_y = render_block(curr_y, "Strategic Impact", impact_items)

    curr_y = render_block(curr_y, "Career Trajectory", data.get('experience'))
    curr_y = render_block(curr_y, "The Arsenal (Technical)", data.get('tech_skills'), True)
    curr_y = render_block(curr_y, "Leadership & Soft Skills", data.get('soft_skills'), True)
    curr_y = render_block(curr_y, "Innovation Portfolio", data.get('projects'))
    curr_y = render_block(curr_y, "Professional Credentials", data.get('certifications'))
    curr_y = render_block(curr_y, "Distinctions", data.get('awards'))
    curr_y = render_block(curr_y, "Educational Background", data.get('education'))
    curr_y = render_block(curr_y, "Volunteer Impact", data.get('volunteer'))
    curr_y = render_block(curr_y, "Linguistic Proficiency", data.get('languages'))
    curr_y = render_block(curr_y, "Thought Leadership", data.get('publications'))
    curr_y = render_block(curr_y, "Personal Interests", data.get('hobbies'))
    curr_y = render_block(curr_y, "Professional References", data.get('references'))
    
    if data.get('custom_title') and data.get('custom_content'):
        curr_y = render_block(curr_y, data.get('custom_title'), data.get('custom_content'))

    return bytes(pdf.output())


# Gemini AI model will be configured in the main loop if an API key is provided




def get_table_download_link(df,filename,text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

# ── UTILS ──────────────────────────────────────────────────────────────────
def robust_json_load(s):
    """Attempt to parse JSON with advanced recovery for LLM errors."""
    import json, re
    if not s: return None
    s = s.strip()
    
    # 1. Try Standard Parse
    try:
        return json.loads(s)
    except Exception:
        pass

    # 2. Advanced Cleanup
    try:
        # Fix Python-style booleans/None
        s = re.sub(r'\bTrue\b', 'true', s)
        s = re.sub(r'\bFalse\b', 'false', s)
        s = re.sub(r'\bNone\b', 'null', s)
        
        # Replace single quotes with double quotes for keys/values
        # This regex avoids replacing quotes inside words like "don't"
        s = re.sub(r"(?<=[\{\s,])'(\w+)'(?=\s*:)", r'"\1"', s) # Keys
        s = re.sub(r"(?<=:\s*)'([^']*)'(?=[\s,\}])", r'"\1"', s) # Values
        
        # Remove trailing commas
        s = re.sub(r",\s*([\]}])", r"\1", s)
        
        # Handle double quotes inside strings (common in Llama)
        # This is risky but often helps: try to fix unescaped quotes in values
        # s = re.sub(r'(?<=: ")(.*?)"(?=,)', lambda m: m.group(1).replace('"', "'"), s)
        
        return json.loads(s)
    except Exception:
        # 3. Last Resort: Find the largest { } block
        try:
            match = re.search(r'\{.*\}', s, re.DOTALL)
            if match:
                clean_block = match.group()
                # Repeat basic fixes on block
                clean_block = re.sub(r'\bTrue\b', 'true', clean_block)
                clean_block = re.sub(r'\bFalse\b', 'false', clean_block)
                return json.loads(clean_block)
        except:
            pass
    return None

def get_value_case_insensitive(d, key, default=None):
    if not isinstance(d, dict): return default
    for k, v in d.items():
        if str(k).lower() == str(key).lower():
            return v
    return default




def insert_data(name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses, full_json="{}"):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (name, email, str(res_score), timestamp,str(no_of_pages), reco_field, cand_level, skills,recommended_skills,courses, full_json)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


def insert_builder_data(username, data, template, timestamp):
    sql = """INSERT INTO elite_builder_data 
             (Username, Name, Email, Phone, Address, Linkedin, Objective, Summary, Experience, Education, 
              Tech_Skills, Soft_Skills, Projects, Certifications, Languages, Awards, Publications, 
              Volunteer, Hobbies, References_Text, Custom_Title, Custom_Content, Template_Choice, Timestamp) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (
        username, data.get('name'), data.get('email'), data.get('phone'), data.get('address'),
        data.get('linkedin'), data.get('objective'), data.get('summary'), data.get('experience'),
        data.get('education'), data.get('tech_skills'), data.get('soft_skills'), data.get('projects'),
        data.get('certifications'), data.get('languages'), data.get('awards'), data.get('publications'),
        data.get('volunteer'), data.get('hobbies'), data.get('references'), data.get('custom_title'),
        data.get('custom_content'), template, timestamp
    )
    cursor.execute(sql, values)
    connection.commit()

st.set_page_config(
   page_title="Smart Resume Builder and Analyzer",
   page_icon='✨',
)
def run():
    st.write("<!-- System Debug: run() started -->", unsafe_allow_html=True)
    
    # SETUP & DOWNLOADS
    try:
        import nltk
        nltk.download('stopwords', quiet=True)
    except: pass

    # DB CONNECTION
    global connection, cursor
    try:
        import pymysql
        connection = pymysql.connect(host='localhost',user='root',password='1972', connect_timeout=5)
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS cv;")
        cursor.execute("USE cv;")
        
        try:
            cursor.execute("ALTER TABLE user_data ADD COLUMN full_analysis_json LONGTEXT;")
            connection.commit()
        except: pass

        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS elite_builder_data (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Username VARCHAR(255),
            Name VARCHAR(255),
            Email VARCHAR(255),
            Phone VARCHAR(255),
            Address TEXT,
            Linkedin TEXT,
            Objective TEXT,
            Summary TEXT,
            Experience LONGTEXT,
            Education LONGTEXT,
            Tech_Skills LONGTEXT,
            Soft_Skills LONGTEXT,
            Projects LONGTEXT,
            Certifications LONGTEXT,
            Languages LONGTEXT,
            Awards LONGTEXT,
            Publications LONGTEXT,
            Volunteer LONGTEXT,
            Hobbies LONGTEXT,
            References_Text LONGTEXT,
            Custom_Title VARCHAR(255),
            Custom_Content LONGTEXT,
            Template_Choice VARCHAR(255),
            Timestamp VARCHAR(255)
        );
        """)
        connection.commit()
    except Exception as e:
        st.error(f"❌ Database Connection Failed: {str(e)}")
        st.info("Please ensure MySQL is running and the password is correct.")
        st.stop()

    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;600;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif !important;
            letter-spacing: -0.01em;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
        }

        /* 1. Cinematic Deep Space Background */
        .stApp {
            background: #020617 !important;
            color: #ffffff !important;
        }

        /* FORCE ALL TEXT VISIBILITY */
        p, li, span, div, .stMarkdown, label {
            color: #ffffff !important;
            font-weight: 400;
        }
        
        /* Force Input Labels to be Pure White and Visible */
        [data-testid="stWidgetLabel"] p {
            color: #ffffff !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
            opacity: 1 !important;
        }

        /* Fix File Uploader Visibility & Icon */
        .stFileUploader section {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 2px dashed #3b82f6 !important;
        }
        
        .stFileUploader [data-testid="stBaseButton-secondary"] {
            background: #3b82f6 !important;
            color: white !important;
        }

        [data-testid="stFileUploaderFileData"] {
            background-color: #ffffff !important;
            border-radius: 12px !important;
            padding: 10px !important;
            margin-top: 10px !important;
        }
        
        /* Ultra-specific selector to beat the global white text rule */
        .stFileUploader [data-testid="stFileUploaderFileData"] div,
        .stFileUploader [data-testid="stFileUploaderFileData"] p,
        .stFileUploader [data-testid="stFileUploaderFileData"] span,
        .stFileUploader [data-testid="stFileUploaderFileData"] small {
            color: #000000 !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stFileUploaderFileData"] svg {
            fill: #000000 !important;
        }

        /* Ambient Pulsing Glows */
        @keyframes pulse-glow {
            0% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.1); }
            100% { opacity: 0.3; transform: scale(1); }
        }

        .stApp::before {
            content: '';
            position: fixed;
            top: -10%; left: -10%;
            width: 40%; height: 40%;
            background: radial-gradient(circle, rgba(56, 189, 248, 0.1), transparent 70%);
            filter: blur(100px);
            z-index: -1;
            animation: pulse-glow 10s infinite ease-in-out;
        }

        /* 2. Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* 3. The Hyper-Glass Sidebar */
        [data-testid="stSidebar"] {
            background: rgba(2, 6, 23, 0.95) !important;
            backdrop-filter: blur(32px) saturate(200%) !important;
            -webkit-backdrop-filter: blur(32px) saturate(200%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        [data-testid="stSidebar"] * {
            color: #f1f5f9 !important;
        }

        /* 4. Platinum Iridescent Headings */
        h1, h2, h3, h4, h5 {
            background: linear-gradient(135deg, #fff 0%, #cbd5e1 50%, #94a3b8 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            font-weight: 700 !important;
            letter-spacing: -0.03em !important;
            text-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            margin-bottom: 1rem !important;
        }

        /* 5. Premium Input Architecture */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background: 
