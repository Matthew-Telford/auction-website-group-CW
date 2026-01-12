from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, IntegerField, Value, F, Max
from django.core.files.base import ContentFile
from .models import User, Item, Bid, Message
import json
import re
import io
from datetime import date
from PIL import Image


@ensure_csrf_cookie
def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, "api/spa/index.html", {})


"""
Example fetch request for user login
------------------------------------------------
    await fetch("http://localhost:8000/login/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        credentials: "include", // Important: sends cookies
        body: JSON.stringify({ email, password }),
    });

"""


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
            user_data["profile_picture"] = request.build_absolute_uri(
                user.profile_picture.url
            )
        else:
            user_data["profile_picture"] = None

        return JsonResponse(
            {"success": True, "message": "Login successful", "user": user_data}
        )
    else:
        return JsonResponse({"error": "Invalid email or password"}, status=401)


"""
Example fetch request for get user profile
------------------------------------------------
    await fetch("http://localhost:8000/profile/", {
        method: "GET",
        credentials: "include",
    });

"""


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
        "profile_picture": request.build_absolute_uri(user.profile_picture.url)
        if user.profile_picture
        else None,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }

    return JsonResponse(user_data)


"""
Example fetch request for upload profile picture
------------------------------------------------
    const formData = new FormData();
    formData.append("profile_picture", fileInput.files[0]);
    
    await fetch("http://localhost:8000/profile/picture/upload/", {
        method: "POST",
        credentials: "include",
        body: formData,
    });

"""


@login_required
@csrf_exempt
def upload_profile_picture(request):
    """Upload or update user's profile picture"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    if "profile_picture" not in request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    user = request.user
    profile_picture = request.FILES["profile_picture"]

    # Validate file size BEFORE processing (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if profile_picture.size > max_size:
        return JsonResponse(
            {"error": "File too large. Maximum size is 5MB"}, status=400
        )

    try:
        # Open and verify the image using Pillow
        image = Image.open(profile_picture)
        
        # Verify it's actually an image (this will raise an exception if not)
        image.verify()
        
        # Re-open the image after verify() (verify() closes the file)
        profile_picture.seek(0)
        image = Image.open(profile_picture)
        
        # Convert RGBA to RGB if necessary (for JPEG compatibility)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Resize if image is too large (optional but recommended)
        max_dimension = 1024  # Max width or height
        if image.width > max_dimension or image.height > max_dimension:
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Save the processed image to a BytesIO buffer
        output = io.BytesIO()
        image_format = 'JPEG'  # Standardize to JPEG
        image.save(output, format=image_format, quality=85, optimize=True)
        output.seek(0)
        
        # Delete old profile picture if exists
        if user.profile_picture:
            user.profile_picture.delete(save=False)
        
        # Save the processed image
        filename = f"user_{user.id}_profile.jpg"
        user.profile_picture.save(
            filename,
            ContentFile(output.read()),
            save=True
        )
        
        return JsonResponse(
            {
                "success": True,
                "message": "Profile picture uploaded successfully",
                "profile_picture": request.build_absolute_uri(user.profile_picture.url),
            }
        )
        
    except (IOError, OSError) as e:
        # Handle Pillow errors (invalid image, corrupt file, etc.)
        return JsonResponse(
            {"error": "Invalid or corrupt image file"}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"Failed to process image: {str(e)}"}, status=500
        )


"""
Example fetch request for delete profile picture
------------------------------------------------
    await fetch("http://localhost:8000/profile/picture/delete/", {
        method: "DELETE",
        credentials: "include",
    });

"""


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

    return JsonResponse(
        {"success": True, "message": "Profile picture deleted successfully"}
    )


"""
Example fetch request for user signup
------------------------------------------------
    await fetch("http://localhost:8000/signup/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify({
            first_name: "John",
            last_name: "Doe",
            email: "john@example.com",
            password: "securepass123",
            date_of_birth: "1990-01-01"
        }),
    });

