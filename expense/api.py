
import calendar
from datetime import date

from expense.views import _build_monthly_summary

from .models import DailyExpense

from django.http import JsonResponse


def monthly_summary_api(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    return _build_monthly_summary(request, year, month)