# raw_trade_data.csv 파일 활용
# HS코드가 85로 시작하는(반도체류) + 국가명 미국 또는 베트남 + 수출 금액 0 보다 큰 수(실제 수출 실적이 있는) 행만
# 다중 조건으로 필터링한 뒤, 수출 금액 상위 10건을 화면에 보여 주고 report.csv 로 저장
# streamlit 사용 : streamlit run 9-8-1.py

# 깃허브용 수정해봄!

import os
import pandas as pd
import streamlit as st

# 웹 페이지 제목 설정
st.title("📊 HS 85(반도체류) 대미•대베트남 수출 상위 10건 분석")

# 1. 파일 경로 설정 (현재 파일 기준 상위 폴더의 common 폴더 참조)
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "..", "common", "raw_trade_data.csv")
output_path = os.path.join(current_dir, "report.csv")

try:
    # 1. 데이터 불러오기
    # (인코딩 문제 발생 시 encoding='cp949' 또는 'euc-kr'로 변경 가능)
    df = pd.read_csv(file_path, dtype={"HS코드": str})

    st.subheader("1. 원본 데이터 미리보기")
    st.write(f"총 {len(df):,}개의 데이터가 있습니다.")
    st.dataframe(df.head())

    # 2. 다중 조건 필터링
    # 조건 1: HS코드가 '85'로 시작 (반도체류)
    cond1 = df["hs_code"].astype(str).str.startswith("85")

    # 조건 2: 국가명이 '미국' 또는 '베트남'
    cond2 = df["국가명"].isin(["미국", "베트남"])

    # 조건 3: 수출 금액이 0보다 큰 수 (실제 수출 실적 존재)
    cond3 = df["수출금액"] > 0

    filtered_df = df[cond1 & cond2 & cond3]

    # 3. 수출 금액 기준 상위 10건 추출
    top10_df = filtered_df.sort_values(by="수출금액", ascending=False).head(10)

    # 4. 화면 출력
    st.subheader("2. 조건 필터링 후 수출금액 상위 10건")
    st.dataframe(top10_df)

    # 5. report.csv로 저장 (한글 깨짐 방지를 위해 utf-8-sig 사용)
    top10_df.to_csv("report.csv", index=False, encoding="utf-8-sig")
    st.success("✅ 'report.csv' 파일로 저장이 완료되었습니다!")

    # (선택) Streamlit 화면에서 바로 다운로드할 수 있는 버튼 추가
    csv_data = top10_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 필터링된 결과 다운로드 (report.csv)",
        data=csv_data,
        file_name="report.csv",
        mime="text/csv",
    )

except FileNotFoundError:
    st.error(f"'{file_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인해 주세요.")
except KeyError as e:
    st.error(f"컬럼명을 확인해 주세요. 찾을 수 없는 컬럼: {e}")