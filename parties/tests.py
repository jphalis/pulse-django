from datetime import datetime, timedelta
from django.test import TestCase

from accounts.models import MyUser
from parties.models import Party


def make_user(email='user@test.com', full_name='Test User', password='abc1234'):
    return MyUser.objects.create_user(email=email, full_name=full_name,
                                      password=password)


class PartyCreateUnitTest(TestCase):
    def setUp(self):
        user = make_user()
        Party.objects.party_create(
            user=user,
            party_type=Party.SOCIAL,
            name='name of party',
            location='1 Oak NYC',
            party_size=Party.SMALL,
            party_month=8,
            party_day=25,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=3),
            description='An an valley indeed so no wonder future nature vanity. '
                        'Debating all she mistaken indulged believed provided declared.',)

    def test_party_created(self):
        party = Party.objects.get(name='name of party')
        self.assertEqual(party.name, 'name of party', "Party name "
            "should be: name of party. Instead was: {}".format(party.name))
