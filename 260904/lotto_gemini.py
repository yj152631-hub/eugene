import streamlit as st
import random
import time
import base64
import os
from datetime import datetime

st.set_page_config(
    page_title="로또 번호 생성기", 
    page_icon="🍀",
    layout="centered"
)

current_dir = os.path.dirname(os.path.abspath(__file__))
font_file = os.path.join(current_dir, "Griun_Fromsol-Rg.ttf")

def get_base64_font(font_path):
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    return None

font_base64 = get_base64_font(font_file)

font_css = ""
if font_base64:
    font_css = f"""
    @font-face {{
        font-family: 'Griun_Fromsol-Rg';
        src: url(data:font/ttf;charset=utf-8;base64,{font_base64}) format('truetype');
        font-weight: normal;
        font-style: normal;
    }}
    """
else:
    st.warning(f"⚠️ '{font_file}' 파일을 찾을 수 없습니다. 파이썬 파일과 같은 폴더에 넣어주세요.")

st.markdown(f"""
<style>
    {font_css}
    .stApp {{
        background-color: #F0FDF4 !important;
        color: #222222 !important;
    }}
    html, body, [class*="css"], .stMarkdown, p, span, div, label, button, a, strong, b {{
        font-family: 'Griun_Fromsol-Rg', sans-serif !important;
        color: #222222 !important;
        font-weight: normal !important;
    }}
    .block-container {{
        text-align: center !important;
        max-width: 600px !important;
        padding: 3rem 1rem 2rem 1rem !important;
    }}
    div[data-testid="stMarkdownContainer"] {{
        text-align: center !important;
        width: 100%;
    }}
    .custom-title {{
        font-size: 2.2rem !important; 
        font-weight: normal !important;
        color: #111111 !important;
        margin-top: 10px;
        margin-bottom: 5px;
    }}
    .custom-caption {{
        font-size: 1.0rem !important; 
        font-weight: normal !important;
        color: #555555 !important;
        margin-bottom: 20px;
    }}
    @keyframes blink {{
        0% {{ opacity: 0.2; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.2; }}
    }}
    .blinking-text {{
        font-size: 1.1em;
        color: #2E7D32;
        margin-bottom: 10px;
        font-weight: normal !important;
        animation: blink 1.2s infinite ease-in-out;
    }}
    div[data-testid="stInfo"] {{
        background-color: #E2FDCB !important;
        border: 1px solid #C5E6A3 !important;
        color: #222222 !important;
        width: fit-content !important;
        margin: 15px auto !important;
        text-align: center !important;
        border-radius: 10px;
    }}
    div[data-testid="stInfo"] * {{
        font-family: 'Griun_Fromsol-Rg', sans-serif !important;
        color: #222222 !important;
        font-weight: normal !important;
    }}
    div.st-key-lotto_generate_btn {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }}
    div.st-key-lotto_generate_btn > button {{
        background-color: #4CAF50 !important;
        color: white !important;
        font-family: 'Griun_Fromsol-Rg', sans-serif !important;
        font-size: 18px !important;
        font-weight: normal !important;
        border-radius: 30px !important;
        padding: 8px 24px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transition: 0.3s !important;
        width: auto !important;
    }}
    div.st-key-lotto_generate_btn > button * {{
        color: white !important;
        font-weight: normal !important;
    }}
    div.st-key-lotto_generate_btn > button:hover {{
        background-color: #45a049 !important;
        box-shadow: 0 6px 10px rgba(0,0,0,0.2) !important;
    }}
    div.st-key-re_generate_btn > button {{
        background-color: #4CAF50 !important;
        color: white !important;
        font-family: 'Griun_Fromsol-Rg', sans-serif !important;
        font-size: 18px !important;
        font-weight: normal !important;
        border-radius: 30px !important;
        padding: 8px 24px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transition: 0.3s !important;
        width: 100% !important;
    }}
    div.st-key-re_generate_btn > button * {{
        color: white !important;
        font-weight: normal !important;
    }}
    div.st-key-re_generate_btn > button:hover {{
        background-color: #45a049 !important;
        box-shadow: 0 6px 10px rgba(0,0,0,0.2) !important;
    }}
    div.stLinkButton > a {{
        background-color: #FFFFFF !important;
        color: #2E7D32 !important;
        font-family: 'Griun_Fromsol-Rg', sans-serif !important;
        font-size: 18px !important;
        font-weight: normal !important;
        border-radius: 30px !important;
        padding: 8px 24px !important;
        border: 2px solid #4CAF50 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        text-decoration: none !important;
        transition: 0.3s !important;
        width: 100% !important;
        display: block !important;
        text-align: center !important;
    }}
    div.stLinkButton > a * {{
        color: #2E7D32 !important;
        font-weight: normal !important;
    }}
    div.stLinkButton > a:hover {{
        background-color: #F1F8F5 !important;
        color: #1B5E20 !important;
        border-color: #45a049 !important;
    }}
    @media (max-width: 768px) {{
        .lotto-result-text {{
            font-size: 0.88em !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

if "generated" not in st.session_state:
    st.session_state.generated = False

st.markdown('<div class="custom-title">🎱 로또 번호 자동 생성기!</div>', unsafe_allow_html=True)
st.markdown('<div class="custom-caption">버튼을 누르면 로또 번호 5세트가 자동으로 생성됩니다.</div>', unsafe_allow_html=True)

def get_ball_emoji(num: int) -> str:
    if num <= 10:
        return '🟡'  
    elif num <= 20:
        return '🔵'  
    elif num <= 30:
        return '🔴'  
    elif num <= 40:
        return '⚫'  
    else:
        return '🟢'  

def lotto_one_set() -> list:
    numbers = set()
    while len(numbers) < 6:
        numbers.add(random.randint(1, 45))
    return sorted(numbers)

st.markdown("---")

if not st.session_state.generated:
    if st.button('🍀 5세트 번호 생성하기', key='lotto_generate_btn'):
        st.session_state.generated = True
        st.rerun()

if st.session_state.generated:
    gif_placeholder = st.empty()
    cute_gif_url = "https://media.tenor.com/7D-5oM-y_B8AAAAi/gacha-machine.gif"
    
    with gif_placeholder.container():
        st.markdown('<div class="blinking-text">✨ 1등 당첨 번호를 생성하는 중... ✨</div>', unsafe_allow_html=True)
        st.image(cute_gif_url, width=220)
            
    time.sleep(2.5)
    gif_placeholder.empty()
    st.balloons()  
    
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.info(f'⏱️ 생성 시각 : {now_str}')

    for set_index in range(1, 6):
        lotto_nums = lotto_one_set()
        formatted_balls = " ".join([f"{get_ball_emoji(n)} {n:02d}" for n in lotto_nums])
        st.markdown(f'<p class="lotto-result-text" style="font-size: 1.1em; text-align: center; margin: 6px; color: #222222; font-weight: normal;">{set_index}세트 : &nbsp; {formatted_balls}</p >', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="font-size: 1.3em; text-align: center; font-weight: normal; color: #111111; margin-bottom: 10px;">🍀 행운을 빕니다! 🍀</p >', unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.link_button("🛒 로또 사러 가기", "https://www.dhlottery.co.kr/", use_container_width=True)
    with col_btn2:
        if st.button("🔄 다시 생성하기", key='re_generate_btn', use_container_width=True):
            st.rerun()