"""


def user_signup(request):
    """Create a new user account"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Handle JSON body from fetch
    try:
        data = json.loads(request.body)
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        password = data.get("password")
        date_of_birth = data.get("date_of_birth")
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    # Validate required fields
    if not all([first_name, last_name, email, password, date_of_birth]):
        return JsonResponse(
            {
                "error": "All fields are required (first_name, last_name, email, password, date_of_birth)"
            },
            status=400,
        )

    # Check if user already exists
    if User.objects.filter(email=email).exists():
        return JsonResponse(
            {"error": "User with this email already exists"}, status=400
        )

    try:
        # Create the user
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            date_of_birth=date_of_birth,
        )

        # Log the user in automatically after signup
        login(request, user)

        # Return user data
        user_data = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_picture": None,
        }

        return JsonResponse(
            {
                "success": True,
                "message": "Account created successfully",
                "user": user_data,
            }
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"Failed to create account: {str(e)}"}, status=500
        )


"""
Example fetch request for get paginated items
------------------------------------------------
    // Without pagination or search
    await fetch("http://localhost:8000/items/", {
        method: "GET",
    });

    // With search and pagination
    await fetch("http://localhost:8000/items/?search=laptop&start=0&end=10", {
        method: "GET",
    });

"""


def get_paginated_items(request):
    """
    Get active auction items with optional search and pagination.
    Only returns items where the auction end date has not passed.
    Query parameters:
    - search: keyword to search in title and description
    - start: starting index for pagination (inclusive)
    - end: ending index for pagination (exclusive)
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Get query parameters
    search_keyword = request.GET.get("search", "").strip()
    start = request.GET.get("start")
    end = request.GET.get("end")

    # Start with all items where auction has not ended
    today = date.today()
    items = Item.objects.filter(auction_end_date__gte=today)

    # Apply search filter if keyword provided
    if search_keyword:
        # Escape special regex characters to prevent regex injection
        escaped_keyword = re.escape(search_keyword)

        # Filter items that contain the keyword in title or description
        search_filter = Q(title__icontains=search_keyword) | Q(
            description__icontains=search_keyword
        )
        items = items.filter(search_filter)

        # Calculate relevance score with different weights
        # Priority: title exact match > title partial > description exact > description partial
        items = items.annotate(
            relevance_score=Case(
                # Exact word match in title (highest priority) - weight: 100
                When(title__iregex=r"\b" + escaped_keyword + r"\b", then=Value(100)),
                # Partial match in title - weight: 50
                When(title__icontains=search_keyword, then=Value(50)),
                # Exact word match in description - weight: 20
                When(
                    description__iregex=r"\b" + escaped_keyword + r"\b", then=Value(20)
                ),
                # Partial match in description - weight: 10
                When(description__icontains=search_keyword, then=Value(10)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by("-relevance_score", "-created_at")
    else:
        # Default ordering by creation date (newest first)
        items = items.order_by("-created_at")

    # Apply pagination if both start and end are provided
    if start is not None and end is not None:
        try:
            start = int(start)
            end = int(end)
            if start < 0 or end < 0:
                return JsonResponse(
                    {"error": "Pagination indices must be non-negative"}, status=400
                )
            if start > end:
                return JsonResponse(
                    {"error": "Start index must be less than or equal to end index"},
                    status=400,
                )
            items = items[start:end]
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid pagination parameters"}, status=400)

    # Serialize items
    items_data = []
    for item in items:
        item_data = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "minimum_bid": item.minimum_bid,
            "auction_end_date": str(item.auction_end_date),
            "created_at": item.created_at.isoformat(),
        }

        # Add owner information
        if item.owner:
            item_data["owner"] = {
                "id": item.owner.id,
                "name": f"{item.owner.first_name} {item.owner.last_name}",
                "email": item.owner.email,
            }
        else:
            item_data["owner"] = None

        # Add auction winner information
        if item.auction_winner:
            item_data["auction_winner"] = {
                "id": item.auction_winner.id,
                "name": f"{item.auction_winner.first_name} {item.auction_winner.last_name}",
            }
        else:
            item_data["auction_winner"] = None

        # Add item image URL if exists
        if item.item_image:
            item_data["item_image"] = request.build_absolute_uri(item.item_image.url)
        else:
            item_data["item_image"] = None

        items_data.append(item_data)

    return JsonResponse(
        {"success": True, "items": items_data, "count": len(items_data)}
    )


"""
Example fetch request for create item
------------------------------------------------
    await fetch("http://localhost:8000/items/create/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify({
            title: "Vintage Watch",
            description: "Beautiful vintage watch in great condition",
            minimum_bid: 100,
            auction_end_date: "2026-02-15"
        }),
    });

