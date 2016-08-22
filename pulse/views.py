from django.shortcuts import render

# Create views here.


def home(request):
    return render(request, 'index.html', {'domain': request.get_host()})


# REMOVE WHEN IN PRODUCTION ! ! !


def randomword(length):
    import random
    import string
    return ''.join(random.choice(string.lowercase) for i in range(length))


def generate_rand_data(request):
    from datetime import datetime, timedelta
    from django.contrib import messages
    from accounts.models import Follower, MyUser
    from notifications.signals import notify
    from parties.models import Party

    MyUser.objects.create_user(
        email='user@test.com',
        full_name='Test User',
        password='abc1234')

    for num in range(20):
        MyUser.objects.create_user(
            email='{0}@sample.com'.format(randomword(7)),
            full_name='{0} {1}'.format(randomword(5), randomword(8)),
            password='abc1234')

    last_user = MyUser.objects.all().last()
    last_user_id = last_user.id
    for num in range(last_user_id - 11, last_user_id):
        Party.objects.party_create(
            user=MyUser.objects.get(id=num),
            party_type=Party.SOCIAL,
            name=randomword(12),
            location='1 Oak NYC',
            party_size=Party.SMALL,
            party_month=8,
            party_day=25,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=3),
            description='An an valley indeed so no wonder future nature vanity. '
                        'Debating all she mistaken indulged believed provided declared.',
        )

    test_user_party = MyUser.objects.get(email='user@test.com')
    party = Party.objects.party_create(
        user=test_user_party,
        party_type=Party.SOCIAL,
        name='test party',
        location='1 Oak NYC',
        party_size=Party.SMALL,
        party_month=8,
        party_day=25,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=3),
        description='An an valley indeed so no wonder future nature vanity. '
                    'Debating all she mistaken indulged believed provided declared.',
    )
    for val in range(last_user_id - 4, last_user_id):
        if not val == test_user_party.id:
            attendee = MyUser.objects.get(id=val)
            party.attendees.add(attendee)
            party.save()
            notify.send(
                attendee,
                recipient=party.user,
                verb='{0} will be attending your party'.format(
                    attendee.get_full_name)
            )

    viewing_user = MyUser.objects.get(id=last_user_id)
    follower, created = Follower.objects.get_or_create(user=viewing_user)
    the_user = MyUser.objects.get(email='user@test.com')
    followed, created = Follower.objects.get_or_create(user=the_user)

    followed.followers.add(follower)
    notify.send(
        viewing_user,
        recipient=the_user,
        verb='{0} is following you'.format(viewing_user.get_full_name)
    )

    messages.success(request, "Data created!")
    return render(request, 'index.html', {})
