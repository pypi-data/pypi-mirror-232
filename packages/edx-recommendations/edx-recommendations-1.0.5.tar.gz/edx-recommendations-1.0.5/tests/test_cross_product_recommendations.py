"""
Tests for Learner Recommendations views and related functions.
"""

import json
from unittest import mock

from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from test_utils.constants import mock_cross_product_recommendation_keys
from test_utils.factories import UserFactory
from test_utils.helpers import get_general_recommendations


class TestRecommendationsContextView(APITestCase):
    """
    Tests for the Recommendations Context View
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.password = "test"
        self.url = reverse_lazy("learner_dashboard_recommendations_context")

    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    def test_successful_response(self, country_code_from_ip_mock):
        """
        Test that country code gets sent back for authenticated user
        """

        country_code_from_ip_mock.return_value = "za"
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.get(self.url)
        response_data = json.loads(response.content)

        self.assertEqual(response_data["countryCode"], "za")

    def test_unauthenticated_response(self):
        """
        Test that a 401 is sent back if an unauthenticated user calls endpoint
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)


class TestCrossProductRecommendationsView(APITestCase):
    """
    Tests for the Cross Product Recommendations View
    """

    def setUp(self):
        super().setUp()
        self.associated_course_keys = ["edx+HL1", "edx+HL2"]

    def _get_url(self, course_key):
        """
        Returns the API url
        """
        return reverse_lazy(
            "course_about_page_cross_product",
            kwargs={'course_id': f'course-v1:{course_key}+Test_Course'}
        )

    def _get_recommended_courses(self, num_of_courses_with_restriction=0, active_course_run=True):
        """
        Returns an array of two discovery courses with or without country restrictions
        """
        courses = []
        restriction_obj = {
            "restriction_type": "blocklist",
            "countries": ["CN"],
            "states": []
        }

        for course_key in enumerate(self.associated_course_keys):
            location_restriction = restriction_obj if num_of_courses_with_restriction > 0 else None
            advertised_course_run_uuid = "jh76b2c9-589b-4d1e-88c1-b01a02db3a9c" if active_course_run else None

            courses.append({
                "key": course_key[1],
                "uuid": "6f8cb2c9-589b-4d1e-88c1-b01a02db3a9c",
                "title": f"Title {course_key[0]}",
                "image": {
                        "src": "https://www.logo_image_url.com",
                },
                "url_slug": "https://www.marketing_url.com",
                "course_type": "executive-education",
                "owners": [
                    {
                            "key": "org-1",
                            "name": "org 1",
                            "logo_image_url": "https://discovery.com/organization/logos/org-1.png",
                    },
                ],
                "course_runs": [
                    {
                        "key": "course-v1:Test+2023_T2",
                        "marketing_url": "https://www.marketing_url.com",
                        "availability": "Current",
                        "uuid": "jh76b2c9-589b-4d1e-88c1-b01a02db3a9c",
                        "status": "published"
                    }
                ],
                "advertised_course_run_uuid": advertised_course_run_uuid,
                "location_restriction": location_restriction,
            })

            if num_of_courses_with_restriction > 0:
                num_of_courses_with_restriction -= 1

        return courses

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    def test_successful_response(
        self, country_code_from_ip_mock, get_course_data_mock,
    ):
        """
        Verify valid cross product course recommendations are returned.
        """
        country_code_from_ip_mock.return_value = "za"
        mock_course_data = self._get_recommended_courses()
        get_course_data_mock.side_effect = [mock_course_data[0], mock_course_data[1]]

        response = self.client.get(self._get_url('edx+HL0'))
        response_content = json.loads(response.content)
        course_data = response_content["courses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(course_data), 2)

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    def test_one_course_country_restriction_response(
        self, country_code_from_ip_mock, get_course_data_mock,
    ):
        """
        Verify valid cross product course recommendation is returned
        if there is a location restriction on a product
        """
        country_code_from_ip_mock.return_value = "cn"
        mock_course_data = self._get_recommended_courses(1)
        get_course_data_mock.side_effect = [mock_course_data[0], mock_course_data[1]]

        response = self.client.get(self._get_url('edx+HL0'))
        response_content = json.loads(response.content)
        course_data = response_content["courses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(course_data), 1)
        self.assertEqual(course_data[0]["title"], "Title 1")

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    def test_both_course_country_restriction_response(
        self, country_code_from_ip_mock, get_course_data_mock,
    ):
        """
        Verify no courses are returned if both courses have a location restriction
        for the users country.
        """
        country_code_from_ip_mock.return_value = "cn"
        mock_course_data = self._get_recommended_courses(2)

        get_course_data_mock.side_effect = [mock_course_data[0], mock_course_data[1]]

        response = self.client.get(self._get_url('edx+HL0'))
        response_content = json.loads(response.content)
        course_data = response_content["courses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(course_data), 0)

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    def test_no_associated_course_response(self):
        """
        Verify an empty array of courses is returned if there are no associated course keys.
        """
        response = self.client.get(self._get_url('No+Associations'))
        response_content = json.loads(response.content)
        course_data = response_content["courses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(course_data), 0)

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    def test_no_response_from_discovery(self, country_code_from_ip_mock, get_course_data_mock):
        """
        Verify an empty array of courses is returned if discovery returns two empty dictionaries.
        """
        country_code_from_ip_mock.return_value = "za"
        get_course_data_mock.side_effect = [{}, {}]

        response = self.client.get(self._get_url('edx+HL0'))
        response_content = json.loads(response.content)
        course_data = response_content["courses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(course_data), 0)

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    def test_no_active_course_runs_response(self, country_code_from_ip_mock, get_course_data_mock):
        """
        Verify that an empty array of courses is returned if courses do not have an active course run.
        """
        country_code_from_ip_mock.return_value = "za"
        mock_course_data = self._get_recommended_courses(0, active_course_run=False)
        get_course_data_mock.side_effect = [mock_course_data[0], mock_course_data[1]]

        response = self.client.get(self._get_url('edx+HL0'))
        reponse_content = json.loads(response.content)
        course_data = reponse_content["courses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(course_data), 0)


class TestProductRecommendationsView(APITestCase):
    """
    Tests for Product Recommendations View
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.client.login(username=self.user.username, password="test")
        self.associated_course_keys = ["edx+HL1", "edx+HL2"]
        self.amplitude_keys = [
            "edx+CS0",
            "edx+CS10",
            "edx+CS20",
            "edx+CS30",
            "edx+CS40",
            "edx+CS50",
            "edx+CS60",
            "edx+CS70",
            "edx+CS80",
            "edx+CS90",
        ]
        self.amplitude_course_run_keys = [f"course-v1:{course_key}+2023_T2" for course_key in self.amplitude_keys]
        self.enrolled_course_run_keys = self.amplitude_course_run_keys[3:8]
        self.enrolled_course_keys = self.amplitude_keys[3:8]
        self.amplitude_location_restriction_keys = self.amplitude_keys[0:3]
        self.cross_product_location_restriction_keys = self.associated_course_keys[0]

    def _get_url(self, course_key=None):
        """
        Returns the product recommendations url with or without the course key
        """
        if course_key:
            return reverse_lazy(
                "learner_dashboard_cross_product",
                kwargs={'course_id': f'course-v1:{course_key}+Test_Course'}
            )

        return reverse_lazy(
            "learner_dashboard_amplitude_v2"
        )

    def _get_product_recommendations(self, course_keys, keys_with_restriction=None):
        """
        Returns course data based on the number of course keys passed in
        with a location restriction object if a list of keys for location restriction courses is passed in
        """
        courses = []

        for key in course_keys:
            course = {
                "title": f"Title for {key}",
                "image": {
                    "src": "https://www.logo_image_url.com",
                },
                "course_type": "executive-education",
                "owners": [
                    {
                        "key": "org-1",
                        "name": "org 1",
                        "logo_image_url": "https://discovery.com/organization/logos/org-1.png",
                    },
                ],
                "course_runs": [
                    {
                        "key": f"course-v1:{key}+2023_T2",
                        "marketing_url": "https://www.marketing_url.com",
                        "availability": "Current",
                        "uuid": "jh76b2c9-589b-4d1e-88c1-b01a02db3a9c",
                        "status": "published"
                    }
                ],
                "marketing_url": "https://www.marketing_url.com/course/some-course",
                "advertised_course_run_uuid": f"course-v1:{key}+2023_T2",
            }
            if keys_with_restriction and key in keys_with_restriction:
                course.update({
                    "location_restriction": {
                        "restriction_type": "blocklist",
                        "countries": ["CN"],
                        "states": []
                    }
                })

            courses.append(course)

        return courses

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    @mock.patch("edx_recommendations.api.utils._get_user_enrolled_course_keys")
    @mock.patch("edx_recommendations.api.utils.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_amplitude_course_recommendations")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.is_user_enrolled_in_ut_austin_masters_program")
    def test_successful_response(
        self,
        is_user_enrolled_in_ut_austin_masters_program_mock,
        country_code_from_ip_mock,
        get_amplitude_course_recommendations_mock,
        get_course_data_view_mock,
        get_course_data_util_mock,
        get_user_enrolled_course_keys_mock,
    ):
        """
        Verify 2 cross product course recommendations are returned
        and 4 amplitude courses are returned
        """
        is_user_enrolled_in_ut_austin_masters_program_mock.return_value = False
        country_code_from_ip_mock.return_value = "za"
        get_user_enrolled_course_keys_mock.return_value = []
        get_amplitude_course_recommendations_mock.return_value = [False, True, self.amplitude_keys]

        mock_cross_product_course_data = self._get_product_recommendations(self.associated_course_keys)
        mock_amplitude_course_data = self._get_product_recommendations(self.amplitude_keys)
        get_course_data_view_mock.side_effect = mock_cross_product_course_data
        get_course_data_util_mock.side_effect = mock_amplitude_course_data

        response = self.client.get(self._get_url('edx+HL0'))
        response_content = json.loads(response.content)
        cross_product_course_data = response_content["crossProductCourses"]
        amplitude_course_data = response_content["amplitudeCourses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(cross_product_course_data), 2)
        self.assertEqual(len(amplitude_course_data), 4)

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    @mock.patch("edx_recommendations.api.utils._get_user_enrolled_course_keys")
    @mock.patch("edx_recommendations.api.utils.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_amplitude_course_recommendations")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.is_user_enrolled_in_ut_austin_masters_program")
    def test_successful_course_filtering(
        self,
        is_user_enrolled_in_ut_austin_masters_program_mock,
        country_code_from_ip_mock,
        get_amplitude_course_recommendations_mock,
        get_course_data_view_mock,
        get_course_data_util_mock,
        get_user_enrolled_course_keys_mock,
    ):
        """
        Verify 1 cross product course recommendation is returned
        and 2 amplitude courses are returned with filtering done for
        enrolled courses and courses with country restrictions
        """
        is_user_enrolled_in_ut_austin_masters_program_mock.return_value = False
        country_code_from_ip_mock.return_value = "cn"
        get_user_enrolled_course_keys_mock.return_value = self.enrolled_course_run_keys
        get_amplitude_course_recommendations_mock.return_value = [False, True, self.amplitude_keys]

        mock_cross_product_course_data = self._get_product_recommendations(
            self.associated_course_keys, self.cross_product_location_restriction_keys
        )
        mock_amplitude_course_data = self._get_product_recommendations(
            self.amplitude_keys, self.amplitude_location_restriction_keys
        )
        get_course_data_view_mock.side_effect = mock_cross_product_course_data
        get_course_data_util_mock.side_effect = mock_amplitude_course_data

        response = self.client.get(self._get_url('edx+HL0'))
        response_content = json.loads(response.content)
        cross_product_course_data = response_content["crossProductCourses"]
        amplitude_course_data = response_content["amplitudeCourses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(cross_product_course_data), 1)
        self.assertEqual(len(amplitude_course_data), 2)
        for course in amplitude_course_data:
            course_key = course["title"][2]
            assert course_key not in [*self.amplitude_location_restriction_keys, *self.enrolled_course_keys]
        for course in cross_product_course_data:
            course_key = course["title"][2]
            assert course_key not in self.cross_product_location_restriction_keys

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    @mock.patch("django.conf.settings.GENERAL_RECOMMENDATIONS", get_general_recommendations())
    @mock.patch("edx_recommendations.api.utils._get_user_enrolled_course_keys")
    @mock.patch("edx_recommendations.api.utils.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_amplitude_course_recommendations")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.is_user_enrolled_in_ut_austin_masters_program")
    def test_fallback_recommendations_when_enrolled_courses_removed(
        self,
        is_user_enrolled_in_ut_austin_masters_program_mock,
        country_code_from_ip_mock,
        get_amplitude_course_recommendations_mock,
        get_course_data_view_mock,
        get_course_data_util_mock,
        get_user_enrolled_course_keys_mock
    ):
        """
        Verify 2 cross product course recommendations are returned
        and 4 fallback amplitude recommendations are returned if no courses are left
        after filtering due to courses being already enrolled in
        """
        is_user_enrolled_in_ut_austin_masters_program_mock.return_value = False
        country_code_from_ip_mock.return_value = "za"
        get_user_enrolled_course_keys_mock.return_value = self.amplitude_course_run_keys
        get_amplitude_course_recommendations_mock.return_value = [False, True, self.amplitude_keys]

        mock_cross_product_course_data = self._get_product_recommendations(self.associated_course_keys)
        mock_amplitude_course_data = self._get_product_recommendations(self.amplitude_keys)
        get_course_data_view_mock.side_effect = mock_cross_product_course_data
        get_course_data_util_mock.side_effect = mock_amplitude_course_data

        response = self.client.get(self._get_url('edx+HL0'))
        response_content = json.loads(response.content)
        cross_product_course_data = response_content["crossProductCourses"]
        amplitude_course_data = response_content["amplitudeCourses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(cross_product_course_data), 2)
        self.assertEqual(len(amplitude_course_data), 4)
        for course in amplitude_course_data:
            self.assertEqual(course["title"], "Introduction to Computer Science and Programming Using Python")

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    @mock.patch("django.conf.settings.GENERAL_RECOMMENDATIONS", get_general_recommendations())
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_amplitude_course_recommendations")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.is_user_enrolled_in_ut_austin_masters_program")
    def test_fallback_recommendations_when_error_querying_amplitude(
        self,
        is_user_enrolled_in_ut_austin_masters_program_mock,
        country_code_from_ip_mock,
        get_amplitude_course_recommendations_mock,
        get_course_data_mock,
    ):
        """
        Verify 2 cross product course recommendations are returned
        and 4 fallback amplitude recommendations are returned
        if there was an error querying amplitude for recommendations
        """
        is_user_enrolled_in_ut_austin_masters_program_mock.return_value = False
        country_code_from_ip_mock.return_value = "za"
        get_amplitude_course_recommendations_mock.side_effect = Exception()

        mock_cross_product_course_data = self._get_product_recommendations(self.associated_course_keys)
        get_course_data_mock.side_effect = mock_cross_product_course_data

        response = self.client.get(self._get_url('edx+HL0'))
        response_content = json.loads(response.content)
        cross_product_course_data = response_content["crossProductCourses"]
        amplitude_course_data = response_content["amplitudeCourses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(cross_product_course_data), 2)
        self.assertEqual(len(amplitude_course_data), 4)
        for course in amplitude_course_data:
            self.assertEqual(course["title"], "Introduction to Computer Science and Programming Using Python")

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    @mock.patch("django.conf.settings.GENERAL_RECOMMENDATIONS", get_general_recommendations())
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_amplitude_course_recommendations")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.is_user_enrolled_in_ut_austin_masters_program")
    def test_fallback_recommendations_when_no_amplitude_recommended_keys(
        self,
        is_user_enrolled_in_ut_austin_masters_program_mock,
        country_code_from_ip_mock,
        get_amplitude_course_recommendations_mock,
        get_course_data_mock,
    ):
        """
        Verify 2 cross product course recommendations are returned
        and 4 fallback amplitude recommendations are returned
        if amplitude gave back no course keys
        """
        is_user_enrolled_in_ut_austin_masters_program_mock.return_value = False
        country_code_from_ip_mock.return_value = "za"
        get_amplitude_course_recommendations_mock.side_effect = [False, True, []]

        mock_cross_product_course_data = self._get_product_recommendations(self.associated_course_keys)
        get_course_data_mock.side_effect = mock_cross_product_course_data

        response = self.client.get(self._get_url('edx+HL0'))
        response_content = json.loads(response.content)
        cross_product_course_data = response_content["crossProductCourses"]
        amplitude_course_data = response_content["amplitudeCourses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(cross_product_course_data), 2)
        self.assertEqual(len(amplitude_course_data), 4)
        for course in amplitude_course_data:
            self.assertEqual(course["title"], "Introduction to Computer Science and Programming Using Python")

    @mock.patch("django.conf.settings.CROSS_PRODUCT_RECOMMENDATIONS_KEYS", mock_cross_product_recommendation_keys)
    @mock.patch("edx_recommendations.api.utils._get_user_enrolled_course_keys")
    @mock.patch("edx_recommendations.api.utils.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_amplitude_course_recommendations")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.is_user_enrolled_in_ut_austin_masters_program")
    def test_response_with_amplitude_and_no_cross_product_courses(
        self,
        is_user_enrolled_in_ut_austin_masters_program_mock,
        country_code_from_ip_mock,
        get_amplitude_course_recommendations_mock,
        get_course_data_mock,
        get_user_enrolled_course_keys_mock
    ):
        """
        Verify that if no cross product courses are returned,
        then 4 fallback amplitude recommendations will still be returned
        """
        is_user_enrolled_in_ut_austin_masters_program_mock.return_value = False
        country_code_from_ip_mock.return_value = "za"
        get_user_enrolled_course_keys_mock.return_value = self.enrolled_course_run_keys
        get_amplitude_course_recommendations_mock.return_value = [False, True, self.amplitude_keys]

        mock_amplitude_course_data = self._get_product_recommendations(self.amplitude_keys)
        get_course_data_mock.side_effect = mock_amplitude_course_data

        response = self.client.get(self._get_url('No+Association'))
        response_content = json.loads(response.content)
        cross_product_course_data = response_content["crossProductCourses"]
        amplitude_course_data = response_content["amplitudeCourses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(cross_product_course_data), 0)
        self.assertEqual(len(amplitude_course_data), 4)

    @mock.patch("edx_recommendations.api.utils._get_user_enrolled_course_keys")
    @mock.patch("edx_recommendations.api.utils.get_course_data")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.get_amplitude_course_recommendations")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.is_user_enrolled_in_ut_austin_masters_program")
    def test_amplitude_only_url_response(
        self,
        is_user_enrolled_in_ut_austin_masters_program_mock,
        country_code_from_ip_mock,
        get_amplitude_course_recommendations_mock,
        get_course_data_mock,
        get_user_enrolled_course_keys_mock
    ):
        """
        Verify that if no course key was provided in the url,
        only 1 field for amplitude courses are sent back
        """
        is_user_enrolled_in_ut_austin_masters_program_mock.return_value = False
        country_code_from_ip_mock.return_value = "za"
        get_user_enrolled_course_keys_mock.return_value = self.enrolled_course_run_keys
        get_amplitude_course_recommendations_mock.return_value = [False, True, self.amplitude_keys]

        mock_amplitude_course_data = self._get_product_recommendations(self.amplitude_keys)
        get_course_data_mock.side_effect = mock_amplitude_course_data

        response = self.client.get(self._get_url())
        response_content = json.loads(response.content)
        amplitude_course_data = response_content["amplitudeCourses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_content), 1)
        self.assertEqual(len(amplitude_course_data), 4)

    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.is_user_enrolled_in_ut_austin_masters_program")
    def test_zero_cross_product_and_amplitude_recommendations(
        self,
        is_user_enrolled_in_ut_austin_masters_program_mock,
        country_code_from_ip_mock,
    ):
        """
        Verify 0 cross product course recommendations are returned
        and 0 amplitude courses are returned if the user is enrolled in ut austin masters program
        """
        is_user_enrolled_in_ut_austin_masters_program_mock.return_value = True
        country_code_from_ip_mock.return_value = "za"

        response = self.client.get(self._get_url('edx+HL0'))
        response_content = json.loads(response.content)
        cross_product_course_data = response_content["crossProductCourses"]
        amplitude_course_data = response_content["amplitudeCourses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(cross_product_course_data), 0)
        self.assertEqual(len(amplitude_course_data), 0)

    @mock.patch("edx_recommendations.api.cross_product_recommendations.country_code_from_ip")
    @mock.patch("edx_recommendations.api.cross_product_recommendations.is_user_enrolled_in_ut_austin_masters_program")
    def test_zero_amplitude_recommendations(
        self,
        is_user_enrolled_in_ut_austin_masters_program_mock,
        country_code_from_ip_mock,
    ):
        """
        Verify that 0 amplitude courses are returned
        if the user is enrolled in ut austin masters program
        """
        is_user_enrolled_in_ut_austin_masters_program_mock.return_value = True
        country_code_from_ip_mock.return_value = "za"

        response = self.client.get(self._get_url())
        response_content = json.loads(response.content)
        amplitude_course_data = response_content["amplitudeCourses"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(amplitude_course_data), 0)
