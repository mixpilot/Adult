# Decorators Documentation

This document describes all decorators used in the adult entertainment website.

## Custom Decorators (`core/decorators.py`)

### 1. `@age_verified_required`
**Purpose:** Ensures user has verified their age (18+)

**Usage:**
```python
@age_verified_required
def browse_users(request):
    # View code
```

**Behavior:**
- Checks if user is authenticated
- Verifies user has `date_of_birth` set
- Confirms user is at least 18 years old
- Redirects to profile if age not verified
- Redirects to home if under 18

**Applied to:**
- `connections/browse_users`
- `connections/user_profile`
- `connections/connect_user`

---

### 2. `@premium_required`
**Purpose:** Ensures user has premium access

**Usage:**
```python
@premium_required
def premium_content(request):
    # View code
```

**Behavior:**
- Checks if user is authenticated
- TODO: Check premium subscription status
- Currently allows all authenticated users (placeholder)

**Note:** This is a placeholder for future premium subscription implementation.

---

### 3. `@verified_user_required`
**Purpose:** Ensures user account is verified

**Usage:**
```python
@verified_user_required
def verified_feature(request):
    # View code
```

**Behavior:**
- Checks if user is authenticated
- Verifies `user.is_verified` is True
- Redirects to profile if not verified

---

### 4. `@rate_limit(max_requests, period, key_prefix)`
**Purpose:** Rate limits requests to prevent abuse

**Usage:**
```python
@rate_limit(max_requests=10, period=60, key_prefix='action_name')
def some_view(request):
    # View code
```

**Parameters:**
- `max_requests`: Maximum number of requests allowed
- `period`: Time period in seconds
- `key_prefix`: Cache key prefix for tracking

**Behavior:**
- Tracks requests per user (authenticated) or IP (anonymous)
- Returns 429 error if limit exceeded
- Uses Django cache for tracking

**Applied to:**
- `accounts/register_view` (5 requests/hour)
- `accounts/login_view` (10 requests/5 minutes)
- `content/upload_content` (10 requests/hour)
- `connections/connect_user` (20 requests/minute)
- `connections/block_user` (10 requests/5 minutes)
- `connections/chat` (30 requests/minute)

---

### 5. `@staff_or_owner_required`
**Purpose:** Ensures user is staff or owns the resource

**Usage:**
```python
@staff_or_owner_required
def edit_content(request, content_id):
    # View code
```

**Behavior:**
- Checks if user is authenticated
- Allows access if user is staff
- Otherwise, ownership must be checked in view

---

### 6. `@ajax_required`
**Purpose:** Ensures request is AJAX

**Usage:**
```python
@ajax_required
def ajax_endpoint(request):
    # View code
```

**Behavior:**
- Checks for `X-Requested-With: XMLHttpRequest` header
- Returns JSON error if not AJAX

---

### 7. `@check_premium_content`
**Purpose:** Checks if content is premium and user has access

**Usage:**
```python
@check_premium_content
def content_detail(request, slug):
    # View code
```

**Behavior:**
- Checks if content with slug is premium
- Redirects to login if not authenticated
- TODO: Check premium subscription

**Applied to:**
- `content/content_detail`

---

## Django Built-in Decorators

### `@login_required`
**Purpose:** Requires user to be authenticated

**Usage:**
```python
from django.contrib.auth.decorators import login_required

@login_required
def protected_view(request):
    # View code
```

**Applied to:**
- All profile views
- All connection views
- Content upload view

---

### `@require_POST`
**Purpose:** Only allows POST requests

**Usage:**
```python
from django.views.decorators.http import require_POST

@require_POST
def post_only_view(request):
    # View code
```

**Applied to:**
- `connections/connect_user`
- `connections/block_user`

---

### `@require_http_methods(["GET", "POST"])`
**Purpose:** Restricts allowed HTTP methods

**Usage:**
```python
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def get_post_view(request):
    # View code
```

**Applied to:**
- `accounts/register_view`
- `accounts/login_view`
- `content/upload_content`
- `connections/chat`

---

## Decorator Stacking

Multiple decorators can be stacked. Order matters - they execute from bottom to top:

```python
@login_required              # 3. Check authentication
@age_verified_required       # 2. Check age verification
@rate_limit(...)            # 1. Check rate limit
@require_POST               # 0. Check HTTP method
def my_view(request):
    # View code
```

**Execution order:**
1. `@require_POST` - Check HTTP method
2. `@rate_limit` - Check rate limit
3. `@age_verified_required` - Check age
4. `@login_required` - Check authentication
5. View function executes

---

## Best Practices

1. **Always use `@login_required` before custom decorators** that require authentication
2. **Use `@rate_limit` on public endpoints** to prevent abuse
3. **Combine `@age_verified_required` with `@login_required`** for adult content
4. **Use `@require_http_methods`** to restrict allowed methods
5. **Stack decorators in logical order** (method → rate limit → auth → permissions)

---

## Future Enhancements

- [ ] Add premium subscription check to `@premium_required`
- [ ] Add IP-based rate limiting for anonymous users
- [ ] Add decorator for content moderation
- [ ] Add decorator for email verification
- [ ] Add decorator for 2FA (two-factor authentication)
