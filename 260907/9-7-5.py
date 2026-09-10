# 인코딩 자동 감지 + 한글 폰트 막대그래프
# 여러 인코딩('uft-8-sig', 'cp949', 'euc-kr') 순서대로 시도
# 내가 쓸 폰트가 같은 경로에 있어야 함
# 객실 등급별 생존율 막대그래프 생성 후 그림으로 저장   chart.png
# 실행 : streamlit run 9-7-5.py

import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib import font_manager

st.title('📊 인코딩 자동 감지 + 한글 폰트 막대그래프 (Titanic 연습)')
st.caption('여러 인코딩을 순서대로 시도해서 파일을 읽고, 객실 등급별 생존율을 그래프로 그립니다.')

CSV_PATH = os.path.join(os.path.dirname(__file__), 'titanic.csv')
CSV_FONT = os.path.join(os.path.dirname(__file__), 'NanumSquareNeo-Variable.ttf')

def read_csv_with_encodings(file_path):

    encodings = ['utf-8-sig', 'cp949', 'euc-kr']
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            st.write(f"{enc}으로 읽었습니다.")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    st.error("지원하는 모든 인코딩으로 파일을 읽는 데 실패했습니다.")
    return None


# 인코딩 자동 감지로 csv 읽기

st.subheader('1) 인코딩 자동 감지')

df = read_csv_with_encodings(CSV_PATH)

st.markdown('---')
# 객실 등급(Pclass) 별 생존율 집계
# Survived 사망 0 / 생존 1 등급별 평균을 내면 그 자체가 등급의 생존 비율이 된다.

st.subheader('2) 객실 등급별 생존율')

pclass_survival_rate = df.groupby('Pclass')['Survived'].mean().sort_index()
st.dataframe((pclass_survival_rate * 100).round(1).rename('생존율(%)'))

st.markdown('---')

# df_df = st.dataframe((pclass_survival_rate * 100).round(1).rename('생존율(%)'))
# st.write(df_df)

# 차트 그리기

st.subheader('3) 객실 등급별 생존율 막대그래프')

try : 
    # 폰트 파일이 없으면 FileNotFoundError 발생
    font_prop = font_manager.FontProperties(fname=CSV_FONT)
    # matplotlib font_manager에 폰트를 등록하고, 전역 폰트로 설정
    font_manager.fontManager.addfont(CSV_FONT)
    plt.rcParams['font.family'] = font_prop.get_name()
    st.write('NanumSquareNeo-Variable 폰트를 적용했습니다.')
except FileNotFoundError :
    st.warning('폰트 파일을 찾을 수 없습니다.')

fig, ax = plt.subplots(figsize=(8,5))
(pclass_survival_rate * 100).plot(kind='bar', color='green', ax=ax)
ax.set_title('객실 등급별 생존율')
ax.set_xlabel('객실 등급(Pclass)')
ax.set_ylabel('생존율(%)')

st.pyplot(fig)

output_png = output_path = os.path.join(os.path.dirname(__file__),'chart_png')
fig.savefig(output_png)