from django.test import TestCase, Client
from django.contrib.auth import authenticate, get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
import json
import io
from PIL import Image
from .models import Item, Bid

User = get_user_model()


class UserModelTest(TestCase):
    """Test custom User model"""
    
    def setUp(self):
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'date_of_birth': date(1990, 1, 1),
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'john@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_superuser)
    
    def test_create_user_without_email_raises_error(self):
        """Test that creating user without email raises ValueError"""
        data = self.user_data.copy()
        data['email'] = ''
        
        with self.assertRaises(ValueError):
            User.objects.create_user(**data)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(**self.user_data)
        
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_user_email_is_unique(self):
        """Test that duplicate emails are not allowed"""
        User.objects.create_user(**self.user_data)
        
        with self.assertRaises(Exception):  # IntegrityError
            User.objects.create_user(**self.user_data)
    
    def test_user_email_normalization(self):
        """Test email domain is normalized (lowercased)"""
        data = self.user_data.copy()
        data['email'] = 'TEST@EXAMPLE.COM'
        user = User.objects.create_user(**data)
        
        # Django only normalizes domain, not local part
        self.assertEqual(user.email, 'TEST@example.com')
    
    def test_username_field_is_email(self):
        """Test that USERNAME_FIELD is email"""
        self.assertEqual(User.USERNAME_FIELD, 'email')
    
    def test_user_str_method(self):
        """Test string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'john@example.com')
    
    def test_is_staff_property(self):
        """Test is_staff returns is_admin value"""
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_staff)
        
        user.is_admin = True
        self.assertTrue(user.is_staff)


class AuthenticationTest(TestCase):
    """Test authentication functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
    
    def test_authenticate_with_valid_credentials(self):
        """Test authentication with correct email and password"""
        user = authenticate(username='test@example.com', password='testpass123')
        
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
    
    def test_authenticate_with_wrong_password(self):
        """Test authentication fails with wrong password"""
        user = authenticate(username='test@example.com', password='wrongpass')
        
        self.assertIsNone(user)
    
    def test_authenticate_with_wrong_email(self):
        """Test authentication fails with wrong email"""
        user = authenticate(username='wrong@example.com', password='testpass123')
        
        self.assertIsNone(user)
    
    def test_authenticate_inactive_user(self):
        """Test inactive users cannot authenticate"""
        self.user.is_active = False
        self.user.save()
        
        user = authenticate(username='test@example.com', password='testpass123')
        
        self.assertIsNone(user)


