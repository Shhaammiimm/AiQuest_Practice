import calendar
from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.utils import timezone
from .models import Borrow, Item, Lend
from .forms import ItemForm, LendForm, BorrowForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def home_page(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    line_total = ExpressionWrapper(
        F('price') * F('quantity'),
        output_field=DecimalField(max_digits=18, decimal_places=2),
    )
    items = Item.objects.filter(user=request.user).annotate(line_total=line_total)

    month_items = items.filter(date__range=(month_start, today))
    year_items = items.filter(date__range=(year_start, today))
    month_summary = month_items.aggregate(total=Sum('line_total'), count=Count('id'))
    year_summary = year_items.aggregate(total=Sum('line_total'), count=Count('id'))
    today_summary = items.filter(date=today).aggregate(total=Sum('line_total'), count=Count('id'))
    month_spend_days = month_items.values('date').distinct().count()

    trend_start = (month_start - timedelta(days=1)).replace(day=1)
    for _ in range(4):
        trend_start = (trend_start - timedelta(days=1)).replace(day=1)
    trend_rows = (
        items.filter(date__range=(trend_start, today))
        .values('date__year', 'date__month')
        .annotate(total=Sum('line_total'))
    )
    trend_totals = {
        (row['date__year'], row['date__month']): row['total'] or Decimal('0.00')
        for row in trend_rows
    }
    months = []
    cursor = trend_start
    for _ in range(6):
        total = trend_totals.get((cursor.year, cursor.month), Decimal('0.00'))
        months.append({
            'label': cursor.strftime('%b'),
            'year': cursor.year,
            'total': total,
            'is_current': cursor.year == today.year and cursor.month == today.month,
        })
        cursor = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
    peak = max((month['total'] for month in months), default=Decimal('0.00'))
    for month in months:
        month['bar_height'] = max(5, int(month['total'] / peak * 100)) if peak else 5

    largest_item = year_items.order_by('-line_total', '-date').first()
    return render(request, 'expense/home.html', {
        'today': today,
        'month_total': month_summary['total'] or Decimal('0.00'),
        'month_count': month_summary['count'],
        'month_spend_days': month_spend_days,
        'month_daily_average': (month_summary['total'] or Decimal('0.00')) / month_spend_days if month_spend_days else Decimal('0.00'),
        'year_total': year_summary['total'] or Decimal('0.00'),
        'year_count': year_summary['count'],
        'year_daily_average': (year_summary['total'] or Decimal('0.00')) / today.timetuple().tm_yday,
        'today_total': today_summary['total'] or Decimal('0.00'),
        'today_count': today_summary['count'],
        'largest_item': largest_item,
        'monthly_trend': months,
        'recent_items': items.order_by('-date', '-created_at')[:6],
    })

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

@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
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
        user=request.user,
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

    item = get_object_or_404(Item, id=item_id, user=request.user)

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

    item = get_object_or_404(Item, id=item_id, user=request.user)

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
        .filter(user=request.user, date__year=year, date__month=month)
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
        user=request.user,
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


@login_required
def add_lend(request):
    if request.method == 'POST':
        form = LendForm(request.POST)
        if form.is_valid():
            lend = form.save(commit=False)
            lend.user = request.user
            lend.save()
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
            return redirect('expense:lend_list')
    else:
        form = LendForm()
    return render(request, 'expense/add.html', {'form': form})


@login_required
def lend_list_page(request):
    lends = Lend.objects.filter(user=request.user)
    total_lend_amount = lends.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'expense/lend_list.html', {
        'lends': lends,
        'total_lend_amount': total_lend_amount,
    })


def edit_lend(request, lend_id):
    lend = get_object_or_404(Lend, pk=lend_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = LendForm(request.POST, instance=lend)
        if form.is_valid():
            lend = form.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'record': {
                        'id': lend.id,
                        'name': lend.name,
                        'amount': str(lend.amount),
                        'date': lend.lend_date.strftime('%Y-%m-%d'),
                        'return_date': lend.return_date.strftime('%Y-%m-%d') if lend.return_date else '',
                        'description': lend.description or '',
                    },
                })
            messages.success(request, 'Lend record updated successfully!')
            return redirect('expense:lend_list')
        if is_ajax:
            return JsonResponse({'success': False, 'errors': form.errors.get_json_data()}, status=400)
    else:
        form = LendForm(instance=lend)
    return render(request, 'expense/add.html', {'form': form, 'is_edit': True})


@require_POST
def delete_lend(request, lend_id):
    lend = get_object_or_404(Lend, pk=lend_id, user=request.user)
    lend.delete()
    messages.success(request, 'Lend record deleted successfully!')
    return redirect('expense:lend_list')

    
@login_required     
def add_borrow(request):
    if request.method == 'POST':
        form = BorrowForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            borrow.user = request.user
            borrow.save()
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Borrow record added successfully!',
                    'borrow': {
                        'id': borrow.id,
                        'name': borrow.name,
                        'amount': float(borrow.amount),
                        'borrow_date': borrow.borrow_date.strftime('%Y-%m-%d'),
                        'return_date': borrow.return_date.strftime('%Y-%m-%d') if borrow.return_date else None,
                        'description': borrow.description or '',
                    }
                })
            messages.success(request, "Borrow record added successfully!")
            return redirect('expense:borrow_list')
    else:
        form = BorrowForm()
    return render(request, 'expense/add_borrow.html', {'form': form})

@login_required
def borrow_list_page(request):
    borrows = Borrow.objects.filter(user=request.user)
    total_borrow_amount = borrows.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'expense/borrow_list.html', {
        'borrows': borrows,
        'total_borrow_amount': total_borrow_amount,
    })


def edit_borrow(request, borrow_id):
    borrow = get_object_or_404(Borrow, pk=borrow_id, user=request.user)
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        form = BorrowForm(request.POST, instance=borrow)
        if form.is_valid():
            borrow = form.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'record': {
                        'id': borrow.id,
                        'name': borrow.name,
                        'amount': str(borrow.amount),
                        'date': borrow.borrow_date.strftime('%Y-%m-%d'),
                        'return_date': borrow.return_date.strftime('%Y-%m-%d') if borrow.return_date else '',
                        'description': borrow.description or '',
                    },
                })
            messages.success(request, 'Borrow record updated successfully!')
            return redirect('expense:borrow_list')
        if is_ajax:
            return JsonResponse({'success': False, 'errors': form.errors.get_json_data()}, status=400)
    else:
        form = BorrowForm(instance=borrow)
    return render(request, 'expense/add_borrow.html', {'form': form, 'is_edit': True})


@require_POST
def delete_borrow(request, borrow_id):
    borrow = get_object_or_404(Borrow, pk=borrow_id, user=request.user)
    borrow.delete()
    messages.success(request, 'Borrow record deleted successfully!')
    return redirect('expense:borrow_list')