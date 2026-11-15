"""실행: python -m unittest discover -s tests -v"""
import unittest
from pathlib import Path
from unittest.mock import patch

import folium
import pandas as pd

from course_map import build_course_map, point_description, prepare_course, show_course_map


ROOT = Path(__file__).resolve().parent.parent


class CourseMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.waypoints = pd.read_csv(ROOT / 'data/waypoints.csv', dtype={'대회번호': str})
        cls.races = pd.read_csv(ROOT / 'data/marathons_raw.csv', dtype={'번호': str})

    def peace(self, distance='10km'):
        return self.waypoints[
            self.waypoints['대회번호'].eq('41766') & self.waypoints['종목'].eq(distance)
        ].copy()

    def test_numeric_order_without_changing_input_or_repeated_locations(self):
        original = self.peace().iloc[::-1].copy()
        original['순서'] = original['순서'].astype(int).astype(str)
        before = original.copy(deep=True)
        prepared = prepare_course(original)
        self.assertEqual(prepared['순서'].tolist(), list(range(1, 34)))
        self.assertEqual(len(prepared), 33)
        pd.testing.assert_frame_equal(original, before)
        self.assertEqual(prepared[['위도', '경도']].values.tolist(),
                         self.peace().sort_values('순서')[['위도', '경도']].values.tolist())

    def test_invalid_interior_point_stops_route_instead_of_bridging_gap(self):
        for column, value in [('위도', None), ('위도', float('inf')), ('경도', 181),
                              ('위도', -91), ('순서', 0), ('순서', 1.5),
                              ('순서', float('inf')), ('순서', '문자')]:
            with self.subTest(column=column, value=value):
                broken = self.peace().astype({'순서': object, '위도': object, '경도': object})
                broken.iloc[10, broken.columns.get_loc(column)] = value
                with self.assertRaises(ValueError):
                    prepare_course(broken)
        duplicate = self.peace()
        duplicate.iloc[1, duplicate.columns.get_loc('순서')] = 1
        with self.assertRaises(ValueError):
            prepare_course(duplicate)

    def test_route_and_all_markers_keep_original_coordinates(self):
        points = prepare_course(self.peace())
        course_map = build_course_map(points)
        lines = [item for item in course_map._children.values()
                 if isinstance(item, folium.PolyLine)]
        markers = [item for item in course_map._children.values()
                   if isinstance(item, folium.CircleMarker)]
        expected = points[['위도', '경도']].values.tolist()
        self.assertEqual(lines[0].locations, expected)
        self.assertEqual([marker.location for marker in markers], expected)
        self.assertEqual(len(markers), 33)
        self.assertIn('#16803d', [marker.options['fillColor'] for marker in markers])
        self.assertIn('#9333ea', [marker.options['fillColor'] for marker in markers])

    def test_repeated_start_finish_and_single_point_render(self):
        points = prepare_course(self.peace()).iloc[[0, -1]].copy()
        points.loc[points.index[-1], ['위도', '경도']] = points.iloc[0][['위도', '경도']].values
        course_map = build_course_map(points)
        markers = [item for item in course_map._children.values()
                   if isinstance(item, folium.CircleMarker)]
        self.assertEqual(markers[0].location, markers[1].location)
        self.assertGreater(markers[0].options['radius'], markers[1].options['radius'])
        self.assertIn('fitBounds', build_course_map(points.iloc[:1]).get_root().render())

    def test_csv_text_is_escaped_in_popup(self):
        point = self.peace().iloc[0].copy()
        point['경유지명'] = '<script>alert(1)</script>'
        description = point_description(point)
        self.assertNotIn('<script>', description)
        self.assertIn('&lt;script&gt;', description)

    def test_all_registered_real_courses_can_build(self):
        valid = self.waypoints[~self.waypoints['구분'].isin(['대회취소', '코스정보없음'])]
        count = 0
        for (race_id, distance), course in valid.groupby(['대회번호', '종목']):
            with self.subTest(race_id=race_id, distance=distance):
                points = prepare_course(course)
                self.assertIn('L.polyline', build_course_map(points).get_root().render())
                count += 1
        self.assertGreater(count, 0)

    def test_selected_distance_and_race_get_distinct_component_keys(self):
        rendered = []
        for race_id, distance in [('41766', '10km'), ('41766', '5km'), ('41259', '10km')]:
            race = self.races[self.races['번호'].eq(race_id)].iloc[0]
            with patch('course_map.st') as ui, patch('course_map.st_folium') as component:
                ui.selectbox.return_value = distance
                show_course_map(race, self.waypoints)
                component.assert_called_once()
                ui.radio.assert_not_called()
                ui.plotly_chart.assert_not_called()
                ui.iframe.assert_not_called()
                actual_map = component.call_args.args[0]
                line = next(item for item in actual_map._children.values()
                            if isinstance(item, folium.PolyLine))
                expected = self.waypoints[self.waypoints['대회번호'].eq(race_id)
                                          & self.waypoints['종목'].eq(distance)]
                self.assertEqual(line.locations, expected.sort_values('순서')[['위도', '경도']].values.tolist())
                self.assertEqual(component.call_args.kwargs['returned_objects'], [])
                rendered.append(component.call_args.kwargs['key'])
        self.assertEqual(len(set(rendered)), 3)

    def test_empty_cancelled_unavailable_and_invalid_courses_show_no_map(self):
        cases = [(None, self.waypoints),
                 (pd.Series({'번호': 'missing'}), self.waypoints),
                 (pd.Series({'번호': '41801'}), self.waypoints),
                 (pd.Series({'번호': '41522'}), self.waypoints),
                 (pd.Series({'번호': '41914'}), self.waypoints)]
        broken = self.peace()
        broken.iloc[10, broken.columns.get_loc('위도')] = float('nan')
        cases.append((pd.Series({'번호': '41766'}), broken))
        for race, waypoints in cases:
            with self.subTest(race=race), patch('course_map.st') as ui, patch('course_map.st_folium') as component:
                ui.selectbox.return_value = '8km' if race is not None and race['번호'] == '41914' else '10km'
                show_course_map(race, waypoints)
                component.assert_not_called()
                self.assertTrue(ui.info.called or ui.warning.called)


if __name__ == '__main__':
    unittest.main()