class LoginViewTest(TestCase):
    """Test login view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
    
    def test_login_with_json(self):
        """Test login with JSON body"""
        response = self.client.post(
            '/login/',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('user', data)
    
    def test_login_with_form_data(self):
        """Test login with form data"""
        response = self.client.post(
            '/login/',
            {
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_login_with_invalid_credentials(self):
        """Test login with wrong password"""
        response = self.client.post(
            '/login/',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'wrongpass'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)
    
    def test_login_without_email(self):
        """Test login without email"""
        response = self.client.post(
            '/login/',
            data=json.dumps({'password': 'testpass123'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_login_without_password(self):
        """Test login without password"""
        response = self.client.post(
            '/login/',
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_login_get_method_not_allowed(self):
        """Test GET request to login returns 405"""
        response = self.client.get('/login/')
        
        self.assertEqual(response.status_code, 405)


class ProfileViewTest(TestCase):
    """Test profile endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_get_profile(self):
        """Test getting user profile"""
        response = self.client.get('/profile/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['first_name'], 'Test')
    
    def test_get_profile_unauthenticated(self):
        """Test profile requires login"""
        self.client.logout()
        response = self.client.get('/profile/')
        
        self.assertEqual(response.status_code, 302)  # Redirect to login


class ProfilePictureTest(TestCase):
    """Test profile picture upload/delete"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def create_test_image(self):
        """Create a test image file"""
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'PNG')
        file.seek(0)
        return SimpleUploadedFile('test.png', file.getvalue(), content_type='image/png')
    
    def test_upload_profile_picture(self):
        """Test uploading a profile picture"""
        image = self.create_test_image()
        
        response = self.client.post(
            '/profile/picture/upload/',
            {'profile_picture': image}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('profile_picture', data)
        
        # Verify in database
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile_picture)
    
    def test_upload_without_file(self):
        """Test upload without file returns error"""
        response = self.client.post('/profile/picture/upload/')
        
        self.assertEqual(response.status_code, 400)
    
    def test_delete_profile_picture(self):
        """Test deleting profile picture"""
        # First upload
        image = self.create_test_image()
        self.user.profile_picture = image
        self.user.save()
        
        # Then delete
        response = self.client.delete('/profile/picture/delete/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify deleted
        self.user.refresh_from_db()
        self.assertFalse(self.user.profile_picture)
    
    def test_delete_nonexistent_picture(self):
        """Test deleting when no picture exists"""
        response = self.client.delete('/profile/picture/delete/')
        
        self.assertEqual(response.status_code, 404)


class UserUpdateTest(TestCase):
    """Test user updates"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='Original',
            last_name='Name',
            email='original@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
    
    def test_update_user_fields(self):
        """Test updating user fields"""
        self.user.first_name = 'Updated'
        self.user.last_name = 'User'
        self.user.save()
        
        updated = User.objects.get(id=self.user.id)
        self.assertEqual(updated.first_name, 'Updated')
        self.assertEqual(updated.last_name, 'User')
    
    def test_update_password(self):
        """Test updating user password"""
        self.user.set_password('newpass456')
        self.user.save()
        
        # Old password shouldn't work
        user = authenticate(username='original@example.com', password='testpass123')
        self.assertIsNone(user)
        
        # New password should work
        user = authenticate(username='original@example.com', password='newpass456')
        self.assertIsNotNone(user)
    
    def test_updated_at_changes(self):
        """Test that updated_at changes on save"""
        original_time = self.user.updated_at
        
        self.user.first_name = 'Changed'
        self.user.save()
        
        self.user.refresh_from_db()
        self.assertGreater(self.user.updated_at, original_time)


class ItemModelTest(TestCase):
    """Test Item model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.future_date = date.today() + timedelta(days=7)
    
    def test_create_item(self):
        """Test creating an item"""
        item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.user,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
        
        self.assertEqual(item.title, 'Test Item')
        self.assertEqual(item.owner, self.user)
        self.assertEqual(item.minimum_bid, 100)
        self.assertIsNone(item.auction_winner)
    
    def test_item_str_method(self):
        """Test string representation"""
        item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.user,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
        self.assertEqual(str(item), 'Test Item')
    
    def test_item_related_names(self):
        """Test reverse relationships work correctly"""
        item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.user,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
        
        # Test owned_items reverse relationship
        self.assertIn(item, self.user.owned_items.all())
        
        # Test won_items reverse relationship
        item.auction_winner = self.user
        item.save()
        self.assertIn(item, self.user.won_items.all())


class GetPaginatedItemsTest(TestCase):
    """Test get paginated items view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        
        # Create test items with different dates
        future_date = date.today() + timedelta(days=7)
        past_date = date.today() - timedelta(days=1)
        
        # Active items
        Item.objects.create(
            title='Laptop Computer',
            description='High-end gaming laptop',
            owner=self.user,
            minimum_bid=1000,
            auction_end_date=future_date
        )
        Item.objects.create(
            title='Vintage Watch',
            description='Classic timepiece with laptop parts',
            owner=self.user,
            minimum_bid=500,
            auction_end_date=future_date
        )
        Item.objects.create(
            title='Smartphone',
            description='Latest model phone',
            owner=self.user,
            minimum_bid=800,
            auction_end_date=future_date
        )
        
        # Expired item (should be filtered out)
        Item.objects.create(
            title='Expired Item',
            description='This should not appear',
            owner=self.user,
            minimum_bid=100,
            auction_end_date=past_date
        )
    
    def test_get_all_items(self):
        """Test getting all active items"""
        response = self.client.get('/items/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 3)  # Only active items
        self.assertEqual(len(data['items']), 3)
    
    def test_expired_items_filtered_out(self):
        """Test that expired items are not returned"""
        response = self.client.get('/items/')
        data = response.json()
        
        titles = [item['title'] for item in data['items']]
        self.assertNotIn('Expired Item', titles)
    
    def test_pagination(self):
        """Test pagination works correctly"""
        response = self.client.get('/items/?start=0&end=2')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 2)
        self.assertEqual(len(data['items']), 2)
    
    def test_search_in_title(self):
        """Test searching by title"""
        response = self.client.get('/items/?search=laptop')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data['count'], 1)
        # Should find the Laptop item first (exact match in title)
        self.assertIn('Laptop', data['items'][0]['title'])
    
    def test_search_in_description(self):
        """Test searching in description"""
        response = self.client.get('/items/?search=gaming')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertIn('gaming', data['items'][0]['description'].lower())
    
    def test_search_with_pagination(self):
        """Test search combined with pagination"""
        response = self.client.get('/items/?search=laptop&start=0&end=1')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
    
    def test_invalid_pagination_parameters(self):
        """Test invalid pagination parameters"""
        response = self.client.get('/items/?start=invalid&end=10')
        self.assertEqual(response.status_code, 400)
        
        response = self.client.get('/items/?start=-1&end=10')
        self.assertEqual(response.status_code, 400)
        
        response = self.client.get('/items/?start=10&end=5')
        self.assertEqual(response.status_code, 400)
    
    def test_get_method_only(self):
        """Test only GET method is allowed"""
        response = self.client.post('/items/')
        self.assertEqual(response.status_code, 405)