"""


@login_required
def create_item(request):
    """Create a new auction item"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Handle JSON body
    try:
        data = json.loads(request.body)
        title = data.get("title")
        description = data.get("description")
        minimum_bid = data.get("minimum_bid")
        auction_end_date = data.get("auction_end_date")
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    # Validate required fields (checking for None explicitly to allow 0 values)
    if (
        title is None
        or description is None
        or minimum_bid is None
        or auction_end_date is None
    ):
        return JsonResponse(
            {
                "error": "All fields are required (title, description, minimum_bid, auction_end_date)"
            },
            status=400,
        )

    # Check for empty strings
    if not title or not description or not auction_end_date:
        return JsonResponse(
            {"error": "Title, description, and auction_end_date cannot be empty"},
            status=400,
        )

    # Validate minimum bid is positive
    try:
        minimum_bid = int(minimum_bid)
        if minimum_bid <= 0:
            return JsonResponse(
                {"error": "Minimum bid must be greater than 0"}, status=400
            )
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid minimum bid value"}, status=400)

    # Validate auction end date
    try:
        auction_end_date_obj = date.fromisoformat(auction_end_date)
        if auction_end_date_obj <= date.today():
            return JsonResponse(
                {"error": "Auction end date must be in the future"}, status=400
            )
    except (ValueError, TypeError):
        return JsonResponse(
            {"error": "Invalid date format. Use YYYY-MM-DD"}, status=400
        )

    try:
        # Create the item
        item = Item.objects.create(
            title=title,
            description=description,
            owner=request.user,
            minimum_bid=minimum_bid,
            auction_end_date=auction_end_date_obj,
        )

        # Return item data
        item_data = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "minimum_bid": item.minimum_bid,
            "auction_end_date": str(item.auction_end_date),
            "created_at": item.created_at.isoformat(),
            "owner": {
                "id": request.user.id,
                "name": f"{request.user.first_name} {request.user.last_name}",
                "email": request.user.email,
            },
        }

        return JsonResponse(
            {"success": True, "message": "Item created successfully", "item": item_data}
        )
    except Exception as e:
        return JsonResponse({"error": f"Failed to create item: {str(e)}"}, status=500)


"""
Example fetch request for update item
------------------------------------------------
    await fetch("http://localhost:8000/items/123/update/", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify({
            title: "Updated Title",
            minimum_bid: 150
        }),
    });

"""


