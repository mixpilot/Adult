"""
Quick script to create sample testimonials so Phase 2 features are visible.
Run this from Django shell: python manage.py shell < create_sample_data.py
Or run: python manage.py shell, then paste the code below.
"""

from content.models import Testimonial, ActivityLog
from accounts.models import User
from content.models import Content

# Create sample testimonials if users exist
users = User.objects.all()[:5]
if users.exists():
    sample_testimonials = [
        {
            'text': 'Amazing platform! Found exactly what I was looking for. The content quality is top-notch and the community is great.',
            'rating': 5
        },
        {
            'text': 'Best adult entertainment site I\'ve used. Premium features are worth every penny. Highly recommend!',
            'rating': 5
        },
        {
            'text': 'Met my partner here! The matching system works perfectly. Great experience overall.',
            'rating': 5
        },
        {
            'text': 'Creators are professional and content is diverse. Love the premium features!',
            'rating': 4
        },
        {
            'text': 'Easy to use, great interface, and lots of content. What more could you ask for?',
            'rating': 5
        }
    ]
    
    created_count = 0
    for i, user in enumerate(users):
        if i < len(sample_testimonials):
            testimonial, created = Testimonial.objects.get_or_create(
                user=user,
                defaults={
                    'text': sample_testimonials[i]['text'],
                    'rating': sample_testimonials[i]['rating'],
                    'is_featured': True,
                    'is_approved': True
                }
            )
            if created:
                created_count += 1
    
    print(f"Created {created_count} sample testimonials")
else:
    print("No users found. Please create users first.")

# Activity feed should already be populated by the view logic
print("Sample data creation complete!")
print("\nTo see testimonials, make sure they are:")
print("1. Created (run this script)")
print("2. Marked as 'is_featured=True' and 'is_approved=True'")
print("3. View the home page - testimonials section should appear")
