from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Category, Tag, Content, ContentImage, Comment, ContentReport, Testimonial, ActivityLog, Bookmark, WatchHistory, ContentLike


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ContentImageInline(TabularInline):
    model = ContentImage
    extra = 1


@admin.register(Content)
class ContentAdmin(ModelAdmin):
    list_display = ['title', 'content_type', 'category', 'uploader', 'status', 'views', 'likes', 'is_featured', 'is_premium', 'created_at']
    list_filter = ['status', 'content_type', 'category', 'is_featured', 'is_premium', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'uploader__username']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ContentImageInline]
    filter_horizontal = ['tags']
    readonly_fields = ['views', 'likes', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_editable = ['is_featured', 'is_premium']
    actions = ['approve_content', 'reject_content', 'feature_content', 'unfeature_content', 'mark_premium', 'mark_free', 'reset_views']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'content_type', 'category', 'tags', 'uploader')
        }),
        ('Media', {
            'fields': ('thumbnail', 'video_file', 'video_url')
        }),
        ('Status & Settings', {
            'fields': ('status', 'rejection_reason', 'is_featured', 'is_premium')
        }),
        ('Statistics', {
            'fields': ('views', 'likes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_content(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f'{count} content item(s) approved.')
    approve_content.short_description = "✓ Approve selected content"
    
    def reject_content(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f'{count} content item(s) rejected.')
    reject_content.short_description = "✗ Reject selected content"
    
    def feature_content(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} content item(s) featured.')
    feature_content.short_description = "⭐ Feature selected content"
    
    def unfeature_content(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} content item(s) unfeatured.')
    unfeature_content.short_description = "Remove feature from selected content"
    
    def mark_premium(self, request, queryset):
        count = queryset.update(is_premium=True)
        self.message_user(request, f'{count} content item(s) marked as premium.')
    mark_premium.short_description = "💎 Mark as premium"
    
    def mark_free(self, request, queryset):
        count = queryset.update(is_premium=False)
        self.message_user(request, f'{count} content item(s) marked as free.')
    mark_free.short_description = "🆓 Mark as free"
    
    def reset_views(self, request, queryset):
        count = queryset.update(views=0)
        self.message_user(request, f'Views reset for {count} content item(s).')
    reset_views.short_description = "🔄 Reset views count"


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ['content', 'user', 'text_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['text', 'user__username', 'content__title']
    list_editable = ['is_approved']
    actions = ['approve_comments', 'reject_comments']
    date_hierarchy = 'created_at'
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comment Preview'
    
    def approve_comments(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f'{count} comment(s) approved.')
    approve_comments.short_description = "✓ Approve selected comments"
    
    def reject_comments(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f'{count} comment(s) rejected.')
    reject_comments.short_description = "✗ Reject selected comments"


@admin.register(ContentReport)
class ContentReportAdmin(ModelAdmin):
    list_display = ['content', 'reported_by', 'reason_preview', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['content__title', 'reported_by__username', 'reason']
    list_editable = ['status']
    actions = ['mark_reviewed', 'mark_closed', 'mark_open']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    def reason_preview(self, obj):
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    reason_preview.short_description = 'Reason'
    
    def mark_reviewed(self, request, queryset):
        count = queryset.update(status='reviewed')
        self.message_user(request, f'{count} report(s) marked as reviewed.')
    mark_reviewed.short_description = "✓ Mark as reviewed"
    
    def mark_closed(self, request, queryset):
        count = queryset.update(status='closed')
        self.message_user(request, f'{count} report(s) marked as closed.')
    mark_closed.short_description = "✓ Mark as closed"
    
    def mark_open(self, request, queryset):
        count = queryset.update(status='open')
        self.message_user(request, f'{count} report(s) marked as open.')
    mark_open.short_description = "↻ Reopen selected reports"


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ['user', 'rating', 'is_featured', 'is_approved', 'created_at']
    list_filter = ['is_featured', 'is_approved', 'rating', 'created_at']
    search_fields = ['text', 'user__username']
    list_editable = ['is_featured', 'is_approved']


@admin.register(ActivityLog)
class ActivityLogAdmin(ModelAdmin):
    list_display = ['activity_type', 'user', 'content', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['message', 'user__username', 'content__title']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Bookmark)
class BookmarkAdmin(ModelAdmin):
    list_display = ['user', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'content__title']
    date_hierarchy = 'created_at'


@admin.register(WatchHistory)
class WatchHistoryAdmin(ModelAdmin):
    list_display = ['user', 'content', 'watched_at', 'watch_duration']
    list_filter = ['watched_at']
    search_fields = ['user__username', 'content__title']
    date_hierarchy = 'watched_at'


@admin.register(ContentLike)
class ContentLikeAdmin(ModelAdmin):
    list_display = ['user', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'content__title']
    date_hierarchy = 'created_at'
