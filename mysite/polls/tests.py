import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from polls.models import Poll

class PollMethodTest(TestCase):
    def test_was_published_recently_with_future_poll(self):
	"""Vrati false ako je datum u budućnosti"""
        future_poll = Poll(pub_date = timezone.now() + datetime.timedelta(days=30))
	self.assertEqual(future_poll.was_published_recently(), False)
    def test_was_published_recently_with_olf_poll(self):
	"""Vrati false ako je datum stariji od jednog dana"""
	old_poll = Poll(pub_date = timezone.now() - datetime.timedelta(days=30))
	self.assertEqual(old_poll.was_published_recently(), False)
    def test_was_published_recently_with_recent_poll(self):
	"""Vrati true ako je objava unutar jednog dana"""
	recent_poll = Poll(pub_date = timezone.now() - datetime.timedelta(hours=1))
	self.assertEqual(recent_poll.was_published_recently(), True)

def create_poll(question, days):
    """Stvara poll sa offsetom dana koliko iznosi days"""
    return Poll.objects.create(question=question, pub_date=timezone.now() + datetime.timedelta(days=days))

class PollViewTests(TestCase):
    def test_index_view_with_no_polls(self):
        """Ako ne postoje pollovi, javi to"""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])
    def test_index_view_with_a_past_poll(self):
        """Pollovi koji su objavljeni u prošlosti, javi to"""
        create_poll(question="Past poll.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll.>']
        )
    def test_index_view_with_a_future_poll(self):
        """Pollovi koji će biti objavljeni u budućnosti, nemoj to još objaviti"""
        create_poll(question="Future poll.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])
    def test_index_view_with_future_poll_and_past_poll(self):
        """Ako postoje Pollovi u prošlosti i budućnosti, samo prošle objavi"""
        create_poll(question="Past poll.", days=-30)
        create_poll(question="Future poll.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll.>']
        )
    def test_index_view_with_two_past_polls(self):
        """Ako postoje dva prošla pollova, objavi ih"""
        create_poll(question="Past poll 1.", days=-30)
        create_poll(question="Past poll 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
             ['<Poll: Past poll 2.>', '<Poll: Past poll 1.>']
        )
class PollIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_poll(self):
	"""Ako je poll u budućnosti, vrati 404"""
	future_poll = create_poll(question="Future poll.", days=5)
	response = self.client.get(reverse('polls:detail', args=(future_poll.id,)))
	self.assertEqual(response.status_code, 404)
    def test_detail_view_with_a_past_poll(self):
	"""Ako je poll u prošlosti, pokaži ga"""
	past_poll = create_poll(question="Past poll.", days=-5)
	response = self.client.get(reverse('polls:detail', args=(past_poll.id,)))
	self.assertContains(response, past_poll.question, status_code = 200)