@login_required
@csrf_exempt
def update_item(request, item_id):
    """Update an existing auction item (owner or admin only)"""
    if request.method != "PUT":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Get the item
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)

    # Check permissions - must be owner or admin
    if item.owner != request.user and not request.user.is_admin:
        return JsonResponse(
            {"error": "You don't have permission to edit this item"}, status=403
        )

    # Handle JSON body
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    # Update fields if provided
    if "title" in data:
        item.title = data["title"]

    if "description" in data:
        item.description = data["description"]

    if "minimum_bid" in data:
        try:
            minimum_bid = int(data["minimum_bid"])
            if minimum_bid <= 0:
                return JsonResponse(
                    {"error": "Minimum bid must be greater than 0"}, status=400
                )
            item.minimum_bid = minimum_bid
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid minimum bid value"}, status=400)

    if "auction_end_date" in data:
        try:
            auction_end_date_obj = date.fromisoformat(data["auction_end_date"])
            if auction_end_date_obj <= date.today():
                return JsonResponse(
                    {"error": "Auction end date must be in the future"}, status=400
                )
            item.auction_end_date = auction_end_date_obj
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "Invalid date format. Use YYYY-MM-DD"}, status=400
            )

    try:
        item.save()

        # Return updated item data
        item_data = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "minimum_bid": item.minimum_bid,
            "auction_end_date": str(item.auction_end_date),
            "created_at": item.created_at.isoformat(),
        }

        if item.owner:
            item_data["owner"] = {
                "id": item.owner.id,
                "name": f"{item.owner.first_name} {item.owner.last_name}",
                "email": item.owner.email,
            }

        return JsonResponse(
            {"success": True, "message": "Item updated successfully", "item": item_data}
        )
    except Exception as e:
        return JsonResponse({"error": f"Failed to update item: {str(e)}"}, status=500)


"""
Example fetch request for delete item
------------------------------------------------
    await fetch("http://localhost:8000/items/123/delete/", {
        method: "DELETE",
        credentials: "include",
    });

"""


@login_required
@csrf_exempt
def delete_item(request, item_id):
    """Delete an auction item (owner or admin only)"""
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Get the item
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)

    # Check permissions - must be owner or admin
    if item.owner != request.user and not request.user.is_admin:
        return JsonResponse(
            {"error": "You don't have permission to delete this item"}, status=403
        )

    try:
        # Delete associated image if exists
        if item.item_image:
            item.item_image.delete(save=False)

        item.delete()

        return JsonResponse({"success": True, "message": "Item deleted successfully"})
    except Exception as e:
        return JsonResponse({"error": f"Failed to delete item: {str(e)}"}, status=500)


"""
Example fetch request for get user items
------------------------------------------------
    // Get current user's items
    await fetch("http://localhost:8000/users/me/items/", {
        method: "GET",
        credentials: "include",
    });

    // Get specific user's items
    await fetch("http://localhost:8000/users/123/items/", {
        method: "GET",
        credentials: "include",
    });

"""


@login_required
def get_user_items(request, user_id=None):
    """Get all items owned by a specific user"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # If no user_id provided, use the current user
    if user_id is None:
        user_id = request.user.id

    # Get the user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # Get all items owned by this user
    items = Item.objects.filter(owner=user).order_by("-created_at")

    # Serialize items
    items_data = []
    for item in items:
        item_data = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "minimum_bid": item.minimum_bid,
            "auction_end_date": str(item.auction_end_date),
            "created_at": item.created_at.isoformat(),
            "is_active": item.auction_end_date >= date.today(),
        }

        # Add owner information
        if item.owner:
            item_data["owner"] = {
                "id": item.owner.id,
                "name": f"{item.owner.first_name} {item.owner.last_name}",
                "email": item.owner.email,
            }
        else:
            item_data["owner"] = None

        # Add auction winner information
        if item.auction_winner:
            item_data["auction_winner"] = {
                "id": item.auction_winner.id,
                "name": f"{item.auction_winner.first_name} {item.auction_winner.last_name}",
            }
        else:
            item_data["auction_winner"] = None

        # Add item image URL if exists
        if item.item_image:
            item_data["item_image"] = request.build_absolute_uri(item.item_image.url)
        else:
            item_data["item_image"] = None

        items_data.append(item_data)

    return JsonResponse(
        {
            "success": True,
            "user": {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
            },
            "items": items_data,
            "count": len(items_data),
        }
    )


"""
Example fetch request for create bid
------------------------------------------------
    await fetch("http://localhost:8000/bids/create/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify({
            item_id: 123,
            bid_amount: 150
        }),
    });

