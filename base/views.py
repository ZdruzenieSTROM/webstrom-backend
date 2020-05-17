from django.shortcuts import render


def react_test(request):
    return render(request, 'react_test.html')
