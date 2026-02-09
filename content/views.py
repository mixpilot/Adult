from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
from core.decorators import check_premium_content, rate_limit
from .models import Content, Category, Tag, Comment, ContentReport, Bookmark, WatchHistory, ActivityLog, ContentLike
from .forms import CommentForm, ContentReportForm


@login_required
def content_list(request):
    """List all content with filtering and pagination."""
    # Only show approved content to non-staff users
    if request.user.is_staff:
        contents = Content.objects.all()
    else:
        contents = Content.objects.filter(status='approved')
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        contents = contents.filter(category__slug=category_slug)
    
    # Filter by tag
    tag_slug = request.GET.get('tag')
    if tag_slug:
        contents = contents.filter(tags__slug=tag_slug)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        contents = contents.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Advanced filters
    content_type_filter = request.GET.get('content_type')
    if content_type_filter:
        contents = contents.filter(content_type=content_type_filter)
    
    premium_filter = request.GET.get('premium')
    if premium_filter == 'true':
        contents = contents.filter(is_premium=True)
    elif premium_filter == 'false':
        contents = contents.filter(is_premium=False)
    
    # Enhanced ordering options
    order_by = request.GET.get('order_by', '-created_at')
    valid_orders = ['-created_at', '-views', '-likes', 'title', 'created_at', 'views', 'likes']
    if order_by in valid_orders:
        contents = contents.order_by(order_by)
    else:
        contents = contents.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(contents, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.annotate(content_count=Count('contents'))
    tags = Tag.objects.annotate(content_count=Count('contents')).order_by('name')
    featured_content = Content.objects.filter(is_featured=True)[:6]
    
    # Get user's bookmarked and liked content IDs (if authenticated)
    bookmarked_ids = []
    liked_ids = []
    if request.user.is_authenticated:
        bookmarked_ids = Bookmark.objects.filter(user=request.user).values_list('content_id', flat=True)
        liked_ids = ContentLike.objects.filter(user=request.user).values_list('content_id', flat=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'featured_content': featured_content,
        'current_category': category_slug,
        'current_tag': tag_slug,
        'search_query': search_query,
        'bookmarked_ids': bookmarked_ids,
        'current_content_type': content_type_filter,
        'current_premium_filter': premium_filter,
        'current_order_by': order_by,
        'liked_ids': liked_ids,
    }
    return render(request, 'content/list.html', context)


@check_premium_content
def content_detail(request, slug):
    """Detail view for content."""
    content = get_object_or_404(Content, slug=slug)
    content.increment_views()
    
    # Track watch history if user is authenticated
    if request.user.is_authenticated:
        WatchHistory.objects.get_or_create(
            user=request.user,
            content=content,
            defaults={'watch_duration': 0}
        )
        # Log activity
        ActivityLog.objects.create(
            activity_type='content_viewed',
            user=request.user,
            content=content,
            message=f"{request.user.username} started watching {content.title[:30]}..."
        )
    
    # Get smart recommendations based on category and tags
    related_content = Content.objects.filter(
        Q(category=content.category) | Q(tags__in=content.tags.all())
    ).exclude(id=content.id).distinct()[:6]
    
    # If not enough related content, get by category only
    if related_content.count() < 6:
        category_content = Content.objects.filter(
            category=content.category
        ).exclude(id=content.id)[:6 - related_content.count()]
        related_content = list(related_content) + list(category_content)
    
    # Get user's bookmark and like status
    is_bookmarked = False
    is_liked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, content=content).exists()
        is_liked = ContentLike.objects.filter(user=request.user, content=content).exists()
    
    comments = content.comments.filter(is_approved=True)
    # Default forms (used for GET and for redisplay on validation errors)
    form = CommentForm()
    report_form = ContentReportForm()

    if request.method == 'POST':
        # Comment submission
        if 'text' in request.POST:
            if not request.user.is_authenticated:
                messages.warning(request, 'Please login to comment.')
                return redirect('accounts:login')

            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.content = content
                comment.user = request.user
                comment.save()
                messages.success(request, 'Comment added successfully!')
                return redirect('content:detail', slug=slug)
        # Content report submission
        elif 'reason' in request.POST:
            if not request.user.is_authenticated:
                messages.warning(request, 'Please login to report content.')
                return redirect('accounts:login')
            report_form = ContentReportForm(request.POST)
            if report_form.is_valid():
                report = report_form.save(commit=False)
                report.content = content
                report.reported_by = request.user
                report.save()
                messages.success(request, 'Thank you. Your report has been submitted for review.')
                return redirect('content:detail', slug=slug)
    
    context = {
        'content': content,
        'related_content': related_content,
        'comments': comments,
        'form': form,
        'report_form': report_form,
        'is_bookmarked': is_bookmarked,
        'is_liked': is_liked,
    }
    return render(request, 'content/detail.html', context)


