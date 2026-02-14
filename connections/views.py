from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from core.decorators import age_verified_required, rate_limit, ajax_required
from .models import UserProfile, ProfilePhoto, Connection, Message, Visit, UserReport
from .forms import UserProfileForm, ProfilePhotoForm, MessageForm, UserSearchForm, UserReportForm
from accounts.models import User


@login_required
@age_verified_required
def browse_users(request):
    """Browse and search for escorts (only users with escort profiles)."""
    # Escorts don't need to browse other escorts - they're service providers
    if request.user.user_type == 'escort':
        messages.info(request, 'This page is for clients looking for escorts.')
        return redirect('core:home')
    
    form = UserSearchForm(request.GET)
    
    # By default show all verified escorts (User.is_verified OR profile is/id/phone verified)
    # Photo optional so verified escorts show even before uploading a photo
    users = User.objects.exclude(id=request.user.id).filter(
        user_type='escort',
        hookup_profile__isnull=False,
        hookup_profile__hide_from_search=False,
    ).filter(
        Q(is_verified=True) |
        Q(hookup_profile__is_verified=True) |
        Q(hookup_profile__id_verified=True) |
        Q(hookup_profile__phone_verified=True)
    ).select_related('hookup_profile').distinct()
    
    # Filter by search criteria
    if form.is_valid():
        if form.cleaned_data.get('gender'):
            users = users.filter(hookup_profile__gender=form.cleaned_data['gender'])
        
        if form.cleaned_data.get('seeking'):
            # Users seeking the current user's gender or everyone
            current_user_gender = getattr(request.user.hookup_profile, 'gender', None)
            if current_user_gender:
                users = users.filter(
                    Q(hookup_profile__seeking=current_user_gender) |
                    Q(hookup_profile__seeking='everyone')
                )
        
        if form.cleaned_data.get('min_age'):
            users = users.filter(hookup_profile__age__gte=form.cleaned_data['min_age'])
        
        if form.cleaned_data.get('max_age'):
            users = users.filter(hookup_profile__age__lte=form.cleaned_data['max_age'])
        
        if form.cleaned_data.get('city'):
            users = users.filter(hookup_profile__city__icontains=form.cleaned_data['city'])
        
        if form.cleaned_data.get('area'):
            users = users.filter(hookup_profile__area=form.cleaned_data['area'])
        
        if form.cleaned_data.get('online_only'):
            users = users.filter(hookup_profile__is_online=True)
        
        # Advanced filters
        if form.cleaned_data.get('body_type'):
            users = users.filter(hookup_profile__body_type=form.cleaned_data['body_type'])
        
        if form.cleaned_data.get('ethnicity'):
            users = users.filter(hookup_profile__ethnicity=form.cleaned_data['ethnicity'])
        
        if form.cleaned_data.get('education_level'):
            users = users.filter(hookup_profile__education_level=form.cleaned_data['education_level'])
        
        if form.cleaned_data.get('relationship_status'):
            users = users.filter(hookup_profile__relationship_status=form.cleaned_data['relationship_status'])
        
        if form.cleaned_data.get('smokes'):
            users = users.filter(hookup_profile__smokes=form.cleaned_data['smokes'])
        
        if form.cleaned_data.get('drinks'):
            users = users.filter(hookup_profile__drinks=form.cleaned_data['drinks'])
        
        if form.cleaned_data.get('verified_only'):
            users = users.filter(
                Q(is_verified=True) |
                Q(hookup_profile__is_verified=True) |
                Q(hookup_profile__id_verified=True) |
                Q(hookup_profile__phone_verified=True)
            )
        
        if form.cleaned_data.get('photo_verified_only'):
            # Escorts with any profile photos (basic photo verification proxy)
            users = users.filter(hookup_profile__profile_photos__isnull=False).distinct()
    
    # Exclude blocked users
    blocked_connections = Connection.objects.filter(
        from_user=request.user,
        status='blocked'
    ).values_list('to_user_id', flat=True)
    users = users.exclude(id__in=blocked_connections)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'connections/browse.html', context)


