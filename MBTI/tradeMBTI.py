import streamlit as st
import base64
import os

# 페이지 기본 설정
st.set_page_config(page_title="무역 직무 MBTI", page_icon="🚢", layout="centered")

# --- 1. 폰트 및 디자인 설정 (CSS 주입) ---
@st.cache_data
def get_base64_font(font_path):
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# 폰트 NanumSquareNeo-Variable 적용
font_base64 = get_base64_font("NanumSquareNeo-Variable.ttf")

# CSS 스타일 정의
css = f"""
<style>
/* 배경색 연한 하늘색으로 변경 */
.stApp {{
    background-color: #E6F3FF;
}}

/* 폰트 적용 */
"""
if font_base64:
    css += f"""
    @font-face {{
        font-family: 'NanumSquareNeo';
        src: url(data:font/ttf;charset=utf-8;base64,{font_base64}) format('truetype');
    }}
    * {{
        font-family: 'NanumSquareNeo', sans-serif !important;
    }}
    """

css += """
/* 본문 텍스트, 버튼 텍스트 크기 전체적으로 60% 수준 축소 (약 17px) */
.stMarkdown p, .stButton button p, div[data-testid="stAlert"] p {
    font-size: 17px !important;
    line-height: 1.6 !important;
}

/* 설명 문구 가운데 정렬 */
.stMarkdown p.center-desc {
    text-align: center !important;
}

/* 질문(h3) 및 결과 소제목(h3) 폰트 크기 축소 및 가운데 정렬 */
h3 {
    text-align: center !important;
    font-size: 22px !important;
    margin-bottom: 20px !important;
}

/* ★ 메인 타이틀(h1) 및 결과 제목(h2) 폰트 크기 대폭 축소 ★ */
h1 {
    text-align: center !important;
    font-size: 28px !important;
    padding-bottom: 10px !important;
}

h2 {
    text-align: center !important;
    font-size: 24px !important;
}

/* 결과창 설명 박스 가운데 정렬 */
div[data-testid="stAlert"] {
    text-align: center !important;
}

/* 부드러운 페이지 전환 애니메이션 */
.block-container {
    animation: smoothLoad 0.5s ease-in-out;
}

@keyframes smoothLoad {
    0% { opacity: 0; transform: translateY(15px); }
    100% { opacity: 1; transform: translateY(0); }
}

/* 결과창 강조 슬라이드업 애니메이션 추가 */
.result-highlight {
    animation: slideUpHighlight 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    opacity: 0;
    transform: translateY(60px);
}

@keyframes slideUpHighlight {
    100% { opacity: 1; transform: translateY(0); }
}

/* 일반 버튼(선택지, 다시하기) 디자인 다듬기 (버튼 패딩도 글자 크기에 맞춰 축소) */
div.stButton > button[kind="secondary"] {
    transition: all 0.3s ease;
    border-radius: 12px;
    background-color: #ffffff;
    border: 1px solid #b3d9ff;
    padding: 12px !important; 
}
div.stButton > button[kind="secondary"]:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    border: 1px solid #66b3ff;
}

/* 시작하기 버튼(빨간색 포인트) 디자인 */
div.stButton > button[kind="primary"] {
    transition: all 0.3s ease;
    border-radius: 12px;
    background-color: #FF4B4B !important;
    color: white !important;
    border: none !important;
    padding: 12px !important; 
    font-weight: bold;
}
div.stButton > button[kind="primary"]:hover {
    transform: scale(1.05);
    background-color: #FF3333 !important;
    box-shadow: 0 6px 15px rgba(255, 75, 75, 0.3);
}
</style>
"""

st.markdown(css, unsafe_allow_html=True)


