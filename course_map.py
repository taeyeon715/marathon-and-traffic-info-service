"""담당: 건우. 대회·종목별 원본 좌표를 Folium 지도에 표시한다."""
from html import escape
from math import isfinite

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

def prepare_course(course):
    """원본을 복사해 숫자 오류를 검사하고 경유지 순서대로 정렬한다."""
    points = course.copy()
    if points.empty:
        raise ValueError('등록된 코스 좌표가 없어요')
    for column in ['순서', '위도', '경도']:
        points[column] = pd.to_numeric(points[column], errors='coerce')
        if not points[column].map(isfinite).all():
            raise ValueError('순서나 좌표에 빈칸·숫자 오류가 있어요. 원본 데이터를 확인해 주세요')
    if (points['순서'] <= 0).any() or (points['순서'] % 1 != 0).any():
        raise ValueError('경유지 순서는 양의 정수여야 해요')
    if points['순서'].duplicated().any():
        raise ValueError('경유지 순서가 중복되어 있어요. 원본 데이터를 확인해 주세요')
    if not (points['위도'].between(-90, 90).all()
            and points['경도'].between(-180, 180).all()):
        raise ValueError('위도·경도 범위를 벗어난 좌표가 있어요. 원본 데이터를 확인해 주세요')
    return points.sort_values('순서', kind='stable').reset_index(drop=True)


def point_description(point):
    """지점명에 HTML 문자가 있어도 안전하게 설명을 표시한다."""
    name = '' if pd.isna(point['경유지명']) else str(point['경유지명']).strip()
    kind = '' if pd.isna(point['구분']) else str(point['구분']).strip()
    name, kind = name or '이름 없는 경유지', kind or '경유'
    return (f"<b>{int(point['순서'])}. {escape(name)}</b><br>{escape(kind)}"
            f"<br>위도 {point['위도']}<br>경도 {point['경도']}")


def build_course_map(points):
    """지도 만들기 → 선 추가 → 지점 추가 → 전체 코스 범위 맞추기."""
    locations = points[['위도', '경도']].values.tolist()
    course_map = folium.Map(location=locations[0], tiles='OpenStreetMap',
                            zoom_start=14, control_scale=True)
    if len(locations) > 1:
        folium.PolyLine(locations, color='#2563eb', weight=4, opacity=1,
                        tooltip='입력 좌표를 순서대로 연결한 코스').add_to(course_map)
    for _, point in points.iterrows():
        kind = '' if pd.isna(point['구분']) else str(point['구분']).strip()
        # 출발·도착이 겹쳐도 초록 원 둘레와 보라 원이 함께 보이도록 크기를 다르게 한다.
        if '출발' in kind:
            color, radius = '#16803d', 11
        elif '도착' in kind:
            color, radius = '#9333ea', 7
        elif '반환' in kind:
            color, radius = '#dc2626', 8
        else:
            color, radius = '#64748b', 4
        description = point_description(point)
        folium.CircleMarker(
            location=[point['위도'], point['경도']], radius=radius,
            color='white', weight=1, fill=True, fill_color=color, fill_opacity=1,
            tooltip=description, popup=folium.Popup(description, max_width=300),
        ).add_to(course_map)
    course_map.fit_bounds([
        points[['위도', '경도']].min().tolist(),
        points[['위도', '경도']].max().tolist(),
    ], padding=(25, 25), max_zoom=16)
    return course_map


def show_course_map(race, waypoints):
    """기존 app.py가 부르는 함수. 선택한 대회·종목만 표시한다."""
    st.subheader('코스 지도')
    if race is None:
        st.info('대회를 클릭하면 코스 지도가 나와요')
        return
    race_id = str(race['번호']).strip()
    course = waypoints[waypoints['대회번호'].astype(str).str.strip().eq(race_id)].copy()
    if course.empty:
        st.info('이 대회에는 등록된 코스 정보가 없어요')
        return
    course['구분'] = course['구분'].fillna('').astype(str).str.strip()
    if course['구분'].eq('대회취소').any():
        st.warning('취소된 대회라 코스 지도를 제공하지 않아요')
        return
    course['종목'] = course['종목'].fillna('').astype(str).str.strip()
    distances = course.loc[course['종목'].ne(''), '종목'].drop_duplicates().tolist()
    if not distances:
        st.info('이 대회에는 등록된 코스 정보가 없어요')
        return
    distance = st.selectbox('지도 종목', distances, key=f'course_distance_{race_id}')
    selected = course[course['종목'].eq(distance)]
    if selected['구분'].eq('코스정보없음').any():
        st.info(f'{distance} 코스 정보가 아직 등록되지 않았어요')
        return
    try:
        points = prepare_course(selected)
    except ValueError as error:
        # 오류 행을 빼고 이어 그리면 실제로 없는 지름길을 표시할 수 있다.
        st.warning(str(error))
        return
    st.caption(f"{race['대회명']} · {distance} · 경유지 {len(points)}개")
    st_folium(build_course_map(points), height=500, use_container_width=True,
              key=f'course_map_{race_id}_{distance}', returned_objects=[])
    st.caption('초록: 출발 · 빨강: 반환 · 보라: 도착 · 회색: 경유 · 지점을 누르면 설명이 나와요')
    st.caption('수집한 좌표를 순서대로 직선 연결한 지도예요. 실제 도로와 차이가 있을 수 있어요')
