from django.contrib import admin

from core.models import Attendance, Employee, LeaveRequest, Payroll

# Register your models here.
admin.site.register(Employee)
admin.site.register(LeaveRequest)
admin.site.register(Attendance)
admin.site.register(Payroll)



