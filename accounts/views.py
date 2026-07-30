from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_http_methods
from core.decorators import rate_limit
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User


@require_http_methods(["GET", "POST"])
@rate_limit(max_requests=5, period=3600, key_prefix='register')
def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            login(request, user)

            # Sellers (escorts) are free — activate and send to dashboard
            if user.user_type == 'escort':
                if not user.is_verified:
                    user.is_verified = True
                    user.save(update_fields=['is_verified'])
                messages.success(
                    request,
                    f'Welcome, {username}! Seller accounts are free — complete your profile to start receiving clients.',
                )
                return redirect('core:home')

            # Buyers must subscribe before using the platform
            messages.success(
                request,
                f'Welcome, {username}! Choose a plan to unlock browsing and messaging.',
            )
            return redirect(reverse('subscriptions:plans') + '?new_user=1')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view."""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Handle "Remember me" - set session expiry
                if remember_me:
                    # Session expires in 2 weeks (persistent cookie)
                    request.session.set_expiry(1209600)  # 14 days in seconds
                    # Ensure the session cookie is persistent (not session-only)
                    request.session.setdefault('remember_me', True)
                else:
                    # Session expires when browser closes (session cookie)
                    request.session.set_expiry(0)
                    request.session.setdefault('remember_me', False)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url and next_url.startswith('/') and '//' not in next_url:
                    return redirect(next_url)
                return redirect('core:home')
    else:
        form = UserLoginForm()
    next_param = request.GET.get('next', '')
    return render(request, 'accounts/login.html', {'form': form, 'next': next_param})


@login_required
def profile_view(request):
    """User profile view."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Account statistics
    from content.models import Content, Comment
    from connections.models import Connection, Message
    
    stats = {
        'content_uploaded': Content.objects.filter(uploader=request.user).count(),
        'comments_made': Comment.objects.filter(user=request.user).count(),
        'connections': Connection.objects.filter(
            from_user=request.user, status='matched'
        ).count(),
        'messages_sent': Message.objects.filter(sender=request.user).count(),
        'account_created': request.user.date_joined.strftime('%B %d, %Y') if request.user.date_joined else 'N/A',
        'last_login': request.user.last_login.strftime('%B %d, %Y at %I:%M %p') if request.user.last_login else 'Never',
    }
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'stats': stats
    })


@login_required
@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Custom logout view with success message."""
    from django.contrib.auth import logout
    
    # Store username for message
    username = request.user.username
    
    # Update user's online status if they have a hookup profile
    try:
        if hasattr(request.user, 'hookup_profile'):
            request.user.hookup_profile.is_online = False
            request.user.hookup_profile.save(update_fields=['is_online'])
    except Exception:
        pass  # Ignore if profile doesn't exist
    
    # Logout the user (clears session)
    logout(request)
    
    # Show success message
    messages.success(request, f'You have been successfully logged out. Goodbye, {username}!')
    
    # Redirect to home page
    return redirect('core:home')
