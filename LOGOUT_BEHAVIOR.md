# Logout Behavior Documentation

## What Happens After Logout

When a user clicks "Logout" from the navigation menu, the following sequence occurs:

### 1. **User Clicks Logout**
- User clicks "Logout" from the dropdown menu in the navigation bar
- URL: `/accounts/logout/`
- Method: GET or POST (both supported)

### 2. **Logout Process**

The custom `logout_view` performs the following steps:

#### a. **Store Username**
- Captures the username before logout (for personalized message)

#### b. **Update Online Status**
- If user has a hookup profile, sets `is_online = False`
- Updates the profile in the database
- This ensures other users see the user as offline

#### c. **Logout User**
- Calls Django's `logout(request)` function
- This:
  - Clears the user's session data
  - Removes authentication cookies
  - Flushes the session from the database
  - User is no longer authenticated

#### d. **Success Message**
- Displays a personalized success message:
  - "You have been successfully logged out. Goodbye, [username]!"
  - Message appears at the top of the next page

#### e. **Redirect**
- Redirects to the home page (`/`)
- User sees the home page as a logged-out visitor

### 3. **After Redirect**

On the home page, the user will see:

- **Navigation Bar Changes:**
  - User dropdown menu disappears
  - "Login" and "Register" buttons appear
  - "Connect" link disappears (requires login)

- **Success Message:**
  - Green success alert at the top
  - Shows: "You have been successfully logged out. Goodbye, [username]!"
  - Can be dismissed by clicking the X button

- **Home Page Content:**
  - Featured content carousel
  - Latest content grid
  - Category showcase
  - Site statistics
  - All public content is still visible

### 4. **Session Cleanup**

Django automatically handles:
- Session data cleared
- Authentication tokens removed
- CSRF tokens reset
- All user-specific session variables cleared

### 5. **User State After Logout**

- ✅ **Not authenticated** - `request.user.is_authenticated = False`
- ✅ **Anonymous user** - `request.user` is an `AnonymousUser`
- ✅ **Online status** - Set to `False` (if hookup profile exists)
- ✅ **Session cleared** - All session data removed
- ✅ **Can browse** - Can still view public content
- ❌ **Cannot access** - Protected pages require login again

---

## Protected Pages After Logout

After logout, users will be redirected to login if they try to access:

- `/accounts/profile/` - Account settings
- `/connections/browse/` - Browse users
- `/connections/my-profile/` - Hookup profile
- `/connections/connections/` - My connections
- `/connections/messages/` - Messages
- `/content/upload/` - Upload content
- Any page with `@login_required` decorator

---

## Configuration

The logout behavior is configured in:

**`config/settings.py`:**
```python
LOGOUT_REDIRECT_URL = 'core:home'  # Redirects to home page
```

**`accounts/views.py`:**
```python
@login_required
@require_http_methods(["GET", "POST"])
def logout_view(request):
    # Custom logout logic
```

**`accounts/urls.py`:**
```python
path('logout/', views.logout_view, name='logout'),
```

---

## Security Features

1. **Requires Authentication** - `@login_required` ensures only logged-in users can logout
2. **HTTP Method Restriction** - Only GET and POST allowed
3. **Session Cleanup** - Complete session data removal
4. **CSRF Protection** - Django's CSRF middleware protects logout endpoint

---

## Future Enhancements

Potential improvements:
- [ ] Logout from all devices option
- [ ] Logout confirmation dialog
- [ ] Logout activity logging
- [ ] "Remember me" token cleanup
- [ ] Email notification on logout (optional)

---

## User Experience Flow

```
User clicks "Logout"
    ↓
Logout view processes:
    - Update online status
    - Clear session
    - Show success message
    ↓
Redirect to home page
    ↓
User sees:
    - Success message
    - Home page as guest
    - Login/Register buttons
```

---

## Testing Logout

To test logout functionality:

1. **Login** to the website
2. **Navigate** to any page
3. **Click** "Logout" from user menu
4. **Verify:**
   - Success message appears
   - Redirected to home page
   - Navigation shows Login/Register
   - Cannot access protected pages
   - Online status updated (if applicable)
