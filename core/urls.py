from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('profile/', views.change_pin, name='profile'),
    path('admin_employee/add/', views.admin_employee_add_edit, name='admin_employee_add'),
    path('admin_employee/edit/<int:emp_id>/', views.admin_employee_add_edit, name='admin_employee_edit'),
    path('admin_employee/toggle-status/<int:emp_id>/', views.admin_toggle_status, name='admin_toggle_status'),
    path('admin_employee/reset-pin/<int:emp_id>/', views.admin_employee_pin_reset, name='admin_employee_reset_pin'),
    path('admin_employee/<int:emp_id>/report/', views.admin_employee_leave_report, name='admin_employee_leave_report'),
    path('employee/apply-leave/', views.apply_leave, name='apply_leave'),
    path('employee/leave-history/', views.leave_history_report, name='leave_history'),
]
