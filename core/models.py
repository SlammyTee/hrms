from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    join_date = models.DateField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    is_hr = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name()

class LeaveRequest(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    applied_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.status}"
    
class AttendanceDay(models.Model):
    date = models.DateField(unique=True)
    is_open = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date} - {'Open' if self.is_open else 'Closed'}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.username} - {self.date} - {self.status}"


class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Calculate the net pay before saving the model
        self.net_pay = self.salary + self.bonus - self.deductions
        super(Payroll, self).save(*args, **kwargs)  # Save the model
    
    def __str__(self):
        return f"{self.employee.user.username} - {self.month}/{self.year}"

    

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title