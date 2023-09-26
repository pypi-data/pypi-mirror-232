"""
Tests for the `platform-plugin-braze` signals module.
"""

from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from edx_braze.signals import identify_user_upon_registration

User = get_user_model()


class SignalsTest(TestCase):
    """Tests for signals.py"""

    @override_settings(EDX_BRAZE_API_KEY='test-api-key')
    @override_settings(EDX_BRAZE_API_SERVER='http://test.braze.com')
    @mock.patch('edx_braze.signals.requests')
    def test_identify_happy_path(self, mock_requests):
        user = User(email='test@example.com')

        identify_user_upon_registration(user=user)

        assert mock_requests.post.call_count == 1
        assert mock_requests.post.call_args[0] == ()
        assert mock_requests.post.call_args[1] == {
            'url': 'http://test.braze.com/users/identify',
            'headers': {'Authorization': 'Bearer test-api-key'},
            'json': {
                'aliases_to_identify': [
                    {
                        'external_id': str(user.id),
                        'user_alias': {
                            'alias_label': 'hubspot',
                            'alias_name': 'test@example.com',
                        },
                    },
                    {
                        'external_id': str(user.id),
                        'user_alias': {
                            'alias_label': 'Enterprise',
                            'alias_name': 'test@example.com',
                        },
                    },
                ],
            },
        }

    @override_settings(EDX_BRAZE_API_KEY=None)
    @override_settings(EDX_BRAZE_API_SERVER=None)
    @mock.patch('edx_braze.signals.requests')
    def test_identify_exits_if_no_config(self, mock_requests):
        identify_user_upon_registration()
        assert mock_requests.post.call_count == 0

    @override_settings(EDX_BRAZE_API_KEY='test-api-key')
    @override_settings(EDX_BRAZE_API_SERVER='http://test.braze.com')
    @mock.patch('edx_braze.signals.requests')
    @mock.patch('edx_braze.signals.log')
    def test_identify_logs_errors(self, mock_log, mock_requests):
        user = User(email='test@example.com')
        mock_requests.post.side_effect = Exception

        identify_user_upon_registration(user=user)

        assert mock_requests.post.call_count == 1
        assert mock_log.exception.call_count == 1  # log instead of bubbling up