class CreateItemTest(TestCase):
    """Test create item view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.client.force_login(self.user)
        self.future_date = date.today() + timedelta(days=7)
    
    def test_create_item_success(self):
        """Test successfully creating an item"""
        response = self.client.post(
            '/items/create/',
            data=json.dumps({
                'title': 'New Item',
                'description': 'Item description',
                'minimum_bid': 100,
                'auction_end_date': str(self.future_date)
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['item']['title'], 'New Item')
        self.assertEqual(data['item']['minimum_bid'], 100)
        
        # Verify in database
        self.assertTrue(Item.objects.filter(title='New Item').exists())
    
    def test_create_item_requires_authentication(self):
        """Test that creating item requires login"""
        self.client.logout()
        response = self.client.post(
            '/items/create/',
            data=json.dumps({
                'title': 'New Item',
                'description': 'Item description',
                'minimum_bid': 100,
                'auction_end_date': str(self.future_date)
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_create_item_missing_fields(self):
        """Test creating item with missing fields"""
        response = self.client.post(
            '/items/create/',
            data=json.dumps({
                'title': 'New Item'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_create_item_invalid_minimum_bid(self):
        """Test creating item with invalid minimum bid"""
        response = self.client.post(
            '/items/create/',
            data=json.dumps({
                'title': 'New Item',
                'description': 'Item description',
                'minimum_bid': 0,
                'auction_end_date': str(self.future_date)
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('Minimum bid must be greater than 0', data['error'])
    
    def test_create_item_past_end_date(self):
        """Test creating item with past auction end date"""
        past_date = date.today() - timedelta(days=1)
        response = self.client.post(
            '/items/create/',
            data=json.dumps({
                'title': 'New Item',
                'description': 'Item description',
                'minimum_bid': 100,
                'auction_end_date': str(past_date)
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('future', data['error'].lower())
    
    def test_post_method_only(self):
        """Test only POST method is allowed"""
        response = self.client.get('/items/create/')
        self.assertEqual(response.status_code, 405)


class UpdateItemTest(TestCase):
    """Test update item view"""
    
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            first_name='Owner',
            last_name='User',
            email='owner@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            first_name='Other',
            last_name='User',
            email='other@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        
        self.future_date = date.today() + timedelta(days=7)
        self.item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
    
    def test_owner_can_update_item(self):
        """Test owner can update their item"""
        self.client.force_login(self.owner)
        
        response = self.client.put(
            f'/items/{self.item.id}/update/',
            data=json.dumps({
                'title': 'Updated Title',
                'minimum_bid': 200
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['item']['title'], 'Updated Title')
        self.assertEqual(data['item']['minimum_bid'], 200)
        
        # Verify in database
        self.item.refresh_from_db()
        self.assertEqual(self.item.title, 'Updated Title')
        self.assertEqual(self.item.minimum_bid, 200)
    
    def test_admin_can_update_any_item(self):
        """Test admin can update any item"""
        self.client.force_login(self.admin)
        
        response = self.client.put(
            f'/items/{self.item.id}/update/',
            data=json.dumps({
                'title': 'Admin Updated'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.title, 'Admin Updated')
    
    def test_non_owner_cannot_update_item(self):
        """Test non-owner cannot update item"""
        self.client.force_login(self.other_user)
        
        response = self.client.put(
            f'/items/{self.item.id}/update/',
            data=json.dumps({
                'title': 'Hacked Title'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('permission', data['error'].lower())
        
        # Verify not updated in database
        self.item.refresh_from_db()
        self.assertEqual(self.item.title, 'Test Item')
    
    def test_update_nonexistent_item(self):
        """Test updating non-existent item returns 404"""
        self.client.force_login(self.owner)
        
        response = self.client.put(
            '/items/99999/update/',
            data=json.dumps({'title': 'Updated'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_update_requires_authentication(self):
        """Test update requires login"""
        response = self.client.put(
            f'/items/{self.item.id}/update/',
            data=json.dumps({'title': 'Updated'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_put_method_only(self):
        """Test only PUT method is allowed"""
        self.client.force_login(self.owner)
        response = self.client.get(f'/items/{self.item.id}/update/')
        self.assertEqual(response.status_code, 405)


class DeleteItemTest(TestCase):
    """Test delete item view"""
    
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            first_name='Owner',
            last_name='User',
            email='owner@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            first_name='Other',
            last_name='User',
            email='other@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        
        self.future_date = date.today() + timedelta(days=7)
    
    def test_owner_can_delete_item(self):
        """Test owner can delete their item"""
        item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
        item_id = item.id
        
        self.client.force_login(self.owner)
        response = self.client.delete(f'/items/{item_id}/delete/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify deleted from database
        self.assertFalse(Item.objects.filter(id=item_id).exists())
    
    def test_admin_can_delete_any_item(self):
        """Test admin can delete any item"""
        item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
        item_id = item.id
        
        self.client.force_login(self.admin)
        response = self.client.delete(f'/items/{item_id}/delete/')
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Item.objects.filter(id=item_id).exists())
    
    def test_non_owner_cannot_delete_item(self):
        """Test non-owner cannot delete item"""
        item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
        
        self.client.force_login(self.other_user)
        response = self.client.delete(f'/items/{item.id}/delete/')
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('permission', data['error'].lower())
        
        # Verify not deleted
        self.assertTrue(Item.objects.filter(id=item.id).exists())
    
    def test_delete_nonexistent_item(self):
        """Test deleting non-existent item returns 404"""
        self.client.force_login(self.owner)
        
        response = self.client.delete('/items/99999/delete/')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_requires_authentication(self):
        """Test delete requires login"""
        item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
        
        response = self.client.delete(f'/items/{item.id}/delete/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_delete_method_only(self):
        """Test only DELETE method is allowed"""
        item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
        
        self.client.force_login(self.owner)
        response = self.client.get(f'/items/{item.id}/delete/')
        self.assertEqual(response.status_code, 405)


class GetUserItemsTest(TestCase):
    """Test get user items view"""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            first_name='User',
            last_name='One',
            email='user1@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            first_name='User',
            last_name='Two',
            email='user2@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        
        future_date = date.today() + timedelta(days=7)
        past_date = date.today() - timedelta(days=1)
        
        # User1's items (active and expired)
        Item.objects.create(
            title='User1 Active Item 1',
            description='Description',
            owner=self.user1,
            minimum_bid=100,
            auction_end_date=future_date
        )
        Item.objects.create(
            title='User1 Active Item 2',
            description='Description',
            owner=self.user1,
            minimum_bid=200,
            auction_end_date=future_date
        )
        Item.objects.create(
            title='User1 Expired Item',
            description='Description',
            owner=self.user1,
            minimum_bid=150,
            auction_end_date=past_date
        )
        
        # User2's item
        Item.objects.create(
            title='User2 Item',
            description='Description',
            owner=self.user2,
            minimum_bid=300,
            auction_end_date=future_date
        )
    
    def test_get_specific_user_items(self):
        """Test getting items for a specific user"""
        self.client.force_login(self.user1)
        
        response = self.client.get(f'/users/{self.user1.id}/items/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 3)  # All items including expired
        
        # Verify items belong to user1
        for item in data['items']:
            self.assertEqual(item['owner']['id'], self.user1.id)
    
    def test_get_my_items(self):
        """Test getting current user's items"""
        self.client.force_login(self.user2)
        
        response = self.client.get('/users/me/items/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['items'][0]['title'], 'User2 Item')
    
    def test_items_include_active_status(self):
        """Test that items include is_active flag"""
        self.client.force_login(self.user1)
        
        response = self.client.get('/users/me/items/')
        data = response.json()
        
        # Check each item has is_active field
        for item in data['items']:
            self.assertIn('is_active', item)
    
    def test_get_nonexistent_user_items(self):
        """Test getting items for non-existent user"""
        self.client.force_login(self.user1)
        
        response = self.client.get('/users/99999/items/')
        self.assertEqual(response.status_code, 404)
    
    def test_requires_authentication(self):
        """Test get user items requires login"""
        response = self.client.get(f'/users/{self.user1.id}/items/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_get_method_only(self):
        """Test only GET method is allowed"""
        self.client.force_login(self.user1)
        response = self.client.post('/users/me/items/')
        self.assertEqual(response.status_code, 405)


class BidModelTest(TestCase):
    """Test Bid model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            first_name='Owner',
            last_name='User',
            email='owner@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.future_date = date.today() + timedelta(days=7)
        self.item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
    
    def test_create_bid(self):
        """Test creating a bid"""
        bid = Bid.objects.create(
            bidder=self.user,
            item=self.item,
            bid_amount=150
        )
        
        self.assertEqual(bid.bidder, self.user)
        self.assertEqual(bid.item, self.item)
        self.assertEqual(bid.bid_amount, 150)
        self.assertIsNotNone(bid.created_at)
    
    def test_bid_related_names(self):
        """Test reverse relationships work correctly"""
        bid = Bid.objects.create(
            bidder=self.user,
            item=self.item,
            bid_amount=150
        )
        
        # Check that we can query bids from item
        self.assertEqual(self.item.bid_set.count(), 1)
        self.assertIn(bid, self.item.bid_set.all())


class CreateBidTest(TestCase):
    """Test create bid view"""
    
    def setUp(self):
        self.client = Client()
        self.bidder = User.objects.create_user(
            first_name='Bidder',
            last_name='User',
            email='bidder@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            first_name='Owner',
            last_name='User',
            email='owner@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.future_date = date.today() + timedelta(days=7)
        self.item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
    
    def test_create_bid_success(self):
        """Test successfully creating a bid"""
        self.client.force_login(self.bidder)
        
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': self.item.id,
                'bid_amount': 150
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['bid']['bid_amount'], 150)
        
        # Verify in database
        self.assertTrue(Bid.objects.filter(item=self.item, bidder=self.bidder).exists())
    
    def test_create_bid_meets_minimum(self):
        """Test bid that exactly meets minimum bid"""
        self.client.force_login(self.bidder)
        
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': self.item.id,
                'bid_amount': 100
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Bid.objects.filter(item=self.item, bid_amount=100).exists())
    
    def test_create_bid_below_minimum(self):
        """Test bid below minimum bid fails"""
        self.client.force_login(self.bidder)
        
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': self.item.id,
                'bid_amount': 50
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('minimum bid', data['error'].lower())
    
    def test_create_bid_higher_than_existing(self):
        """Test creating a bid higher than existing bids"""
        # Create first bid
        Bid.objects.create(bidder=self.bidder, item=self.item, bid_amount=150)
        
        # Create another user and bid higher
        user2 = User.objects.create_user(
            first_name='User2',
            last_name='Test',
            email='user2@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.client.force_login(user2)
        
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': self.item.id,
                'bid_amount': 200
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Bid.objects.filter(item=self.item).count(), 2)
    
    def test_create_bid_equal_to_highest(self):
        """Test bid equal to highest bid fails"""
        # Create first bid
        Bid.objects.create(bidder=self.bidder, item=self.item, bid_amount=150)
        
        # Try to bid same amount
        user2 = User.objects.create_user(
            first_name='User2',
            last_name='Test',
            email='user2@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.client.force_login(user2)
        
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': self.item.id,
                'bid_amount': 150
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('greater than', data['error'].lower())
    
    def test_create_bid_lower_than_highest(self):
        """Test bid lower than highest bid fails"""
        # Create first bid
        Bid.objects.create(bidder=self.bidder, item=self.item, bid_amount=150)
        
        # Try to bid lower amount
        user2 = User.objects.create_user(
            first_name='User2',
            last_name='Test',
            email='user2@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.client.force_login(user2)
        
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': self.item.id,
                'bid_amount': 120
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_owner_cannot_bid_on_own_item(self):
        """Test owner cannot bid on their own item"""
        self.client.force_login(self.owner)
        
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': self.item.id,
                'bid_amount': 150
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('own item', data['error'].lower())
    
    def test_cannot_bid_on_expired_auction(self):
        """Test cannot bid on expired auction"""
        past_date = date.today() - timedelta(days=1)
        expired_item = Item.objects.create(
            title='Expired Item',
            description='Test description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=past_date
        )
        
        self.client.force_login(self.bidder)
        
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': expired_item.id,
                'bid_amount': 150
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('ended', data['error'].lower())
    
    def test_create_bid_invalid_amount(self):
        """Test creating bid with invalid amount"""
        self.client.force_login(self.bidder)
        
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': self.item.id,
                'bid_amount': -10
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_create_bid_missing_fields(self):
        """Test creating bid with missing fields"""
        self.client.force_login(self.bidder)
        
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': self.item.id
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_create_bid_nonexistent_item(self):
        """Test creating bid for non-existent item"""
        self.client.force_login(self.bidder)
        
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': 99999,
                'bid_amount': 150
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_create_bid_requires_authentication(self):
        """Test creating bid requires login"""
        response = self.client.post(
            '/bids/create/',
            data=json.dumps({
                'item_id': self.item.id,
                'bid_amount': 150
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_post_method_only(self):
        """Test only POST method is allowed"""
        self.client.force_login(self.bidder)
        response = self.client.get('/bids/create/')
        self.assertEqual(response.status_code, 405)


class DeleteBidTest(TestCase):
    """Test delete bid view"""
    
    def setUp(self):
        self.client = Client()
        self.bidder = User.objects.create_user(
            first_name='Bidder',
            last_name='User',
            email='bidder@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            first_name='Other',
            last_name='User',
            email='other@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            first_name='Owner',
            last_name='User',
            email='owner@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.future_date = date.today() + timedelta(days=7)
        self.item = Item.objects.create(
            title='Test Item',
            description='Test description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=self.future_date
        )
    
    def test_bidder_can_delete_own_bid(self):
        """Test bidder can delete their own bid"""
        bid = Bid.objects.create(
            bidder=self.bidder,
            item=self.item,
            bid_amount=150
        )
        bid_id = bid.id
        
        self.client.force_login(self.bidder)
        response = self.client.delete(f'/bids/{bid_id}/delete/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify deleted from database
        self.assertFalse(Bid.objects.filter(id=bid_id).exists())
    
    def test_admin_can_delete_any_bid(self):
        """Test admin can delete any bid"""
        bid = Bid.objects.create(
            bidder=self.bidder,
            item=self.item,
            bid_amount=150
        )
        bid_id = bid.id
        
        self.client.force_login(self.admin)
        response = self.client.delete(f'/bids/{bid_id}/delete/')
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Bid.objects.filter(id=bid_id).exists())
    
    def test_non_bidder_cannot_delete_bid(self):
        """Test non-bidder cannot delete bid"""
        bid = Bid.objects.create(
            bidder=self.bidder,
            item=self.item,
            bid_amount=150
        )
        
        self.client.force_login(self.other_user)
        response = self.client.delete(f'/bids/{bid.id}/delete/')
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('permission', data['error'].lower())
        
        # Verify not deleted
        self.assertTrue(Bid.objects.filter(id=bid.id).exists())
    
    def test_delete_nonexistent_bid(self):
        """Test deleting non-existent bid returns 404"""
        self.client.force_login(self.bidder)
        
        response = self.client.delete('/bids/99999/delete/')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_requires_authentication(self):
        """Test delete requires login"""
        bid = Bid.objects.create(
            bidder=self.bidder,
            item=self.item,
            bid_amount=150
        )
        
        response = self.client.delete(f'/bids/{bid.id}/delete/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_delete_method_only(self):
        """Test only DELETE method is allowed"""
        bid = Bid.objects.create(
            bidder=self.bidder,
            item=self.item,
            bid_amount=150
        )
        
        self.client.force_login(self.bidder)
        response = self.client.get(f'/bids/{bid.id}/delete/')
        self.assertEqual(response.status_code, 405)


class GetUserBidsTest(TestCase):
    """Test get user bids view"""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            first_name='User',
            last_name='One',
            email='user1@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            first_name='User',
            last_name='Two',
            email='user2@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            first_name='Owner',
            last_name='User',
            email='owner@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        
        future_date = date.today() + timedelta(days=7)
        
        # Create items
        self.item1 = Item.objects.create(
            title='Item 1',
            description='Description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=future_date
        )
        self.item2 = Item.objects.create(
            title='Item 2',
            description='Description',
            owner=self.owner,
            minimum_bid=200,
            auction_end_date=future_date
        )
        
        # User1's bids
        Bid.objects.create(bidder=self.user1, item=self.item1, bid_amount=150)
        Bid.objects.create(bidder=self.user1, item=self.item2, bid_amount=250)
        
        # User2's bid
        Bid.objects.create(bidder=self.user2, item=self.item1, bid_amount=200)
    
    def test_get_own_bids(self):
        """Test getting own bids"""
        self.client.force_login(self.user1)
        
        response = self.client.get('/users/me/bids/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 2)
        
        # Verify bids belong to user1
        for bid in data['bids']:
            self.assertEqual(bid['bidder']['id'], self.user1.id)
    
    def test_get_specific_user_bids_as_admin(self):
        """Test admin can get specific user's bids"""
        self.client.force_login(self.admin)
        
        response = self.client.get(f'/users/{self.user2.id}/bids/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['bids'][0]['bidder']['id'], self.user2.id)
    
    def test_cannot_get_other_user_bids(self):
        """Test user cannot get another user's bids"""
        self.client.force_login(self.user1)
        
        response = self.client.get(f'/users/{self.user2.id}/bids/')
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('permission', data['error'].lower())
    
    def test_get_bids_for_nonexistent_user(self):
        """Test getting bids for non-existent user"""
        self.client.force_login(self.admin)
        
        response = self.client.get('/users/99999/bids/')
        self.assertEqual(response.status_code, 404)
    
    def test_requires_authentication(self):
        """Test get user bids requires login"""
        response = self.client.get('/users/me/bids/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_get_method_only(self):
        """Test only GET method is allowed"""
        self.client.force_login(self.user1)
        response = self.client.post('/users/me/bids/')
        self.assertEqual(response.status_code, 405)


class GetItemBidsTest(TestCase):
    """Test get item bids view"""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            first_name='User',
            last_name='One',
            email='user1@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            first_name='User',
            last_name='Two',
            email='user2@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            first_name='Owner',
            last_name='User',
            email='owner@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        
        future_date = date.today() + timedelta(days=7)
        
        # Create item
        self.item = Item.objects.create(
            title='Test Item',
            description='Description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=future_date
        )
        
        # Create bids
        Bid.objects.create(bidder=self.user1, item=self.item, bid_amount=150)
        Bid.objects.create(bidder=self.user2, item=self.item, bid_amount=200)
        Bid.objects.create(bidder=self.user1, item=self.item, bid_amount=250)
    
    def test_get_item_bids(self):
        """Test getting all bids for an item"""
        self.client.force_login(self.user1)
        
        response = self.client.get(f'/items/{self.item.id}/bids/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 3)
        
        # Verify bids are sorted by amount (highest first)
        self.assertEqual(data['bids'][0]['bid_amount'], 250)
        self.assertEqual(data['bids'][1]['bid_amount'], 200)
        self.assertEqual(data['bids'][2]['bid_amount'], 150)
    
    def test_get_bids_for_nonexistent_item(self):
        """Test getting bids for non-existent item"""
        self.client.force_login(self.user1)
        
        response = self.client.get('/items/99999/bids/')
        self.assertEqual(response.status_code, 404)
    
    def test_get_bids_for_item_with_no_bids(self):
        """Test getting bids for item with no bids"""
        future_date = date.today() + timedelta(days=7)
        item_no_bids = Item.objects.create(
            title='No Bids Item',
            description='Description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=future_date
        )
        
        self.client.force_login(self.user1)
        response = self.client.get(f'/items/{item_no_bids.id}/bids/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['bids']), 0)
    
    def test_requires_authentication(self):
        """Test get item bids requires login"""
        response = self.client.get(f'/items/{self.item.id}/bids/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_get_method_only(self):
        """Test only GET method is allowed"""
        self.client.force_login(self.user1)
        response = self.client.post(f'/items/{self.item.id}/bids/')
        self.assertEqual(response.status_code, 405)


class GetUserBiddedItemsTest(TestCase):
    """Test get user bidded items view"""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            first_name='User',
            last_name='One',
            email='user1@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            first_name='User',
            last_name='Two',
            email='user2@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        self.owner = User.objects.create_user(
            first_name='Owner',
            last_name='User',
            email='owner@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        
        future_date = date.today() + timedelta(days=7)
        past_date = date.today() - timedelta(days=1)
        
        # Create active item
        self.active_item = Item.objects.create(
            title='Active Item',
            description='Description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=future_date
        )
        
        # Create expired item (won by user1)
        self.won_item = Item.objects.create(
            title='Won Item',
            description='Description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=past_date
        )
        
        # Create expired item (lost by user1)
        self.lost_item = Item.objects.create(
            title='Lost Item',
            description='Description',
            owner=self.owner,
            minimum_bid=100,
            auction_end_date=past_date
        )
        
        # User1 bids on active item (winning)
        Bid.objects.create(bidder=self.user1, item=self.active_item, bid_amount=150)
        
        # User1 bids on won item (highest bid)
        Bid.objects.create(bidder=self.user1, item=self.won_item, bid_amount=200)
        
        # User1 bids on lost item (not highest)
        Bid.objects.create(bidder=self.user1, item=self.lost_item, bid_amount=150)
        Bid.objects.create(bidder=self.user2, item=self.lost_item, bid_amount=200)
    
    def test_get_own_bidded_items(self):
        """Test getting own bidded items"""
        self.client.force_login(self.user1)
        
        response = self.client.get('/users/me/bidded-items/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 3)
    
    def test_bidded_items_show_correct_status(self):
        """Test bidded items show correct auction status"""
        self.client.force_login(self.user1)
        
        response = self.client.get('/users/me/bidded-items/')
        data = response.json()
        
        items_by_title = {item['title']: item for item in data['items']}
        
        # Check active item status
        self.assertEqual(items_by_title['Active Item']['status'], 'ongoing')
        self.assertTrue(items_by_title['Active Item']['is_winning'])
        
        # Check won item status
        self.assertEqual(items_by_title['Won Item']['status'], 'won')
        self.assertTrue(items_by_title['Won Item']['is_winning'])
        
        # Check lost item status
        self.assertEqual(items_by_title['Lost Item']['status'], 'lost')
        self.assertFalse(items_by_title['Lost Item']['is_winning'])
    
    def test_bidded_items_show_latest_bid(self):
        """Test bidded items show user's latest bid"""
        self.client.force_login(self.user1)
        
        # User1 makes multiple bids on active item
        Bid.objects.create(bidder=self.user1, item=self.active_item, bid_amount=180)
        Bid.objects.create(bidder=self.user1, item=self.active_item, bid_amount=220)
        
        response = self.client.get('/users/me/bidded-items/')
        data = response.json()
        
        active_item_data = next(
            item for item in data['items'] if item['title'] == 'Active Item'
        )
        
        # Should show highest bid amount (220)
        self.assertEqual(active_item_data['my_latest_bid']['bid_amount'], 220)
    
    def test_bidded_items_no_duplicates(self):
        """Test items appear only once even with multiple bids"""
        self.client.force_login(self.user1)
        
        # Create multiple bids on same item
        Bid.objects.create(bidder=self.user1, item=self.active_item, bid_amount=180)
        Bid.objects.create(bidder=self.user1, item=self.active_item, bid_amount=200)
        Bid.objects.create(bidder=self.user1, item=self.active_item, bid_amount=220)
        
        response = self.client.get('/users/me/bidded-items/')
        data = response.json()
        
        # Count how many times active_item appears
        active_item_count = sum(
            1 for item in data['items'] if item['title'] == 'Active Item'
        )
        
        self.assertEqual(active_item_count, 1)
    
    def test_admin_can_view_other_user_bidded_items(self):
        """Test admin can view other user's bidded items"""
        self.client.force_login(self.admin)
        
        response = self.client.get(f'/users/{self.user1.id}/bidded-items/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['user']['id'], self.user1.id)
    
    def test_cannot_view_other_user_bidded_items(self):
        """Test user cannot view another user's bidded items"""
        self.client.force_login(self.user2)
        
        response = self.client.get(f'/users/{self.user1.id}/bidded-items/')
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn('permission', data['error'].lower())
    
    def test_user_with_no_bids(self):
        """Test user with no bids returns empty list"""
        user_no_bids = User.objects.create_user(
            first_name='No',
            last_name='Bids',
            email='nobids@example.com',
            date_of_birth=date(1990, 1, 1),
            password='testpass123'
        )
        
        self.client.force_login(user_no_bids)
        response = self.client.get('/users/me/bidded-items/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['items']), 0)
    
    def test_requires_authentication(self):
        """Test get bidded items requires login"""
        response = self.client.get('/users/me/bidded-items/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_get_method_only(self):
        """Test only GET method is allowed"""
        self.client.force_login(self.user1)
        response = self.client.post('/users/me/bidded-items/')
        self.assertEqual(response.status_code, 405)
