from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView


# Create your views here.

class PostDetailView(DetailView):
    pass

class PostListView(ListView):
    pass
