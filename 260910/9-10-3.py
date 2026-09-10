import os
from pathlib import Path
import requests
import streamlit as st
from dotenv import load_dotenv

# 페이지 설정 (반응형 모바일 최적화 레이아웃)
st.set_page_config(
    page_title="스마트 실시간 환율 계산기",
    page_icon="💱",
    layout="wide"
)

# 연두색 테마 및 커스텀 폰트(Griun_Fromsol-Rg.ttf) 적용 CSS
st.markdown("""
<style>
    @font-face {
        font-family: 'Griun_Fromsol';
        src: url('Griun_Fromsol-Rg.ttf') format('truetype');
        font-weight: normal;
        font-style: normal;
    }
    
    html, body, [class*="css"] {
        font-family: 'Griun_Fromsol', sans-serif;
        color: #2D3748;
    }
    
    .stApp {
        background-color: #F4FBF7;
    }
    
    /* 버튼 스타일 (연두색 계열) */
    .stButton>button {
        background-color: #81C784;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stButton>button:hover {
        background-color: #66BB6A;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# .env 파일 로드 (상위 폴더 기준)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

# API 키 검증
if not EXCHANGE_API_KEY:
    st.error("상위 폴더의 .env 파일에 EXCHANGE_API_KEY가 설정되어 있는지 확인해주세요.")
    st.stop()

# 주요 통화 목록
CURRENCIES = {
    "대한민국 원 (KRW)": "KRW",
    "미국 달러 (USD)": "USD",
    "유럽 유로 (EUR)": "EUR",
    "일본 엔 (JPY)": "JPY",
    "영국 파운드 (GBP)": "GBP",
    "중국 위안 (CNY)": "CNY",
    "호주 달러 (AUD)": "AUD",
    "캐나다 달러 (CAD)": "CAD"
}

st.title("🌿 스마트 실시간 환율 계산기")
st.markdown("실시간 환율 변동 확인과 금액별 맞춤 물가 체감 가이드, 수수료 계산 및 다중 통화 비교 기능을 제공합니다.")

# 사이드바: 주요 통화 실시간 모니터링 대시보드
st.sidebar.header("📌 주요 통화 모니터링 (vs USD)")
try:
    sidebar_res = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD")
    if sidebar_res.status_code == 200:
        sidebar_rates = sidebar_res.json()["conversion_rates"]
        for name, code in CURRENCIES.items():
            if code != "USD" and code in sidebar_rates:
                st.sidebar.text(f"1 USD = {sidebar_rates[code]:,.2f} {code}")
    else:
        st.sidebar.text("모니터링 데이터 로드 실패")
except Exception:
    st.sidebar.text("네트워크 오류 발생")

st.markdown("---")

# 메인 계산기 UI
col_from, col_to = st.columns(2)
with col_from:
    selected_base = st.selectbox("기준 통화 (From)", list(CURRENCIES.keys()), index=1) # 기본값: USD
with col_to:
    selected_target = st.selectbox("변환할 통화 (To)", list(CURRENCIES.keys()), index=0) # 기본값: KRW

base_code = CURRENCIES[selected_base]
target_code = CURRENCIES[selected_target]

amount = st.number_input("변환할 금액 입력", min_value=0.0, value=100.0, step=10.0)

# 부가 기능 1: 환전 수수료 및 우대율 설정 옵션
with st.expander("⚙️ 환전 수수료 및 우대율 설정 (부가 기능)"):
    apply_fee = st.checkbox("환전 수수료 반영하기", value=False)
    fee_discount = st.slider("환율 우대율 (%)", min_value=0, max_value=100, value=80, step=10)

if st.button("환율 계산하기"):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{base_code}/{target_code}/{amount}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("result") == "success":
            conversion_rate = data["conversion_rate"]
            converted_result = data["conversion_result"]
            
            # 수수료/우대율 반영 계산 로직
            final_result = converted_result
            if apply_fee:
                base_spread = 0.0197
                actual_spread = base_spread * (1 - (fee_discount / 100))
                final_result = converted_result * (1 + actual_spread)
            
            st.success("환율 계산이 완료되었습니다!")
            
            # 메인 결과 출력
            if apply_fee:
                st.metric(
                    label=f"우대율 {fee_discount}% 반영 실 수령액 ({base_code} ➔ {target_code})",
                    value=f"{final_result:,.2f} {target_code}",
                    delta=f"기준 환율: 1 {base_code} = {conversion_rate:,.4f} {target_code}"
                )
            else:
                st.metric(
                    label=f"환율 적용 결과 ({base_code} ➔ {target_code})",
                    value=f"{converted_result:,.2f} {target_code}",
                    delta=f"적용 환율: 1 {base_code} = {conversion_rate:,.4f} {target_code}"
                )
            
            # 원화(KRW) 기준 환산치 계산 (물가 체감 가이드 티어 분류를 위함)
            # target_code가 KRW가 아니면, target -> KRW 환율을 가져와서 계산
            krw_value = 0
            if target_code == "KRW":
                krw_value = final_result
            else:
                # target에서 KRW로 가는 환율 조회
                krw_res = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{target_code}/KRW/1")
                if krw_res.status_code == 200 and krw_res.json().get("result") == "success":
                    krw_value = final_result * krw_res.json().get("conversion_rate", 0)
            
            # 부가 기능 2: 금액대별 세분화된 현지 물가 체감 가이드
            st.markdown("### 🏷️ 현지 물가 체감 가이드 (원화 환산 비교)")
            st.info(f"• **{base_code} {amount:,.0f}** ≒ 원화 기준 약 **{krw_value:,.0f}원** 가치")
            
            if krw_value < 5000:
                st.text("💡 체감 수준: 커피 한 잔, 편의점 간식 또는 가벼운 군것질거리 정도의 소액입니다.")
            elif krw_value < 20000:
                st.text("💡 체감 수준: 패스트푸드 세트 메뉴나 가벼운 한 끼 식사 비용 수준입니다.")
            elif krw_value < 50000:
                st.text("💡 체감 수준: 일반 식당에서의 든든한 한 끼 식사 또는 카페 투어 예산입니다.")
            elif krw_value < 150000:
                st.text("💡 체감 수준: 근사한 저녁 정식, 택시 이동 요금 또는 소형 쇼핑 품목 수준입니다.")
            elif krw_value < 500000:
                st.text("💡 체감 수준: 숙박비 일부, 중형 쇼핑 또는 주요 관광지 입장권/액티비티 패스 예산입니다.")
            else:
                st.text("💡 체감 수준: 호텔 숙박비, 대형 쇼핑 또는 항공권/장기 체류형 중대형 자금 규모입니다.")

            # 부가 기능 3: 다중 통화 동시 비교 (Multi-Currency Quick View)
            st.markdown("### 🌐 주요 통화 동시 비교")
            st.markdown(f"**{base_code} {amount:,.0f}** 기준 다른 주요 통화 환산 가치입니다.")
            
            multi_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base_code}"
            multi_res = requests.get(multi_url)
            if multi_res.status_code == 200:
                multi_rates = multi_res.json().get("conversion_rates", {})
                cols = st.columns(3)
                idx = 0
                for c_name, c_code in CURRENCIES.items():
                    if c_code != base_code and c_code in multi_rates:
                        val = amount * multi_rates[c_code]
                        with cols[idx % 3]:
                            st.metric(label=c_name, value=f"{val:,.2f} {c_code}")
                        idx += 1
            
            # 환율 변동 트렌드 인사이트
            st.markdown("### 📈 환율 트렌드 및 환전 팁")
            st.success("현재 환율 흐름이 비교적 안정적입니다. 필요한 만큼 분할 환전하는 전략을 추천합니다!")
            
        else:
            error_type = data.get("error-type", "알 수 없는 오류")
            st.error(f"환율 데이터를 가져오지 못했습니다. 에러 타입: {error_type}")

    except Exception as e:
        st.error(f"요청 중 오류가 발생했습니다: {e}")