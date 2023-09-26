"""
Database models for notices.
"""
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from notices.data import AcknowledgmentResponseTypes


User = get_user_model()


class Notice(TimeStampedModel):
    """
    Model to house a notice's content and additional data.

    .. no_pii:
    """

    name = models.CharField(max_length=128, help_text="Name for the notice that needs to be acknowledged")
    active = models.BooleanField()
    history = HistoricalRecords(app="notices")
    head_content = models.TextField(
        default="",
        help_text=(
            "HTML content to be included in the <head> block. Should contain all javascript / styles. "
            "Shared for all translated templates"
        ),
    )
    launch_date = models.DateTimeField(
        default=timezone.now, help_text="All users created after this date will not be show the notice"
    )

    class Meta:
        """Model metadata."""

        app_label = "notices"

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        return f"<Notice {self.name}>"


class TranslatedNoticeContent(TimeStampedModel):
    """
    A model to house a translated html notice and the language it's translated into.

    A Notice may have multiple TranslatedNoticeContents, with no more than one for each
    language.

    .. no_pii:
    """

    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name="translated_notice_content")
    language_code = models.CharField(
        max_length=10,
        help_text=(
            "The language code (e.g. en, es-419). Must be a released language in DarkLang if DarkLang is enabled."
        ),
    )
    html_content = models.TextField(help_text="HTML content to be included in a notice view's <body> block.")
    history = HistoricalRecords(app="notices")

    class Meta:
        """Model metadata."""

        app_label = "notices"
        unique_together = ["notice", "language_code"]


class AcknowledgedNotice(TimeStampedModel):
    """
    Model to track if and when a user has acknowledged the notice.

    Lack of an entry denotes a user has not acknowledged the notice.

    .. no_pii:
    """

    RESPONSE_TYPE_CHOICES = [
        (AcknowledgmentResponseTypes.CONFIRMED.value, "Confirmed"),
        (AcknowledgmentResponseTypes.DISMISSED.value, "Dismissed"),
    ]
    FINAL_RESPONSE_TYPE = AcknowledgmentResponseTypes.CONFIRMED

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notice_acknowledgments")
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name="acknowledgments")
    response_type = models.CharField(max_length=32, choices=RESPONSE_TYPE_CHOICES)
    snooze_count = models.IntegerField(default=0)
    history = HistoricalRecords(app="notices")

    class Meta:
        """Model metadata."""

        app_label = "notices"

    def save(self, *args, **kwargs):
        """
        Overridden so that if a user has confirmed a notice,they can't redact that confirmation.
        """
        try:
            old_instance = AcknowledgedNotice.objects.get(pk=self.pk)
        except AcknowledgedNotice.DoesNotExist:
            pass
        else:
            if old_instance.response_type == self.FINAL_RESPONSE_TYPE.value:
                self.response_type = self.FINAL_RESPONSE_TYPE
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        return f"<AcknowledgedNotice by user {self.user.id} for notice {self.notice.name}>"
