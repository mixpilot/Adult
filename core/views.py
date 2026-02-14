from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from content.models import Content, Category, Testimonial, ActivityLog, WatchHistory, Bookmark
from accounts.models import User
from connections.models import Connection, Visit


def home(request):
    """Home page view with trending and premium features."""
    # Only show approved content to non-staff users
    if request.user.is_staff:
        content_filter = {}
    else:
        content_filter = {'status': 'approved'}
    
    # Featured content
    featured_content = list(Content.objects.filter(is_featured=True, **content_filter)[:12])
    
    # Split featured content into carousel slides (6 items per slide)
    featured_slides = []
    for i in range(0, len(featured_content), 6):
        featured_slides.append(featured_content[i:i+6])
    
    # Trending content (last 24 hours)
    one_day_ago = timezone.now() - timedelta(hours=24)
    trending_content = Content.objects.filter(
        created_at__gte=one_day_ago,
        **content_filter
    ).order_by('-views', '-likes')[:12]
    
    # Trending this hour (more granular)
    one_hour_ago = timezone.now() - timedelta(hours=1)
    trending_this_hour = Content.objects.filter(
        created_at__gte=one_hour_ago,
        **content_filter
    ).order_by('-views', '-likes')[:8]
    
    # Most watched today
    most_watched_today = Content.objects.filter(
        created_at__gte=one_day_ago,
        **content_filter
    ).order_by('-views')[:8]
    
    # Most liked today
    most_liked_today = Content.objects.filter(
        created_at__gte=one_day_ago,
        **content_filter
    ).order_by('-likes')[:8]
    
    # Most bookmarked
    most_bookmarked = Content.objects.filter(**content_filter).annotate(
        bookmark_count=Count('bookmarked_by')
    ).filter(bookmark_count__gt=0).order_by('-bookmark_count')[:8]
    
    # Fastest growing creators (users who uploaded most content in last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    fastest_growing_creators = User.objects.annotate(
        recent_uploads=Count('uploaded_content', filter=Q(uploaded_content__created_at__gte=seven_days_ago))
    ).filter(recent_uploads__gt=0).order_by('-recent_uploads')[:6]
    
    # Premium content (blurred previews)
    premium_content = Content.objects.filter(is_premium=True, **content_filter).order_by('-views')[:12]
    
    # Latest content
    latest_content = Content.objects.filter(**content_filter)[:24]
    
    # Smart recommendations (if user is authenticated and has watch history)
    recommended_content = None
    if request.user.is_authenticated:
        user_watch_history = WatchHistory.objects.filter(user=request.user).select_related('content')
        if user_watch_history.exists():
            # Get categories and tags from watched content
            watched_categories = user_watch_history.values_list('content__category_id', flat=True).distinct()
            watched_tags = []
            for history in user_watch_history[:5]:  # Check last 5 watched
                watched_tags.extend(history.content.tags.values_list('id', flat=True))
            
            # Recommend content based on watched categories and tags
            recommended_content = Content.objects.filter(
                Q(category_id__in=watched_categories) | Q(tags__id__in=watched_tags),
                **content_filter
            ).exclude(
                id__in=user_watch_history.values_list('content_id', flat=True)
            ).distinct()[:12]
    
    # Categories
    categories = Category.objects.all()[:8]
    
    # Dating teasers (if user is authenticated)
    nearby_users_count = None
    profile_views_count = None
    if request.user.is_authenticated:
        try:
            # Count users with profiles (simplified - would use location in real app)
            nearby_users_count = User.objects.exclude(id=request.user.id).filter(
                hookup_profile__isnull=False
            ).count()
            # Profile views
            profile_views_count = Visit.objects.filter(visited_user=request.user).count()
        except:
            pass
    
    # Creator spotlight (top uploaders)
    top_creators = User.objects.annotate(
        content_count=Count('uploaded_content')
    ).filter(content_count__gt=0).order_by('-content_count')[:6]
    
    # Testimonials (featured and approved)
    testimonials = Testimonial.objects.filter(is_approved=True, is_featured=True)[:6]
    
    # Live activity feed - ONLY for admin dashboard (privacy: don't show other users' activities to regular users)
    recent_activities = None  # Only admins should see this
    
    # Site statistics (only approved content for non-staff)
    total_content = Content.objects.filter(**content_filter).count()
    total_users = User.objects.count()
    total_matches = Connection.objects.filter(status='matched').count()
    total_views = Content.objects.filter(**content_filter).aggregate(total=Sum('views'))['total'] or 0
    
    context = {
        'featured_content': featured_content,
        'featured_slides': featured_slides,
        'trending_content': trending_content,
        'trending_this_hour': trending_this_hour,
        'most_watched_today': most_watched_today,
        'most_liked_today': most_liked_today,
        'most_bookmarked': most_bookmarked,
        'premium_content': premium_content,
        'latest_content': latest_content,
        'recommended_content': recommended_content,
        'categories': categories,
        'nearby_users_count': nearby_users_count,
        'profile_views_count': profile_views_count,
        'top_creators': top_creators,
        'fastest_growing_creators': fastest_growing_creators,
        'testimonials': testimonials,
        'total_content': total_content,
        'total_users': total_users,
        'total_matches': total_matches,
        'total_views': total_views,
    }
    
    # Use different template based on user type
    if request.user.is_authenticated:
        # Admin dashboard
        if request.user.is_staff or request.user.is_superuser:
            # Add admin-specific context
            from subscriptions.models import Subscription, Payment
            from connections.models import Message
            
            # Recent activities - ONLY visible to admins for moderation
            admin_recent_activities = ActivityLog.objects.select_related('user', 'content').order_by('-created_at')[:20]
            
            admin_context = {
                **context,
                'pending_content': Content.objects.filter(status='pending').count(),
                'pending_users': User.objects.filter(is_verified=False).count(),
                'total_subscriptions': Subscription.objects.filter(
                    status__in=['active', 'trialing'],
                    current_period_end__gt=timezone.now()
                ).count(),
                'total_revenue': Payment.objects.filter(status='completed').aggregate(
                    total=Sum('amount')
                )['total'] or 0,
                'recent_users': User.objects.order_by('-date_joined')[:10],
                'recent_payments': Payment.objects.filter(status='completed').order_by('-created_at')[:10],
                'active_connections': Connection.objects.filter(status='matched').count(),
                'total_messages': Message.objects.count(),
                'recent_activities': admin_recent_activities,  # Admin-only activity feed
            }
            return render(request, 'core/home_admin.html', admin_context)
        # Escort dashboard
        elif request.user.user_type == 'escort':
            # Add escort-specific context
            from subscriptions.models import CreatorEarning, Tip
            from connections.models import Visit, Message
            
            # Verification banner: use User.is_verified (admin sets this when user is verified)
            is_verified = request.user.is_verified
            needs_verification = not is_verified
            
            escort_context = {
                **context,
                'is_verified': is_verified,
                'needs_verification': needs_verification,
                'total_earnings': CreatorEarning.objects.filter(creator=request.user).aggregate(
                    total=Sum('creator_share')
                )['total'] or 0,
                'pending_earnings': CreatorEarning.objects.filter(
                    creator=request.user, status='pending'
                ).aggregate(total=Sum('creator_share'))['total'] or 0,
                'available_earnings': CreatorEarning.objects.filter(
                    creator=request.user, status='available'
                ).aggregate(total=Sum('creator_share'))['total'] or 0,
                'profile_views': Visit.objects.filter(visited_user=request.user).count(),
                'profile_views_today': Visit.objects.filter(
                    visited_user=request.user,
                    created_at__gte=timezone.now().replace(hour=0, minute=0, second=0)
                ).count(),
                'new_messages': Message.objects.filter(
                    recipient=request.user, is_read=False
                ).count(),
                'total_tips': Tip.objects.filter(to_user=request.user).aggregate(
                    total=Sum('amount')
                )['total'] or 0,
                'recent_earnings': CreatorEarning.objects.filter(
                    creator=request.user
                ).order_by('-created_at')[:10],
            }
            return render(request, 'core/home_escort.html', escort_context)
        # Client dashboard (default)
        else:
            # Verification banner: use User.is_verified (admin sets this when user is verified)
            is_client_verified = request.user.is_verified
            needs_verification = not is_client_verified
            
            client_context = {
                **context,
                'is_client_verified': is_client_verified,
                'needs_verification': needs_verification,
            }
            return render(request, 'core/home_authenticated.html', client_context)
    else:
        return render(request, 'core/home.html', context)


def terms_of_service(request):
    """Terms of Service page."""
    return render(request, 'core/terms.html')


def privacy_policy(request):
    """Privacy Policy page."""
    return render(request, 'core/privacy.html')


def dmca_policy(request):
    """DMCA Policy page."""
    return render(request, 'core/dmca.html')


def compliance_2257(request):
    """2257 Compliance page."""
    return render(request, 'core/2257.html')


def premium_landing(request):
    """Premium benefits landing page."""
    return render(request, 'core/premium.html')