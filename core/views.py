from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from datetime import date
from . forms import LoginForm, ChangePinForm, EmployeeForm, LeaveForm
from . models import Employee, Leave
from .utils import get_leave_report

def login_view(request):
    if not Employee.objects.filter(phone='9999999999').exists():
        Employee.objects.create(
            first_name='Admin',
            last_name='User',
            phone='9999999999',
            pin='1234',
            role='Admin',
            status='Active',
            total_cs_leave=0,
            total_e_leave=0
        )

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            pin = form.cleaned_data['pin']
            try:
                user = Employee.objects.get(phone=phone, pin=pin, status='Active')
                request.session['user_id'] = user.id
                request.session['role'] = user.role

                messages.success(request, f'Welcome, {user.first_name}!')

                if user.role == 'Admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('employee_dashboard')
            except Employee.DoesNotExist:
                messages.error(request, 'Invalid Credentials or Inactive User')
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form':form})

def logout(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

def admin_dashboard(request):
    if request.session.get('role') != 'Admin':
        return redirect('login')

    admin = Employee.objects.get(id=request.session['user_id'])

    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status','').strip()
    leave_filter = request.GET.get('leave_filter', '').strip()

    employees = Employee.objects.filter(role='Employee')

    if search:
        employees = employees.filter(
            Q(first_name__icontains=search)  |
            Q(last_name__icontains=search)  |
            Q(phone__icontains=search)
        )
    if status_filter:
        employees = employees.filter(status=status_filter)

    if not employees.exists():
        return render(request, 'core/admin_dashboard.html', {
            'admin': admin,
            'employee_data': [],
            'search': search,
            'status_filter': status_filter,
            'no_match': True
        })

    employee_data = []

    for emp in employees:
        report = get_leave_report(emp)

        if leave_filter == 'month' and not report['month_leaves']:
            continue
        elif leave_filter == 'quarter' and not report['quarter_leaves']:
            continue
        elif leave_filter == 'year' and not report['fy_leaves']:
            continue

        employee_data.append({
            'emp':emp,
            'month': report['month_days'],
            'quarter': report['quarter_days'],
            'fy': report['fy_days'],
            'cs_taken': report['cs_taken'],
            'e_taken': report['e_taken'],
            'cs_remaining': report['cs_remaining'],
            'e_remaining': report['e_remaining'],
            'leave_filter': leave_filter,
        })

    employee_data.sort(key=lambda x:x['emp'].first_name.lower())

    return render(request, 'core/admin_dashboard.html', {
        'admin':admin,
        'employee_data':employee_data,
        'search': search,
        'status_filter': status_filter,
        'no_match': False
        })


def admin_employee_leave_report(request, emp_id):
    if request.session.get('role') != 'Admin':
        return redirect('login')
    
    employee = Employee.objects.get(id=emp_id)
    leaves_data = get_leave_report(employee)

    return render(request, 'core/admin_employee_report.html',{
        'employee': employee,
        **leaves_data
    })


def employee_dashboard(request):
    if request.session.get('role') != 'Employee':
        return redirect('login')
    
    employee = Employee.objects.get(id=request.session['user_id'])
    leave_data = get_leave_report(employee)

    return render(request, 'core/employee_dashboard.html', {
        'employee':employee,
        **leave_data
        })


def apply_leave(request):
    if request.session.get('role') != 'Employee':
        return redirect('login')
    
    employee = Employee.objects.get(id=request.session['user_id'])

    if request.method == "POST":
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            num_days = (leave.end_date - leave.start_date).days + 1

        if leave.start_date > leave.end_date:
            messages.error(request, 'End date cannot be of before start date.')
        else:
            report = get_leave_report(employee)

            if leave.leave_type == 'CS' and report['cs_taken'] + num_days > employee.total_cs_leave:
                messages.error(request, 'Insufficient CS leave balance.')
            elif leave.leave_type == 'E' and report['e_taken'] + num_days > employee.total_e_leave:
                messages.error(request, ' Insufficient E leave balance.')
            else:
                leave.save()
                messages.success(request, 'Leave applied successfully!')
                return redirect('employee_dashboard')
    else:
        form = LeaveForm()

    return render(request, 'core/apply_leave.html', {'form':form})


def leave_history_report(request):
    if request.session.get('role') != 'Employee':
        return redirect('login')
    
    employee = Employee.objects.get(id=request.session['user_id'])
    leave_data = get_leave_report(employee)

    return render(request, 'core/leave_history.html', {
        'employee': employee,
        **leave_data
    })


def change_pin(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = Employee.objects.get(id=request.session['user_id'])
    role = request.session.get('role')

    if request.method == 'POST':
        form = ChangePinForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['current_pin'] != user.pin:
                form.add_error('current_pin', 'Incorrect Current Pin')
            else:
                user.pin = form.cleaned_data['new_pin']
                user.save()
                messages.success(request, 'Pin changed successfully!')
                if role == 'Admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('employee_dashboard')
    else:
        form = ChangePinForm()
    
    return render(request, 'core/profile.html', {
        'user':user,
        'form':form,
        'role':role
    })


def admin_employee_add_edit(request, emp_id=None):
    if request.session.get('role') != 'Admin':
        return redirect('login')
    
    employee = Employee.objects.get(id=emp_id) if emp_id else None

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            emp = form.save(commit=False)
            if not emp_id:
                emp.pin = '0000'
            emp.save()
            messages.success(request, 'Employee saved sucessfully.')
            return redirect('admin_dashboard')
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'core/admin_employee_form.html', {
        'form':form,
        'edit':bool(emp_id)
    })

def admin_toggle_status(request, emp_id):
    if request.session.get('role') != 'Admin':
        return redirect('login')
    
    emp = Employee.objects.get(id=emp_id)
    emp.status = 'Inactive' if emp.status == 'Active' else 'Active'
    emp.save()
    messages.success(request, f"{emp.first_name}'s status updated to {emp.status}.")
    return redirect('admin_dashboard')

def admin_employee_pin_reset(request, emp_id):
    if request.session.get('role') != 'Admin':
        return redirect('login')
    
    emp = Employee.objects.get(id=emp_id)
    emp.pin = '0000'
    emp.save()
    messages.success(request, f"{emp.first_name}'s PIN reset to 0000.")
    return redirect('admin_dashboard')

