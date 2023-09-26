"""Tests Notices API Views"""
import json

from django.test import TestCase
from edx_toggles.toggles.testutils import override_waffle_flag
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from notices.data import AcknowledgmentResponseTypes
from notices.models import AcknowledgedNotice
from notices.rest_api.v1.views import AcknowledgeNotice, ListUnacknowledgedNotices
from notices.toggles import ENABLE_NOTICES
from test_utils.factories import AcknowledgedNoticeFactory, NoticeFactory, UserFactory


class ListUnacknowledgedNoticesTests(TestCase):
    """Tests for the ListUnacknowledgedNotices view"""

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.request_factory = APIRequestFactory()
        self.view = ListUnacknowledgedNotices.as_view()

    @override_waffle_flag(ENABLE_NOTICES, active=True)
    def test_no_notices(self):
        request = self.request_factory.get("/api/v1/unacknowledged/")
        force_authenticate(request, user=self.user)
        response = self.view(request)
        # reformat response from list of OrderedDicts to list of Dict
        results = response.data["results"]
        assert results == []

    @override_waffle_flag(ENABLE_NOTICES, active=True)
    def test_single_notice(self):
        notice_1 = NoticeFactory(active=True)
        request = self.request_factory.get("/api/v1/unacknowledged/")
        force_authenticate(request, user=self.user)
        response = self.view(request)
        results = response.data["results"]
        assert len(results) == 1
        assert results == [reverse("notices:notice-detail", kwargs={"pk": notice_1.id}, request=request)]

    @override_waffle_flag(ENABLE_NOTICES, active=True)
    def test_multiple_notices(self):
        notice_1 = NoticeFactory(active=True)
        notice_2 = NoticeFactory(active=True)
        notice_3 = NoticeFactory(active=True)
        request = self.request_factory.get("/api/v1/unacknowledged/")
        force_authenticate(request, user=self.user)
        response = self.view(request)
        results = response.data["results"]
        assert len(results) == 3
        # cast to set to avoid ordering issues
        assert set(results) == set(
            [
                reverse("notices:notice-detail", kwargs={"pk": notice_1.id}, request=request),
                reverse("notices:notice-detail", kwargs={"pk": notice_2.id}, request=request),
                reverse("notices:notice-detail", kwargs={"pk": notice_3.id}, request=request),
            ]
        )

    @override_waffle_flag(ENABLE_NOTICES, active=True)
    def test_some_acknowledged(self):
        """
        Test that when a user response to some (but not all) the API only returns the unacknowledged ones

        Also tests that response type is not taken into account when choosing to display
        """
        notice_1 = NoticeFactory(active=True)
        notice_2 = NoticeFactory(active=True)
        notice_3 = NoticeFactory(active=True)
        # acknowledge the middle notice
        AcknowledgedNoticeFactory(user=self.user, notice=notice_2, response_type=AcknowledgmentResponseTypes.CONFIRMED)
        AcknowledgedNoticeFactory(user=self.user, notice=notice_1, response_type=AcknowledgmentResponseTypes.DISMISSED)
        request = self.request_factory.get("/api/v1/unacknowledged/")
        force_authenticate(request, user=self.user)
        response = self.view(request)
        results = response.data["results"]
        assert len(results) == 1
        assert results == [
            reverse("notices:notice-detail", kwargs={"pk": notice_3.id}, request=request),
        ]


class AcknowledgeNoticeTests(TestCase):
    """Tests for the AcknowledgeNotice view"""

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.request_factory = APIRequestFactory()
        self.view = AcknowledgeNotice.as_view()

    def test_valid_acknowledgement(self):
        notice_1 = NoticeFactory(active=True)
        request = self.request_factory.post(
            "/api/v1/acknowledge/",
            {"notice_id": notice_1.id, "acknowledgment_type": AcknowledgmentResponseTypes.CONFIRMED.value},
        )
        force_authenticate(request, user=self.user)
        response = self.view(request)
        assert response.data is None
        assert response.status_code == 204
        # Verify the acknowledgment made it to the DB
        assert AcknowledgedNotice.objects.filter(user=self.user, notice=notice_1).first() is not None

    def test_no_notice_data(self):
        NoticeFactory(active=True)
        request = self.request_factory.post("/api/v1/acknowledge/")
        force_authenticate(request, user=self.user)
        response = self.view(request)

        assert response.status_code == 400
        json_response_data = json.loads(json.dumps(response.data))
        assert json_response_data == {"notice_id": "notice_id field required"}

    def test_invalid_notice_data(self):
        notice_1 = NoticeFactory(active=True)
        request = self.request_factory.post(
            "/api/v1/acknowledge/",
            {"notice_id": notice_1.id + 1, "acknowledgment_type": AcknowledgmentResponseTypes.CONFIRMED.value},
        )
        force_authenticate(request, user=self.user)
        response = self.view(request)

        assert response.status_code == 400
        json_response_data = json.loads(json.dumps(response.data))
        assert json_response_data == {"notice_id": "notice_id field does not match an existing active notice"}

    def test_invalid_response_type(self):
        INVALID_CHOICE = "invalid_CHOICE"
        notice_1 = NoticeFactory(active=True)
        request = self.request_factory.post(
            "/api/v1/acknowledge/", {"notice_id": notice_1.id, "acknowledgment_type": INVALID_CHOICE}
        )
        force_authenticate(request, user=self.user)
        response = self.view(request)
        assert response.status_code == 400
        json_response_data = json.loads(json.dumps(response.data))
        acknowledgment_type_values = [e.value for e in AcknowledgmentResponseTypes]
        assert json_response_data == {
            "acknowledgment_type": f"acknowledgment_type must be one of the following: {acknowledgment_type_values}"
        }

    def test_unauthenticated_call(self):
        notice_1 = NoticeFactory(active=True)
        request = self.request_factory.post(
            "/api/v1/acknowledge/",
            {"notice_id": notice_1.id + 1, "acknowledgment_type": AcknowledgmentResponseTypes.CONFIRMED},
        )
        response = self.view(request)
        assert response.status_code == 401
