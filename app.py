# 실행: streamlit run app.py
import pandas as pd
import streamlit as st

from race_list import show_race_list   # 예린
from course_map import show_course_map # 건우
from traffic import show_traffic       # 하진
from faq import show_faq               # 서영

st.set_page_config(page_title='마라톤 코스 모아보기 & 교통 정보', layout='wide')

# 데이터 불러오기 (번호는 글자로 읽어야 앞자리가 안 깨짐)
races = pd.read_csv('data/marathons_raw.csv', dtype={'번호': str})
waypoints = pd.read_csv('data/waypoints.csv', dtype={'대회번호': str})

# 1. 제목 (가운데)
st.markdown("<h1 style='text-align:center'>마라톤 코스 모아보기 & 교통 정보</h1>", unsafe_allow_html=True)

# 2. 월 선택
month = st.radio('월 선택', ['2026-11', '2026-12'],
                 format_func=lambda m: m[:4] + '년 ' + str(int(m[5:])) + '월',
                 horizontal=True)

# 3. 본문: 왼쪽(목록 + 지도) / 오른쪽(교통통제)
left, right = st.columns([2, 1])

with left:
    race = show_race_list(races, month)  # 클릭한 대회 한 줄 (없으면 None)
    show_course_map(race, waypoints)

with right:
    show_traffic(race)

# 4. 하단 질문 버튼
st.divider()
show_faq()
