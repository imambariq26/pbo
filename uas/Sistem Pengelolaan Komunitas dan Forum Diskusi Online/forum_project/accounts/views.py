# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from forum.models import Notification, Topic, Comment


@login_required
def dashboard(request):
    recent_topics = Topic.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_comments = Comment.objects.order_by('-created_at')[:5]
    context = {
        'recent_topics': recent_topics,
        'recent_comments': recent_comments,
    }
    return render(request, 'registrasi/dashboard.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registrasi berhasil! Silahkan login.')
            return redirect('login')  # pastikan kamu memiliki view login (misal dari django.contrib.auth)
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def profile(request, user_id):
    user_profile = get_object_or_404(User, id=user_id)
    return render(request, 'accounts/profile.html', {'user_profile': user_profile})

@login_required
def notifications(request):
    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'accounts/notifications.html', {'notifications': notifs})

def profile(request, user_id):
    user_profile = get_object_or_404(User, id=user_id)
    topics = user_profile.topics.all()
    comments = user_profile.comments.all()
    return render(request, 'accounts/profile.html', {
        'user_profile': user_profile,
        'topics': topics,
        'comments': comments,
    })

