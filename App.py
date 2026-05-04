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
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #fff !important;
            border-radius: 14px !important;
            padding: 16px !important;
            font-size: 0.95rem !important;
            backdrop-filter: blur(10px) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            background: rgba(255, 255, 255, 0.05) !important;
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15), inset 0 2px 4px rgba(0,0,0,0.3) !important;
            transform: translateY(-1px);
        }

        /* 6. Liquid Obsidian Buttons */
        .stButton>button {
            background: rgba(255, 255, 255, 0.05) !important;
            color: #fff !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 12px 32px !important;
            border-radius: 14px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-size: 0.8rem !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
            backdrop-filter: blur(10px);
        }
        
        .stButton>button:hover {
            background: #fff !important;
            color: #020617 !important;
            border-color: #fff !important;
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 20px rgba(255,255,255,0.2) !important;
        }

        /* Primary Action Override */
        button[kind="primary"] {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            border: none !important;
        }
        button[kind="primary"]:hover {
            background: #fff !important;
            color: #2563eb !important;
        }

        /* 7. Advanced Cards & Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(255, 255, 255, 0.03) !important;
            padding: 8px !important;
            border-radius: 18px !important;
            gap: 8px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
        }

        .stTabs [data-baseweb="tab"] {
            height: 45px !important;
            border-radius: 12px !important;
            background: transparent !important;
            color: #94a3b8 !important;
            transition: all 0.3s ease !important;
            border: none !important;
            padding: 0 20px !important;
        }

        .stTabs [aria-selected="true"] {
            background: rgba(255, 255, 255, 0.1) !important;
            color: #fff !important;
            font-weight: 600 !important;
        }

        /* 8. Neon File Uploader */
        .stFileUploader {
            border: 2px dashed rgba(255, 255, 255, 0.1) !important;
            border-radius: 24px !important;
            background: rgba(255, 255, 255, 0.01) !important;
            padding: 60px 40px !important;
            transition: all 0.4s ease !important;
        }
        
        .stFileUploader:hover {
            border-color: #3b82f6 !important;
            background: rgba(59, 130, 246, 0.05) !important;
            box-shadow: 0 0 50px rgba(59, 130, 246, 0.1) !important;
        }

        /* 9. Metrics with Glass Cards */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03) !important;
            padding: 24px !important;
            border-radius: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(20px);
        }

        /* 10. Crystal Success/Info Alerts */
        .stAlert {
            background: rgba(15, 23, 42, 0.9) !important;
            color: #ffffff !important;
        }
        .stAlert p { color: #ffffff !important; }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    st.title("Smart Resume Builder and Analyzer")

    # DB and tables are set up above

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(500) NOT NULL,
                     Email_ID VARCHAR(500) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field BLOB NOT NULL,
                     User_level BLOB NOT NULL,
                     Actual_skills BLOB NOT NULL,
                     Recommended_skills BLOB NOT NULL,
                     Recommended_courses BLOB NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    
    # Create user credentials table
    cred_sql = """CREATE TABLE IF NOT EXISTS user_credentials
                  (ID INT NOT NULL AUTO_INCREMENT,
                   Username varchar(255) NOT NULL UNIQUE,
                   Email varchar(255) NOT NULL,
                   Password_Hash varchar(255) NOT NULL,
                   PRIMARY KEY (ID));"""
    cursor.execute(cred_sql)
    
    # Create builder submissions table
    builder_sql = """CREATE TABLE IF NOT EXISTS builder_submissions
                     (ID INT NOT NULL AUTO_INCREMENT,
                      Username VARCHAR(255),
                      Name VARCHAR(255),
                      Email VARCHAR(255),
                      Timestamp VARCHAR(50),
                      ResumeData_JSON LONGTEXT,
                      PRIMARY KEY (ID));"""
    cursor.execute(builder_sql)

    # Create cover letter table
    cl_sql = """CREATE TABLE IF NOT EXISTS cover_letter_submissions
                 (ID INT NOT NULL AUTO_INCREMENT,
                  Username VARCHAR(255),
                  Timestamp VARCHAR(50),
                  Job_Description LONGTEXT,
                  Generated_Letter LONGTEXT,
                  PRIMARY KEY (ID));"""
    cursor.execute(cl_sql)
    
    # Create job matches table
    jm_sql = """CREATE TABLE IF NOT EXISTS job_match_submissions
                 (ID INT NOT NULL AUTO_INCREMENT,
                  Username VARCHAR(255),
                  Timestamp VARCHAR(50),
                  Analysis_JSON LONGTEXT,
                  PRIMARY KEY (ID));"""
    cursor.execute(jm_sql)
    
    connection.commit()

    with st.sidebar:
        # Display Premium Black Logo
        try:
            logo = Image.open('./Logo/logo.png')
            st.image(logo, use_container_width=True)
        except:
            pass
        
        st.markdown("---")
        st.subheader("🤖 Local AI Status")
        import ollama
        try:
            models = ollama.list()['models']
            model_names = [m['model'] for m in models]
            
            # Model Selection
            selected_model = st.selectbox("Active AI Model", 
                                         options=model_names if model_names else ["llama3.2", "llama3"],
                                         index=0 if model_names else 0)
            st.session_state.ollama_model = selected_model
            
            if selected_model in model_names:
                st.success(f"Model Ready: {selected_model}")
            else:
                st.warning(f"{selected_model} not found")
                if st.button("Pull Selected Model"):
                    with st.spinner(f"Downloading {selected_model}..."):
                        try:
                            ollama.pull(selected_model)
                            st.success("Download Complete!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Pull failed: {e}")

            st.markdown("---")
            st.info("💡 **Memory Issue?** If 'llama3' fails, pull **llama3.2** (3B) — it's 2x faster and uses much less RAM.")
            if st.button("Pull Llama3.2 (Lightweight)"):
                with st.spinner("Downloading Llama3.2..."):
                    try:
                        ollama.pull('llama3.2')
                        st.success("Llama3.2 Ready!")
                        st.session_state.ollama_model = "llama3.2"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Pull failed: {e}")

        except Exception as e:
            st.error(f"Ollama Offline: {str(e)}")

    if 'role' not in st.session_state:
        query_role = st.query_params.get("role", None)
        query_user = st.query_params.get("user", None)
        if query_role and query_user:
            st.session_state.role = query_role
            st.session_state.current_user = query_user
        else:
            st.session_state.role = None
            st.session_state.current_user = None

    if st.session_state.role is None:
        st.markdown("### Welcome! Please Login or Sign Up")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            l_user = st.text_input("Username", key="l_user")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            if st.button("Login", key="btn_login"):
                if l_user == 'admin' and l_pass == 'admin123':
                    st.session_state.role = 'Admin'
                    st.session_state.current_user = 'Admin'
                    st.query_params["role"] = "Admin"
                    st.query_params["user"] = "Admin"
                    st.rerun()
                else:
                    pass_hash = hashlib.sha256(l_pass.encode()).hexdigest()
                    cursor.execute("SELECT * FROM user_credentials WHERE Username=%s AND Password_Hash=%s", (l_user, pass_hash))
                    record = cursor.fetchone()
                    if record:
                        st.session_state.role = 'User'
                        st.session_state.current_user = l_user
                        st.query_params["role"] = "User"
                        st.query_params["user"] = l_user
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password")
                        
        with tab2:
            s_user = st.text_input("Choose Username", key="s_user")
            s_email = st.text_input("Email", key="s_email")
            s_pass = st.text_input("Choose Password", type="password", key="s_pass")
            if st.button("Sign Up", key="btn_signup"):
                if not s_user or not s_email or not s_pass:
                    st.warning("Please fill all fields")
                else:
                    cursor.execute("SELECT * FROM user_credentials WHERE Username=%s", (s_user,))
                    if cursor.fetchone():
                        st.error("Username already exists. Please choose another one.")
                    else:
                        pass_hash = hashlib.sha256(s_pass.encode()).hexdigest()
                        cursor.execute("INSERT INTO user_credentials (Username, Email, Password_Hash) VALUES (%s, %s, %s)", (s_user, s_email, pass_hash))
                        connection.commit()
                        st.success("Account created successfully! Please log in.")
        
        st.stop()

    if st.session_state.role == 'User':
        col_u1, col_u2 = st.columns([8, 2])
        with col_u1:
            st.success(f"Welcome {st.session_state.current_user} !")
        with col_u2:
            if st.button("Logout", key="btn_logout"):
                st.session_state.role = None
                st.session_state.current_user = None
                st.query_params.clear()
                st.rerun()
                
        tab_analyzer, tab_builder, tab_cover_letter, tab_interview, tab_jobs = st.tabs(['Resume Analyzer', 'Resume Builder', 'Cover Letter', 'Interview Prep', 'Job Matches'])
        with tab_analyzer:
            st.markdown('''<h5 style='text-align: left; color: #8b5cf6;'> Upload your resume, and get smart recommendations</h5>''',
                        unsafe_allow_html=True)
            pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
            if pdf_file is not None:
                with st.spinner('Uploading your Resume...'):
                    time.sleep(1)

                os.makedirs('./Uploaded_Resumes', exist_ok=True)
                # Append timestamp to avoid Windows file lock PermissionError on rerun
                save_image_path = f'./Uploaded_Resumes/{int(time.time())}_{pdf_file.name}'
                with open(save_image_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                from pyresparser import ResumeParser
                resume_data = ResumeParser(save_image_path).get_extracted_data()
                if resume_data:
                    ## Get the whole resume data
                    resume_text = pdf_reader(save_image_path)

                    st.header("**Resume Analysis**")
                    st.success("Your resume has been parsed.")

                    # Hardcoded API key for seamless 1-click experience
                    api_key = "AIzaSyBuNU5p0aQa53K4A-Kuybr3AIdf8T4mYzI"

                    st.markdown("<br>", unsafe_allow_html=True)
                    # --- LOCAL LLAMA3 VIA OLLAMA ---
                    if st.button("Start analysis", type="primary", use_container_width=True):
                        with st.spinner("Analyzing your resume locally with Llama3..."):
                            import ollama
                            import json
                            
                            prompt = f"""
                            ROLE: ELITE EXECUTIVE RECRUITER & ATS ANALYZER
                            TASK: Provide a rigorous 10-factor analysis of the resume below.
                            
                            SCORING GUIDELINES:
                            - 0-30: Section is missing or extremely poor.
                            - 40-60: Standard/Average.
                            - 70-90: Strong, metrics-driven.
                            - 95-100: World-class elite.
                            
                            STRICT OUTPUT FORMAT: RAW JSON ONLY. No preamble.
                            
                            JSON STRUCTURE:
                            {{
                                "ATS_Score": 0,
                                "Recommended_Role": "",
                                "Candidate_Level": "",
                                "Sections": {{
                                    "Executive_Summary": {{"Score": 0, "Verdict": "", "Strengths": [], "Weaknesses": [], "Critical_Red_Flags": [], "Actionable_Steps": []}},
                                    "Business_Value_ROI": {{"Score": 0, "Verdict": "", "Strengths": [], "Weaknesses": [], "Critical_Red_Flags": [], "Actionable_Steps": []}},
                                    "Professional_Trajectory": {{"Score": 0, "Verdict": "", "Strengths": [], "Weaknesses": [], "Critical_Red_Flags": [], "Actionable_Steps": []}},
                                    "Metrics_Action_Verbs": {{"Score": 0, "Verdict": "", "Strengths": [], "Weaknesses": [], "Critical_Red_Flags": [], "Actionable_Steps": []}},
                                    "Technical_Arsenal": {{"Score": 0, "Verdict": "", "Strengths": [], "Weaknesses": [], "Critical_Red_Flags": [], "Actionable_Steps": []}},
                                    "Leadership_Cultural_Fit": {{"Score": 0, "Verdict": "... (and so on for all 10 factors)"}}
                                }}
                            }}
                            
                            FACTORS TO ANALYZE:
                            1. Executive_Summary
                            2. Business_Value_ROI
                            3. Professional_Trajectory
                            4. Metrics_Action_Verbs
                            5. Technical_Arsenal
                            6. Leadership_Cultural_Fit
                            7. Storytelling_Narrative
                            8. Formatting_Visual_Hierarchy
                            9. Tone_Language_Readability
                            10. Final_Verdict_Action_Plan

                            IMPORTANT: You MUST evaluate each factor honestly. Do NOT return 0 unless the data is missing. Be efficient and concise.
                            
                            RESUME TEXT:
                            {resume_text}
                            """
                            try:
                                response = ollama.generate(model=st.session_state.get('ollama_model', 'llama3'), prompt=prompt, options={"temperature": 0.0, "top_k": 20, "top_p": 0.9, "num_ctx": 4096})
                                raw_response = response['response']
                                clean_json = raw_response.replace('```json', '').replace('```', '').strip()
                                
                                # Find boundaries
                                start = clean_json.find('{')
                                end = clean_json.rfind('}')
                                if start != -1 and end != -1:
                                    clean_json = clean_json[start:end+1]
                                
                                ai_data = robust_json_load(clean_json)
                                
                                if not ai_data:
                                    st.error("AI returned a malformed response that couldn't be parsed. Please try again.")
                                    st.expander("Debug: Cleaned JSON").code(clean_json)
                                    st.expander("Debug: Raw Response").write(raw_response)
                                    return

                                # Flatten 'Sections' if model nested it
                                if "Sections" in ai_data and isinstance(ai_data["Sections"], dict):
                                    sections = ai_data.pop("Sections")
                                    ai_data.update(sections)

                                # Save intelligent data to Database
                                ts = time.time()
                                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                timestamp = str(cur_date+'_'+cur_time)

                                insert_data(
                                    resume_data.get('name', 'N/A'), 
                                    resume_data.get('email', 'N/A'), 
                                    str(ai_data.get('ATS_Score', 0)), 
                                    timestamp,
                                    str(resume_data.get('no_of_pages', 1)), 
                                    ai_data.get('Recommended_Role', 'Unknown'), 
                                    ai_data.get('Candidate_Level', 'Unknown'), 
                                    str(ai_data.get('Technical_Arsenal', {}).get('Strengths', [])),
                                    "See Llama3 Report", 
                                    "See Llama3 Report",
                                    clean_json
                                )

                                # Display the Report in a Top 0.001% UX
                                st.balloons()
                                st.markdown("## 📊 Ultimate AI Resume Audit (Llama3)")

                                score_col, role_col, level_col = st.columns(3)
                                with score_col:
                                    st.metric("Executive ATS Score", f"{ai_data.get('ATS_Score')}/100")
                                with role_col:
                                    st.metric("Best Fit Role", ai_data.get('Recommended_Role'))
                                with level_col:
                                    st.metric("Seniority", ai_data.get('Candidate_Level'))

                                st.markdown("---")

                                def render_dashboard_tab(tab_data):
                                    score = get_value_case_insensitive(tab_data, 'Score', 0)
                                    try: score = int(float(score))
                                    except: score = 0
                                    st.metric("Section Score", f"{score}/100")

                                    if not tab_data or not isinstance(tab_data, dict):
                                        return

                                    verdict = get_value_case_insensitive(tab_data, 'Verdict', 'N/A')
                                    st.info(f"**Verdict:** {verdict}")

                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.success("**Strengths**")
                                        items = tab_data.get('Strengths', [])
                                        if not items: st.markdown("- No strengths identified.")
                                        for s in items: st.markdown(f"- {s}")
                                    with col2:
                                        st.warning("**Weaknesses & Gaps**")
                                        items = tab_data.get('Weaknesses', [])
                                        if not items: st.markdown("- No weaknesses identified.")
                                        for w in items: st.markdown(f"- {w}")

                                    col3, col4 = st.columns(2)
                                    with col3:
                                        st.error("**Critical Red Flags**")
                                        items = tab_data.get('Critical_Red_Flags', [])
                                        if not items: st.markdown("- No critical red flags identified.")
                                        for r in items: st.markdown(f"- {r}")
                                    with col4:
                                        st.info("**Actionable Steps**")
                                        items = tab_data.get('Actionable_Steps', [])
                                        if not items: st.markdown("- No actionable steps provided.")
                                        for a in items: st.markdown(f"- {a}")

                                # The navigation menu
                                tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
                                    "Summary", "Business ROI", "Trajectory", "Metrics", 
                                    "Skills", "Leadership", "Storytelling", "Formatting", 
                                    "Tone", "Action Plan"
                                ])

                                with tab1: render_dashboard_tab(get_value_case_insensitive(ai_data, 'Executive_Summary', {}))
                                with tab2: render_dashboard_tab(get_value_case_insensitive(ai_data, 'Business_Value_ROI', {}))
                                with tab3: render_dashboard_tab(get_value_case_insensitive(ai_data, 'Professional_Trajectory', {}))
                                with tab4: render_dashboard_tab(get_value_case_insensitive(ai_data, 'Metrics_Action_Verbs', {}))
                                with tab5: render_dashboard_tab(get_value_case_insensitive(ai_data, 'Technical_Arsenal', {}))
                                with tab6: render_dashboard_tab(get_value_case_insensitive(ai_data, 'Leadership_Cultural_Fit', {}))
                                with tab7: render_dashboard_tab(get_value_case_insensitive(ai_data, 'Storytelling_Narrative', {}))
                                with tab8: render_dashboard_tab(get_value_case_insensitive(ai_data, 'Formatting_Visual_Hierarchy', {}))
                                with tab9: render_dashboard_tab(get_value_case_insensitive(ai_data, 'Tone_Language_Readability', {}))
                                with tab10: render_dashboard_tab(get_value_case_insensitive(ai_data, 'Final_Verdict_Action_Plan', {}))
                            except Exception as e:
                                st.error(f"Analysis failed. Llama3 Error: {e}")

                    st.markdown("---")

                    connection.commit()
                else:
                    st.error('Something went wrong..')
        with tab_builder:
            col_header, col_demo = st.columns([8, 2])
            with col_header:
                st.markdown("<h2 style='margin:0;'>✨ Elite Resume Builder</h2>", unsafe_allow_html=True)
            with col_demo:
                st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
                if st.button("DEMO", type="secondary"):
                    st.session_state.demo_loaded = True
                    st.rerun()
            
            st.markdown("Fill out any of the 15 customizable sections below to generate an ATS-optimized, top 0.001% PDF resume.")
            demo = st.session_state.get('demo_loaded', False)
            
            with st.form("elite_resume_builder_form"):
                st.markdown("---")
                st.subheader("1. Contact Essentials")
                b_name = st.text_input("Full Name", value="Alex Stratos" if demo else "")
                b_email = st.text_input("Email Address", value="alex.stratos@premium.io" if demo else "")
                b_phone = st.text_input("Phone Number", value="+1 (555) 987-6543" if demo else "")
                b_address = st.text_input("Location (City, Country)", value="San Francisco, CA" if demo else "")
                b_linkedin = st.text_input("LinkedIn/Portfolio URL", value="linkedin.com/in/alexstratos" if demo else "")

                st.markdown("---")
                st.subheader("2. Professional Objective")
                b_objective = st.text_area("Career Objective", height=80, value="To leverage a decade of engineering leadership and architectural expertise to drive hyper-scale growth and technological innovation in a visionary FAANG-tier organization." if demo else "")

                st.markdown("---")
                st.subheader("3. Executive Summary")
                b_summary = st.text_area("Professional Summary", height=120, value="Visionary engineering leader with a decade of experience architecting distributed systems handling millions of daily transactions. Proven track record of scaling engineering teams from 5 to 50+ members while reducing cloud infrastructure costs by 40%." if demo else "")
                
                st.markdown("---")
                st.subheader("4. Career Trajectory (Experience)")
                b_experience = st.text_area("Work Experience (Include Company, Dates, Role, and Bullet Points)", height=200, value="""TechNova Solutions | 2020 - Present
Director of Engineering
- Spearheaded the architectural migration from a monolithic legacy system to a microservices architecture, resulting in a 300% improvement in API response times.
- Managed and scaled an engineering organization of 45+ engineers across 6 cross-functional pods, improving delivery cadence by 25%.
- Negotiated enterprise cloud contracts and optimized AWS resource allocation, slashing annual infrastructure OPEX by $1.2M.

Quantum Financial | 2016 - 2020
Lead Backend Engineer
- Designed and implemented a high-frequency trading execution engine in C++ and Go, processing trades with sub-millisecond latency.
- Mentored a team of 8 junior engineers, leading to 3 internal promotions within 18 months.""" if demo else "")

                st.markdown("---")
                st.subheader("5. Educational Background")
                b_education = st.text_area("Education (Include Degree, Institution, and Year)", height=120, value="""Master of Science in Computer Science | Stanford University | 2016
- Specialization in Distributed Systems and Artificial Intelligence
- Graduated with Distinction (GPA: 3.9/4.0)

Bachelor of Science in Software Engineering | MIT | 2014""" if demo else "")
                
                st.markdown("---")
                st.subheader("6. Technical Arsenal (Hard Skills)")
                b_tech_skills = st.text_area("Technical Skills (Comma separated)", height=100, value="Python, Go, C++, Rust, React, Node.js, AWS, Kubernetes, Docker, PostgreSQL, Redis, Apache Kafka, GraphQL, Terraform" if demo else "")
                
                st.markdown("---")
                st.subheader("7. Leadership & Soft Skills")
                b_soft_skills = st.text_area("Soft Skills (Comma separated)", height=100, value="Cross-functional Leadership, Agile Scaling, Cloud Cost Optimization, Mentorship, Strategic Planning, Public Speaking" if demo else "")

                st.markdown("---")
                st.subheader("8. Innovation Portfolio (Projects)")
                b_projects = st.text_area("Notable Projects (Describe key achievements)", height=120, value="""OpenSource DB Connector (Maintainer)
- Created and maintain a highly popular Python database connector with over 500k monthly downloads on PyPI.
- Merged over 100+ PRs from the community and enforce strict CI/CD pipelines.

Project Phoenix (TechNova)
- Internal code name for the zero-downtime database migration affecting 10M+ users.""" if demo else "")
                
                st.markdown("---")
                st.subheader("9. Professional Certifications")
                b_certifications = st.text_area("Certifications & Licenses", height=100, value="""AWS Certified Solutions Architect - Professional (2023)
Certified Kubernetes Administrator (CKA)
Scrum Master Certified (SMC)""" if demo else "")

                st.markdown("---")
                st.subheader("10. Distinguished Awards")
                b_awards = st.text_area("Awards & Honors", height=100, value="""TechNova Innovator of the Year (2022)
HackMIT First Place Overall (2013)""" if demo else "")

                st.markdown("---")
                st.subheader("11. Volunteer Impact")
                b_volunteer = st.text_area("Volunteer Experience", height=100, value="""Code for America - Lead Mentor (2018-Present)
Girls Who Code - Guest Speaker""" if demo else "")

                st.markdown("---")
                st.subheader("12. Linguistic Proficiency")
                b_languages = st.text_area("Languages Spoken", height=100, value="""English (Native)
Mandarin (Fluent)
Spanish (Conversational)""" if demo else "")

                st.markdown("---")
                st.subheader("13. Thought Leadership")
                b_publications = st.text_area("Publications & Presentations", height=100, value="""Scaling Microservices at Edge (QCon 2021)
The Future of Serverless Architectures (Medium, 2020)""" if demo else "")

                st.markdown("---")
                st.subheader("14. Personal Interests (Hobbies)")
                b_hobbies = st.text_area("Hobbies & Interests", height=100, value="Ultra-marathon running, Specialty Coffee Roasting, Amateur Chess" if demo else "")
                
                st.markdown("---")
                st.subheader("15. Custom Elite Section")
                b_custom_title = st.text_input("Custom Section Title (e.g., Patents, Military Service)", value="International Experience" if demo else "")
                b_custom_content = st.text_area("Custom Section Content", height=100, value="Managed remote teams across 4 time zones (US, Europe, Asia) for global software rollout." if demo else "")
                
                b_references = "Available upon request."
                
                st.markdown("---")
                submit_elite = st.form_submit_button("Generate Ultimate FAANG Resume", type="primary")
            
            if submit_elite:
                # Generate Timestamp
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)

                data = {
                    'name': b_name, 'email': b_email, 'phone': b_phone, 'address': b_address, 'linkedin': b_linkedin,
                    'objective': b_objective, 'summary': b_summary, 'experience': b_experience, 'education': b_education,
                    'tech_skills': b_tech_skills, 'soft_skills': b_soft_skills, 'projects': b_projects,
                    'certifications': b_certifications, 'languages': b_languages, 'awards': b_awards,
                    'publications': b_publications, 'volunteer': b_volunteer, 'hobbies': b_hobbies, 'references': b_references,
                    'custom_title': b_custom_title, 'custom_content': b_custom_content
                }
                
                # PDF generation
                pdf_bytes = generate_elite_pdf(data)
                
                # Save to Database
                import json
                try:
                    builder_insert_sql = """INSERT INTO builder_submissions (Username, Name, Email, Timestamp, ResumeData_JSON)
                                            VALUES (%s, %s, %s, %s, %s)"""
                    cursor.execute(builder_insert_sql, (st.session_state.current_user, b_name, b_email, timestamp, json.dumps(data)))
                    connection.commit()
                except Exception as e:
                    st.error(f"Database error: {str(e)}")
                
                st.success("Ultimate FAANG Resume successfully generated!")
                st.download_button(
                    label="⬇️ Download Your Premium PDF",
                    data=pdf_bytes,
                    file_name=f"{b_name.replace(' ', '_')}_Elite_Resume.pdf" if b_name else "Elite_Resume.pdf",
                    mime="application/pdf"
                )
        
        with tab_cover_letter:
            st.markdown('''<h5 style='text-align: left; color: #10b981;'> AI-Powered Elite Cover Letter Generator</h5>''',
                        unsafe_allow_html=True)
            st.info("🎯 **Objective**: Transform your resume into a compelling narrative that grabs the attention of hiring managers at the world's most innovative companies.")
            
            cl_pdf = st.file_uploader("Upload Resume for Cover Letter", type=["pdf"], key="cl_pdf")
            job_desc = st.text_area("Target Job Description (Optional but Recommended)", height=100, placeholder="Paste the job description here to tailor your cover letter...")
            
            if cl_pdf is not None:
                if st.button("Generate Elite Cover Letter", type="primary", use_container_width=True):
                    with st.spinner("Crafting your professional narrative..."):
                        import ollama
                        temp_path = f'./Uploaded_Resumes/cl_{int(time.time())}_{cl_pdf.name}'
                        with open(temp_path, "wb") as f:
                            f.write(cl_pdf.getbuffer())
                        
                        raw_text = pdf_reader(temp_path)
                        try:
                            prompt = f"""
                            You are a world-class career coach and executive copywriter. 
                            Write a highly professional, persuasive, and modern cover letter based on the following resume content.
                            
                            Instructions:
                            1. Tone: Confident, professional, and results-oriented.
                            2. Structure: Introduction, 2 core value-add paragraphs, and a strong call to action.
                            3. Use specific metrics and achievements from the resume.
                            4. If a job description is provided, tailor the letter to solve the specific problems mentioned.
                            
                            Resume Content:
                            {raw_text}
                            
                            Target Job Description:
                            {job_desc if job_desc else "General High-Tier Technology Role"}
                            """
                            
                            response = ollama.generate(model=st.session_state.get('ollama_model', 'llama3'), prompt=prompt, options={"temperature": 0.0, "top_k": 20, "top_p": 0.9, "num_ctx": 4096})
                            letter_text = response['response']
                            
                            # Store in DB
                            ts = time.time()
                            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                            timestamp = str(cur_date+'_'+cur_time)
                            
                            try:
                                cl_insert_sql = """INSERT INTO cover_letter_submissions (Username, Timestamp, Job_Description, Generated_Letter)
                                                  VALUES (%s, %s, %s, %s)"""
                                cursor.execute(cl_insert_sql, (st.session_state.current_user, timestamp, job_desc if job_desc else "N/A", letter_text))
                                connection.commit()
                            except: pass

                            st.markdown("---")
                            st.markdown("### ✉️ Your Tailored Cover Letter")
                            st.markdown(letter_text)
                            st.success("Cover letter generated and saved! Copy and refine it for your application.")
                        except Exception as e:
                            st.error(f"Llama3 Error: {str(e)}")
        
        with tab_interview:
            st.markdown('''<h5 style='text-align: left; color: #3b82f6;'> AI-Powered Interview Simulation & Question Generator</h5>''',
                        unsafe_allow_html=True)
            
            st.info("💡 **Strategy**: Our AI analyzes your specific career trajectory and skills to generate the exact questions FAANG recruiters would ask you.")
            
            interview_pdf = st.file_uploader("Upload Resume for Question Generation", type=["pdf"], key="interview_pdf")
            num_questions = st.number_input("Number of questions to generate", min_value=1, max_value=25, value=5)
            
            if interview_pdf is not None:
                if st.button("Generate Interview Questions", type="primary", use_container_width=True):
                    with st.spinner("Analyzing profile and generating questions..."):
                        import ollama
                        temp_path = f'./Uploaded_Resumes/int_{int(time.time())}_{interview_pdf.name}'
                        with open(temp_path, "wb") as f:
                            f.write(interview_pdf.getbuffer())
                        
                        raw_text = pdf_reader(temp_path)
                        
                        try:
                            prompt = f"""
                            You are an elite executive interviewer at a top-tier technology firm (Google, Meta, OpenAI). 
                            Based on the following resume text, generate exactly {num_questions} sophisticated and tailored interview questions.
                            
                            Instructions:
                            1. Mix behavioral (STAR method), deep technical, and system design/leadership questions.
                            2. Questions must be specific to the projects and technologies mentioned in the resume.
                            3. For each question, provide a 1-sentence 'Pro-Tip' for the candidate.
                            
                            Format the output beautifully with markdown. Use glassmorphic-style dividers.
                            
                            Resume Content:
                            {raw_text}
                            """
                            
                            response = ollama.generate(model=st.session_state.get('ollama_model', 'llama3'), prompt=prompt, options={"temperature": 0.0, "top_k": 20, "top_p": 0.9, "num_ctx": 4096})
                            st.markdown("---")
                            st.markdown("### 🏆 AI Interview Prep: Tailored for You")
                            st.markdown(response['response'])
                            st.success("Questions generated successfully! Practice these to crush your next interview.")
                        except Exception as e:
                            st.error(f"Llama3 Error: {str(e)}")

        with tab_jobs:
            st.markdown('''<h5 style='text-align: left; color: #f59e0b;'> Live Market Matches & Job Insights</h5>''',
                        unsafe_allow_html=True)
            st.info("🚀 **Market Opportunity**: We analyze your resume against current hiring trends to find your best matches on LinkedIn and Naukri.")
            
            job_pdf = st.file_uploader("Upload Resume for Job Matching", type=["pdf"], key="job_pdf")
            
            if job_pdf is not None:
                if st.button("Find My Market Value", type="primary", use_container_width=True):
                    with st.spinner("Analyzing market data for your profile..."):
                        temp_path = f'./Uploaded_Resumes/job_{int(time.time())}_{job_pdf.name}'
                        with open(temp_path, "wb") as f:
                            f.write(job_pdf.getbuffer())
                        
                        raw_text = pdf_reader(temp_path)
                        
                        import ollama
                        try:
                            prompt = f"""
                            You are an elite AI Career Matchmaker. Analyze the following resume and generate a detailed job market compatibility report.
                            Output a STRICT JSON object (no markdown).
                            
                            Keys required:
                            "Recommended_Path": The #1 career path for this candidate.
                            "Top_3_Role_Matches": [
                                {{"Title": "...", "Match_Score": 95, "Why": "...", "LinkedIn_Search_Query": "..."}},
                                {{"Title": "...", "Match_Score": 88, "Why": "...", "LinkedIn_Search_Query": "..."}},
                                {{"Title": "...", "Match_Score": 82, "Why": "...", "LinkedIn_Search_Query": "..."}}
                            ],
                            "Market_Value": {{"Salary_Range": "...", "Demand_Level": "High/Critical/Medium"}},
                            "Target_Keywords": "Skill1, Skill2, Skill3"
                            
                            CRITICAL: Output ONLY the JSON object. No preamble, no explanation. Escape all quotes.
                            
                            Resume Content:
                            {raw_text}
                            """
                            
                            response = ollama.generate(model=st.session_state.get('ollama_model', 'llama3'), prompt=prompt, options={"temperature": 0.0, "top_k": 20, "top_p": 0.9, "num_ctx": 4096})
                            raw_response = response['response']
                            clean_json_text = raw_response.replace('```json', '').replace('```', '').strip()
                            
                            start = clean_json_text.find('{')
                            end = clean_json_text.rfind('}')
                            if start != -1 and end != -1:
                                clean_json_text = clean_json_text[start:end+1]
                            
                            job_data = robust_json_load(clean_json_text)
                            
                            if not job_data:
                                st.error("AI returned a malformed response that couldn't be parsed. Please try again.")
                                st.expander("Debug: Cleaned JSON").code(clean_json_text)
                                st.expander("Debug: Raw Response").write(raw_response)
                                return
                            
                            # Store in DB
                            ts = time.time()
                            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                            timestamp = str(cur_date+'_'+cur_time)
                            
                            try:
                                jm_insert_sql = """INSERT INTO job_match_submissions (Username, Timestamp, Analysis_JSON)
                                                  VALUES (%s, %s, %s)"""
                                cursor.execute(jm_insert_sql, (st.session_state.current_user, timestamp, clean_json_text))
                                connection.commit()
                            except: pass
                            
                            st.markdown(f"## 🚀 {job_data.get('Recommended_Path')}")
                            st.markdown(f"**Market Demand:** {job_data['Market_Value']['Demand_Level']} | **Est. Salary:** {job_data['Market_Value']['Salary_Range']}")
                            
                            st.markdown("---")
                            st.markdown("### 🏆 Top Role Matches")
                            
                            for match in job_data['Top_3_Role_Matches']:
                                with st.expander(f"{match['Title']} — {match['Match_Score']}% Match"):
                                    st.write(f"**Why you match:** {match['Why']}")
                                    l_query = match['LinkedIn_Search_Query'].replace(' ', '%20')
                                    n_query = match['LinkedIn_Search_Query'].replace(' ', '%20')
                                    
                                    col_l, col_n = st.columns(2)
                                    with col_l:
                                        st.markdown(f'''<a href="https://www.linkedin.com/jobs/search/?keywords={l_query}" target="_blank" style="text-decoration: none; background: #0077b5; color: white; padding: 8px 16px; border-radius: 5px; font-size: 0.9em;">LinkedIn Live Jobs</a>''', unsafe_allow_html=True)
                                    with col_n:
                                        st.markdown(f'''<a href="https://www.naukri.com/{match['Title'].replace(' ', '-')}-jobs?k={n_query}" target="_blank" style="text-decoration: none; background: #ff7519; color: white; padding: 8px 16px; border-radius: 5px; font-size: 0.9em;">Naukri Live Jobs</a>''', unsafe_allow_html=True)
                            
                            st.success("Analysis complete. Explore these live feeds to find your next breakthrough role.")
                        except Exception as e:
                            st.error(f"Llama3 Market Analysis Error: {str(e)}")

    elif st.session_state.role == 'Admin':
        ## Admin Side
        col_admin1, col_admin2 = st.columns([8, 2])
        with col_admin1:
            st.success("Welcome to Admin Dashboard !")
        with col_admin2:
            if st.button("Logout", key="btn_admin_logout"):
                st.session_state.role = None
                st.session_state.current_user = None
                st.query_params.clear()
                st.rerun()

        # Fetch Data
        cursor.execute('''SELECT * FROM user_data''')
        analyzer_raw = cursor.fetchall()
        df_analyzer = pd.DataFrame(analyzer_raw, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                         'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                         'Recommended Course', 'Full Analysis JSON'])
        for col in df_analyzer.columns:
            df_analyzer[col] = df_analyzer[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)

        cursor.execute('''SELECT ID, Username, Name, Email, Timestamp, ResumeData_JSON FROM builder_submissions''')
        builder_raw = cursor.fetchall()
        df_builder = pd.DataFrame(builder_raw, columns=['ID', 'Username', 'Name', 'Email', 'Timestamp', 'ResumeData_JSON'])
        
        cursor.execute('''SELECT ID, Username, Timestamp, Job_Description, Generated_Letter FROM cover_letter_submissions''')
        cl_raw = cursor.fetchall()
        df_cl = pd.DataFrame(cl_raw, columns=['ID', 'Username', 'Timestamp', 'Job Description', 'Generated Letter'])

        cursor.execute('''SELECT ID, Username, Timestamp, Analysis_JSON FROM job_match_submissions''')
        jm_raw = cursor.fetchall()
        df_jm = pd.DataFrame(jm_raw, columns=['ID', 'Username', 'Timestamp', 'Analysis_JSON'])
        
        adm_tab1, adm_tab2, adm_tab3, adm_tab4 = st.tabs(["📊 Analyzer Data", "✨ Builder Submissions", "✉️ Cover Letters", "🚀 Job Matches"])
        
        with adm_tab1:
            st.header("**Parsed Resumes (Analyzer)**")
            st.dataframe(df_analyzer, use_container_width=True)
            st.markdown(get_table_download_link(df_analyzer,'Analyzer_Report.csv','Download Analyzer Report'), unsafe_allow_html=True)
            
            st.markdown("---")
            st.header("🎯 Ultimate Candidate Deep-Dive")
            df_valid_json = df_analyzer[df_analyzer['Full Analysis JSON'].notna() & (df_analyzer['Full Analysis JSON'] != '{}') & (df_analyzer['Full Analysis JSON'] != '')]
            
            if not df_valid_json.empty:
                candidate_list = df_valid_json['Name'] + " (" + df_valid_json['Email'] + ")"
                selected_cand = st.selectbox("Select Candidate to view Ultimate Dashboard", options=list(candidate_list), index=None, placeholder="Select...")
                
                if selected_cand is not None:
                    selected_row = df_valid_json[df_valid_json['Name'] + " (" + df_valid_json['Email'] + ")" == selected_cand].iloc[0]
                    json_str = selected_row['Full Analysis JSON']
                    try:
                        import json
                        cand_data = json.loads(json_str, strict=False)
                        st.markdown(f"## 🏆 {selected_row['Name']}'s Ultimate Profile")
                        score_col, role_col, level_col = st.columns(3)
                        with score_col: st.metric("Executive ATS Score", f"{cand_data.get('ATS_Score')}/100")
                        with role_col: st.metric("Best Fit Role", cand_data.get('Recommended_Role'))
                        with level_col: st.metric("Seniority", cand_data.get('Candidate_Level'))
                        
                        st.markdown("---")
                        def render_admin_dashboard_tab(tab_data):
                            score = get_value_case_insensitive(tab_data, 'Score', 0)
                            try: score = int(float(score))
                            except: score = 0
                            st.metric("Section Score", f"{score}/100")
                            if not tab_data or not isinstance(tab_data, dict): return
                            verdict = get_value_case_insensitive(tab_data, 'Verdict', 'N/A')
                            st.info(f"**Verdict:** {verdict}")
                            c1, c2 = st.columns(2)
                            with c1:
                                st.success("**Strengths**")
                                for s in tab_data.get('Strengths', []): st.markdown(f"- {s}")
                            with c2:
                                st.warning("**Weaknesses & Gaps**")
                                for w in tab_data.get('Weaknesses', []): st.markdown(f"- {w}")
                        
                        a_tab1, a_tab2, a_tab3, a_tab4, a_tab5 = st.tabs(["Summary", "Business ROI", "Trajectory", "Skills", "Action Plan"])
                        with a_tab1: render_admin_dashboard_tab(get_value_case_insensitive(cand_data, 'Executive_Summary', {}))
                        with a_tab2: render_admin_dashboard_tab(get_value_case_insensitive(cand_data, 'Business_Value_ROI', {}))
                        with a_tab3: render_admin_dashboard_tab(get_value_case_insensitive(cand_data, 'Professional_Trajectory', {}))
                        with a_tab4: render_admin_dashboard_tab(get_value_case_insensitive(cand_data, 'Technical_Arsenal', {}))
                        with a_tab5: render_admin_dashboard_tab(get_value_case_insensitive(cand_data, 'Final_Verdict_Action_Plan', {}))
                    except: st.error("Failed to load JSON data.")

        with adm_tab2:
            st.header("**Builded Resumes (Executive Builder)**")
            if not df_builder.empty:
                st.dataframe(df_builder.drop(columns=['ResumeData_JSON']), use_container_width=True)
                st.markdown(get_table_download_link(df_builder,'Builder_Submissions.csv','Download Builder Report'), unsafe_allow_html=True)
                
                st.markdown("---")
                st.subheader("📄 Submission Inspector")
                selected_b = st.selectbox("Select Submission to inspect details", options=list(df_builder['Name'] + " (" + df_builder['Timestamp'] + ")"))
                if selected_b:
                    b_row = df_builder[df_builder['Name'] + " (" + df_builder['Timestamp'] + ")" == selected_b].iloc[0]
                    try:
                        import json
                        b_json = json.loads(b_row['ResumeData_JSON'])
                        with st.expander("View Full Submission JSON", expanded=True):
                            st.json(b_json)
                    except: st.error("Error parsing submission data.")
            else:
                st.info("No resumes have been built yet.")

        with adm_tab3:
            st.header("✉️ Generated Cover Letters")
            if not df_cl.empty:
                st.dataframe(df_cl.drop(columns=['Generated Letter']), use_container_width=True)
                st.markdown("---")
                st.subheader("📝 Letter Preview")
                selected_cl = st.selectbox("Select Record to view Letter", options=list(df_cl['Username'] + " (" + df_cl['Timestamp'] + ")"))
                if selected_cl:
                    cl_row = df_cl[df_cl['Username'] + " (" + df_cl['Timestamp'] + ")" == selected_cl].iloc[0]
                    st.text_area("Target Job Description", value=cl_row['Job Description'], height=150, disabled=True)
                    st.markdown("---")
                    st.markdown(cl_row['Generated Letter'])
            else:
                st.info("No cover letters generated yet.")

        with adm_tab4:
            st.header("🚀 Job Market Matches")
            if not df_jm.empty:
                st.dataframe(df_jm.drop(columns=['Analysis_JSON']), use_container_width=True)
                st.markdown("---")
                st.subheader("🔍 Match Details")
                selected_jm = st.selectbox("Select Record to view Job Matches", options=list(df_jm['Username'] + " (" + df_jm['Timestamp'] + ")"))
                if selected_jm:
                    jm_row = df_jm[df_jm['Username'] + " (" + df_jm['Timestamp'] + ")" == selected_jm].iloc[0]
                    try:
                        import json
                        jm_data = json.loads(jm_row['Analysis_JSON'])
                        st.json(jm_data)
                    except: st.error("Error parsing job match data.")
            else:
                st.info("No job matches generated yet.")

run()
