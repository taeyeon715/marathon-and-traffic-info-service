# 담당: 서영 - 자주 묻는 질문
import streamlit as st

# TODO(서영): 질문과 답변 채우기
FAQ = {
    '질문 1': '답변 1',
    '질문 2': '답변 2',
    '질문 3': '답변 3',
    '질문 4': '답변 4',
}


def show_faq():
    """질문 버튼을 나란히 두고, 누른 버튼의 답변을 보여준다."""
    st.subheader('자주 묻는 질문')

    cols = st.columns(len(FAQ))
    for col, question in zip(cols, FAQ):
        if col.button(question, width='stretch'):
            st.session_state['answer'] = FAQ[question]  # 누른 답변 기억

    st.info(st.session_state.get('answer', '버튼을 누르면 답변이 나와요'))