@login_required
@age_verified_required
def user_profile(request, user_id):
    """View another user's profile."""
    profile_user = get_object_or_404(User, id=user_id)
    
    if profile_user == request.user:
        return redirect('connections:my_profile')
    
    # Track visit
    Visit.objects.get_or_create(
        visitor=request.user,
        visited_user=profile_user
    )
    
    # Get connection status
    connection = Connection.objects.filter(
        from_user=request.user,
        to_user=profile_user
    ).first()
    
    reverse_connection = Connection.objects.filter(
        from_user=profile_user,
        to_user=request.user
    ).first()
    
    is_matched = connection and connection.status == 'matched'
    is_pending = connection and connection.status == 'pending'
    has_reverse_connection = reverse_connection is not None
    
    # Get profile visit count
    visit_count = Visit.objects.filter(visited_user=profile_user).count()
    
    # Get all profile photos
    profile_photos = ProfilePhoto.objects.filter(user=profile_user).order_by('is_primary', 'order', 'created_at')

    # Handle user report submission
    report_form = None
    if request.method == 'POST' and 'reason' in request.POST:
        report_form = UserReportForm(request.POST)
        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.reported_user = profile_user
            report.reported_by = request.user
            report.save()
            messages.success(request, 'Thank you. Your report has been submitted for review.')
            return redirect('connections:user_profile', user_id=user_id)
    else:
        report_form = UserReportForm()

    context = {
        'profile_user': profile_user,
        'connection': connection,
        'is_matched': is_matched,
        'is_pending': is_pending,
        'has_reverse_connection': has_reverse_connection,
        'visit_count': visit_count,
        'profile_photos': profile_photos,
        'report_form': report_form,
    }
    return render(request, 'connections/user_profile.html', context)


@login_required
def my_profile(request):
    """User's own profile."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    photos = ProfilePhoto.objects.filter(user=request.user)
    
    # Handle photo deletion
    if request.method == 'POST' and 'delete_photo_id' in request.POST:
        photo_id = request.POST.get('delete_photo_id')
        photo = get_object_or_404(ProfilePhoto, id=photo_id, user=request.user)
        photo.delete()
        messages.success(request, 'Photo deleted successfully.')
        return redirect('connections:my_profile')
    
    elif request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('connections:my_profile')
    else:
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'profile': profile,
        'profile_form': profile_form,
        'photos': photos,
    }
    return render(request, 'connections/my_profile.html', context)


@login_required
@age_verified_required
@require_POST
@rate_limit(max_requests=20, period=60, key_prefix='connect_user')
def connect_user(request, user_id):
    """Send a connection request (like/favorite)."""
    to_user = get_object_or_404(User, id=user_id)
    
    if to_user == request.user:
        return JsonResponse({'error': 'Cannot connect with yourself'}, status=400)
    
    connection, created = Connection.objects.get_or_create(
        from_user=request.user,
        to_user=to_user,
        defaults={'status': 'pending'}
    )
    
    if not created:
        return JsonResponse({'error': 'Connection already exists'}, status=400)
    
    # Check for mutual match
    reverse_connection = Connection.objects.filter(
        from_user=to_user,
        to_user=request.user,
        status='pending'
    ).first()
    
    if reverse_connection:
        # It's a match!
        connection.status = 'matched'
        connection.save()
        reverse_connection.status = 'matched'
        reverse_connection.save()
        return JsonResponse({'status': 'matched', 'message': 'It\'s a match!'})
    
    return JsonResponse({'status': 'pending', 'message': 'Connection sent!'})


@login_required
@require_POST
@rate_limit(max_requests=10, period=300, key_prefix='block_user')
def block_user(request, user_id):
    """Block a user."""
    to_user = get_object_or_404(User, id=user_id)
    
    connection, created = Connection.objects.get_or_create(
        from_user=request.user,
        to_user=to_user
    )
    connection.status = 'blocked'
    connection.save()
    
    messages.success(request, f'{to_user.username} has been blocked.')
    return redirect('connections:browse')


@login_required
def connections_list(request):
    """List user's connections (matches, pending, etc.)."""
    sent_connections = Connection.objects.filter(from_user=request.user)
    received_connections = Connection.objects.filter(to_user=request.user)
    
    matches = sent_connections.filter(status='matched')
    pending_sent = sent_connections.filter(status='pending')
    pending_received = received_connections.filter(status='pending')
    
    context = {
        'matches': matches,
        'pending_sent': pending_sent,
        'pending_received': pending_received,
    }
    return render(request, 'connections/connections_list.html', context)


