import os
from pathlib import Path
import requests
import streamlit as st
import base64  # 폰트 변환을 위해 추가된 모듈

# 페이지 설정 (반응형 모바일 최적화 레이아웃)
st.set_page_config(
    page_title="스마트 무역/환율 대시보드",
    page_icon="💱",
    layout="wide"
)

# ----------------------------------------
# 폰트 파일을 Base64로 변환하여 CSS에 적용하는 로직
# ----------------------------------------
font_path = "Griun_Fromsol-Rg.ttf"
font_css = ""

# 폰트 파일이 같은 폴더에 있는지 확인 후 변환
if os.path.exists(font_path):
    with open(font_path, "rb") as f:
        font_data = f.read()
    font_base64 = base64.b64encode(font_data).decode("utf-8")
    
    # f-string을 사용하므로 CSS의 중괄호는 {{ }}로 두 번 감싸야 합니다.
    font_css = f"""
    <style>
        @font-face {{
            font-family: 'Griun_Fromsol';
            src: url('data:font/ttf;charset=utf-8;base64,{font_base64}') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        
        html, body, [class*="css"] {{
            font-family: 'Griun_Fromsol', sans-serif !important;
            color: #2D3748;
        }}
        
        .stApp {{
            background-color: #F4FBF7;
        }}
        
        /* 버튼 스타일 (연두색 계열) */
        .stButton>button {{
            background-color: #81C784;
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .stButton>button:hover {{
            background-color: #66BB6A;
            color: white;
        }}
    </style>
    """
else:
    st.warning("경고: 'Griun_Fromsol-Rg.ttf' 폰트 파일을 찾을 수 없습니다. 기본 폰트로 렌더링됩니다.")

# 변환된 CSS 적용
if font_css:
    st.markdown(font_css, unsafe_allow_html=True)
# ----------------------------------------

# Streamlit Secrets에서 API 키 로드
try:
    EXCHANGE_API_KEY = st.secrets["EXCHANGE_API_KEY"]
except KeyError:
    st.error("Streamlit Cloud 설정(Secrets)에 EXCHANGE_API_KEY가 입력되지 않았습니다.")
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

st.title("🌿 최유진의 스마트 무역/환율 대시보드")
st.markdown("무역 데이터 시각화와 실시간 환율 분석을 위해 구축한 나만의 맞춤형 환율 대시보드입니다.")

# 사이드바: 주요 통화 실시간 모니터링 대시보드 (기준: 원화 KRW)
st.sidebar.header("📌 주요 통화 모니터링 (vs 원화)")
try:
    sidebar_res = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/KRW")
    if sidebar_res.status_code == 200:
        sidebar_rates = sidebar_res.json()["conversion_rates"]
        for name, code in CURRENCIES.items():
            if code != "KRW" and code in sidebar_rates:
                rate_value = sidebar_rates[code]
                krw_per_unit = 1 / rate_value if rate_value > 0 else 0
                if code == "JPY":
                    st.sidebar.text(f"100엔(JPY) ≒ {krw_per_unit * 100:,.1f} KRW")
                else:
                    st.sidebar.text(f"1 {code} ≒ {krw_per_unit:,.2f} KRW")
    else:
        st.sidebar.text("모니터링 데이터 로드 실패")
except Exception:
    st.sidebar.text("네트워크 오류 발생")

st.markdown("---")

# 메인 계산기 UI
col_from, col_to = st.columns(2)
with col_from:
    selected_base = st.selectbox("기준 통화 (From)", list(CURRENCIES.keys()), index=1)
