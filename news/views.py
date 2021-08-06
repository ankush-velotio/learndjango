from django.shortcuts import render


def reporter(request):
    context = {'reporter_name': "Alex"}
    return render(request, 'reporter.html', context)
