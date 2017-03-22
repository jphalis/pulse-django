from django.shortcuts import render

# Create views here.


def home(request):
    return render(request, 'index.html', {'domain': request.get_host()})


def privacy_policy(request):
    return render(request, 'privacy_policy.html', {})


def terms_of_use(request):
    return render(request, 'terms_of_use.html', {})
