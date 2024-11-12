from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
import calendar

from .models import Task
from .forms import TaskForm


# Create your views here.

@login_required
def home_view(request):
    tasks = Task.objects.filter(user=request.user)
    tasks = tasks.order_by('due_date', 'created_at')

    # Обработка формы
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)  # Не сохраняем сразу, чтобы установить пользователя
            task.user = request.user
            task.save()
            return redirect('home')  # Перенаправляем на главную страницу после добавления задачи
    else:
        form = TaskForm()

    return render(request, 'tasks/home.html', {'tasks': tasks, 'form': form})


@login_required
@require_POST
def add_task(request):
    form = TaskForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.save()
        return JsonResponse({
            'status': 'success',
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'completed': task.completed,
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M'),
                'due_date': task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else '',
            }
        })
    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return JsonResponse({'status': 'success', 'task_id': task_id})


@login_required
def calendar_view(request, year=None, month=None):
    today = timezone.now()
    if year is None or month is None:
        year = today.year
        month = today.month
    else:
        year = int(year)
        month = int(month)

    # Расчет предыдущего и следующего месяцев
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # Получаем задачи для выбранного месяца
    tasks = Task.objects.filter(due_date__year=year, due_date__month=month)

    # Создаем календарь
    cal = calendar.monthcalendar(year, month)
    days_with_tasks = {task.due_date.day for task in tasks}

    context = {
        'calendar': cal,
        'year': year,
        'month': month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'days_with_tasks': days_with_tasks,
    }

    if month == today.month:
        context['today'] = today.day

    return render(request, 'tasks/calendar.html', context)
