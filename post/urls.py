from django.urls import path

from post.views import PostDetailView, PostListView

app_name = 'post'

urlpatterns = [
    path('post/<int:pk>/', PostDetailView.as_view(), name=''),
    path('post-feed/', PostListView.as_view(), name='')
]
