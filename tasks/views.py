from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

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