"""


@login_required
def create_bid(request):
    """Create a new bid on an item"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Handle JSON body
    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")
        bid_amount = data.get("bid_amount")
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    # Validate required fields
    if item_id is None or bid_amount is None:
        return JsonResponse(
            {"error": "Both item_id and bid_amount are required"}, status=400
        )

    # Get the item
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)

    # Check if auction has ended
    if item.auction_end_date < date.today():
        return JsonResponse({"error": "Auction has ended for this item"}, status=400)

    # Check if bidder is the owner
    if item.owner == request.user:
        return JsonResponse({"error": "You cannot bid on your own item"}, status=403)

    # Validate bid amount
    try:
        bid_amount = int(bid_amount)
        if bid_amount <= 0:
            return JsonResponse(
                {"error": "Bid amount must be greater than 0"}, status=400
            )
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid bid amount"}, status=400)

    # Get the current highest bid for this item
    highest_bid = Bid.objects.filter(item=item).aggregate(Max("bid_amount"))[
        "bid_amount__max"
    ]

    # Determine minimum required bid
    if highest_bid is not None:
        # There are existing bids, must be higher than the highest bid
        if bid_amount <= highest_bid:
            return JsonResponse(
                {
                    "error": f"Bid must be greater than the current highest bid of {highest_bid}"
                },
                status=400,
            )
    else:
        # No existing bids, must meet or exceed minimum bid
        if bid_amount < item.minimum_bid:
            return JsonResponse(
                {
                    "error": f"Bid must be at least the minimum bid of {item.minimum_bid}"
                },
                status=400,
            )

    try:
        # Create the bid
        bid = Bid.objects.create(bidder=request.user, item=item, bid_amount=bid_amount)

        # Return bid data
        bid_data = {
            "id": bid.id,
            "bid_amount": bid.bid_amount,
            "created_at": bid.created_at.isoformat(),
            "bidder": {
                "id": request.user.id,
                "name": f"{request.user.first_name} {request.user.last_name}",
                "email": request.user.email,
            },
            "item": {"id": item.id, "title": item.title},
        }

        return JsonResponse(
            {"success": True, "message": "Bid placed successfully", "bid": bid_data}
        )
    except Exception as e:
        return JsonResponse({"error": f"Failed to create bid: {str(e)}"}, status=500)


"""
Example fetch request for delete bid
------------------------------------------------
    await fetch("http://localhost:8000/bids/123/delete/", {
        method: "DELETE",
        credentials: "include",
    });

"""


@login_required
@csrf_exempt
def delete_bid(request, bid_id):
    """Delete a bid (bidder or admin only)"""
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Get the bid
    try:
        bid = Bid.objects.get(id=bid_id)
    except Bid.DoesNotExist:
        return JsonResponse({"error": "Bid not found"}, status=404)

    # Check permissions - must be bidder or admin
    if bid.bidder != request.user and not request.user.is_admin:
        return JsonResponse(
            {"error": "You don't have permission to delete this bid"}, status=403
        )

    try:
        bid.delete()

        return JsonResponse({"success": True, "message": "Bid deleted successfully"})
    except Exception as e:
        return JsonResponse({"error": f"Failed to delete bid: {str(e)}"}, status=500)


"""
Example fetch request for get user bids
------------------------------------------------
    // Get current user's bids
    await fetch("http://localhost:8000/users/me/bids/", {
        method: "GET",
        credentials: "include",
    });

    // Get specific user's bids (admin only)
    await fetch("http://localhost:8000/users/123/bids/", {
        method: "GET",
        credentials: "include",
    });

"""


