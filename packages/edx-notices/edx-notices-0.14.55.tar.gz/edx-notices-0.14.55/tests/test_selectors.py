"""
Tests for the Notices app's data fetching utilities.
"""
import datetime

from django.conf import settings
from django.test import TestCase, override_settings

from notices.data import AcknowledgmentResponseTypes
from notices.selectors import get_active_notices, get_visible_notices
from test_utils.factories import AcknowledgedNoticeFactory, NoticeFactory, UserFactory


class TestSelectors(TestCase):
    """
    Test for Selector functions business logic.
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory(date_joined=datetime.datetime.fromisoformat("2015-01-01"))

    def test_get_active_notices(self):
        old_active_notice = NoticeFactory(active=True, launch_date=datetime.datetime.fromisoformat("2020-10-31"))
        new_active_notice = NoticeFactory(active=True, launch_date=datetime.datetime.fromisoformat("2021-10-31"))
        results = get_active_notices()
        assert list(results) == [old_active_notice, new_active_notice]

        sign_up_date = datetime.datetime.fromisoformat("2021-10-27")
        results = get_active_notices(before_date=sign_up_date)
        assert list(results) == [new_active_notice]

    def test_get_visible_notices(self):
        """
        Happy path. Verifies that "visible" (active and unacknowledged) notice data is returned as expected for a user.
        """
        active_notice = NoticeFactory(active=True)
        active_notice2 = NoticeFactory(active=True)
        active_notice_acked = NoticeFactory(active=True)
        NoticeFactory(active=False)

        AcknowledgedNoticeFactory(
            user=self.user, notice=active_notice_acked, response_type=AcknowledgmentResponseTypes.CONFIRMED
        )

        results = get_visible_notices(self.user)
        assert list(results) == [active_notice, active_notice2]

    @override_settings(FEATURES={"NOTICES_SNOOZE_HOURS": 4})
    def test_snoozed_notices(self):
        """
        Tests that snoozed notices are only snoozed for the `NOTICES_SNOOZE_HOURS` amount of time
        """
        SNOOZE_HOURS = settings.FEATURES["NOTICES_SNOOZE_HOURS"]

        active_notice = NoticeFactory(active=True)
        latest_snooze_time = datetime.datetime.now() - datetime.timedelta(hours=SNOOZE_HOURS)

        # acknowledgment an hour older than the snooze limit
        AcknowledgedNoticeFactory(
            user=self.user,
            notice=active_notice,
            response_type=AcknowledgmentResponseTypes.DISMISSED,
            modified=latest_snooze_time - datetime.timedelta(hours=1),
        )

        results = get_visible_notices(self.user)
        assert len(results) == 1
        assert list(results) == [active_notice]

        # acknowledgment an hour newer than the snooze limit
        AcknowledgedNoticeFactory(
            user=self.user,
            notice=active_notice,
            response_type=AcknowledgmentResponseTypes.DISMISSED,
            modified=latest_snooze_time + datetime.timedelta(hours=1),
        )

        results = get_visible_notices(self.user)
        assert len(results) == 0

    @override_settings(FEATURES={"NOTICES_SNOOZE_COUNT_LIMIT": 3})
    def test_snooze_count_notices(self):
        """
        Tests that notices can only be snoozed NOTICES_SNOOZE_COUNT_LIMIT times
        """
        notices_snooze_count_limit = settings.FEATURES["NOTICES_SNOOZE_COUNT_LIMIT"]
        active_notice = NoticeFactory(active=True)

        AcknowledgedNoticeFactory(
            user=self.user,
            notice=active_notice,
            response_type=AcknowledgmentResponseTypes.DISMISSED,
            snooze_count=notices_snooze_count_limit + 1,
        )
        results = get_visible_notices(self.user)
        assert len(results) == 1
        assert list(results) == [active_notice]

        # snooze count >= limit
        AcknowledgedNoticeFactory(
            user=self.user, notice=active_notice, response_type=AcknowledgmentResponseTypes.DISMISSED, snooze_count=1
        )

        results = get_visible_notices(self.user)
        assert len(results) == 0

    @override_settings(
        FEATURES={"NOTICES_SNOOZE_HOURS": 4, "NOTICES_SNOOZE_COUNT_LIMIT": 3, "NOTICES_MAX_SNOOZE_DAYS": 30}
    )
    def test_snoozed_notices_with_count(self):
        """
        Tests the interaction between snoozing a notice and the snooze limit.
        """
        SNOOZE_HOURS = settings.FEATURES["NOTICES_SNOOZE_HOURS"]
        notices_snooze_count_limit = settings.FEATURES["NOTICES_SNOOZE_COUNT_LIMIT"]
        max_snooze_days = settings.FEATURES["NOTICES_MAX_SNOOZE_DAYS"]

        active_notice = NoticeFactory(active=True)
        latest_snooze_time = datetime.datetime.now() - datetime.timedelta(hours=SNOOZE_HOURS)

        # acknowledgment an hour older than the snooze limit
        ack_test = AcknowledgedNoticeFactory(
            user=self.user,
            notice=active_notice,
            response_type=AcknowledgmentResponseTypes.DISMISSED,
            modified=latest_snooze_time - datetime.timedelta(hours=1),
        )

        results = get_visible_notices(self.user)
        assert len(results) == 1
        assert list(results) == [active_notice]

        # acknowledgment an hour newer than the snooze limit, but snooze_limit exceeded
        ack_test.modified = latest_snooze_time + datetime.timedelta(hours=1)
        ack_test.snooze_count = notices_snooze_count_limit + 1
        ack_test.save()

        results = get_visible_notices(self.user)
        assert len(results) == 1
        assert list(results) == [active_notice]

        # acknowledgment an hour newer than the snooze limit
        ack_test.modified = latest_snooze_time + datetime.timedelta(hours=1)
        ack_test.snooze_count = 1
        ack_test.save()

        results = get_visible_notices(self.user)
        assert len(results) == 0

        # acknowledgment an hour newer than the snooze limit, but max_snooze_days exceeded
        ack_test.modified = latest_snooze_time + datetime.timedelta(hours=1)
        ack_test.snooze_count = 1
        ack_test.created = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=max_snooze_days + 2)
        ack_test.save()

        results = get_visible_notices(self.user)
        assert len(results) == 1
        assert list(results) == [active_notice]

        # Created 2 days ago
        ack_test.created = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2)
        ack_test.modified = latest_snooze_time + datetime.timedelta(hours=0)
        ack_test.snooze_count = 1
        ack_test.save()

        results = get_visible_notices(self.user)
        assert len(results) == 0
