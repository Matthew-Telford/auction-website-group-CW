from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import User
import json


def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, "api/spa/index.html", {})


def user_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    # Handle JSON body from fetch
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
    except (json.JSONDecodeError, ValueError):
        # Fallback to form data
        email = request.POST.get("email")
        password = request.POST.get("password")
    
    if not email or not password:
        return JsonResponse({"error": "Email and password are required"}, status=400)
    
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        
        # Include user data with profile picture URL
        user_data = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        
        # Add profile picture URL if exists
        if user.profile_picture:
            user_data["profile_picture"] = request.build_absolute_uri(user.profile_picture.url)
        else:
            user_data["profile_picture"] = None
        
        return JsonResponse({
            "success": True,
            "message": "Login successful",
            "user": user_data
        })
    else:
        return JsonResponse({"error": "Invalid email or password"}, status=401)


@login_required
def get_user_profile(request):
    """Get the current user's profile"""
    user = request.user
    
    user_data = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "date_of_birth": str(user.date_of_birth),
        "profile_picture": request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }
    
    return JsonResponse(user_data)


@login_required
@csrf_exempt
def upload_profile_picture(request):
    """Upload or update user's profile picture"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    if 'profile_picture' not in request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)
    
    user = request.user
    profile_picture = request.FILES['profile_picture']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if profile_picture.content_type not in allowed_types:
        return JsonResponse({
            "error": "Invalid file type. Allowed types: JPEG, PNG, GIF, WebP"
        }, status=400)
    
    # Validate file size (e.g., max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if profile_picture.size > max_size:
        return JsonResponse({
            "error": "File too large. Maximum size is 5MB"
        }, status=400)
    
    # Delete old profile picture if exists
    if user.profile_picture:
        user.profile_picture.delete(save=False)
    
    # Save new profile picture
    user.profile_picture = profile_picture
    user.save()
    
    return JsonResponse({
        "success": True,
        "message": "Profile picture uploaded successfully",
        "profile_picture": request.build_absolute_uri(user.profile_picture.url)
    })


@login_required
@csrf_exempt
def delete_profile_picture(request):
    """Delete user's profile picture"""
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    user = request.user
    
    if not user.profile_picture:
        return JsonResponse({"error": "No profile picture to delete"}, status=404)
    
    # Delete the file
    user.profile_picture.delete(save=False)
    user.profile_picture = None
    user.save()
    
    return JsonResponse({
        "success": True,
        "message": "Profile picture deleted successfully"
    })