@login_required
def get_user_bids(request, user_id=None):
    """Get all bids made by a specific user (own bids only, unless admin)"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # If no user_id provided, use the current user
    if user_id is None:
        user_id = request.user.id

    # Get the user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # Check permissions - users can only view their own bids unless they're an admin
    if user != request.user and not request.user.is_admin:
        return JsonResponse(
            {"error": "You don't have permission to view another user's bids"},
            status=403,
        )

    # Get all bids made by this user
    bids = (
        Bid.objects.filter(bidder=user).select_related("item").order_by("-created_at")
    )

    # Serialize bids
    bids_data = []
    for bid in bids:
        bid_data = {
            "id": bid.id,
            "bid_amount": bid.bid_amount,
            "created_at": bid.created_at.isoformat(),
        }

        # Add bidder information
        if bid.bidder:
            bid_data["bidder"] = {
                "id": bid.bidder.id,
                "name": f"{bid.bidder.first_name} {bid.bidder.last_name}",
                "email": bid.bidder.email,
            }
        else:
            bid_data["bidder"] = None

        # Add item information
        if bid.item:
            bid_data["item"] = {
                "id": bid.item.id,
                "title": bid.item.title,
                "auction_end_date": str(bid.item.auction_end_date),
                "is_active": bid.item.auction_end_date >= date.today(),
            }
        else:
            bid_data["item"] = None

        bids_data.append(bid_data)

    return JsonResponse(
        {
            "success": True,
            "user": {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
            },
            "bids": bids_data,
            "count": len(bids_data),
        }
    )


"""
Example fetch request for get item bids
------------------------------------------------
    await fetch("http://localhost:8000/items/123/bids/", {
        method: "GET",
        credentials: "include",
    });

"""


@login_required
def get_item_bids(request, item_id):
    """Get all bids for a specific item"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Get the item
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)

    # Get all bids for this item
    bids = (
        Bid.objects.filter(item=item).select_related("bidder").order_by("-bid_amount")
    )

    # Serialize bids
    bids_data = []
    for bid in bids:
        bid_data = {
            "id": bid.id,
            "bid_amount": bid.bid_amount,
            "created_at": bid.created_at.isoformat(),
        }

        # Add bidder information
        if bid.bidder:
            bid_data["bidder"] = {
                "id": bid.bidder.id,
                "name": f"{bid.bidder.first_name} {bid.bidder.last_name}",
                "email": bid.bidder.email,
            }
        else:
            bid_data["bidder"] = None

        bids_data.append(bid_data)

    return JsonResponse(
        {
            "success": True,
            "item": {
                "id": item.id,
                "title": item.title,
                "minimum_bid": item.minimum_bid,
                "auction_end_date": str(item.auction_end_date),
                "is_active": item.auction_end_date >= date.today(),
            },
            "bids": bids_data,
            "count": len(bids_data),
        }
    )


"""
Example fetch request for get user bidded items
------------------------------------------------
    // Get current user's bidded items
    await fetch("http://localhost:8000/users/me/bidded-items/", {
        method: "GET",
        credentials: "include",
    });

    // Get specific user's bidded items (admin only)
    await fetch("http://localhost:8000/users/123/bidded-items/", {
        method: "GET",
        credentials: "include",
    });

"""


