import calendar
from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from .models import Item
from .forms import ItemForm
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
                    'item': {
                        'id': item.id,
                        'name': item.name,
                        'price': float(item.price),
                        'quantity': float(item.quantity),
                        'location': item.location,
                        'total': float(item.total),
                        'description': item.description,
                        'date': item.date.strftime('%Y-%m-%d'),
                    }
                })
            messages.success(request, "Item added successfully!")
            return redirect('expense:add_item')
    else:
        form = ItemForm()
    today_items = Item.objects.filter(
        date=date.today()
    ).order_by('-created_at')    

    return render(request, 'expense/add_item.html', {
        'form': form,
        'today_items': today_items,
        'today_items_data': [serialize_item(item) for item in today_items],
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

            'item': {
                'id': item.id,
                'name': item.name,
                'price': float(item.price),
                'quantity': float(item.quantity),
                'location': item.location or '',
                'total': float(item.price * item.quantity),
                'date': item.date.strftime('%Y-%m-%d'),
                'description': item.description or '',
            }
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