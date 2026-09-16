import calendar
from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from .models import Item
from .forms import ItemForm


def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Item added successfully!")
            return redirect('expense:add_item')
    else:
        form = ItemForm()

    return render(request, 'expense/add_item.html', {'form': form})


def monthly_list_page(request):
    return render(request, 'expense/monthly_list.html')


def monthly_summary_api(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    items_qs = (
        Item.objects
        .filter(date__year=year, date__month=month)
        .annotate(line_total=ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField()))
        .values('date')
        .annotate(total=Sum('line_total'), count=Count('id'))
        .order_by('date')
    )

    day_summary = {item['date'].day: item for item in items_qs}
    days_in_month = calendar.monthrange(year, month)[1]

    data = []
    for day in range(1, days_in_month + 1):
        summary = day_summary.get(day)
        data.append({
            'day': day,
            'date': f"{year}-{month:02d}-{day:02d}",
            'total': float(summary['total']) if summary else 0,
            'count': summary['count'] if summary else 0,
        })
    return JsonResponse(data, safe=False)


def day_detail_api(request, year, month, day):
    items = Item.objects.filter(date__year=year, date__month=month, date__day=day)
    data = [
        {
            'name': item.name,
            'price': float(item.price),
            'quantity': float(item.quantity),
            'total': float(item.total),
        }
        for item in items
    ]
    return JsonResponse(data, safe=False)