with col_to:
    selected_target = st.selectbox("변환할 통화 (To)", list(CURRENCIES.keys()), index=0)

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
            
            final_result = converted_result
            if apply_fee:
                base_spread = 0.0197
                actual_spread = base_spread * (1 - (fee_discount / 100))
                final_result = converted_result * (1 + actual_spread)
            
            st.success("환율 계산이 완료되었습니다!")
            
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
            
            krw_value = 0
            if target_code == "KRW":
                krw_value = final_result
            else:
                krw_res = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{target_code}/KRW/1")
                if krw_res.status_code == 200 and krw_res.json().get("result") == "success":
                    krw_value = final_result * krw_res.json().get("conversion_rate", 0)
            
            # 부가 기능 2: 금액대별 세분화된 현지 물가 체감 가이드
            st.markdown("### 🏷️ 현지 물가 체감 가이드")
            
            if base_code != "KRW":
                st.info(f"• 입력하신 **{base_code} {amount:,.0f}**은(는) 원화로 약 **{krw_value:,.0f}원** 수준입니다.")
            
            if krw_value < 2000:
                st.text("💡 체감 수준: 가벼운 편의점 간식, 껌, 생수 한 병 수준의 소액입니다.")
            elif krw_value < 5000:
                st.text("💡 체감 수준: 테이크아웃 커피 한 잔, 대중교통 기본 요금 정도의 금액입니다.")
            elif krw_value < 10000:
                st.text("💡 체감 수준: 프랜차이즈 햄버거 세트, 저렴한 식당에서의 한 끼 비용입니다.")
            elif krw_value < 20000:
                st.text("💡 체감 수준: 캐주얼한 식당에서의 든든한 한 끼, 영화 티켓 한 장 수준입니다.")
            elif krw_value < 50000:
                st.text("💡 체감 수준: 레스토랑 1인 식사, 2~3인용 치킨/피자, 가벼운 의류 쇼핑 예산입니다.")
            elif krw_value < 100000:
                st.text("💡 체감 수준: 근사한 저녁 정식 세트, 패밀리 레스토랑 외식, 소형 쇼핑 품목 수준입니다.")
            elif krw_value < 250000:
                st.text("💡 체감 수준: 비즈니스 호텔 1박 숙박비, 국내선 항공권, 브랜드 의류 쇼핑 예산입니다.")
            elif krw_value < 500000:
                st.text("💡 체감 수준: 고급 호텔(호캉스) 1박, 프리미엄 전자기기, 단거리 해외 항공권 규모입니다.")
            elif krw_value < 1000000:
                st.text("💡 체감 수준: 명품 소품, 동남아시아 단기 여행 경비 수준의 중대형 자금입니다.")
            else:
                st.text("💡 체감 수준: 장거리 해외 항공권, 하이엔드 전자기기, 장기 체류형 대형 자금 규모입니다.")

            # 부가 기능 3: 다중 통화 동시 비교
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
            
            # 부가 기능 4: 실시간 환율 데이터 기반 동적 트렌드 인사이트
            st.markdown("### 📈 실시간 데이터 기반 환율 인사이트")
            
            spot_res = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/USD/KRW")
            if spot_res.status_code == 200:
                usdkrw_rate = spot_res.json().get("conversion_rate", 1300)
                
                if base_code == "USD" or target_code == "USD":
                    if usdkrw_rate >= 1400:
                        st.warning(f"현재 원/달러 환율이 {usdkrw_rate:,.2f}원으로 높은 수준(고환율기)입니다. 큰 금액 한 번에 환전하기보다는 소액씩 나누어 환전(분할 환전)하는 것을 강력히 추천합니다!")
                    elif usdkrw_rate <= 1250:
                        st.success(f"현재 원/달러 환율이 {usdkrw_rate:,.2f}원으로 비교적 안정적이거나 원화 강세 구간입니다. 여행이나 달러 매수에 유리한 타이밍입니다!")
                    else:
                        st.info(f"현재 원/달러 환율은 {usdkrw_rate:,.2f}원 선으로 완만하게 움직이고 있습니다. 주 단위 추이를 보며 필요 분량만큼 환전하세요.")
                else:
                    st.info(f"선택하신 통화 쌍의 현재 적용 환율({conversion_rate:,.4f})을 바탕으로 할 때, 외환 시장의 단기 변동성이 크지 않은 상태입니다. 우대 쿠폰을 활용해 알뜰하게 환전해 보세요.")
            else:
                st.info("현재 환율 흐름이 안정적입니다. 수수료 우대를 챙겨서 필요한 만큼만 환전하세요.")
            
        else:
            error_type = data.get("error-type", "알 수 없는 오류")
            st.error(f"환율 데이터를 가져오지 못했습니다. 에러 타입: {error_type}")

    except Exception as e:
        st.error(f"요청 중 오류가 발생했습니다: {e}")