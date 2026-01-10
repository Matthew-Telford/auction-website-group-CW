from django.test import TestCase, Client
from django.contrib.auth import authenticate, get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
import json
import io
from PIL import Image

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
