from datetime import date, datetime
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, Coalesce
from django.shortcuts import render

from expenses import models


def index(request):
    x = models.Expense.objects \
        .annotate(month=TruncMonth('expense_date')) \
        .values('month') \
        .annotate(value=Count('id')) \
        .order_by('month') \
        .values('month', 'value').all()
    y = [x.filter(month=date(datetime.now().year, i, 1)) for i in range(1, 13)]
    z = [0 if y[i].count() == 0 else y[i].get()['value'] for i in range(0, 12)]

    x1 = models.Expense.objects \
        .annotate(month=TruncMonth('expense_date')) \
        .values('month') \
        .annotate(value=Sum('expensepart__amount')) \
        .order_by('month') \
        .values('month', 'value').all()
    y1 = [x1.filter(month=date(datetime.now().year, i, 1)) for i in range(1, 13)]
    z1 = [0 if y1[i].count() == 0 else float(y1[i].get()['value']) for i in range(0, 12)]

    return render(request, 'stats/index.html', {
        'year': models.Expense.objects.filter(reimbursement__isnull=False).aggregate(year=Coalesce(Sum('expensepart__amount'), 0))['year'],
        'highscore': models.Profile.objects.filter(expense__reimbursement__isnull=False).annotate(
            total_amount=Sum('expense__expensepart__amount')
        ).filter(total_amount__gte=0).order_by('-total_amount')[:10],
        'month_count': z,
        'month_sum': z1
    })
