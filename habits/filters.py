import django_filters

from .models import Habit


class HabitFilter(django_filters.FilterSet):
    action = django_filters.CharFilter(field_name="action", lookup_expr="icontains")
    place = django_filters.CharFilter(field_name="place", lookup_expr="icontains")
    is_public = django_filters.BooleanFilter()
    is_pleasant = django_filters.BooleanFilter()
    time_after = django_filters.TimeFilter(field_name="time", lookup_expr="gte")
    time_before = django_filters.TimeFilter(field_name="time", lookup_expr="lte")
    periodicity = django_filters.NumberFilter()

    class Meta:
        model = Habit
        fields = ["is_public", "is_pleasant", "periodicity"]
