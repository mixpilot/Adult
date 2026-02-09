from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserProfile(models.Model):
    """Extended user profile for hookup features."""
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non-binary', 'Non-Binary'),
        ('other', 'Other'),
        ('prefer-not-to-say', 'Prefer not to say'),
    ]
    
    SEEKING_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non-binary', 'Non-Binary'),
        ('everyone', 'Everyone'),
    ]
    
    BODY_TYPE_CHOICES = [
        ('slim', 'Slim'),
        ('average', 'Average'),
        ('athletic', 'Athletic'),
        ('curvy', 'Curvy'),
        ('plus', 'Plus Size'),
        ('other', 'Other'),
    ]
    
    ETHNICITY_CHOICES = [
        ('african', 'African'),
        ('afro_caribbean', 'Afro-Caribbean'),
        ('mixed', 'Mixed'),
        ('arab', 'Arab'),
        ('asian', 'Asian'),
        ('caucasian', 'Caucasian'),
        ('other', 'Other'),
    ]
    
    EDUCATION_CHOICES = [
        ('none', 'Prefer not to say'),
        ('secondary', 'High school / Secondary'),
        ('college', 'College / Diploma'),
        ('university', 'University Degree'),
        ('postgrad', 'Postgraduate'),
    ]
    
    RELATIONSHIP_STATUS_CHOICES = [
        ('single', 'Single'),
        ('dating', 'Dating'),
        ('married', 'Married'),
        ('complicated', 'It\'s complicated'),
    ]
    
    FREQUENCY_CHOICES = [
        ('no', 'No'),
        ('occasionally', 'Occasionally'),
        ('yes', 'Yes'),
    ]
    
    AREA_CHOICES = [
        ('mirema', 'Mirema'),
        ('kasarani', 'Kasarani'),
        ('wandani', 'Wandani'),
        ('kimbo', 'Kimbo (Githurai Kimbo)'),
        ('roysambu', 'Roysambu'),
        ('zimmerman', 'Zimmerman'),
        ('githurai', 'Githurai'),
        ('thika_road_other', 'Other Thika Road Area'),
        ('nairobi_other', 'Other Nairobi Area'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hookup_profile')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    seeking = models.CharField(max_length=20, choices=SEEKING_CHOICES, default='everyone')
    age = models.PositiveIntegerField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, help_text="City or town (e.g., Nairobi)")
    area = models.CharField(
        max_length=50,
        choices=AREA_CHOICES,
        blank=True,
        help_text="Area/estate (e.g., Mirema, Kasarani, Kimbo)"
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="More detailed description, building or street (optional)"
    )
    bio = models.TextField(max_length=500, blank=True)
    interests = models.CharField(max_length=200, blank=True, help_text="Comma-separated interests")
    
    # Advanced attributes
    body_type = models.CharField(max_length=20, choices=BODY_TYPE_CHOICES, blank=True)
    ethnicity = models.CharField(max_length=20, choices=ETHNICITY_CHOICES, blank=True)
    height_cm = models.PositiveIntegerField(blank=True, null=True)
    weight_kg = models.PositiveIntegerField(blank=True, null=True)
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True)
    relationship_status = models.CharField(max_length=20, choices=RELATIONSHIP_STATUS_CHOICES, blank=True)
    smokes = models.CharField(max_length=15, choices=FREQUENCY_CHOICES, blank=True)
    drinks = models.CharField(max_length=15, choices=FREQUENCY_CHOICES, blank=True)
    
    # Advanced media
    video_intro = models.FileField(
        upload_to='profile_videos/',
        blank=True,
        null=True,
        help_text="Short video introduction (optional)"
    )
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    
    # Verification
    is_verified = models.BooleanField(default=False, help_text="Basic profile verification")
    id_verified = models.BooleanField(default=False, help_text="ID document verified by admin")
    phone_verified = models.BooleanField(default=False, help_text="Phone number verified")
    
    # Privacy & visibility
    VISIBILITY_CHOICES = [
        ('public', 'Public - Visible to everyone'),
        ('members', 'Members Only - Visible to logged in users'),
        ('connections', 'Connections Only - Visible only to your matches'),
    ]
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='members',
        help_text="Who can see your full profile"
    )
    show_online_status = models.BooleanField(
        default=True,
        help_text="Allow others to see when you are online"
    )
    hide_from_search = models.BooleanField(
        default=False,
        help_text="Hide your profile from browse/search results"
    )
    incognito_mode = models.BooleanField(
        default=False,
        help_text="View other profiles without appearing in their visitors list"
    )
    
    # Social links
    instagram = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    snapchat = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    profile_photos = models.ManyToManyField('ProfilePhoto', blank=True, related_name='profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def profile_completeness(self):
        """
        Simple profile completeness score (0-100).
        Counts key fields that are filled in.
        """
        score = 0
        total = 8  # number of checks
        
        if self.bio:
            score += 1
        if self.age:
            score += 1
        if self.location:
            score += 1
        if self.interests:
            score += 1
        if self.profile_photos.exists():
            score += 1
        if self.video_intro:
            score += 1
        if self.is_verified or self.id_verified or self.phone_verified:
            score += 1
        if any([self.instagram, self.twitter, self.snapchat, self.website]):
            score += 1
        
        return int((score / total) * 100)

    @property
    def is_active_now(self):
        """Check if user is currently active (online in last 5 minutes)."""
        if self.is_online:
            return True
        time_diff = timezone.now() - self.last_seen
        return time_diff.total_seconds() < 300  # 5 minutes
    
    @property
    def is_escort_verified(self):
        """Check if escort meets minimum verification requirements (phone + photo)."""
        if self.user.user_type != 'escort':
            return False
        has_phone = self.phone_verified
        has_photo = self.profile_photos.exists()
        return has_phone and has_photo
    
    @property
    def verification_status(self):
        """Get verification status string."""
        if self.id_verified:
            return 'id_verified'
        elif self.phone_verified:
            return 'phone_verified'
        elif self.is_verified:
            return 'basic_verified'
        return 'unverified'


class ProfilePhoto(models.Model):
    """User profile photos."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_photos')
    photo = models.ImageField(upload_to='profile_photos/')
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_primary', 'order', 'created_at']

    def __str__(self):
        return f"{self.user.username}'s Photo {self.id}"


class Connection(models.Model):
    """Connection between users (like/favorite)."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('matched', 'Matched'),
        ('blocked', 'Blocked'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_connections')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_connections')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['from_user', 'to_user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"

    def match(self):
        """Check if this connection has a mutual match."""
        return Connection.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user,
            status__in=['pending', 'matched']
        ).exists()


class Message(models.Model):
    """Direct messages between users."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"

    def mark_as_read(self):
        """Mark message as read."""
        self.is_read = True
        self.save(update_fields=['is_read'])


class Visit(models.Model):
    """Track profile visits."""
    visitor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_visits')
    visited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visitors')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['visitor', 'visited_user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.visitor.username} visited {self.visited_user.username}"


class UserReport(models.Model):
    """User reports about other users for safety/moderation."""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('reviewed', 'Reviewed'),
        ('closed', 'Closed'),
    ]

    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_against')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reports')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on {self.reported_user.username} by {self.reported_by.username}"