from django.shortcuts import render
from django.shortcuts import redirect

# Create views here.


def home(request):
    return render(request, 'index.html', {'domain': request.get_host()})


def privacy_policy(request):
    return render(request, 'privacy_policy.html', {})


def terms_of_use(request):
    return render(request, 'terms_of_use.html', {})


# REMOVE WHEN IN PRODUCTION ! ! !


def randomword(length):
    import random
    import string
    return ''.join(random.choice(string.lowercase) for i in range(length))


def generate_rand_data(request):
    import random
    from datetime import datetime, timedelta
    from django.contrib import messages
    from accounts.models import Follower, MyUser
    from feed.signals import feed_item
    from notifications.signals import notify
    from parties.models import Party

    if MyUser.objects.filter(email='user@test.com').exists():
        messages.error(request, "You should already have data available.")
    else:
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
        coordinates = (
            ['-6.21931', '9.06958'],
            ['2.72985', '-60.87716'],
            ['54.70628', '131.61506'],
            ['-27.80537', '139.59436'],
            ['39.75070', '17.92816'],
            ['6.46050', '24.88215'],
            ['2.51270', '-60.48829'],
        )
        i = 0
        for num in coordinates:
            user = MyUser.objects.order_by('?').first()
            party = Party.objects.party_create(
                user=user,
                party_type=Party.SOCIAL,
                name=randomword(12),
                location='1 Oak NYC',
                latitude=coordinates[i][0],
                longitude=coordinates[i][1],
                party_size=Party.SMALL,
                party_month=random.randint(10, 12),
                party_day=random.randint(1, 28),
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=random.randint(1, 7)),
                description='An an valley indeed so no wonder future nature vanity. '
                            'Debating all she mistaken indulged believed provided declared.',
            )
            party.save()
            feed_item.send(
                user,
                verb='created an event',
                target=party,
            )
            i += 1

        test_user_party = MyUser.objects.get(email='user@test.com')
        party, created = Party.objects.get_or_create(
            user=test_user_party,
            party_type=Party.SOCIAL,
            name='test party',
            location='Hoboken, NJ',
            latitude="40.743991",
            longitude="-74.032363",
            party_size=Party.SMALL,
            party_month=11,
            party_day=25,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=3),
            description='An an valley indeed so no wonder future nature vanity. '
                        'Debating all she mistaken indulged believed provided declared.',
        )
        feed_item.send(
            test_user_party,
            verb='created an event',
            target=party,
        )

        for val in range(last_user_id - 4, last_user_id):
            if not val == test_user_party.id:
                attendee = MyUser.objects.get(id=val)
                party.attendees.add(attendee)
                party.save()
                notify.send(
                    attendee,
                    recipient=party.user,
                    verb='will be attending your party',
                    target=party,
                )
                feed_item.send(
                    attendee,
                    verb='will be attending {0}\'s party'.format(
                        party.user.get_full_name),
                    target=party,
                )

        viewing_user = MyUser.objects.get(id=last_user_id)
        follower, created = Follower.objects.get_or_create(user=viewing_user)
        the_user = MyUser.objects.get(email='user@test.com')
        followed, created = Follower.objects.get_or_create(user=the_user)

        followed.followers.add(follower)
        follower.followers.add(followed)
        notify.send(
            viewing_user,
            recipient=the_user,
            verb='is following you',
        )
        feed_item.send(
            viewing_user,
            verb='will be attending {0}\'s party'.format(
                the_user.get_full_name),
            target=party,
        )

        messages.success(request, "Data created!")
    return redirect('home')
