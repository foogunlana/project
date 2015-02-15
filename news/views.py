from django.shortcuts import render

# Create your views here.


def home(request):
    context = {"bla": "hello my name is bode"}
    return render(request, 'news/home.html', context)


def article(request):
    context = {"bla": "hello my name is bode"}
    return render(request, 'news/article.html', context)
