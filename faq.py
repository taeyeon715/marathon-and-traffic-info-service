# 담당: 서영 - 자주 묻는 질문
import streamlit as st



# TODO(서영): 질문과 답변 채우기
FAQ = {
    '마라톤 대회 일정은 어디서 확인하나요?': '대회 목록에서 날짜, 대회명, 종목, 코스 유형 등의 정보를 확인할 수 있습니다.',
    '마라톤 코스는 어떻게 확인하나요?': '원하는 대회를 선택하면 해당 대회의 코스 지도와 경로 정보를 확인할 수 있습니다.',
    '대회 당일 교통통제 구간은 어디서 확인하나요?': '원하는 대회를 클릭하면 교통통제 정보를 확인할 수 있습니다.',
    '대회 정보는 실시간으로 업데이트되나요?': '수집 및 정리된 데이터를 바탕으로 정보를 제공합니다.',
}


def show_faq():
    """질문 버튼을 나란히 두고, 누른 버튼의 답변을 보여준다."""
    #제목 영역
    st.divider()

    st.header('자주 묻는 질문')

    st.caption('마라톤 대회와 교통 정보에 대한 궁금증을 해결해 드립니다.')

    #질문 검색창

    search = st.text_input('질문 검색', placeholder='궁금한 내용을 입력하세요.')

    questions = [q for q in FAQ.keys() if search.strip().lower() in q.lower()]

    st.write('')

    #질문 카드 배치

    if questions:
        cols = st.columns(2)

        for i, question in enumerate(questions):
            with cols[i%2]:
                with st.container(border=True):
                    st.caption('? 자주 묻는 질문')

                    if st.button(question, key = f'faq_{list(FAQ.keys()).index(question)}', use_container_width=True):
                        st.session_state['selected_faq'] = question

    else:
        st.warning('검색 결과가 없습니다. 다른 검색어를 입력해 주세요.')

    #선택한 질문에 답변
    selected = st.session_state.get('selected_faq')

    if selected and selected in FAQ:
        st.write('')
        with st.container(border = True):
            st.subheader('답변')
            st.markdown(f'**Q.{selected}**')
            st.info(FAQ[selected])
            if st.button('답변 닫기', key = 'faq_close'):
                del st.session_state['selected_faq']
                st.rerun()
    else:
        st.info('질문을 선택하면 해당 질문의 답변이 표시됩니다.')


    #제목글꼴

    

    # questions = list(FAQ.keys())
    # cols = st.columns(4)

    # for i, question in enumerate(questions):
    #     with cols[i]:
    #         if st.button(question, key=f'faq_{i}', use_container_width=True):
    #             st.session_state['selected_faq'] = question

    # st.write('')

    # selected = st.session_state.get('selected_faq')

    # if selected:
    #     st.info( f"**Q.{selected}**\n\n" f"A.{FAQ[selected]}")

    # else:
    #     st.info('질문 버튼을 누르면 답변이 나와요.')
    # cols = st.columns(len(FAQ))
    # for col, question in zip(cols, FAQ):
    #     if col.button(question, width='stretch'):
    #         st.session_state['answer'] = FAQ[question]  # 누른 답변 기억

    # st.info(st.session_state.get('answer', '버튼을 누르면 답변이 나와요'))
