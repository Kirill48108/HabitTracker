from rest_framework import serializers

from .models import TelegramProfile


class TelegramProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramProfile
        fields = ("id", "chat_id")
        read_only_fields = ("id",)
        # Отключаем UniqueValidator поля chat_id, чтобы разрешить upsert через POST
        extra_kwargs = {
            "chat_id": {"validators": []},
        }

    def create(self, validated_data):
        user = self.context["request"].user
        obj, _ = TelegramProfile.objects.update_or_create(user=user, defaults=validated_data)
        return obj
