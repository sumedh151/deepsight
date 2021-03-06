from django.shortcuts import render
from django.http import HttpResponse

def index(request) :
    """
        Renders DeepSight landing page
    """
    return render(request, 'index.html')

def documentation(request) :
    """
        Renders DeepSight API Documentation
    """
    return render(request, 'documentation.html')