from django.urls import path
from .views import PostListCreateView, CommentListCreateView

urlpatterns = [
    path('posts/', PostListCreateView.as_view()),
    path('comments/', CommentListCreateView.as_view()),
]
