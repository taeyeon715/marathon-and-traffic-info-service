# 담당: 건우 - 코스 지도
import streamlit as st


def show_course_map(race, waypoints):
    """선택한 대회의 코스를 지도로 보여준다."""
    st.subheader('코스 지도')

    if race is None:
        st.info('대회를 클릭하면 코스 지도가 나와요')
        return

    course = waypoints[waypoints['대회번호'] == race['번호']]

    # TODO(건우): folium으로 지도 만들기
    #   - 종목별로 경유지를 '순서'대로 이어 선 그리기
    #   - 출발·반환·도착에 마커 달기
    #   - streamlit_folium의 st_folium(지도)로 화면에 띄우기
    st.write(race['대회명'], '경유지', len(course), '개')
