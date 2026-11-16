# 담당: 서영 - 자주 묻는 질문
import pandas as pd
import streamlit as st
import re

#종목에서 거리 추출하기
def get_distances(event):
    event = str(event)

    distances = []

    if '풀' in event:
        distances.append(42.195)

    if '하프' in event:
        distances.append(21.1)

    numbers = re.findall(r'(\d+(?:\.\d+)?)\s*km', event.lower())

    for number in numbers:
        distance = float(number)

        if distance not in distances:
            distances.append(distance)

    return sorted(distances)

def get_difficulty(distance):

    if distance <= 5:
        return '초급'

    elif distance <= 10:
        return '초중급'

    elif distance <=21.1:
        return '중급'

    else:
        return '상급'

def prepare_data(races):

    df = races.copy()

    df['날짜'] = pd.to_datatime(df['날짜'], erroers = 'coerce')
    return df

def show_difficulty(df):

    st.subheader('마라톤 코스 난이도 분석')

    results = []

    for _, row in df.iterrows():
        distances = get_distances(row['대회종목'])

        for distance in distances:
            results.append({'대회명' :row ['대회명'], '코스 거리':f'{distance}km', '난이도':get_difficulty(distance)})
        result_df = pd.DataFrame(results)

        if result_df.empty:
            st.warning('분석할 수 있는 거리 데이터가 없습니다.')
            return

        level = st.selectbox('원하는 난이도를 선택하세요.', ['전체', '초급', '초중급', '중급', '상급'])

        if level != '전체':
            result_df=result_df[result_df['난이도'] == level]

        st.dataframe(result_df, use_container_width=True,hide_index=True)

        st.caption('거리 기준으로 분류한 참고용 난이도입니다.'
                   '실제 코스의 고도와 경사도는 반영되지 않았습니다.')

def show_season(df):

            st.subheader('계절별 마라톤 코스 분석')

            season = {'봄' : [3,4,5],
                      '여름' : [6,7,8],
                      '가을': [9,10,11],
                      '겨울':[12,1,2]}

            counts = {}

            for season, months in season.item():
                counts[season] = df[df['날짜'].dt.month.isin(months)].shape[0]


            st.write('계절별 데이터에 포함된 대회 수')

            st.dataframe(pd.DataFrame({'계절' : list(counts.key()), '대회 수' : list(counts.values())}), use_container_width=True, hide_index=True)

            season = st.selectbox('분석할 계절을 선택하세요.', list(season.keys()), key='select')

            selected = df[df['날짜'].dt.month.isin(season[season])]

            if selected.empty:

                st.warning(f'현재 데이터에는 {season}에 개최되는 ''대회 정보가 없습니다.')

            else:
                st.success(f'{season}에 개최되는 대회는''f{len(selected)}개입니다.')

                st.dataframe(selected[['대회명', '날짜', '대회지역','대회장소']], use_container_width=True, hide_index=True)

                st.caption('현재 데이터에 기록된 개최 날짜와 장소를 보여줍니다.''계절별 기후나 코스 적합성을 판단하는 데이터는 별도로 필요합니다.')

def show_region(df):
    st.subheader('지역별 마라톤 개최 현황')

    region = df['대회 지역'].dropna().astype(str).str.strip()

    counts = region.value_counts()

    if counts.empty:
        st.warning('지역 데이터가 없습니다')
        return

    result = counts.reset_index()
    result.columns = ['지역', '대회 수']

    st.dataframe(result, use_container_width=True, hide_index=True)

    if len(counts)==1:
        st.warning(f'현재 데이터에는 {counts.index[0]}지역의 ''대회만 기록되어 있습니다.''다른 지역에 대회가 없다고 단정할 수는 없습니다.')

    else:
        least = counts.min()

        st.info('현재 수집된 데이터에서 대회 개최 횟수가'f'가장 적은 지역은{",".join(counts[counts == least].index)}입니다.')

        st.caption('전국 전체 지역 목록이 없으므로''미개최 지역을 확정하려면 추가 지역 데이터가 필요합니다.')



        


def show_faq(races):
    df = prepare_data(races)
    st.header('마라톤 데이터 분석 질문')
    st.caption('궁금한 질문을 선택하면 수집된 마라톤 데이터를 분석해 드립니다')

    questions = ['마라톤 코스별로 난이도를 매겨줘', '계절에 따라 달리기 좋은 마라톤 코스를 추천해줘''마라톤 대회가 아직 열리지 않은 지역이 어디야?']

    cols = st.columns(2)

    for i, question in enumerate(questions):

        with cols[i % 2]:
            if st.button(question, key=f'faq_{i}', use_container_width=True):
                st.session_state['selected_faq'] = i

    st.divider

    selected = st.session_state.get('selected_faq')

    if selected is not None:
        st.subheader('분석 결과')

        if selected == 0:
            show_difficulty(df)

        elif selected == 1:
            show_season(df)

        elif selected == 2:
            show_region(df)

      






# TODO(서영): 질문과 답변 채우기
# FAQ = {
#     '마라톤 대회 일정은 어디서 확인하나요?': '대회 목록에서 날짜, 대회명, 종목, 코스 유형 등의 정보를 확인할 수 있습니다.',
#     '마라톤 코스는 어떻게 확인하나요?': '원하는 대회를 선택하면 해당 대회의 코스 지도와 경로 정보를 확인할 수 있습니다.',
#     '대회 당일 교통통제 구간은 어디서 확인하나요?': '원하는 대회를 클릭하면 교통통제 정보를 확인할 수 있습니다.',
#     '대회 정보는 실시간으로 업데이트되나요?': '수집 및 정리된 데이터를 바탕으로 정보를 제공합니다.',
# }


# def show_faq():
#     """질문 버튼을 나란히 두고, 누른 버튼의 답변을 보여준다."""
#     #제목 영역
#     st.divider()

#     st.header('자주 묻는 질문')

#     st.caption('마라톤 대회와 교통 정보에 대한 궁금증을 해결해 드립니다.')

#     #질문 검색창

#     search = st.text_input('질문 검색', placeholder='궁금한 내용을 입력하세요.')

#     questions = [q for q in FAQ.keys() if search.strip().lower() in q.lower()]

#     st.write('')

#     #질문 카드 배치

#     if questions:
#         cols = st.columns(2)

#         for i, question in enumerate(questions):
#             with cols[i%2]:
#                 with st.container(border=True):
#                     st.caption('? 자주 묻는 질문')

#                     if st.button(question, key = f'faq_{list(FAQ.keys()).index(question)}', use_container_width=True):
#                         st.session_state['selected_faq'] = question

#     else:
#         st.warning('검색 결과가 없습니다. 다른 검색어를 입력해 주세요.')

#     #선택한 질문에 답변
#     selected = st.session_state.get('selected_faq')

#     if selected and selected in FAQ:
#         st.write('')
#         with st.container(border = True):
#             st.subheader('답변')
#             st.markdown(f'**Q.{selected}**')
#             st.info(FAQ[selected])
#             if st.button('답변 닫기', key = 'faq_close'):
#                 del st.session_state['selected_faq']
#                 st.rerun()
#     else:
#         st.info('질문을 선택하면 해당 질문의 답변이 표시됩니다.')


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
