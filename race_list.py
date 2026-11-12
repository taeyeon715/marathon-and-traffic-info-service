# 담당: 예린 - 대회 목록
import re
from datetime import date, timedelta

import pandas as pd
import streamlit as st

WEEKDAYS = ['월', '화', '수', '목', '금', '토', '일']

# 코스 유형: 교통통제가 있으면 '도심 도로', 아니면 장소·대회명의 단어로 판단
TRAIL_WORDS = ['트레일', 'TRAL', '청계산', '수서역', '일자산']
RIVER_WORDS = ['한강', '뚝섬', '신정교', '영롱이', '안양천', '중랑천', '우이천', '물빛무대']
PARK_WORDS = ['공원', '평화광장', '평화의 광장', '평화의광장', '유수지', '축구장', '가든파이브']
COURSE_TYPES = ['도심 도로', '공원', '한강·하천', '산(트레일런)', '기타']

# waypoints.csv의 '구분' 값 → 대회명 뒤에 붙일 짧은 표시
STATUS_LABELS = {'대회취소': '취소', '코스정보없음': '코스 정보 없음'}


@st.cache_data
def load_race_status():
    """waypoints.csv에서 대회취소·코스정보없음 대회를 골라 {대회번호: 표시}로 돌려준다."""
    waypoints = pd.read_csv('data/waypoints.csv', dtype={'대회번호': str})
    marked = waypoints[waypoints['구분'].isin(list(STATUS_LABELS))]
    return dict(zip(marked['대회번호'], marked['구분'].map(STATUS_LABELS)))


def name_with_status(race):
    """취소·코스 정보 없는 대회는 대회명 뒤에 '(취소)' 같은 표시를 붙인다."""
    label = race['표시']
    return f"{race['대회명']} ({label})" if label else race['대회명']


def course_type_of(race):
    """출발 장소와 교통통제 여부로 코스 유형을 추정한다."""
    if race['교통통제'] == 1:  # 도로를 막는 대회는 공원 출발이어도 실제로는 도로를 달림
        return '도심 도로'
    text = f"{race['대회장소']} {race['대회명']} {race['대회종목']}"
    if any(w in text for w in TRAIL_WORDS):
        return '산(트레일런)'
    if any(w in str(race['대회장소']) for w in RIVER_WORDS):
        return '한강·하천'
    if any(w in str(race['대회장소']) for w in PARK_WORDS):
        return '공원'
    return '기타'


