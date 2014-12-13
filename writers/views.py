from django.shortcuts import render

def home(request):
	return render(request, 'stears_test.html', {})