# --- 2. 데이터 정의 (질문 20개 및 직무 6개)[cite: 1] ---
questions = [
    {"q": "바이어와의 첫 미팅에서 나는?", "c1": ("먼저 다가가 스몰톡 리드", "E"), "c2": ("상대의 말을 들으며 차분히 탐색", "I")},
    {"q": "해외 출장 중 저녁 시간은?", "c1": ("현지 파트너들과 식사하며 네트워킹", "E"), "c2": ("숙소에서 쉬며 내일 미팅 준비", "I")},
    {"q": "무역 박람회에 갔을 때 나는?", "c1": ("최대한 많은 부스를 돌며 명함 교환", "E"), "c2": ("타겟팅한 부스만 깊게 조사", "I")},
    {"q": "업무 스트레스가 쌓였을 때?", "c1": ("동료들과 티타임하며 수다로 해소", "E"), "c2": ("조용히 혼자만의 시간 가지기", "I")},
    {"q": "협상 중 분위기가 무거워지면?", "c1": ("가벼운 농담으로 분위기 환기", "E"), "c2": ("본론에 더욱 집중하여 진지하게 돌파", "I")},
    {"q": "신규 아이템을 검토할 때?", "c1": ("과거 데이터와 현재 단가 분석", "S"), "c2": ("미래 시장 트렌드와 성장성 예측", "N")},
    {"q": "바이어의 장문 이메일을 볼 때?", "c1": ("선적일, 수량 등 구체적 조건부터 확인", "S"), "c2": ("이메일의 전체적인 의도 파악", "N")},
    {"q": "클레임 발생 시 먼저 하는 일은?", "c1": ("계약서 조항과 사실관계 확인", "S"), "c2": ("향후 파트너십에 미칠 영향 고려", "N")},
    {"q": "회의 중 아이디어를 낼 때?", "c1": ("즉시 적용 가능한 현실적인 대안", "S"), "c2": ("기존의 틀을 깨는 새로운 기획", "N")},
    {"q": "업무 매뉴얼을 대하는 태도는?", "c1": ("처음부터 끝까지 꼼꼼히 정독", "S"), "c2": ("필요한 부분만 찾아 유연하게 적용", "N")},
    {"q": "파트너사가 납기를 지연시켰을 때?", "c1": ("계약에 따른 페널티 논의", "T"), "c2": ("상대방의 사정을 듣고 조율", "F")},
    {"q": "팀원이 실수했을 때 나의 반응은?", "c1": ("해결책은 뭐야?", "T"), "c2": ("많이 당황했겠다.", "F")},
    {"q": "신규 거래처 선정 시 중요한 것은?", "c1": ("마진율과 객관적인 거래 조건", "T"), "c2": ("상호 신뢰와 장기적 관계 형성", "F")},
    {"q": "업무 중 의견 충돌이 발생하면?", "c1": ("객관적 논리와 근거로 내 의견 관철", "T"), "c2": ("관계가 상하지 않도록 타협점 모색", "F")},
    {"q": "피드백을 전달할 때 나는?", "c1": ("팩트 위주로 명확하고 직설적으로", "T"), "c2": ("상대가 상처받지 않게 돌려서 부드럽게", "F")},
    {"q": "컨테이너 선적 스케줄을 짤 때?", "c1": ("플랜 A부터 C까지 완벽히 세팅", "J"), "c2": ("큰 틀만 잡고 상황에 맞게 유동적 대처", "P")},
    {"q": "갑자기 통관이 지연되어 일정이 꼬이면?", "c1": ("계획이 틀어져 극심한 스트레스", "J"), "c2": ("예상 밖의 일이라 여기고 즉시 대안 모색", "P")},
    {"q": "해외 출장 짐을 쌀 때 나는?", "c1": ("체크리스트를 만들어 미리 준비", "J"), "c2": ("출발 전날 밤 눈에 보이는 대로 챙김", "P")},
    {"q": "중요한 선적 서류 마감이 다가올 때?", "c1": ("며칠 전에 미리 끝내고 여유롭게 검토", "J"), "c2": ("마감 직전 폭발적인 집중력으로 완성", "P")},
    {"q": "퇴근 후 나의 일상은?", "c1": ("정해둔 루틴대로 움직임", "J"), "c2": ("그날의 기분에 따라 즉흥적으로 결정", "P")}
]

