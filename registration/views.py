from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'registration/course_list.html', {'courses': courses})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Check for duplicate enrollment
    already_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    if not already_enrolled and course.seats_available > 0:
        Enrollment.objects.create(user=request.user, course=course)
        course.seats_available -= 1
        course.save()

    return redirect('course_list')

@login_required
def enrolled_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    return render(request, 'registration/enrolled_courses.html', {'enrollments': enrollments})

@login_required
def drop_course(request, course_id):
    enrollment = Enrollment.objects.filter(user=request.user, course_id=course_id).first()
    if enrollment:
        enrollment.course.seats_available += 1
        enrollment.course.save()
        enrollment.delete()
        messages.success(request, "Successfully dropped the course.")
    return redirect('enrolled_courses')
