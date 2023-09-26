"""
Tests for the plugin context functions.
"""
from django.test import TestCase
from edx_toggles.toggles.testutils import override_waffle_flag
from rest_framework.reverse import reverse

from notices.context_api import get_dashboard_context
from notices.data import AcknowledgmentResponseTypes
from notices.toggles import ENABLE_NOTICES
from test_utils.factories import AcknowledgedNoticeFactory, NoticeFactory, UserFactory


@override_waffle_flag(ENABLE_NOTICES, active=True)
class TestContextApi(TestCase):
    """
    Tests for the data that gets passed to the course dashboard via context plugins.
    """

    def create_expected_results(self, data):
        return {
            "unacknowledged_notices": data,
        }

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.context = {"user": self.user}

    def test_get_context(self):
        """
        Happy path. Verifies that only active and unack'd notice data is returned in context data.
        """
        notice = NoticeFactory(active=True)
        notice2 = NoticeFactory(active=True)
        notice3 = NoticeFactory(active=True)
        notice4 = NoticeFactory(active=True)
        NoticeFactory(active=False)

        AcknowledgedNoticeFactory(user=self.user, notice=notice2, response_type=AcknowledgmentResponseTypes.CONFIRMED)
        AcknowledgedNoticeFactory(user=self.user, notice=notice3, response_type=AcknowledgmentResponseTypes.DISMISSED)

        expected_data = [
            reverse("notices:notice-detail", kwargs={"pk": notice.id}),
            reverse("notices:notice-detail", kwargs={"pk": notice4.id}),
        ]
        expected_results = self.create_expected_results(expected_data)

        results = get_dashboard_context(self.context)
        assert results == expected_results

    def test_get_context_no_unackd_notices_for_user(self):
        """
        Verifies that acknowledged notice data isn't returned in context data.
        """
        notice = NoticeFactory(active=True)
        AcknowledgedNoticeFactory(user=self.user, notice=notice, response_type=AcknowledgmentResponseTypes.CONFIRMED)

        expected_results = self.create_expected_results([])

        results = get_dashboard_context(self.context)
        assert results == expected_results

    def test_get_context_no_active_notices_for_user(self):
        """
        Verifies that inactive notice data isn't returned in context data.
        """
        NoticeFactory(active=False)

        expected_results = self.create_expected_results([])

        results = get_dashboard_context(self.context)
        assert results == expected_results
