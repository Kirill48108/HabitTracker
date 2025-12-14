from django.conf import settings
from django.db import models


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits"
    )
    place = models.CharField(max_length=255)
    time = models.TimeField()
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)
    related_habit = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="related_to",
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1, help_text="Периодичность в днях (1-7)"
    )
    reward = models.CharField(max_length=255, blank=True, default="")
    duration = models.PositiveSmallIntegerField(
        default=60, help_text="Длительность в секундах (<=120)"
    )
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.action} @ {self.time} ({'pleasant' if self.is_pleasant else 'useful'})"
