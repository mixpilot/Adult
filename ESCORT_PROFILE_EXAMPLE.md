# Escort Profile Data Example

This document provides a complete example of an escort's profile data structure, including all fields from the User model and UserProfile (hookup_profile) model.

---

## 📋 **Complete Escort Profile Example**

### **1. User Account Data** (`User` model)

```json
{
  "id": 1,
  "username": "sarah_escort",
  "email": "sarah@example.com",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "bio": "Professional and discreet escort service. Available for companionship and entertainment.",
  "avatar": "/media/avatars/sarah_avatar.jpg",
  "date_of_birth": "1995-06-15",
  "phone_number": "+254712345678",
  "user_type": "escort",
  "is_verified": true,
  "is_staff": false,
  "is_superuser": false,
  "is_active": true,
  "date_joined": "2024-01-15T10:30:00Z",
  "last_login": "2024-12-19T14:25:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-12-19T14:25:00Z"
}
```

---

### **2. Extended Profile Data** (`UserProfile` / `hookup_profile`)

```json
{
  "id": 1,
  "user_id": 1,
  
  // Basic Information
  "gender": "female",
  "seeking": "everyone",
  "age": 29,
  "city": "Nairobi",
  "area": "westlands",
  "location": "Westlands, Parklands Road, Building 123",
  "bio": "Elegant and sophisticated companion. I offer discreet, professional services for gentlemen seeking quality companionship. Available for dinner dates, events, travel, and private meetings. Fluent in English and Swahili. Non-smoker, social drinker.",
  "interests": "Travel, Fine Dining, Art, Music, Reading, Fitness, Yoga",
  
  // Physical Attributes
  "body_type": "curvy",
  "ethnicity": "african",
  "height_cm": 168,
  "weight_kg": 65,
  
  // Personal Details
  "education_level": "university",
  "relationship_status": "single",
  "smokes": "no",
  "drinks": "occasionally",
  
  // Media
  "video_intro": "/media/profile_videos/sarah_intro.mp4",
  "profile_photos": [
    {
      "id": 1,
      "photo": "/media/profile_photos/sarah_photo_1.jpg",
      "is_primary": true,
      "order": 0
    },
    {
      "id": 2,
      "photo": "/media/profile_photos/sarah_photo_2.jpg",
      "is_primary": false,
      "order": 1
    },
    {
      "id": 3,
      "photo": "/media/profile_photos/sarah_photo_3.jpg",
      "is_primary": false,
      "order": 2
    }
  ],
  
  // Verification Status
  "is_verified": true,
  "id_verified": true,
  "phone_verified": true,
  "verification_status": "id_verified",
  "is_escort_verified": true,
  
  // Online Status
  "is_online": true,
  "last_seen": "2024-12-19T14:25:00Z",
  "is_active_now": true,
  
  // Privacy & Visibility
  "visibility": "members",
  "show_online_status": true,
  "hide_from_search": false,
  "incognito_mode": false,
  
  // Social Links
  "instagram": "@sarah_escort_ke",
  "twitter": "@sarah_escort",
  "snapchat": "sarah_escort_ke",
  "website": "https://sarah-escort.example.com",
  
  // Profile Metrics
  "profile_completeness": 100,
  
  // Timestamps
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-12-19T14:25:00Z"
}
```

---

### **3. Subscription Information**

```json
{
  "subscription": {
    "id": 1,
    "user_id": 1,
    "plan": {
      "id": 5,
      "name": "Premium",
      "tier": "premium",
      "user_type": "escort",
      "price_monthly": 3899.00,
      "price_quarterly": 10526.00,
      "price_yearly": 37427.00,
      "features": {
        "featured_listing": true,
        "profile_verification_badge": true,
        "unlimited_photos": true,
        "priority_ranking": true,
        "earnings_tracking": true,
        "creator_earnings": true,
        "priority_support": false
      }
    },
    "billing_period": "monthly",
    "is_active": true,
    "start_date": "2024-11-01T00:00:00Z",
    "end_date": "2024-12-01T00:00:00Z",
    "auto_renew": true,
    "created_at": "2024-11-01T10:00:00Z"
  },
  "has_premium_access": true,
  "subscription_tier": "premium"
}
```

---

### **4. Profile Statistics**

```json
{
  "stats": {
    "profile_views": 1247,
    "connection_requests": 89,
    "accepted_connections": 67,
    "messages_received": 234,
    "content_uploads": 15,
    "content_views": 3456,
    "rating": 4.8,
    "reviews_count": 23
  }
}
```

---

### **5. Content Uploads** (if any)

```json
{
  "content": [
    {
      "id": 1,
      "title": "Professional Photo Shoot",
      "category": "photos",
      "file": "/media/content/sarah_content_1.jpg",
      "is_premium": true,
      "views": 456,
      "likes": 89,
      "created_at": "2024-12-01T12:00:00Z"
    },
    {
      "id": 2,
      "title": "Behind the Scenes",
      "category": "videos",
      "file": "/media/content/sarah_content_2.mp4",
      "is_premium": false,
      "views": 234,
      "likes": 45,
      "created_at": "2024-12-05T15:30:00Z"
    }
  ]
}
```

