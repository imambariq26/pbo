# forum/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from .models import Category, Topic, Comment, Vote, Notification
from .forms import TopicForm, CommentForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from .models import Report


def search_topics(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Topic.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_active=True
        ).order_by('-created_at')
    paginator = Paginator(results, 10)
    page = request.GET.get('page')
    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        topics = paginator.page(1)
    except EmptyPage:
        topics = paginator.page(paginator.num_pages)
    return render(request, 'forum/search_results.html', {'topics': topics, 'query': query})

def moderator_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:  # atau custom check sesuai kebutuhan
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'forum/category_list.html', {'categories': categories})

def topic_list(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    topics = category.topics.filter(is_active=True)
    return render(request, 'forum/topic_list.html', {'category': category, 'topics': topics})

def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id, is_active=True)
    comments = topic.comments.all()
    return render(request, 'forum/topic_detail.html', {'topic': topic, 'comments': comments})

@login_required
def topic_create(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            return redirect('forum:topic_detail', topic_id=topic.id)
    else:
        form = TopicForm()
    return render(request, 'forum/topic_create.html', {'form': form})

@login_required
def add_comment(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.created_by = request.user
            comment.topic = topic
            comment.save()

            # Buat notifikasi untuk pembuat topik jika yang mengomentar bukan pembuat topik
            if topic.created_by != request.user:
                Notification.objects.create(
                    recipient=topic.created_by,
                    message=f"{request.user.username} telah mengomentari topik '{topic.title}'",
                    url=f"/forum/topic/{topic.id}/"
                )
            return redirect('forum:topic_detail', topic_id=topic.id)
    else:
        form = CommentForm()
    return render(request, 'forum/add_comment.html', {'form': form, 'topic': topic})

@login_required
def vote(request):
    """
    Endpoint sederhana untuk voting via AJAX.
    Ekspektasi request.POST mengandung:
    - object_type: 'topic' atau 'comment'
    - object_id: id dari object yang akan divote
    - vote: '1' (upvote) atau '-1' (downvote)
    """
    if request.method == 'POST':
        object_type = request.POST.get('object_type')
        object_id = request.POST.get('object_id')
        vote_value = int(request.POST.get('vote'))
        
        # Tentukan content type
        if object_type == 'topic':
            model = Topic
        elif object_type == 'comment':
            model = Comment
        else:
            return JsonResponse({'error': 'Invalid object type'}, status=400)
        
        content_type = ContentType.objects.get_for_model(model)
        obj = get_object_or_404(model, id=object_id)

        # Update atau buat vote baru
        vote_obj, created = Vote.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            defaults={'vote': vote_value}
        )
        if not created:
            # Jika vote sudah ada, update nilainya
            vote_obj.vote = vote_value
            vote_obj.save()

        # Hitung total vote (misal: sum dari semua vote)
        votes = Vote.objects.filter(content_type=content_type, object_id=object_id)
        total_vote = sum(v.vote for v in votes)
        return JsonResponse({'total_vote': total_vote})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@moderator_required
def delete_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    topic.is_active = False  # atau hapus dengan topic.delete()
    topic.save()
    return redirect('forum:topic_list', category_id=topic.category.id)

def moderator_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

@moderator_required
def reports_dashboard(request):
    reports = Report.objects.filter(is_resolved=False).order_by('-created_at')
    return render(request, 'forum/reports_dashboard.html', {'reports': reports})


def topic_list(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    topics_list = category.topics.filter(is_active=True).order_by('-created_at')
    paginator = Paginator(topics_list, 10)  # 10 topik per halaman
    page = request.GET.get('page')

    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        topics = paginator.page(1)
    except EmptyPage:
        topics = paginator.page(paginator.num_pages)

    return render(request, 'forum/topic_list.html', {'category': category, 'topics': topics})
