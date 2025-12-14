from celery import shared_task
from django.utils import timezone

from telegram_app.services import send_telegram_message

from .models import Habit


def _is_due_today(habit):
    # Выполняем каждые habit.periodicity дней, начиная с даты создания.
    # Если сегодня - created_at.date() + k*periodicity
    created = habit.created_at.date()
    today = timezone.localdate()
    delta = (today - created).days
    return delta >= 0 and (delta % habit.periodicity == 0)


@shared_task
def send_habit_reminders():
    now = timezone.localtime()
    hhmm = now.strftime("%H:%M")
    habits = Habit.objects.filter(time__hour=now.hour, time__minute=now.minute)
    for h in habits:
        if not _is_due_today(h):
            continue
        profile = getattr(h.user, "telegram_profile", None)
        if not profile:
            continue
        text = f"Напоминание: {h.action} в {h.place} сейчас ({hhmm})."
        send_telegram_message(profile.chat_id, text)
