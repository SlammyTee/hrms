import random
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from weasyprint import HTML
from .models import Announcement, AttendanceDay, Employee, LeaveRequest, Attendance, Payroll
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import AnnouncementForm, LeaveForm, EmployeeForm, PayrollForm, UserRegisterForm
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password


@login_required
def dashboard_redirect(request):
    try:
        employee = Employee.objects.get(user=request.user)
        if employee.is_hr:
            return redirect('hr_dashboard')
        else:
            return redirect('employee_dashboard')
    except Employee.DoesNotExist:
        return redirect('login')


@login_required
def hr_dashboard(request):
    today = timezone.now().date()
    attendance_day, _ = AttendanceDay.objects.get_or_create(date=today)

    emp_count = Employee.objects.count()
    pending_leaves = LeaveRequest.objects.filter(status='Pending').count()
    approved_leaves = LeaveRequest.objects.filter(
        status='Approved', start_date__month=today.month).count()

    context = {
        'emp_count': emp_count,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'attendance_day': attendance_day,
    }

    return render(request, 'core/hr_dashboard.html', context)


@login_required
def toggle_attendance(request):
    today = timezone.now().date()
    attendance_day, _ = AttendanceDay.objects.get_or_create(date=today)
    attendance_day.is_open = not attendance_day.is_open
    attendance_day.save()
    return redirect('hr_dashboard')


@login_required
def employee_dashboard(request):
    today = timezone.now().date()
    attendance_day = AttendanceDay.objects.filter(date=today).first()
    has_marked_attendance = Attendance.objects.filter(employee=request.user, date=today).exists()
    leaves = LeaveRequest.objects.filter(employee=request.user).order_by('-start_date')
    announcements = Announcement.objects.order_by('-created_at')[:5] 

    context = {
        'leaves': leaves,
        'attendance_day': attendance_day or {'date': today, 'is_open': False},
        'has_marked_attendance': has_marked_attendance,
        'announcements': announcements,
    }

    return render(request, 'core/employee_dashboard.html', context)


@login_required
def employee_list(request):
    employees = Employee.objects.select_related('user').all()
    return render(request, 'core/employee_list.html', {'employees': employees})


@login_required
def leave_requests(request):
    leaves = LeaveRequest.objects.select_related('employee').all()
    return render(request, 'core/leave_requests.html', {'leaves': leaves})



@login_required
def apply_leave(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user  # Updated
            leave.save()
            return redirect('employee_dashboard')
    else:
        form = LeaveForm()
    return render(request, 'core/apply_leave.html', {'form': form})


@login_required
def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'core/edit_employee.html', {'form': form, 'employee': employee})


@login_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        user = employee.user
        employee.delete()
        user.delete()
        return redirect('employee_list')
    return render(request, 'core/confirm_delete.html', {'employee': employee})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard_redirect')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

 
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Employee.objects.create(
                user=user,
                department=form.cleaned_data['department'],
                designation=form.cleaned_data['designation'],
                join_date=form.cleaned_data['join_date'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                is_hr=form.cleaned_data['is_hr']
            )
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def mark_attendance(request):
    today = timezone.now().date()
    try:
        day = AttendanceDay.objects.get(date=today)
    except AttendanceDay.DoesNotExist:
        messages.warning(request, "Attendance has not been opened by HR today.")
        return redirect('employee_dashboard')

    if not day.is_open:
        messages.warning(request, "Attendance is currently closed.")
        return redirect('employee_dashboard')

    if Attendance.objects.filter(employee=request.user, date=today).exists():
        messages.info(request, "You have already marked attendance today.")
        return redirect('employee_dashboard')

    Attendance.objects.create(employee=request.user, date=today, status='Present')
    messages.success(request, "Attendance marked successfully.")
    return redirect('employee_dashboard')


@login_required
def approve_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id)

    if leave.status != 'Pending':
        messages.info(request, "This leave request has already been processed.")
    else:
        leave.status = 'Approved'
        leave.save()
        messages.success(request, "Leave request approved.")

    return redirect('leave_requests')