---

### **6. Connection Requests** (Pending/Matched)

```json
{
  "connections": {
    "pending_sent": 0,
    "pending_received": 12,
    "matched": 67,
    "blocked": 2
  },
  "recent_matches": [
    {
      "user_id": 45,
      "username": "john_client",
      "matched_at": "2024-12-18T10:00:00Z"
    },
    {
      "user_id": 52,
      "username": "mike_client",
      "matched_at": "2024-12-17T14:30:00Z"
    }
  ]
}
```

---

## 📝 **Field Descriptions**

### **User Model Fields:**
- `username`: Unique username for login
- `email`: Email address
- `phone_number`: Mobile number for M-Pesa payments
- `user_type`: Must be `"escort"` for escort profiles
- `is_verified`: General verification status
- `bio`: Short bio (stored in User model)
- `avatar`: Profile picture

### **UserProfile Fields:**

#### **Basic Info:**
- `gender`: `"male"`, `"female"`, `"non-binary"`, `"other"`, `"prefer-not-to-say"`
- `seeking`: Who they're looking for (`"male"`, `"female"`, `"non-binary"`, `"everyone"`)
- `age`: Age in years
- `city`: City name (e.g., "Nairobi")
- `area`: Specific area/estate (from AREA_CHOICES)
- `location`: Detailed location description
- `bio`: Extended bio (max 500 characters)
- `interests`: Comma-separated interests

#### **Physical Attributes:**
- `body_type`: `"slim"`, `"average"`, `"athletic"`, `"curvy"`, `"plus"`, `"other"`
- `ethnicity`: `"african"`, `"afro_caribbean"`, `"mixed"`, `"arab"`, `"asian"`, `"caucasian"`, `"other"`
- `height_cm`: Height in centimeters
- `weight_kg`: Weight in kilograms

#### **Personal Details:**
- `education_level`: `"none"`, `"secondary"`, `"college"`, `"university"`, `"postgrad"`
- `relationship_status`: `"single"`, `"dating"`, `"married"`, `"complicated"`
- `smokes`: `"no"`, `"occasionally"`, `"yes"`
- `drinks`: `"no"`, `"occasionally"`, `"yes"`

#### **Verification:**
- `is_verified`: Basic profile verification
- `id_verified`: ID document verified by admin
- `phone_verified`: Phone number verified
- `is_escort_verified`: Property that checks `phone_verified` AND at least one profile photo

#### **Privacy:**
- `visibility`: `"public"`, `"members"`, `"connections"`
- `show_online_status`: Show when online
- `hide_from_search`: Hide from browse/search
- `incognito_mode`: View profiles without appearing in visitors list

#### **Social Media:**
- `instagram`: Instagram username/handle
- `twitter`: Twitter username/handle
- `snapchat`: Snapchat username
- `website`: Personal website URL

---

## 🔍 **Area Choices** (Nairobi Areas)

Available area options:
- `"mirema"` - Mirema
- `"kasarani"` - Kasarani
- `"wandani"` - Wandani
- `"kimbo"` - Kimbo (Githurai Kimbo)
- `"roysambu"` - Roysambu
- `"zimmerman"` - Zimmerman
- `"githurai"` - Githurai
- `"thika_road_other"` - Other Thika Road Area
- `"nairobi_other"` - Other Nairobi Area
- `"other"` - Other

---

## ✅ **Minimum Requirements for Escort Visibility**

For an escort to be visible in browse/search results, they need:

1. **Phone Verification**: `phone_verified = True`
2. **At Least One Photo**: `profile_photos.exists() = True`
3. **Account Active**: `user.is_active = True`
4. **Not Hidden**: `hide_from_search = False`

The `is_escort_verified` property automatically checks these requirements.

---

## 📊 **Profile Completeness Score**

The profile completeness is calculated based on:
- Bio filled
- Age provided
- Location provided
- Interests filled
- Profile photos uploaded
- Video intro uploaded
- Any verification (is_verified, id_verified, or phone_verified)
- Social links provided (Instagram, Twitter, Snapchat, or Website)

Score ranges from 0-100%.

---

## 💡 **Usage Example in Django**

```python
from accounts.models import User
from connections.models import UserProfile

# Get escort user
escort = User.objects.get(username='sarah_escort')

# Access profile
profile = escort.hookup_profile

# Check verification
is_verified = escort.is_escort_verified()  # True if phone_verified + has photos

# Get profile completeness
completeness = profile.profile_completeness  # 0-100

# Check if online
is_online = profile.is_active_now

# Get all photos
photos = profile.profile_photos.all()

# Get subscription
subscription = escort.subscription if hasattr(escort, 'subscription') else None
```

---

This example represents a fully completed, verified escort profile with premium subscription and active status.