@login_required
def get_user_bidded_items(request, user_id=None):
    """
    Get all items a user has bid on with their most recent bid and auction status.
    Users can only view their own bidded items unless they're an admin.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # If no user_id provided, use the current user
    if user_id is None:
        user_id = request.user.id

    # Get the user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # Check permissions - users can only view their own bidded items unless they're an admin
    if user != request.user and not request.user.is_admin:
        return JsonResponse(
            {"error": "You don't have permission to view another user's bidded items"},
            status=403,
        )

    # Get all distinct items the user has bid on
    item_ids = (
        Bid.objects.filter(bidder=user).values_list("item_id", flat=True).distinct()
    )
    items = Item.objects.filter(id__in=item_ids).select_related("owner")

    today = date.today()
    items_data = []

    for item in items:
        # Get the user's most recent bid on this item
        user_latest_bid = (
            Bid.objects.filter(bidder=user, item=item).order_by("-created_at").first()
        )

        # Get the highest bid on this item
        highest_bid = Bid.objects.filter(item=item).aggregate(Max("bid_amount"))[
            "bid_amount__max"
        ]

        # Get all bids with the highest amount (in case of ties)
        highest_bidders = Bid.objects.filter(
            item=item, bid_amount=highest_bid
        ).values_list("bidder_id", flat=True)

        # Determine auction status
        if item.auction_end_date >= today:
            status = "ongoing"
            is_winning = user.id in highest_bidders if highest_bidders else False
        else:
            # Auction has ended
            if user.id in highest_bidders:
                status = "won"
                is_winning = True
            else:
                status = "lost"
                is_winning = False

        # Build item data
        item_data = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "minimum_bid": item.minimum_bid,
            "auction_end_date": str(item.auction_end_date),
            "is_active": item.auction_end_date >= today,
            "status": status,
            "is_winning": is_winning,
            "highest_bid": highest_bid,
        }

        # Add owner information
        if item.owner:
            item_data["owner"] = {
                "id": item.owner.id,
                "name": f"{item.owner.first_name} {item.owner.last_name}",
                "email": item.owner.email,
            }
        else:
            item_data["owner"] = None

        # Add item image URL if exists
        if item.item_image:
            item_data["item_image"] = request.build_absolute_uri(item.item_image.url)
        else:
            item_data["item_image"] = None

        # Add user's most recent bid information
        if user_latest_bid:
            item_data["my_latest_bid"] = {
                "id": user_latest_bid.id,
                "bid_amount": user_latest_bid.bid_amount,
                "created_at": user_latest_bid.created_at.isoformat(),
            }
        else:
            item_data["my_latest_bid"] = None

        items_data.append(item_data)

    # Sort by auction end date (active auctions first, then by end date)
    items_data.sort(
        key=lambda x: (x["auction_end_date"] < str(today), x["auction_end_date"])
    )

    return JsonResponse(
        {
            "success": True,
            "user": {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
            },
            "items": items_data,
            "count": len(items_data),
        }
    )


"""
Example fetch request for create message
------------------------------------------------
    // Create a top-level message
    await fetch("http://localhost:8000/messages/create/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify({
            item_id: 123,
            message_title: "Question about item",
            message_body: "Is this still available?"
        }),
    });

    // Create a reply message
    await fetch("http://localhost:8000/messages/create/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify({
            item_id: 123,
            message_title: "Re: Question about item",
            message_body: "Yes, it's still available!",
            replying_to_id: 456
        }),
    });

"""


@login_required
def create_message(request):
    """Create a new message on an item (can be a reply or top-level message)"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")
        message_title = data.get("message_title")
        message_body = data.get("message_body")
        replying_to_id = data.get("replying_to_id")
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    if not all([item_id, message_title, message_body]):
        return JsonResponse(
            {"error": "item_id, message_title, and message_body are required"},
            status=400,
        )

    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)

    replying_to = None
    if replying_to_id:
        try:
            replying_to = Message.objects.get(id=replying_to_id)
            if replying_to.item != item:
                return JsonResponse(
                    {
                        "error": "Reply must be connected to the same item as the parent message"
                    },
                    status=400,
                )
        except Message.DoesNotExist:
            return JsonResponse({"error": "Parent message not found"}, status=404)

    try:
        message = Message.objects.create(
            poster=request.user,
            item=item,
            message_title=message_title,
            message_body=message_body,
            replying_to=replying_to,
        )

        message_data = {
            "id": message.id,
            "message_title": message.message_title,
            "message_body": message.message_body,
            "created_at": message.created_at.isoformat(),
            "poster": {
                "id": request.user.id,
                "name": f"{request.user.first_name} {request.user.last_name}",
                "email": request.user.email,
            }
            if message.poster
            else None,
            "item_id": item.id,
            "replying_to_id": replying_to.id if replying_to else None,
            "is_owner": message.poster == item.owner
            if message.poster and item.owner
            else False,
        }

        return JsonResponse(
            {
                "success": True,
                "message": "Message created successfully",
                "data": message_data,
            }
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"Failed to create message: {str(e)}"}, status=500
        )


