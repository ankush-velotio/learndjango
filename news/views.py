from django.shortcuts import render


def reporter(request, reporter_name):
    context = {'reporter_name': reporter_name}
    return render(request, 'reporter.html', context)
