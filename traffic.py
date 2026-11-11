# 담당: 하진 - 교통통제 정보
import streamlit as st


def show_traffic(race):
    """선택한 대회의 교통통제 정보를 보여준다."""
    st.subheader('교통통제 정보')

    if race is None:
        st.info('대회를 클릭하면 교통통제 정보가 나와요')
        return

    # TODO(하진): 통제 구간·시간 안내 (서울시 공지, TOPIS 참고)
    if race['교통통제'] == 1:
        st.warning('교통통제 있음')
    else:
        st.success('교통통제 없음')
