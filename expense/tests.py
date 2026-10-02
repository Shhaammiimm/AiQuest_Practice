from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Borrow, Item, Lend

User = get_user_model()


class RecentlyAddedExpensesTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testuser', password='testpass123')
		self.client.force_login(self.user)
	def test_borrow_records_are_separate_from_lend_records(self):
		lend = Lend.objects.create(
			user=self.user,
			name='Lend only',
			amount=Decimal('100.00'),
			lend_date=date(2026, 9, 20),
		)
		response = self.client.get(reverse('expense:borrow_list'))

		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, 'Lend only')

		response = self.client.post(
			reverse('expense:add_borrow'),
			{
				'name': 'Borrow only',
				'amount': '75.00',
				'borrow_date': '2026-09-21',
				'return_date': '',
				'description': '',
			},
		)

		self.assertRedirects(response, reverse('expense:borrow_list'))
		self.assertEqual(Borrow.objects.count(), 1)
		self.assertEqual(Lend.objects.count(), 1)
		self.assertEqual(Borrow.objects.get().name, 'Borrow only')
		self.assertEqual(Lend.objects.get().pk, lend.pk)

	def test_lend_list_shows_saved_lend_information(self):
		Lend.objects.create(
			user=self.user,
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
		self.assertContains(response, 'Total lent')
		self.assertContains(response, '৳2500.00')
		self.assertContains(response, 'data-edit-record')
		self.assertContains(response, 'data-delete-record')
		self.assertContains(response, 'record-action-modal')

	def test_lend_can_be_edited_and_deleted(self):
		lend = Lend.objects.create(
			user=self.user,
			name='Old lender',
			amount=Decimal('100.00'),
			lend_date=date(2026, 9, 20),
		)
		response = self.client.post(
			reverse('expense:edit_lend', args=[lend.pk]),
			{
				'name': 'Updated lender',
				'amount': '125.00',
				'lend_date': '2026-09-20',
				'return_date': '',
				'description': '',
			},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
		)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json()['success'])
		self.assertEqual(response.json()['record']['name'], 'Updated lender')
		lend.refresh_from_db()
		self.assertEqual(lend.name, 'Updated lender')
		self.assertEqual(lend.amount, Decimal('125.00'))

		response = self.client.post(reverse('expense:delete_lend', args=[lend.pk]))
		self.assertRedirects(response, reverse('expense:lend_list'))
		self.assertFalse(Lend.objects.filter(pk=lend.pk).exists())

	def test_borrow_can_be_edited_and_deleted(self):
		borrow = Borrow.objects.create(
			user=self.user,
			name='Old borrower',
			amount=Decimal('80.00'),
			borrow_date=date(2026, 9, 20),
		)
		response = self.client.post(
			reverse('expense:edit_borrow', args=[borrow.pk]),
			{
				'name': 'Updated borrower',
				'amount': '95.00',
				'borrow_date': '2026-09-20',
				'return_date': '',
				'description': '',
			},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
		)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json()['success'])
		self.assertEqual(response.json()['record']['name'], 'Updated borrower')
		borrow.refresh_from_db()
		self.assertEqual(borrow.name, 'Updated borrower')
		self.assertEqual(borrow.amount, Decimal('95.00'))

		response = self.client.post(reverse('expense:delete_borrow', args=[borrow.pk]))
		self.assertRedirects(response, reverse('expense:borrow_list'))
		self.assertFalse(Borrow.objects.filter(pk=borrow.pk).exists())

	def test_monthly_page_renders(self):
		response = self.client.get(reverse('expense:monthly_list'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'open-monthly-add')

	def test_home_dashboard_summarizes_expenses_and_links_tabs(self):
		Item.objects.create(
			user=self.user,
			name='Dashboard grocery',
			price=Decimal('25.50'),
			quantity=2,
			date=date.today(),
		)
		response = self.client.get(reverse('expense:home'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['month_total'], Decimal('51.00'))
		self.assertEqual(response.context['year_total'], Decimal('51.00'))
		self.assertEqual(response.context['today_total'], Decimal('51.00'))
		self.assertContains(response, 'This month')
		self.assertContains(response, 'This year')
		self.assertContains(response, 'Dashboard grocery')
		self.assertContains(response, 'aria-current="page"')
		self.assertContains(response, 'class="expense-site-footer"')
		self.assertContains(response, 'Shamim Mahamud Shajon')
		self.assertNotContains(response, 'Footer navigation')

	def test_global_tabs_render_with_the_current_section_active(self):
		pages = [
			('add_item', 'Add Item', 'add_item'),
			('monthly_list', 'Monthly List', 'monthly_list'),
			('lend_list', 'Lend List', 'lend_list'),
			('borrow_list', 'Borrow List', 'borrow_list'),
			('add_lend', 'Lend List', 'lend_list'),
			('add_borrow', 'Borrow List', 'borrow_list'),
		]

		for route_name, active_label, active_route in pages:
			with self.subTest(route=route_name):
				response = self.client.get(reverse(f'expense:{route_name}'))
				self.assertEqual(response.status_code, 200)
				self.assertContains(response, 'aria-label="Expense sections"')
				self.assertContains(response, 'class="expense-site-footer"')
				self.assertContains(response, 'Shamim Mahamud Shajon')
				self.assertNotContains(response, 'Footer navigation')
				for tab_label, tab_route in [
					('Add Item', 'add_item'),
					('Monthly List', 'monthly_list'),
					('Lend List', 'lend_list'),
					('Borrow List', 'borrow_list'),
				]:
					self.assertContains(response, reverse(f'expense:{tab_route}'))
				self.assertContains(
					response,
					f'href="{reverse(f"expense:{active_route}")}" class="is-active" aria-current="page"',
				)
				self.assertContains(response, active_label)

	def test_add_page_shows_items_created_within_last_24_hours(self):
		recent_item = Item.objects.create(
			user=self.user,
			name='Recent historical expense',
			price=Decimal('12.50'),
			quantity=1,
			date=date.today() - timedelta(days=3),
		)
		old_item = Item.objects.create(
			user=self.user,
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