# 역량(skills) 및 자격증(certs) 정보 추가[cite: 1]
jobs_mapping = {
    "해외영업 (글로벌 프론티어)": {
        "mbti": ["ESTJ", "ENTJ", "ESTP", "ENTP"], 
        "desc": "목표 지향적이고 협상에 강한 당신! 전 세계를 무대로 뛰는 해외영업이 천직입니다.",
        "role": "신규 해외 바이어 발굴, 수출입 계약 체결, 제품 단가 및 조건 협상, 해외 전시회 참가",
        "skills": "비즈니스 외국어 커뮤니케이션 능력, 유연한 협상력, 글로벌 시장 분석력",
        "certs": "무역영어 1급, OPIc / TOEIC Speaking 등 고급 어학 자격증",
        "avoid": "무역 사무/서류 (하루 종일 모니터만 보며 오타를 검수하는 반복적인 단순 사무는 답답할 수 있어요.)"
    },
    "무역 사무/서류 (디테일 마스터)": {
        "mbti": ["ISTJ", "ISFJ", "INFJ"], 
        "desc": "꼼꼼하고 체계적인 당신! 무역 거래의 뼈대를 완성하는 무역 사무 및 서류 업무에 탁월합니다.",
        "role": "B/L, Invoice 등 수출입 선적 서류 작성 및 검토, L/C(신용장) 조건 확인, 결제 대금 관리",
        "skills": "숫자와 서류를 다루는 꼼꼼함, 체계적인 일정 관리 능력, 무역 규정 이해력",
        "certs": "국제무역사 1급, 무역영어 1급, 외환전문역",
        "avoid": "해외영업 (매번 낯선 사람에게 다가가 맨땅에 헤딩해야 하는 불확실한 환경이 스트레스일 수 있어요.)"
    },
    "포워딩/국제물류 (오퍼레이션 스페셜리스트)": {
        "mbti": ["ESFJ", "ISTP", "ISFP"], 
        "desc": "변수 통제와 상황 대처가 빠른 당신! 최적의 운송 루트를 짜는 포워딩과 물류가 제격입니다.",
        "role": "화물 운송 스케줄 부킹, 최적의 운송 루트 및 운임 기획, 선사 및 화주와의 중간 조율",
        "skills": "신속한 위기 대처 능력, 멀티태스킹, 꼼꼼한 운임 및 부대비용 계산 능력",
        "certs": "물류관리사, 국제물류사, 보세사",
        "avoid": "관세/통관 (융통성 없이 정해진 법규와 매뉴얼대로만 처리해야 하는 정체된 업무는 지루할 수 있어요.)"
    },
    "관세/통관 (컴플라이언스 전문가)": {
        "mbti": ["INTP", "INTJ"], 
        "desc": "원칙을 중시하고 고도의 논리력을 요하는 당신! 법규를 해석하고 가이드를 제시하는 관세/통관 직무에 어울립니다.",
        "role": "수출입 통관 요건 검토, 관세 환급 및 HS Code 분류, FTA 원산지 증명서 발급 및 법적 리스크 관리",
        "skills": "복잡한 법규 해석 능력, 고도의 논리적 사고, 문제 해결을 위한 끈기",
        "certs": "관세사, 원산지관리사, 보세사",
        "avoid": "무역 마케팅 (객관적 논리보다 감성적인 소통과 유행을 좇아야 하는 환경에 흥미를 느끼기 어려워요.)"
    },
    "무역 마케팅 (크리에이티브 디렉터)": {
        "mbti": ["ENFP", "ESFP", "ENFJ"], 
        "desc": "트렌드에 민감하고 소통에 능한 당신! 자사 제품의 매력을 글로벌 시장에 알리는 마케터가 되어보세요.",
        "role": "해외 시장 트렌드 분석, 수출용 제품 패키징 기획, 글로벌 SNS 및 바이어 타겟 프로모션 운영",
        "skills": "최신 트렌드 파악 능력, 창의적인 콘텐츠 기획력, 데이터 기반의 마케팅 전략 수립",
        "certs": "검색광고마케터, 사회조사분석사, ADsP(데이터분석준전문가)",
        "avoid": "무역 사무/서류 (타인과의 소통 없이 하루 종일 숫자와 서류에 파묻혀 지내는 업무는 피곤할 수 있어요.)"
    },
    "글로벌 소싱/구매 (트렌드 헌터)": {
        "mbti": ["INFP"], 
        "desc": "분석력이 뛰어나고 새로운 가치 발굴을 즐기는 당신! 전 세계의 숨은 보석 같은 아이템을 찾아내는 소싱 직무를 추천합니다.",
        "role": "해외 우수 공급업체 발굴, 수입 단가 경쟁력 확보, 글로벌 소비 트렌드에 맞는 신규 아이템 소싱",
        "skills": "공급망 데이터 분석력, 원가 및 수익성 계산, 협력사와의 우호적 관계 유지 능력",
        "certs": "구매자재관리사(KPM), CPSM(국제공인 공급망관리 전문가)",
        "avoid": "포워딩/국제물류 (장기적인 분석보다 당장 터지는 현장의 변수를 실시간으로 쳐내야 하는 압박감이 힘들 수 있어요.)"
    }
}


