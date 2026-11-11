# 담당: 예린 - 대회 목록
import streamlit as st


def show_race_list(races, month):
    """선택한 달의 대회를 표로 보여주고, 클릭한 대회 한 줄을 돌려준다."""
    st.subheader('대회 목록')

    # 날짜가 '2026-11'로 시작하는 대회만
    month_races = races[races['날짜'].str.startswith(month)].reset_index(drop=True)
    table = month_races[['날짜', '대회명', '대회종목', '대회장소', '교통통제']]

    # TODO(예린): 정렬·검색, 종목/교통통제 필터, 취소·코스 없는 대회 표시

    clicked = st.dataframe(table, hide_index=True, width='stretch',
                           on_select='rerun', selection_mode='single-row')

    rows = clicked.selection.rows  # 클릭한 행 번호 목록
    if not rows:
        return None
    return month_races.iloc[rows[0]]
