# 담당: 하진 - 교통통제 정보
import pandas as pd
import streamlit as st

TOPIS_URL = 'https://topis.seoul.go.kr'

#'대회번호':[{'종목': '풀', '구간': '광화문~숭례문', '시간': '05:00~13:00', '출처': 'https://공지-주소'}, ],
TRAFFIC_INFO = { '41865': [  # 11/21 2026 아식스 서울신문 고프리런
        {'구간': '여의도공원 ~ 서강대교 ~ 광흥창역(반환)', '시간': '경찰 공지 전',
         '비고': '통제 시간은 공지가 나오면 추가',
         '출처': 'https://www.newspim.com/news/view/20261113001135'},
    ],
    '41768': [  # 11/22 자이스 스마일 레이스
        {'구간': '여의도공원 ~ 서강대교 ~ 광흥창역(반환)', '시간': '경찰 공지 전',
         '비고': '통제 시간은 공지가 나오면 추가',
         '출처': 'https://www.newspim.com/news/view/20261113001135'},
    ],
    '41766': [  # 11/28 2026 평화런
        {'구간': '여의도공원 ~ 서강대교(반환)', '시간': '경찰 공지 전',
         '비고': '통제 시간은 공지가 나오면 추가',
         '출처': 'https://www.segye.com/newsView/20261102511303'},
    ],
    '41759': [  # 11/29 제14회 안중근 평화 마라톤
        {'구간': '여의도공원 ~ 서강대교(반환)', '시간': '경찰 공지 전',
         '비고': '통제 시간은 공지가 나오면 추가',
         '출처': 'https://www.segye.com/newsView/20261102511303'},
    ],
    '41259': [  # 11/1 2026 jtbc 마라톤
        {'종목': '풀', '구간': '세종대로(출발·집결지)', '시간': '04:00~10:00',
         '출처': 'https://m.news.nate.com/view/20261101n00503'},
        {'종목': '풀', '구간': '종로·청계천로', '시간': '07:46~10:29',
         '출처': 'https://m.news.nate.com/view/20261101n00503'},
        {'종목': '풀', '구간': '신설동역·군자교·잠실대교·올림픽공원', '시간': '07:54~13:35',
         '출처': 'https://m.news.nate.com/view/20261101n00503'},
        {'종목': '10km', '구간': '상암월드컵공원·양화대교·여의도공원', '시간': '07:20~10:40',
         '출처': 'https://m.news.nate.com/view/20261101n00503'},
    ],
    '41848': [  # 11/8 제3회 자유민주 마라톤대회 (10km, 6.10km)
        {'구간': '서울광장~세종대로사거리', '시간': '06:30~10:00',
         '출처': 'https://www.econovill.com/news/articleView.html?idxno=756373'},
        {'구간': '세종대로(세종대로사거리~숭례문)', '시간': '07:00~08:35',
         '출처': 'https://www.econovill.com/news/articleView.html?idxno=756373'},
        {'구간': '종로(세종대로사거리~흥인지문교차로)', '시간': '07:10~08:10(순차 해제 ~08:30)',
         '출처': 'https://www.econovill.com/news/articleView.html?idxno=756373'},
        {'구간': '남대문로·소공로', '시간': '07:00~08:40',
         '출처': 'https://www.econovill.com/news/articleView.html?idxno=756373'},
        {'구간': '을지로(시청삼거리~광교)', '시간': '07:00~08:45',
         '출처': 'https://www.econovill.com/news/articleView.html?idxno=756373'},
        {'구간': '청계천로·무교로', '시간': '07:00~08:55',
         '출처': 'https://www.econovill.com/news/articleView.html?idxno=756373'},
    ],
    '41600': [  # 11/15 2026 MBN 서울마라톤
        {'구간': '광화문광장 ~ 잠실종합운동장 (종로·동대문·성동·광진·송파)', '시간': '04:00~12:00',
         '비고': '구간별로 선수 통과 후 순차 해제. 정확한 시간은 대회 공식 홈페이지 확인',
         '출처': 'https://www.topstarnews.net/news/articleView.html?idxno=16276181'},
    ]
}


@st.cache_data
def load_waypoints():
    return pd.read_csv('data/waypoints.csv', dtype={'대회번호': str})


def has_text(value):
    return isinstance(value, str) and value.strip() != ''


def show_control_info(race):
    items = TRAFFIC_INFO.get(race['번호'])
    if not items:
        st.caption('통제 구간·시간은 서울시 공지가 확인되는 대로 추가돼요')
        return

    for item in items:
        with st.container(border=True):
            if item.get('종목'):
                st.markdown(f"**{item['종목']}**")
            st.markdown(f"- **통제 구간** : {item.get('구간', '-')}")
            st.markdown(f"- **통제 시간** : {item.get('시간', '-')}")
            if item.get('비고'):
                st.markdown(f"- **참고** : {item['비고']}")
            if item.get('출처'):
                st.markdown(f"[서울시 공지 보기]({item['출처']})")


def show_course_summary(race):
    waypoints = load_waypoints()
    course = waypoints[(waypoints['대회번호'] == race['번호'])
                       & waypoints['구분'].isin(['출발', '반환', '도착'])
                       & waypoints['종목'].notna()]
    if course.empty:
        return

    with st.expander('코스 주요 지점 (참고용)'):
        for distance, points in course.sort_values('순서', kind='stable').groupby('종목', sort=False):
            steps = [f"{p['구분']} {p['경유지명']}" for _, p in points.iterrows() if has_text(p['경유지명'])]
            st.markdown(f"**{distance}** : " + ' → '.join(steps))
        st.caption('대회 코스 기준이라 실제 통제 구간과 다를 수 있어요. 정확한 구간은 서울시 공지를 확인해 주세요')


def show_traffic(race):
    """선택한 대회의 교통통제 정보를 보여준다."""
    st.subheader('교통통제 정보')

    if race is None:
        st.info('대회를 클릭하면 교통통제 정보가 나와요')
        return

    if race['표시'] == '취소':
        st.error('취소된 대회예요')
        return

    # TODO(하진): 통제 구간·시간 안내 (서울시 공지, TOPIS 참고)
    if race['교통통제'] == 1:
        st.warning('교통통제 있음')
        show_control_info(race)
        show_course_summary(race)

    else:
        st.success('교통통제 없음')
        st.caption('작은 규모의 통제는 있을 수 있으니 대회 홈페이지의 안내도 확인해 주세요')

    st.link_button('TOPIS에서 실시간 교통정보 보기', TOPIS_URL)
