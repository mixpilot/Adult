"""
Custom decorators for the adult entertainment website.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.http import JsonResponse
from datetime import datetime, timedelta
from accounts.models import User


def age_verified_required(view_func):
    """
    Decorator to ensure user has verified their age (18+).
    Checks if user has a date_of_birth set and is at least 18 years old.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this content.')
            return redirect('accounts:login')
        
        # Check if user has verified age
        if not request.user.date_of_birth:
            messages.warning(request, 'Please verify your age in your profile settings.')
            return redirect('accounts:profile')
        
        # Check if user is at least 18 years old
        today = datetime.now().date()
        age = (today - request.user.date_of_birth).days // 365
        if age < 18:
            messages.error(request, 'You must be 18 years or older to access this content.')
            return redirect('core:home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def premium_required(view_func):
    """
    Decorator to ensure user has premium/buyer access.
    Sellers (escorts) are free; buyers need an active subscription.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this content.')
            return redirect('accounts:login')

        if request.user.needs_paid_subscription():
            messages.warning(request, 'Subscribe to unlock browsing, messaging, and connections.')
            return redirect('subscriptions:plans')

        return view_func(request, *args, **kwargs)
    return _wrapped_view


def buyer_subscription_required(view_func):
    """Alias: buyers must pay; sellers pass through."""
    return premium_required(view_func)


def verified_user_required(view_func):
    """
    Decorator to ensure user account is verified.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this feature.')
            return redirect('accounts:login')
        
        if not request.user.is_verified:
            messages.warning(request, 'Please verify your account to access this feature.')
            return redirect('accounts:profile')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def rate_limit(max_requests=5, period=60, key_prefix='rate_limit'):
    """
    Decorator to rate limit requests.
    
    Args:
        max_requests: Maximum number of requests allowed
        period: Time period in seconds
        key_prefix: Cache key prefix
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                cache_key = f'{key_prefix}_{request.user.id}'
            else:
                cache_key = f'{key_prefix}_{request.META.get("REMOTE_ADDR")}'
            
            # Get current request count
            request_count = cache.get(cache_key, 0)
            
            if request_count >= max_requests:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Rate limit exceeded. Please try again later.'
                    }, status=429)
                messages.error(request, f'Rate limit exceeded. Please wait {period} seconds before trying again.')
                return redirect(request.META.get('HTTP_REFERER', 'core:home'))
            
            # Increment request count
            cache.set(cache_key, request_count + 1, period)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def staff_or_owner_required(view_func):
    """
    Decorator to ensure user is staff or owns the resource.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this feature.')
            return redirect('accounts:login')
        
        # Staff can access anything
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        # Check if user owns the resource (for content uploader, etc.)
        # This will be checked in the view itself
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def ajax_required(view_func):
    """
    Decorator to ensure request is AJAX.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX request required'}, status=400)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def check_premium_content(view_func):
    """
    Decorator to check if content is premium and user has access.
    Used for content detail views.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from content.models import Content
        
        # Get content from slug if available
        slug = kwargs.get('slug')
        if slug:
            try:
                content = Content.objects.get(slug=slug)
                if content.is_premium:
                    if not request.user.is_authenticated:
                        messages.warning(request, 'Please login to access premium content.')
                        return redirect('accounts:login')
                    elif not request.user.has_premium_access():
                        messages.warning(request, 'Premium subscription required to access this content.')
                        return redirect('subscriptions:plans')
            except Content.DoesNotExist:
                pass
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