def category_detail(request, slug):
    """Category detail view."""
    category = get_object_or_404(Category, slug=slug)
    # Only show approved content to non-staff users
    if request.user.is_staff:
        contents = Content.objects.filter(category=category)
    else:
        contents = Content.objects.filter(category=category, status='approved')
    
    paginator = Paginator(contents, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'content/category_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
@rate_limit(max_requests=10, period=3600, key_prefix='upload_content')
def upload_content(request):
    """Upload new content."""
    from django.utils.text import slugify
    from .forms import ContentForm
    from .models import ContentImage
    
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.uploader = request.user
            content.status = 'pending'  # Set to pending for review
            # Generate slug from title
            base_slug = slugify(content.title)
            slug = base_slug
            counter = 1
            while Content.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            content.slug = slug
            
            # Validate video file or URL based on content type
            if content.content_type == 'video':
                if not content.video_file and not content.video_url:
                    form.add_error('video_file', 'Either video file or video URL is required for video content.')
                    form.add_error('video_url', 'Either video file or video URL is required for video content.')
                    return render(request, 'content/upload.html', {
                        'form': form,
                        'categories': Category.objects.all(),
                        'tags': Tag.objects.all()
                    })
            
            content.save()
            form.save_m2m()  # Save many-to-many relationships (tags)
            
            # Handle gallery images if content type is gallery
            if content.content_type == 'gallery':
                images = request.FILES.getlist('gallery_images')
                for idx, image in enumerate(images):
                    ContentImage.objects.create(
                        content=content,
                        image=image,
                        order=idx
                    )
            
            messages.success(request, f'Content "{content.title}" uploaded successfully! It will be reviewed before being published.')
            return redirect('content:detail', slug=content.slug)
    else:
        form = ContentForm()
    
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    return render(request, 'content/upload.html', {
        'form': form,
        'categories': categories,
        'tags': tags
    })


@login_required
@require_POST
@rate_limit(max_requests=30, period=60, key_prefix='bookmark_content')
def toggle_bookmark(request, content_id):
    """Toggle bookmark for content."""
    content = get_object_or_404(Content, id=content_id)
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        content=content
    )
    
    if not created:
        bookmark.delete()
        return JsonResponse({'bookmarked': False, 'message': 'Removed from bookmarks'})
    
    return JsonResponse({'bookmarked': True, 'message': 'Added to bookmarks'})


@login_required
def my_bookmarks(request):
    """User's bookmarked content."""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('content')
    bookmarked_content = [bookmark.content for bookmark in bookmarks]
    
    paginator = Paginator(bookmarked_content, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'content/bookmarks.html', context)


@login_required
def watch_history(request):
    """User's watch history."""
    history = WatchHistory.objects.filter(user=request.user).select_related('content').order_by('-watched_at')
    
    paginator = Paginator(history, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'content/watch_history.html', context)


@login_required
@require_POST
@rate_limit(max_requests=50, period=60, key_prefix='like_content')
def toggle_like(request, content_id):
    """Toggle like for content."""
    content = get_object_or_404(Content, id=content_id)
    like, created = ContentLike.objects.get_or_create(
        user=request.user,
        content=content
    )
    
    if not created:
        like.delete()
        # Update likes count
        content.likes = ContentLike.objects.filter(content=content).count()
        content.save(update_fields=['likes'])
        return JsonResponse({'liked': False, 'likes_count': content.likes, 'message': 'Unliked'})
    
    # Update likes count
    content.likes = ContentLike.objects.filter(content=content).count()
    content.save(update_fields=['likes'])
    
    # Log activity
    ActivityLog.objects.create(
        activity_type='content_liked',
        user=request.user,
        content=content,
        message=f"{request.user.username} liked {content.title[:30]}..."
    )
    return JsonResponse({'liked': True, 'likes_count': content.likes, 'message': 'Liked'})


@login_required
def user_dashboard(request):
    """User's personal dashboard with stats and quick actions."""
    from django.db.models import Count, Sum
    
    # User's content stats
    user_content = Content.objects.filter(uploader=request.user)
    total_uploads = user_content.count()
    approved_content = user_content.filter(status='approved').count()
    pending_content = user_content.filter(status='pending').count()
    total_views = user_content.aggregate(total=Sum('views'))['total'] or 0
    total_likes = user_content.aggregate(total=Sum('likes'))['total'] or 0
    
    # Recent uploads
    recent_uploads = user_content.order_by('-created_at')[:5]
    
    # User's bookmarks count
    bookmarks_count = Bookmark.objects.filter(user=request.user).count()
    
    # Watch history count
    watch_history_count = WatchHistory.objects.filter(user=request.user).count()
    
    # Connection stats
    from connections.models import Connection
    matches_count = Connection.objects.filter(from_user=request.user, status='matched').count()
    pending_connections = Connection.objects.filter(from_user=request.user, status='pending').count()
    
    context = {
        'total_uploads': total_uploads,
        'approved_content': approved_content,
        'pending_content': pending_content,
        'total_views': total_views,
        'total_likes': total_likes,
        'recent_uploads': recent_uploads,
        'bookmarks_count': bookmarks_count,
        'watch_history_count': watch_history_count,
        'matches_count': matches_count,
        'pending_connections': pending_connections,
    }
    return render(request, 'content/dashboard.html', context)
