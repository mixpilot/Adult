# User Type-Based Subscriptions

## ✅ **IMPLEMENTATION COMPLETE**

The subscription system now supports different plans for **Clients** (looking for escorts) and **Escorts** (providing services).

---

## 🎯 **WHAT'S BEEN IMPLEMENTED**

### **1. User Type System**
- ✅ Added `user_type` field to User model
- ✅ Choices: `client` (default) or `escort`
- ✅ Users can change their type in Account Settings
- ✅ Helper methods: `user.is_escort` and `user.is_client`

### **2. Subscription Plans by User Type**
- ✅ Plans can be for: `client`, `escort`, or `both`
- ✅ Each tier (Free, Basic, Premium, VIP) can exist for both types
- ✅ Unique constraint: `(tier, user_type)` - prevents duplicates

### **3. Client Plans Features**
- Unlimited Messaging
- Unlimited Content Access
- Ad-Free Experience
- Advanced Search
- Priority Support

### **4. Escort Plans Features**
- Featured Listing (top placement)
- Profile Verification Badge
- Unlimited Photos
- Priority Ranking (higher in search)
- Earnings Dashboard
- Creator Earnings

### **5. Updated Views & Templates**
- ✅ Subscription plans page filters by user type
- ✅ Shows relevant plans for client or escort
- ✅ Displays appropriate features for each plan
- ✅ Option to switch account type to see other plans

### **6. Profile Settings**
- ✅ Users can set/change their account type
- ✅ Phone number field for mobile payments
- ✅ Clear explanation of client vs escort

---

## 📋 **PLAN STRUCTURE**

### **Client Plans:**
1. **Free** - $0/month
   - Basic browsing
   - Limited messaging

2. **Basic** - $9.99/month
   - Unlimited messaging
   - Basic search

3. **Premium** - $19.99/month
   - Unlimited messaging
   - Unlimited content access
   - Ad-free
   - Advanced search

4. **VIP** - $39.99/month
   - All Premium features
   - Priority support

### **Escort Plans:**
1. **Free** - $0/month
   - Basic profile listing
   - Receive messages

2. **Basic** - $14.99/month
   - Unlimited photos
   - Basic earnings tracking

3. **Premium** - $29.99/month
   - Featured listing
   - Verified badge
   - Priority ranking
   - Earnings dashboard
   - Creator earnings

4. **VIP** - $49.99/month
   - All Premium features
   - Priority support
   - Maximum visibility

---

## 🔄 **USER FLOW**

### **For Clients:**
1. User sets account type to "Client" in settings
2. Views subscription plans page
3. Sees client-specific plans (Free, Basic, Premium, VIP)
4. Subscribes to chosen plan
5. Gets client features (unlimited messaging, content access, etc.)

### **For Escorts:**
1. User sets account type to "Escort" in settings
2. Views subscription plans page
3. Sees escort-specific plans (Free, Basic, Premium, VIP)
4. Subscribes to chosen plan
5. Gets escort features (featured listing, verified badge, earnings, etc.)

### **Switching Types:**
- Users can change account type in Account Settings
- Changing type shows different subscription plans
- Current subscription remains active until it expires

---

## 🛠️ **TO CREATE PLANS**

Run the script to create all plans:
```bash
python create_user_type_plans.py
```

Or create manually in Django admin:
1. Go to `/admin/subscriptions/subscriptionplan/`
2. Create plans with appropriate `user_type`:
   - `client` - For users looking for escorts
   - `escort` - For escorts providing services
   - `both` - Available for both types

---

## 📍 **WHERE USERS SEE THIS**

1. **Account Settings** (`/accounts/profile/`)
   - Set/change account type
   - Set phone number

2. **Subscription Plans** (`/subscriptions/plans/`)
   - Shows plans based on user type
   - Different features displayed for clients vs escorts
   - Option to switch account type

3. **Navigation**
   - "Subscribe" link shows relevant plans
   - Dashboard shows subscription status

---

## ✅ **STATUS**

**Fully Implemented and Ready!**

- ✅ User type system
- ✅ Separate plans for clients and escorts
- ✅ Different features per plan type
- ✅ UI updates to show relevant plans
- ✅ Profile settings to change type

**Next Step:** Create the subscription plans using the script or Django admin.

---

## 💡 **NOTES**

- Users default to "client" type
- Plans can be shared (`user_type='both'`) if needed
- Each tier can have different pricing for clients vs escorts
- Escort plans are typically priced higher (they earn money)
- Client plans focus on access and messaging
- Escort plans focus on visibility and earnings
