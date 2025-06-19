"""
URL configuration for hrms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('dashboard_redirect/', views.dashboard_redirect, name='dashboard_redirect'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('hr-dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employees/', views.employee_list, name='employee_list'),
    path('payroll/', views.payroll_view, name='payroll'),
    path('add-payroll/', views.add_payroll, name='add_payroll'),
    path('announcements/', views.make_announcement, name='announcements'),
    path('list-announcements/', views.announcement_list, name='announcement_list'),
    path('attendance-report/', views.attendance_report, name='attendance_report'),
    path('leaves/', views.leave_requests, name='leave_requests'),
    path('apply-leave/', views.apply_leave, name='apply_leave'),
    path('profile/', views.profile, name='profile'),
    path('attendance/', views.my_attendance, name='attendance'),
    path('toggle-attendance/', views.toggle_attendance, name='toggle_attendance'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('leaves/<int:leave_id>/reject/', views.reject_leave, name='reject_leave'),
    path('leave/<int:leave_id>/approve/', views.approve_leave, name='approve_leave'),
    path('employees/<int:employee_id>/edit/', views.edit_employee, name='edit_employee'),  #  Add this
    path('employees/<int:employee_id>/delete/', views.delete_employee, name='delete_employee'), 
    path('employees/<int:employee_id>/delete/', views.delete_employee, name='delete_employee'), 
    path('payroll/<int:payroll_id>/generate-payslip/', views.generate_payslip, name='generate_payslip'), 
    path('payroll/<int:payroll_id>/mark-as-paid/', views.mark_payroll_as_paid, name='mark_payroll_as_paid'), 

]
