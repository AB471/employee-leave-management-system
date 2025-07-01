from datetime import date
from . models import Leave

def get_leave_report(employee):
    today = date.today()

    current_month = today.month
    current_year = today.year

    if 1 <= current_month <= 3:
        quarter_start = date(current_year, 1, 1)
        quarter_end = date(current_year, 3, 31)
    elif 4 <= current_month <= 6:
        quarter_start = date(current_year, 4, 1)
        quarter_end = date(current_year, 6, 30)
    elif 7 <= current_month <= 9:
        quarter_start = date(current_year, 7, 1)
        quarter_end = date(current_year, 9, 30)
    else:
        quarter_start = date(current_year, 10, 1)
        quarter_end = date(current_year, 12, 31)

    fy_start = date(current_year if current_month >= 4 else current_year - 1, 4, 1)

    leaves = Leave.objects.filter(employee=employee).order_by('start_date')

    def get_days(leaves_queryset, leave_type):
        return sum(
            (l.end_date - l.start_date).days + 1
            for l in leaves_queryset.filter(leave_type=leave_type)
        )
    
    month_leaves = leaves.filter(start_date__month=today.month, start_date__year=today.year)
    quarter_leaves = leaves.filter(start_date__gte=quarter_start, start_date__lte=quarter_end)
    fy_leaves = leaves.filter(start_date__gte=fy_start)
    

    return {
        'all_leaves': leaves,
        'employee': employee,
        'month_leaves': month_leaves,
        'quarter_leaves': quarter_leaves,
        'fy_leaves': fy_leaves,
        'month_days': sum((l.end_date - l.start_date).days + 1 for l in month_leaves),
        'quarter_days': sum((l.end_date - l.start_date).days + 1 for l in quarter_leaves),
        'fy_days': sum((l.end_date - l.start_date).days + 1 for l in fy_leaves),
        'cs_taken': get_days(leaves, 'CS'),
        'e_taken': get_days(leaves, 'E'),
        'cs_remaining': employee.total_cs_leave - get_days(leaves, 'CS'),
        'e_remaining': employee.total_e_leave - get_days(leaves, 'E'),
    }