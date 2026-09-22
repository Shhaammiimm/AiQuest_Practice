from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Item
from .models import Lend


class RecentlyAddedExpensesTests(TestCase):
	def test_lend_list_shows_saved_lend_information(self):
		Lend.objects.create(
			name='Rahim',
			amount=Decimal('2500.00'),
			lend_date=date(2026, 9, 20),
			return_date=date(2026, 10, 1),
			description='Personal loan',
		)

		response = self.client.get(reverse('expense:lend_list'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Rahim')
		self.assertContains(response, '2500.00')
		self.assertContains(response, 'Personal loan')
		self.assertContains(response, 'Total: ৳2500.00')

	def test_monthly_page_renders(self):
		response = self.client.get(reverse('expense:monthly_list'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'open-monthly-add')

	def test_add_page_shows_items_created_within_last_24_hours(self):
		recent_item = Item.objects.create(
			name='Recent historical expense',
			price=Decimal('12.50'),
			quantity=1,
			date=date.today() - timedelta(days=3),
		)
		old_item = Item.objects.create(
			name='Old expense',
			price=Decimal('8.00'),
			quantity=1,
			date=date.today(),
		)
		now = timezone.now()
		Item.objects.filter(pk=recent_item.pk).update(
			created_at=now - timedelta(hours=23)
		)
		Item.objects.filter(pk=old_item.pk).update(
			created_at=now - timedelta(hours=25)
		)

		response = self.client.get(reverse('expense:add_item'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			list(response.context['recent_items']),
			[recent_item],
		)

	def test_ajax_add_response_excludes_created_at_column_data(self):
		response = self.client.post(
			reverse('expense:add_item'),
			{
				'name': 'Historical expense',
				'price': '12.50',
				'quantity': '1',
				'date': '2026-09-20',
				'location': '',
				'description': '',
			},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json()['success'])
		self.assertNotIn('created_at', response.json()['item'])

