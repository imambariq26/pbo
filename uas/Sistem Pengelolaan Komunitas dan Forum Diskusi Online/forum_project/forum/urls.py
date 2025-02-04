# forum/urls.py
from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    # URL untuk menampilkan daftar kategori
    path('', views.category_list, name='category_list'),
    # URL untuk menampilkan topik berdasarkan kategori
    path('category/<int:category_id>/', views.topic_list, name='topic_list'),
    # URL untuk detail topik dan komentar
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    # URL untuk membuat topik baru
    path('topic/create/', views.topic_create, name='topic_create'),
    # URL untuk menambahkan komentar
    path('topic/<int:topic_id>/comment/', views.add_comment, name='add_comment'),
    # URL untuk voting (upvote/downvote)
    path('vote/', views.vote, name='vote'),
    path('search/', views.search_topics, name='search_topics'),
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
]
