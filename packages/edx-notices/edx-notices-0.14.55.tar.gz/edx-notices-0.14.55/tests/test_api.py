"""
Tests for the Notices app's Python API
"""
import datetime

from django.test import TestCase, override_settings
from rest_framework.reverse import reverse

from notices.api import can_dismiss, get_unacknowledged_notices_for_user
from notices.data import AcknowledgmentResponseTypes
from test_utils.factories import AcknowledgedNoticeFactory, NoticeFactory, UserFactory


class TestPythonApi(TestCase):
    """
    Tests for the Notices app's exposed Python API.
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory()

    def test_unackd_active_notices(self):
        """
        Happy path. Verifies that only active and unack'd notice ids are returned to the caller.
        """
        notice = NoticeFactory(active=True)
        notice2 = NoticeFactory(active=True)
        notice3 = NoticeFactory(active=True)
        notice4 = NoticeFactory(active=True)
        NoticeFactory(active=False)

        AcknowledgedNoticeFactory(user=self.user, notice=notice2, response_type=AcknowledgmentResponseTypes.CONFIRMED)
        AcknowledgedNoticeFactory(user=self.user, notice=notice3, response_type=AcknowledgmentResponseTypes.DISMISSED)

        expected_results = [
            reverse("notices:notice-detail", kwargs={"pk": notice.id}),
            reverse("notices:notice-detail", kwargs={"pk": notice4.id}),
        ]

        results = get_unacknowledged_notices_for_user(self.user)
        assert results == expected_results

    def test_no_unackd_notices_for_user(self):
        """
        Verifies an empty list is returned if a user has no unack'd notices.
        """
        notice = NoticeFactory(active=True)
        AcknowledgedNoticeFactory(user=self.user, notice=notice, response_type=AcknowledgmentResponseTypes.CONFIRMED)

        results = get_unacknowledged_notices_for_user(self.user)
        assert results == []

    def test_no_active_notices_for_user(self):
        """
        Verifies an empty list is returned if a user has no active notices.
        """
        NoticeFactory(active=False)

        results = get_unacknowledged_notices_for_user(self.user)
        assert results == []

    @override_settings(FEATURES={"NOTICES_SNOOZE_COUNT_LIMIT": 3})
    def test_can_dismiss_snooze_limit_ack_dne(self):
        """
        Verifies the default behavior of the `can_dismiss` function when a acknowledgment does not exist for a
        user/notice.
        """
        notice = NoticeFactory(active=True)

        assert can_dismiss(self.user, notice)

    @override_settings(FEATURES={"NOTICES_SNOOZE_COUNT_LIMIT": 3})
    def test_can_dismiss_snooze_count_under_limit(self):
        """
        Verifies the behavior of the `can_dismiss` function when the SNOOZE_LIMIT is under the threshhold set in
        configuration.
        """
        notice = NoticeFactory(active=True)
        AcknowledgedNoticeFactory(
            user=self.user, notice=notice, snooze_count=1, response_type=AcknowledgmentResponseTypes.DISMISSED
        )

        assert can_dismiss(self.user, notice)

    @override_settings(FEATURES={"NOTICES_SNOOZE_COUNT_LIMIT": 1})
    def test_can_dismiss_snooze_count_above_limit(self):
        """
        Verifies the behavior of the `can_dismiss` function when the a user shouldn't be allowed to snooze anymore.
        """
        notice = NoticeFactory(active=True)
        AcknowledgedNoticeFactory(
            user=self.user, notice=notice, snooze_count=1, response_type=AcknowledgmentResponseTypes.DISMISSED
        )

        assert not can_dismiss(self.user, notice)

    @override_settings(FEATURES={"NOTICES_MAX_SNOOZE_DAYS": 30})
    def test_can_dismiss_snooze_days_under_limit(self):
        """
        Verifies the behavior of the `can_dismiss` function when a user is under the threshold of days to ack a
        notice.
        """
        notice = NoticeFactory(active=True)
        test_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=10)
        AcknowledgedNoticeFactory(
            user=self.user,
            notice=notice,
            snooze_count=1,
            created=test_date,
            response_type=AcknowledgmentResponseTypes.DISMISSED,
        )

        assert can_dismiss(self.user, notice)

    @override_settings(FEATURES={"NOTICES_MAX_SNOOZE_DAYS": 1})
    def test_can_dismiss_snooze_days_over_limit(self):
        """
        Verifies the behavior of the `can_dismiss` function when a user should no longer be able to dismiss a notice
        based on the "max snooze days" limit.
        """
        notice = NoticeFactory(active=True)
        test_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=10)
        AcknowledgedNoticeFactory(
            user=self.user,
            notice=notice,
            snooze_count=1,
            created=test_date,
            response_type=AcknowledgmentResponseTypes.DISMISSED,
        )

        assert not can_dismiss(self.user, notice)
