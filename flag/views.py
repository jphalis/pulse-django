from django.shortcuts import get_object_or_404

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from parties.models import Party
from .models import Flag


@login_required
@require_http_methods(['POST'])
def flag_create_ajax(request):
    party_pk = request.POST.get('party_pk')
    party = get_object_or_404(Party, pk=party_pk)
    party_creator = party.creator

    flagged, created = Flag.objects.get_or_create(party=party,
                                                  creator=request.user)
    flagged.flag_count = F('flag_count') + 1
    flagged.save()

    party_creator.times_flagged = F('times_flagged') + 1
    party_creator.save()

    send_mail('FLAGGED ITEM',
              'There is a new flagged item with the id: {}'.format(flagged.id),
              settings.DEFAULT_HR_EMAIL, [settings.DEFAULT_HR_EMAIL],
              fail_silently=True)

    data = {
        "party_flagged": True,
    }
    return JsonResponse(data)
