from django import forms
from .models import Comment, Content, Category, ContentImage, Tag, ContentReport


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment...'
            })
        }


class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'description', 'content_type', 'thumbnail', 
                  'video_file', 'video_url', 'category', 'tags', 'is_premium']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter content title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your content...'
            }),
            'content_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_content_type'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'id_thumbnail'
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*',
                'id': 'id_video_file'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Or enter video URL (YouTube, Vimeo, etc.)'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
            'is_premium': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['tags'].queryset = Tag.objects.all()
        self.fields['thumbnail'].required = True
        self.fields['category'].required = False


class ContentImageForm(forms.ModelForm):
    """Form for uploading gallery images."""
    class Meta:
        model = ContentImage
        fields = ['image', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }


class ContentReportForm(forms.ModelForm):
    """Form for reporting content for moderation."""
    class Meta:
        model = ContentReport
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe why this content should be reviewed (e.g., copyright, non-consensual, illegal, etc.).'
            }),
        }
