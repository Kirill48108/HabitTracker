from typing import Any, Dict

from rest_framework.exceptions import ValidationError


class BaseValidator:
    def __call__(self, attrs: Dict[str, Any]) -> None:
        raise NotImplementedError

    @classmethod
    def __fields__(cls):
        return getattr(cls, "fields", None)


class MutuallyExclusiveRewardRelated(BaseValidator):
    fields = ("reward", "related_habit")

    def __call__(self, attrs):
        reward = attrs.get("reward") or ""
        related = attrs.get("related_habit")
        if reward.strip() and related:
            raise ValidationError(
                "Нельзя одновременно указывать вознаграждение и связанную привычку."
            )


class MaxDurationValidator(BaseValidator):
    fields = ("duration",)

    def __call__(self, attrs):
        duration = attrs.get("duration")
        if duration is not None and duration > 120:
            raise ValidationError("Время выполнения должно быть не больше 120 секунд.")


class RelatedMustBePleasant(BaseValidator):
    fields = ("related_habit",)

    def __call__(self, attrs):
        related = attrs.get("related_habit")
        if related and not related.is_pleasant:
            raise ValidationError(
                "В связанные привычки могут попадать только привычки с признаком приятной привычки."
            )


class PleasantCannotHaveRewardOrRelated(BaseValidator):
    fields = ("is_pleasant", "reward", "related_habit")

    def __call__(self, attrs):
        is_pleasant = attrs.get("is_pleasant")
        reward = (attrs.get("reward") or "").strip()
        related = attrs.get("related_habit")
        if is_pleasant and (reward or related):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )


class PeriodicityWithinWeek(BaseValidator):
    fields = ("periodicity",)

    def __call__(self, attrs):
        p = attrs.get("periodicity")
        if p is None:
            return
        if p < 1 or p > 7:
            # Сообщение приведено к ожидаемой в тестах строке (регистр и текст)
            raise ValidationError("периодичность должна быть от 1 до 7")