@login_required
def messages_list(request):
    """List all conversations."""
    # Get all unique users the current user has messaged with
    sent_to = Message.objects.filter(sender=request.user).values_list('recipient', flat=True).distinct()
    received_from = Message.objects.filter(recipient=request.user).values_list('sender', flat=True).distinct()
    user_ids = set(list(sent_to) + list(received_from))
    
    conversations = []
    for user_id in user_ids:
        user = User.objects.get(id=user_id)
        last_message = Message.objects.filter(
            Q(sender=request.user, recipient=user) |
            Q(sender=user, recipient=request.user)
        ).order_by('-created_at').first()
        
        unread_count = Message.objects.filter(
            sender=user,
            recipient=request.user,
            is_read=False
        ).count()
        
        conversations.append({
            'user': user,
            'last_message': last_message,
            'unread_count': unread_count,
        })
    
    conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else timezone.now(), reverse=True)
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'connections/messages_list.html', context)


@login_required
@age_verified_required
@require_http_methods(["GET", "POST"])
@rate_limit(max_requests=30, period=60, key_prefix='send_message')
def chat(request, user_id):
    """Chat with a specific user. Only allowed once connection is accepted (matched)."""
    other_user = get_object_or_404(User, id=user_id)
    
    # Require a matched connection before messaging (both must have accepted)
    is_matched = (
        Connection.objects.filter(
            from_user=request.user, to_user=other_user, status='matched'
        ).exists()
        or Connection.objects.filter(
            from_user=other_user, to_user=request.user, status='matched'
        ).exists()
    )
    if not is_matched:
        messages.warning(
            request,
            'You can message after you connect and they accept. Send a connection request from their profile, then wait for them to accept.'
        )
        return redirect('connections:user_profile', user_id=user_id)
    
    # Clients must be verified to message escorts (User.is_verified e.g. after M-Pesa, or hookup_profile.phone_verified)
    if request.user.is_client and not request.user.is_verified and not request.user.is_client_verified():
        messages.warning(request, 'Please verify your account to message escorts. Subscribe or complete phone verification first.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = other_user
            message.save()
            return redirect('connections:chat', user_id=user_id)
    else:
        form = MessageForm()
    
    # Get all messages between users
    messages_list = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('created_at')
    
    # Mark messages as read
    Message.objects.filter(
        sender=other_user,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    context = {
        'other_user': other_user,
        'messages': messages_list,
        'form': form,
    }
    return render(request, 'connections/chat.html', context)


@login_required
def upload_photo(request):
    """Upload a profile photo."""
    if request.method == 'POST':
        form = ProfilePhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()
            
            # If this is set as primary, unset others
            if photo.is_primary:
                ProfilePhoto.objects.filter(
                    user=request.user
                ).exclude(id=photo.id).update(is_primary=False)
            
            messages.success(request, 'Photo uploaded successfully!')
            return redirect('connections:my_profile')
    else:
        form = ProfilePhotoForm()
    
    return render(request, 'connections/upload_photo.html', {'form': form})