# --- 3. 상태 관리 (Session State) ---
if 'page' not in st.session_state:
    st.session_state.page = -1
if 'scores' not in st.session_state:
    st.session_state.scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}


# --- 4. UI 및 로직 구현 ---
st.title("🚢 무역 직무 MBTI 테스트")
st.divider()

# --- 4-1. 시작 화면 (page == -1) ---
if st.session_state.page == -1:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 18px; font-weight: bold;'>무역 취업을 꿈꾸는 나,<br>어떤 직무가 잘 맞을까? 🤔</div>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button("🚀 시작하기", type="primary", use_container_width=True):
            st.session_state.page = 0
            st.rerun()

# --- 4-2. 질문 진행 중 (0 <= page < 20) ---
elif 0 <= st.session_state.page < len(questions):
    current_q = questions[st.session_state.page]
    
    # 진행도 텍스트
    st.markdown(f"<div style='text-align: right; font-size: 14px; font-weight: bold; color: #555555; margin-bottom: 5px;'>진행도: {st.session_state.page + 1} / {len(questions)}</div>", unsafe_allow_html=True)
    
    # 진행 바
    st.progress((st.session_state.page) / len(questions))
    
    st.subheader(f"Q{st.session_state.page + 1}. {current_q['q']}")
    st.write("")
    
    def handle_click(mbti_type):
        st.session_state.scores[mbti_type] += 1
        st.session_state.page += 1

    st.button(current_q['c1'][0], on_click=handle_click, args=(current_q['c1'][1],), use_container_width=True)
    st.write("") 
    st.button(current_q['c2'][0], on_click=handle_click, args=(current_q['c2'][1],), use_container_width=True)

# --- 4-3. 테스트 완료 (결과 산출) ---
else:
    scores = st.session_state.scores
    res_mbti = ""
    res_mbti += "E" if scores["E"] > scores["I"] else "I"
    res_mbti += "S" if scores["S"] > scores["N"] else "N"
    res_mbti += "T" if scores["T"] > scores["F"] else "F"
    res_mbti += "J" if scores["J"] > scores["P"] else "P"
    
    matched_job_title = ""
    matched_job_desc = ""
    matched_job_role = ""
    matched_job_skills = ""
    matched_job_certs = ""
    matched_job_avoid = ""
    
    for job, data in jobs_mapping.items():
        if res_mbti in data["mbti"]:
            matched_job_title = job
            matched_job_desc = data["desc"]
            matched_job_role = data["role"]
            matched_job_skills = data["skills"]
            matched_job_certs = data["certs"]
            matched_job_avoid = data["avoid"]
            break
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 결과 제목 애니메이션 적용
    st.markdown(f"""
    <div class="result-highlight">
        <h2>🎉 당신의 무역 MBTI는 <strong>{res_mbti}</strong> 입니다!</h2>
        <h3>추천 직무: 🏆 {matched_job_title}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    st.info(f"✨ {matched_job_desc}")
    st.success(f"💼 **이런 일을 해요:** {matched_job_role}")
    st.warning(f"💡 **요구되는 핵심 능력:** {matched_job_skills}")
    st.info(f"📜 **추천 자격증:** {matched_job_certs}")
    st.error(f"🛑 **이런 직무는 피하는 게 좋아요:** {matched_job_avoid}")
    
    st.divider()
    if st.button("테스트 다시 하기", use_container_width=True):
        st.session_state.page = -1 
        st.session_state.scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
        st.rerun()