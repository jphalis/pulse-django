from django.shortcuts import get_object_or_404, render

from parties.models import Party

# Create views here.


def home(request):
    return render(request, 'index.html', {'domain': request.get_host()})


def privacy_policy(request):
    return render(request, 'privacy_policy.html', {})


def terms_of_use(request):
    return render(request, 'terms_of_use.html', {})


def share_party(request, party_pk):
    party = get_object_or_404(Party, pk=party_pk)
    return render(request, 'share_party.html', {'party': party})
