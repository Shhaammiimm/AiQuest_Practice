import calendar
from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.utils import timezone
from .models import Item, Lend
from .forms import ItemForm, LendForm
from django.shortcuts import get_object_or_404


def serialize_item(item):
    return {
        'id': item.id,
        'name': item.name,
        'price': float(item.price),
        'quantity': float(item.quantity),
        'location': item.location or '',
        'date': item.date.strftime('%Y-%m-%d'),
        'description': item.description or '',
        'total': float(item.total),
    }


def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Item added successfully!',
                    'item': serialize_item(item),
                })
            messages.success(request, "Item added successfully!")
            return redirect('expense:add_item')
    else:
        form = ItemForm()
    recent_items = Item.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-created_at')

    return render(request, 'expense/add_item.html', {
        'form': form,
        'recent_items': recent_items,
        'recent_items_data': [serialize_item(item) for item in recent_items],
    })

def edit_item(request, item_id):

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method.'
        }, status=405)

    item = get_object_or_404(Item, id=item_id)

    form = ItemForm(
        request.POST,
        instance=item
    )

    if form.is_valid():

        item = form.save()

        return JsonResponse({
            'success': True,
            'message': 'Expense updated successfully!',

            'item': serialize_item(item),
        })

    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)

def delete_item(request, item_id):

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method.'
        }, status=405)

    item = get_object_or_404(Item, id=item_id)

    item.delete()

    return JsonResponse({
        'success': True,
        'message': 'Expense deleted successfully!'
    })


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

    items = Item.objects.filter(
        date__year=year,
        date__month=month,
        date__day=day
    )

    data = [
        {
            'id': item.id,
            'name': item.name,
            'price': float(item.price),
            'quantity': float(item.quantity),
            'location': item.location or '',
            'description': item.description or '',
            'total': float(item.total),
            'date': item.date.strftime('%Y-%m-%d'),
        }
        for item in items
    ]

    return JsonResponse(data, safe=False)


def add_lend(request):
    if request.method == 'POST':
        form = LendForm(request.POST)
        if form.is_valid():
            lend = form.save()
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Lend record added successfully!',
                    'lend': {
                        'id': lend.id,
                        'name': lend.name,
                        'amount': float(lend.amount),
                        'lend_date': lend.lend_date.strftime('%Y-%m-%d'),
                        'return_date': lend.return_date.strftime('%Y-%m-%d') if lend.return_date else None,
                        'description': lend.description or '',
                    }
                })
            messages.success(request, "Lend record added successfully!")
            return redirect('expense:add_lend')
    else:
        form = LendForm()
    return render(request, 'expense/add.html', {'form': form})


def lend_list_page(request):
    lends = Lend.objects.all()
    total_lend_amount = lends.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'expense/lend_list.html', {
        'lends': lends,
        'total_lend_amount': total_lend_amount,
    })