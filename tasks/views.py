from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm


# Create your views here.

@login_required
def home_view(request):
    tasks = Task.objects.filter(user=request.user)

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
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return JsonResponse({'status': 'success', 'task_id': task_id})