@login_required
def reject_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id)

    if leave.status != 'Pending':
        messages.info(request, "This leave request has already been processed.")
    else:
        leave.status = 'Rejected'
        leave.save()
        messages.warning(request, "Leave request rejected.")

    return redirect('leave_requests')


@login_required
def payroll_view(request):
    payrolls = Payroll.objects.select_related('employee__user').all()

    search_query = request.GET.get('search', '')
    if search_query:
        payrolls = payrolls.filter(
            employee__user__first_name__icontains=search_query
        ) | payrolls.filter(
            employee__user__last_name__icontains=search_query
        )

    status = request.GET.get('status', '')
    if status == 'paid':
        payrolls = payrolls.filter(is_paid=True)
    elif status == 'pending':
        payrolls = payrolls.filter(is_paid=False)

    context = {
        'payrolls': payrolls.order_by('-month'),
    }
    return render(request, 'core/payroll.html', context)


@login_required
def announcement_list(request):
    announcements = Announcement.objects.order_by('-created_at')
    return render(request, 'core/announcement_list.html', {'announcements': announcements})

@login_required
def make_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    
    return render(request, 'core/announcement_form.html', {'form': form})

@login_required
def attendance_report(request):
    date = request.GET.get('date')
    username = request.GET.get('employee')

    records = Attendance.objects.all()
    if date:
        records = records.filter(date=date)
    if username:
        records = records.filter(employee__username=username)

    context = {
        'attendance_records': records,
        'employees': Employee.objects.all(),
    }
    return render(request, 'core/attendance_report.html', context)


@login_required
def add_payroll(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll added successfully.')
            return redirect('payroll')  # Adjust to your payroll list view name
    else:
        form = PayrollForm()
    return render(request, 'core/add_payroll.html', {'form': form})

@login_required
def generate_payslip(request, payroll_id):
    payroll = get_object_or_404(Payroll, id=payroll_id)
    html_string = render(request, 'core/payslip.html', {
        'payroll': payroll,
        'company_name': "Livestock Feeds Plc"
    }).content.decode('utf-8')

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename=payslip_{payroll.employee.user.username}_{payroll.month}.pdf'
    return response

@login_required
def mark_payroll_as_paid(request, payroll_id):
    payroll = get_object_or_404(Payroll, id=payroll_id)
    if not payroll.is_paid:
        payroll.is_paid = True
        payroll.save()
        messages.success(request, f"Payroll ID {payroll.id} marked as paid.")
    else:
        messages.info(request, f"Payroll ID {payroll.id} is already marked as paid.")
    return redirect('payroll')  # replace with your actual payroll list view name

@login_required
def profile(request):
    
    employee = get_object_or_404(Employee, user=request.user)

    return render(request, "core/profile.html", {"employee": employee})


@login_required
def my_attendance(request):
    """
    Attendance history for the logged‑in employee only.
    """
    employee = get_object_or_404(Employee, user=request.user)
    attendance_list = Attendance.objects.filter(employee=request.user)

    context = {"employee": employee, "attendance_list": attendance_list}
    return render(
        request,
        "core/attendance.html", context

    )

def password_reset(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)
            request.session['reset_email'] = email
            request.session['otp'] = str(otp)

            # Send OTP via email
            send_mail(
                subject='Your Password Reset OTP',
                message=f'Your OTP for password reset is {otp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, "Email address not found.")
    return render(request, 'core/password_reset.html')

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('verify_otp')

        session_otp = request.session.get('otp')
        email = request.session.get('reset_email')

        if session_otp == entered_otp:
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()

            # Cleanup
            request.session.pop('otp')
            request.session.pop('reset_email')

            messages.success(request, "Password reset successful. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP.")
    return render(request, 'core/verify_otp.html')

def upload_profile_picture(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)

    if request.method == 'POST' and request.FILES.get('avatar'):
        avatar = request.FILES['avatar']
        employee.avatar = avatar  # Make sure your model has this field
        employee.save()
        messages.success(request, 'Profile picture updated successfully.')
    else:
        messages.error(request, 'Failed to upload profile picture.')

    return redirect('profile',)  # update to match your profile page URL name