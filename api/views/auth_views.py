"""
Authentication-related API views for NextHR.

This module contains all views related to user authentication,
including login, logout, user profile, and CSRF token management.
"""
import json
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])  # Remove all authentication classes to avoid CSRF checks
def api_login(request):
    """
    API endpoint for user authentication
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({
                'error': 'Username and password are required'
            }, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                },
                'message': 'Login successful'
            })
        else:
            return JsonResponse({
                'error': 'Invalid credentials'
            }, status=401)

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Login failed',
            'message': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_logout(request):
    """
    API endpoint for user logout
    """
    try:
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        return JsonResponse({
            'error': 'Logout failed',
            'message': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_profile(request):
    """
    API endpoint to get current user profile
    """
    try:
        user = request.user
        return JsonResponse({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            }
        })
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to fetch user profile',
            'message': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def api_csrf_token(request):
    """
    API endpoint to get a fresh CSRF token
    This endpoint ensures a CSRF cookie is set and returns the token
    """
    try:
        # get_token() will create a new token if needed and ensure the cookie is set
        csrf_token = get_token(request)
        return JsonResponse({
            'csrf_token': csrf_token,
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to generate CSRF token',
            'message': str(e)
        }, status=500)