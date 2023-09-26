"""
edx_recommendations Django application initialization.
"""

from django.apps import AppConfig
from edx_django_utils.plugins.constants import PluginSettings, PluginURLs


class EdxRecommendationsConfig(AppConfig):
    """
    Configuration for the edx_recommendations Django application.
    """

    name = "edx_recommendations"
    label = "edx_recommendations"

    plugin_app = {
        PluginURLs.CONFIG: {
            "lms.djangoapp": {
                PluginURLs.NAMESPACE: "edx_recommendations",
                PluginURLs.APP_NAME: "edx_recommendations",
                PluginURLs.REGEX: "api/edx_recommendations/",
                PluginURLs.RELATIVE_PATH: "api.urls",
            }
        },
        PluginSettings.CONFIG: {
            "lms.djangoapp": {
                "common": {
                    PluginSettings.RELATIVE_PATH: "settings.common",
                },
                'devstack': {
                    PluginSettings.RELATIVE_PATH: 'settings.devstack',
                },
                "production": {
                    PluginSettings.RELATIVE_PATH: "settings.production",
                },
            }
        },
    }
