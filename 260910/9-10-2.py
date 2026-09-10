import os
from pathlib import Path
import requests
import streamlit as st
from dotenv import load_dotenv

# 현재 파일 기준 상위 디렉터리의 .env 파일 경로 설정
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 환경 변수에서 환율 API 키 불러오기
API_KEY = os.getenv("EXCHANGE_API_KEY")

st.title("💱 실시간 환율 계산기")

# API 키 유효성 체크
if not API_KEY:
    st.error(".env 파일에서 EXCHANGE_API_KEY를 찾을 수 없습니다. 상위 폴더의 .env 경로와 키 값을 확인하세요.")
    st.stop()

# 주요 통화 목록 (ExchangeRate-API 기준 코드)
currencies = {
    "대한민국 원 (KRW)": "KRW",
    "미국 달러 (USD)": "USD",
    "유럽 유로 (EUR)": "EUR",
    "일본 엔 (JPY)": "JPY",
    "영국 파운드 (GBP)": "GBP",
    "중국 위안 (CNY)": "CNY",
    "호주 달러 (AUD)": "AUD",
    "캐나다 달러 (CAD)": "CAD"
}

# 사용자 입력 UI
col1, col2 = st.columns(2)
with col1:
    selected_base = st.selectbox("기준 통화 (From)", list(currencies.keys()), index=1) # 기본값: USD
with col2:
    selected_target = st.selectbox("변환할 통화 (To)", list(currencies.keys()), index=0) # 기본값: KRW

base_code = currencies[selected_base]
target_code = currencies[selected_target]

amount = st.number_input("금액 입력", min_value=0.0, value=100.0, step=1.0)

if st.button("환율 계산하기"):
    # ExchangeRate-API 엔드포인트 (v6 기준)
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{base_code}/{target_code}/{amount}"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("result") == "success":
            conversion_rate = data["conversion_rate"]
            converted_result = data["conversion_result"]
            
            st.success("환율 정보를 성공적으로 가져왔습니다!")
            
            # 결과 출력
            st.metric(label=f"환율 적용 결과 ({base_code} ➔ {target_code})", value=f"{converted_result:,.2f} {target_code}")
            st.info(f"적용 환율: 1 {base_code} = {conversion_rate:,.4f} {target_code}")
            
        else:
            error_type = data.get("error-type", "알 수 없는 오류")
            st.error(f"환율 데이터를 가져오지 못했습니다. 에러 타입: {error_type}")

    except Exception as e:
        st.error(f"요청 중 오류가 발생했습니다: {e}")