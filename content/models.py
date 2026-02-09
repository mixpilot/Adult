from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class Category(models.Model):
    """Category model for organizing content."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='category_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('content:category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Tag model for content tagging."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Content(models.Model):
    """Main content model for videos/images."""
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('image', 'Image'),
        ('gallery', 'Gallery'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='video')
    thumbnail = models.ImageField(upload_to='content_thumbnails/')
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='contents')
    tags = models.ManyToManyField(Tag, blank=True, related_name='contents')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_content')
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    
    # Content approval workflow
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection if applicable")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('content:detail', kwargs={'slug': self.slug})

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class ContentImage(models.Model):
    """Model for gallery images."""
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='content_images/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.content.title} - Image {self.order}"


class Comment(models.Model):
    """Comment model for content."""
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.content.title}"


class ContentReport(models.Model):
    """User reports about specific content for moderation."""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('reviewed', 'Reviewed'),
        ('closed', 'Closed'),
    ]

    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_reports')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on {self.content.title} by {self.reported_by.username}"


class Testimonial(models.Model):
    """User testimonials for social proof."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials')
    text = models.TextField()
    rating = models.PositiveIntegerField(default=5, help_text="Rating out of 5")
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"Testimonial by {self.user.username}"


class ActivityLog(models.Model):
    """Activity log for live feed."""
    ACTIVITY_TYPES = [
        ('user_joined', 'User Joined'),
        ('content_viewed', 'Content Viewed'),
        ('content_liked', 'Content Liked'),
        ('match_made', 'Match Made'),
        ('premium_upgrade', 'Premium Upgrade'),
        ('content_uploaded', 'Content Uploaded'),
    ]

    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    content = models.ForeignKey(Content, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    message = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.created_at}"


class Bookmark(models.Model):
    """User bookmarks/favorites for content."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'content']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} bookmarked {self.content.title}"


class WatchHistory(models.Model):
    """Track user watch history for recommendations."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='watched_by')
    watched_at = models.DateTimeField(auto_now_add=True)
    watch_duration = models.PositiveIntegerField(default=0, help_text="Seconds watched")

    class Meta:
        ordering = ['-watched_at']
        indexes = [
            models.Index(fields=['user', '-watched_at']),
        ]

    def __str__(self):
        return f"{self.user.username} watched {self.content.title}"


class ContentLike(models.Model):
    """Track individual user likes for content."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_likes')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='user_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'content']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} liked {self.content.title}"
    