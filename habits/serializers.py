from rest_framework import serializers

from .models import Habit
from .validators import (
    MaxDurationValidator,
    MutuallyExclusiveRewardRelated,
    PeriodicityWithinWeek,
    PleasantCannotHaveRewardOrRelated,
    RelatedMustBePleasant,
)


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "created_at",
        ]
        read_only_fields = ("id", "user", "created_at")
        validators = [
            MutuallyExclusiveRewardRelated(),
            MaxDurationValidator(),
            RelatedMustBePleasant(),
            PleasantCannotHaveRewardOrRelated(),
            PeriodicityWithinWeek(),
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
