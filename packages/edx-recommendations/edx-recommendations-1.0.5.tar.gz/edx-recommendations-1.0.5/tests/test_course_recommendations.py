"""
Tests for course recommendations APIs
"""

import json
from unittest import mock

import ddt
from django.urls import reverse_lazy
from edx_toggles.toggles.testutils import override_waffle_flag
from rest_framework.test import APITestCase

from edx_recommendations.toggles import ENABLE_DASHBOARD_RECOMMENDATIONS, FALLBACK_RECOMMENDATIONS
from test_utils.factories import UserFactory


class TestRecommendationsBase(APITestCase):
    """Recommendations test base class"""

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.client.login(username=self.user.username, password="test")
        self.recommended_courses = [
            "MITx+6.00.1x",
            "IBM+PY0101EN",
            "HarvardX+CS50P",
            "UQx+IELTSx",
            "HarvardX+CS50x",
            "Harvard+CS50z",
            "BabsonX+EPS03x",
            "TUMx+QPLS2x",
            "NYUx+FCS.NET.1",
            "MichinX+101x",
        ]


@ddt.ddt
class TestDashboardRecommendationsApiView(TestRecommendationsBase):
    """Unit tests for the course recommendations on learner home page."""

    url = reverse_lazy("learner_dashboard_amplitude")

    GENERAL_RECOMMENDATIONS = [
        {
            "course_key": "HogwartsX+6.00.1x",
            "logo_image_url": "http://edx.org/images/test.png",
            "marketing_url": "http://edx.org/courses/AI",
            "title": "Defense Against the Dark Arts",
        },
        {
            "course_key": "MonstersX+SC101EN",
            "logo_image_url": "http://edx.org/images/test.png",
            "marketing_url": "http://edx.org/courses/AI",
            "title": "Scaring 101",
        },
    ]

    SERIALIZED_GENERAL_RECOMMENDATIONS = [
        {
            "courseKey": GENERAL_RECOMMENDATIONS[0]["course_key"],
            "logoImageUrl": GENERAL_RECOMMENDATIONS[0]["logo_image_url"],
            "marketingUrl": GENERAL_RECOMMENDATIONS[0]["marketing_url"],
            "title": GENERAL_RECOMMENDATIONS[0]["title"],
        },
        {
            "courseKey": GENERAL_RECOMMENDATIONS[1]["course_key"],
            "logoImageUrl": GENERAL_RECOMMENDATIONS[1]["logo_image_url"],
            "marketingUrl": GENERAL_RECOMMENDATIONS[1]["marketing_url"],
            "title": GENERAL_RECOMMENDATIONS[1]["title"],
        },
    ]

    def setUp(self):
        super().setUp()
        self.course_run_keys = [f"course-v1:{course}+Run_0" for course in self.recommended_courses]

    def _get_filtered_courses(self):
        """
        Returns the filtered course data
        """
        filtered_course = []
        for course_key in self.recommended_courses[:5]:
            filtered_course.append({
                "key": course_key,
                "title": f"Title for {course_key}",
                "logo_image_url": "https://www.logo_image_url.com",
                "marketing_url": "https://www.marketing_url.com",
            })

        return filtered_course

    @override_waffle_flag(ENABLE_DASHBOARD_RECOMMENDATIONS, active=False)
    def test_waffle_flag_off(self):
        """
        Verify API returns 404 if waffle flag is off.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, None)

    @override_waffle_flag(FALLBACK_RECOMMENDATIONS, active=True)
    @override_waffle_flag(ENABLE_DASHBOARD_RECOMMENDATIONS, active=True)
    @mock.patch("django.conf.settings.GENERAL_RECOMMENDATIONS", GENERAL_RECOMMENDATIONS)
    @mock.patch(
        "edx_recommendations.api.course_recommendations.get_amplitude_course_recommendations"
    )
    def test_no_recommendations_from_amplitude(
        self, get_amplitude_course_recommendations_mock
    ):
        """
        Verify API returns general recommendations if no course recommendations from amplitude.
        """
        get_amplitude_course_recommendations_mock.return_value = [False, True, []]

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("isControl"), False)
        self.assertEqual(
            response_content.get("courses"),
            self.SERIALIZED_GENERAL_RECOMMENDATIONS,
        )

    @override_waffle_flag(FALLBACK_RECOMMENDATIONS, active=True)
    @override_waffle_flag(ENABLE_DASHBOARD_RECOMMENDATIONS, active=True)
    @mock.patch("django.conf.settings.GENERAL_RECOMMENDATIONS", GENERAL_RECOMMENDATIONS)
    @mock.patch(
        "edx_recommendations.api.course_recommendations.get_amplitude_course_recommendations",
        mock.Mock(side_effect=Exception),
    )
    def test_amplitude_api_unexpected_error(self):
        """
        Test that if the Amplitude API gives an unexpected error, general recommendations are returned.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("isControl"), None)
        self.assertEqual(
            response_content.get("courses"),
            self.SERIALIZED_GENERAL_RECOMMENDATIONS,
        )

    @override_waffle_flag(ENABLE_DASHBOARD_RECOMMENDATIONS, active=True)
    @mock.patch("edx_recommendations.api.course_recommendations.get_amplitude_course_recommendations")
    @mock.patch("edx_recommendations.api.course_recommendations.filter_recommended_courses")
    def test_amplitude_course_recommendations(
        self, filter_recommended_courses_mock, get_amplitude_course_recommendations_mock
    ):
        """
        Verify API returns course recommendations.
        """
        get_amplitude_course_recommendations_mock.return_value = [
            False,
            True,
            self.recommended_courses,
        ]

        filter_recommended_courses_mock.return_value = self._get_filtered_courses()
        expected_recommendations_length = 5

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("isControl"), False)
        self.assertEqual(
            len(response_content.get("courses")), expected_recommendations_length
        )

    @override_waffle_flag(FALLBACK_RECOMMENDATIONS, active=True)
    @override_waffle_flag(ENABLE_DASHBOARD_RECOMMENDATIONS, active=True)
    @mock.patch("django.conf.settings.GENERAL_RECOMMENDATIONS", GENERAL_RECOMMENDATIONS)
    @mock.patch(
        "edx_recommendations.api.course_recommendations.get_amplitude_course_recommendations"
    )
    def test_dashboard_general_recommendations(
        self, get_amplitude_course_recommendations_mock
    ):
        """
        Test that a user gets general recommendations for the control group.
        """
        get_amplitude_course_recommendations_mock.return_value = [
            True,
            True,
            self.recommended_courses,
        ]

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("isControl"), True)
        self.assertEqual(
            response_content.get("courses"),
            self.SERIALIZED_GENERAL_RECOMMENDATIONS,
        )

    @override_waffle_flag(FALLBACK_RECOMMENDATIONS, active=False)
    @override_waffle_flag(ENABLE_DASHBOARD_RECOMMENDATIONS, active=True)
    @mock.patch("django.conf.settings.GENERAL_RECOMMENDATIONS", GENERAL_RECOMMENDATIONS)
    @mock.patch(
        "edx_recommendations.api.course_recommendations.get_amplitude_course_recommendations"
    )
    def test_fallback_recommendations_disabled(
        self, get_amplitude_course_recommendations_mock
    ):
        """
        Test that a user gets no recommendations for the control group.
        """
        get_amplitude_course_recommendations_mock.return_value = [
            True,
            True,
            [],
        ]

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("isControl"), True)
        self.assertEqual(response_content.get("courses"), [])

    @override_waffle_flag(FALLBACK_RECOMMENDATIONS, active=True)
    @override_waffle_flag(ENABLE_DASHBOARD_RECOMMENDATIONS, active=True)
    @mock.patch("django.conf.settings.GENERAL_RECOMMENDATIONS", GENERAL_RECOMMENDATIONS)
    @mock.patch(
        "edx_recommendations.api.course_recommendations.get_amplitude_course_recommendations"
    )
    @mock.patch("edx_recommendations.api.course_recommendations.filter_recommended_courses")
    def test_no_recommended_courses_after_filtration(
        self, filter_recommended_courses_mock, get_amplitude_course_recommendations_mock
    ):
        """
        Test that if after filtering already enrolled courses from Amplitude recommendations
        we are left with zero personalized recommendations, we return general recommendations.
        """
        filter_recommended_courses_mock.return_value = []
        get_amplitude_course_recommendations_mock.return_value = [
            False,
            True,
            self.recommended_courses,
        ]

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("isControl"), False)
        self.assertEqual(
            response_content.get("courses"),
            self.SERIALIZED_GENERAL_RECOMMENDATIONS,
        )

    @ddt.data(
        (True, False, None),
        (False, True, False),
        (False, False, None),
        (True, True, True),
    )
    @mock.patch("edx_recommendations.api.course_recommendations.segment.track")
    @mock.patch("edx_recommendations.api.course_recommendations.filter_recommended_courses")
    @mock.patch(
        "edx_recommendations.api.course_recommendations.get_amplitude_course_recommendations"
    )
    @override_waffle_flag(ENABLE_DASHBOARD_RECOMMENDATIONS, active=True)
    @ddt.unpack
    def test_recommendations_viewed_segment_event(
        self,
        is_control,
        has_is_control,
        expected_is_control,
        get_amplitude_course_recommendations_mock,
        filter_recommended_courses_mock,
        segment_track_mock
    ):
        """
        Test that Segment event is emitted with desired properties.
        """
        get_amplitude_course_recommendations_mock.return_value = [
            is_control,
            has_is_control,
            self.recommended_courses,
        ]
        filter_recommended_courses_mock.return_value = self._get_filtered_courses()
        self.client.get(self.url)

        if has_is_control and not is_control:
            assert segment_track_mock.call_count == 1
        else:
            assert segment_track_mock.call_count == 2
        assert segment_track_mock.call_args[0][1] == "edx.bi.user.recommendations.viewed"
        self.assertEqual(segment_track_mock.call_args[0][2]["is_control"], expected_is_control)

    @mock.patch("edx_recommendations.api.course_recommendations.segment.track")
    @mock.patch("edx_recommendations.api.course_recommendations.filter_recommended_courses")
    @mock.patch(
        "edx_recommendations.api.course_recommendations.get_amplitude_course_recommendations"
    )
    @override_waffle_flag(ENABLE_DASHBOARD_RECOMMENDATIONS, active=True)
    @ddt.unpack
    def test_recommendations_unavailable_segment_event(
        self,
        get_amplitude_course_recommendations_mock,
        filter_recommended_courses_mock,
        segment_track_mock
    ):
        """
        Test that Segment event is emitted with desired properties.
        """
        get_amplitude_course_recommendations_mock.return_value = [
            False,
            True,
            [],
        ]
        filter_recommended_courses_mock.return_value = self._get_filtered_courses()
        self.client.get(self.url)

        assert segment_track_mock.call_count == 2

    @override_waffle_flag(ENABLE_DASHBOARD_RECOMMENDATIONS, active=True)
    @mock.patch(
        "edx_recommendations.api.course_recommendations.is_user_enrolled_in_ut_austin_masters_program"
    )
    def test_no_recommendations_for_masters_program_learners(
        self, is_user_enrolled_in_ut_austin_masters_program_mock
    ):
        """
        Verify API returns no recommendations if a user is enrolled in UT Austin masters program.
        """
        is_user_enrolled_in_ut_austin_masters_program_mock.return_value = True

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("isControl"), None)
        self.assertEqual(response_content.get("courses"), [])