def signup_status(period, today):
    """'2026년9월1일~2026년10월25일' 같은 접수기간을 오늘과 비교해 접수 상태를 돌려준다."""
    if not isinstance(period, str):  # 접수기간이 비어 있는 대회
        return '정보없음'
    days = re.findall(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', period)
    if len(days) < 2:
        return '정보없음'
    start, end = [date(int(y), int(m), int(d)) for y, m, d in days[:2]]
    if today < start:
        return '접수예정'
    if today <= end:
        return '접수중'
    return '접수마감'


def show_summary(found):
    """기간 요약 숫자 2칸: 대회 수, 교통통제 대회 수."""
    col1, col2 = st.columns(2)
    col1.metric('대회 수', f'{len(found)}개')
    col2.metric('교통통제 대회', f'{(found["교통통제"] == 1).sum()}개')


def text_or_dash(value):
    """비어 있는 값(NaN)이면 '-'를, 아니면 글자 그대로 돌려준다."""
    return value if isinstance(value, str) and value.strip() else '-'


def show_race_detail(race):
    """표에서 누른 대회의 세부 정보를 표 아래 상자에 보여준다."""
    with st.container(border=True):
        st.markdown(f"#### {name_with_status(race)}")

        d = date.fromisoformat(race['날짜'])
        when = f"{race['날짜']} ({WEEKDAYS[d.weekday()]})"
        start_time = text_or_dash(race['대회일시']).split('출발시간:')[-1].strip()  # '... 출발시간:08:00' → '08:00'
        if start_time != '-':
            when += f' · 출발 {start_time}'

        homepage = text_or_dash(race['홈페이지']).replace(' ', '')  # 'http:// abc.com' → 'http://abc.com'

        st.markdown(f"""
- **날짜** : {when}
- **장소** : {text_or_dash(race['대회장소'])}
- **코스 유형** : {race['코스유형']} (출발지·교통통제로 추정)
- **종목** : {text_or_dash(race['대회종목'])}
- **접수** : {text_or_dash(race['접수기간'])} ({race['접수']})
- **교통통제** : {'있음' if race['교통통제'] == 1 else '없음'}
- **주최** : {text_or_dash(race['주최단체'])}
- **홈페이지** : {homepage if homepage == '-' else f'[바로가기]({homepage})'}
""")

        intro = text_or_dash(race['기타소개'])
        if intro != '-':
            with st.expander('대회 소개 보기'):
                st.write(intro)


def show_race_list(races, month=None):
    """고른 기간의 대회를 표로 보여주고, 클릭한 대회 한 줄을 돌려준다.
    (month는 예전 app.py와 호환용으로만 받고 쓰지 않음)
    """
    today = date.today()

    st.subheader('대회 목록')

    # 1. 검색 조건 (표 바로 위에 두 줄로)
    first = date.fromisoformat(races['날짜'].min())  # 데이터의 첫 대회 날짜
    last = date.fromisoformat(races['날짜'].max())   # 데이터의 마지막 대회 날짜

    col1, col2, col3 = st.columns([1, 1, 2])  # 첫째 줄: 시작일 / 종료일 / 대회명 검색
    start = col1.date_input('시작일', value=first, format='YYYY-MM-DD')
    end = col2.date_input('종료일', value=last, format='YYYY-MM-DD')
    keyword = col3.text_input('대회명 검색', placeholder='예: 평화')

    col1, col2, col3 = st.columns([1, 1, 2])  # 둘째 줄: 종목 / 코스 유형 / 체크박스 2개
    event = col1.selectbox('종목', ['전체', '풀', '하프', '10km', '5km'])
    course = col2.selectbox('코스 유형', ['전체'] + COURSE_TYPES)
    no_traffic_only = col3.checkbox('교통통제 없는 대회만')
    signup_only = col3.checkbox('접수중인 대회만')

    if end < start:  # 종료일을 시작일보다 앞으로 고른 경우
        st.warning('종료일이 시작일보다 빨라요. 날짜를 다시 골라 주세요')
        return None

    if end - start > timedelta(days=365):  # 기간은 최대 1년
        end = start + timedelta(days=365)
        st.warning(f'기간은 최대 1년이라 {end}까지만 보여줘요')

    # 2. 조건에 맞는 대회만 남기기
    # 날짜가 'YYYY-MM-DD' 글자라서 글자끼리 크기 비교하면 날짜 비교와 같음
    found = races[(races['날짜'] >= str(start)) & (races['날짜'] <= str(end))].copy()
    found['접수'] = found['접수기간'].apply(lambda p: signup_status(p, today))
    found['코스유형'] = found.apply(course_type_of, axis=1)
    found['표시'] = found['번호'].map(load_race_status()).fillna('')  # 취소·코스 정보 없음만 글자가 들어감

    if keyword:  # 검색어가 대회명에 들어 있는 대회만 (대소문자·띄어쓰기 무시)
        name = found['대회명'].str.replace(' ', '').str.lower()
        found = found[name.str.contains(keyword.replace(' ', '').lower(), regex=False)]

    if event != '전체':  # '하프,10km,5km'를 쉼표로 나눠서 고른 종목이 있는지
        found = found[found['대회종목'].str.split(',').apply(lambda e: event in e)]

    if course != '전체':
        found = found[found['코스유형'] == course]

    if no_traffic_only:
        found = found[found['교통통제'] == 0]

    if signup_only:
        found = found[found['접수'] == '접수중']

    found = found.sort_values('날짜').reset_index(drop=True)

    # 3. 기간 요약 숫자
    show_summary(found)

    # 4. 화면에 보여줄 표: 날짜, 대회명, 종목만 (나머지는 누르면 세부 정보로)
    table = found[['날짜', '대회명', '대회종목']].rename(columns={'대회종목': '종목'})
    table['대회명'] = found.apply(name_with_status, axis=1)  # 취소·코스 정보 없는 대회는 이름 뒤에 표시

    st.caption(f'{start} ~ {end} · 대회를 누르면 아래에 세부 정보가 나와요 · 표 머리를 누르면 정렬돼요')

    if table.empty:
        st.info('조건에 맞는 대회가 없어요')
        return None

    # 5. 표 띄우기

    clicked = st.dataframe(table, hide_index=True, width='stretch',
                           on_select='rerun', selection_mode='single-row',
                           key=f'race_table_{start}_{end}_{keyword}_{event}_{course}_{no_traffic_only}_{signup_only}')

    rows = clicked.selection.rows  # 클릭한 행 번호 목록
    if not rows:
        return None

    race = found.iloc[rows[0]]
    show_race_detail(race)  # 표 바로 아래에 세부 정보
    return race