"""
Example fetch request for get item messages
------------------------------------------------
    await fetch("http://localhost:8000/items/123/messages/", {
        method: "GET",
        credentials: "include",
    });

"""


@login_required
def get_item_messages(request, item_id):
    """Get all messages for a specific item in nested format"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)

    all_messages = (
        Message.objects.filter(item=item)
        .select_related("poster", "replying_to")
        .order_by("created_at")
    )

    messages_dict = {}
    top_level_messages = []

    for message in all_messages:
        message_data = {
            "id": message.id,
            "message_title": message.message_title,
            "message_body": message.message_body,
            "created_at": message.created_at.isoformat(),
            "poster": {
                "id": message.poster.id,
                "name": f"{message.poster.first_name} {message.poster.last_name}",
                "email": message.poster.email,
            }
            if message.poster
            else None,
            "is_owner": message.poster == item.owner
            if message.poster and item.owner
            else False,
            "replying_to_id": message.replying_to.id if message.replying_to else None,
            "replies": [],
        }

        messages_dict[message.id] = message_data

        if message.replying_to is None:
            top_level_messages.append(message_data)

    for message in all_messages:
        if message.replying_to and message.replying_to.id in messages_dict:
            messages_dict[message.replying_to.id]["replies"].append(
                messages_dict[message.id]
            )

    return JsonResponse(
        {
            "success": True,
            "item": {"id": item.id, "title": item.title},
            "messages": top_level_messages,
            "count": len(top_level_messages),
        }
    )


"""
Example fetch request for update message
------------------------------------------------
    await fetch("http://localhost:8000/messages/123/update/", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify({
            message_title: "Updated question",
            message_body: "Updated body text"
        }),
    });

"""


@login_required
@csrf_exempt
def update_message(request, message_id):
    """Update a message (poster or admin only, title and body only)"""
    if request.method != "PUT":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return JsonResponse({"error": "Message not found"}, status=404)

    if message.poster != request.user and not request.user.is_admin:
        return JsonResponse(
            {"error": "You don't have permission to edit this message"}, status=403
        )

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    if "message_title" in data:
        if not data["message_title"]:
            return JsonResponse({"error": "Message title cannot be empty"}, status=400)
        message.message_title = data["message_title"]

    if "message_body" in data:
        if not data["message_body"]:
            return JsonResponse({"error": "Message body cannot be empty"}, status=400)
        message.message_body = data["message_body"]

    try:
        message.save()

        message_data = {
            "id": message.id,
            "message_title": message.message_title,
            "message_body": message.message_body,
            "created_at": message.created_at.isoformat(),
            "poster": {
                "id": message.poster.id,
                "name": f"{message.poster.first_name} {message.poster.last_name}",
                "email": message.poster.email,
            }
            if message.poster
            else None,
            "item_id": message.item.id,
            "replying_to_id": message.replying_to.id if message.replying_to else None,
            "is_owner": message.poster == message.item.owner
            if message.poster and message.item.owner
            else False,
        }

        return JsonResponse(
            {
                "success": True,
                "message": "Message updated successfully",
                "data": message_data,
            }
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"Failed to update message: {str(e)}"}, status=500
        )


"""
Example fetch request for delete message
------------------------------------------------
    await fetch("http://localhost:8000/messages/123/delete/", {
        method: "DELETE",
        credentials: "include",
    });

"""


@login_required
@csrf_exempt
def delete_message(request, message_id):
    """Delete a message (poster or admin only)"""
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return JsonResponse({"error": "Message not found"}, status=404)

    if message.poster != request.user and not request.user.is_admin:
        return JsonResponse(
            {"error": "You don't have permission to delete this message"}, status=403
        )

    try:
        message.delete()

        return JsonResponse(
            {"success": True, "message": "Message deleted successfully"}
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"Failed to delete message: {str(e)}"}, status=500
        )
