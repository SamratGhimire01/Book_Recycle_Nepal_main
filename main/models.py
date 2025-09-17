from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# A model for high-level categories like "Bachelors", "+2", etc.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name

# A model for specific courses like "BBS", "BCA", linked to a Category
class Course(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return f"{self.name} ({self.category.name})"

# The upgraded Book model with all the fields needed for the new card
class Book(models.Model):
    CONDITION_CHOICES = [
        ('As New', 'As New'),
        ('Fine', 'Fine'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Available', 'Available'),
        ('Sold', 'Sold'),
        ('Rejected', 'Rejected'), # <-- ADD THIS NEW STATUS
    ]
    title = models.CharField(max_length=200)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    condition = models.CharField(max_length=50, choices=[('As New', 'As New'), ('Fine', 'Fine'), ('Good', 'Good'), ('Fair', 'Fair')])
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True)


    # --- Core Information ---
    title = models.CharField(max_length=200)
    seller = models.ForeignKey(User, on_delete=models.CASCADE) # The user who listed the book
    
    # --- Linked Information for Filtering ---
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    
    # --- Price Information ---
    price = models.DecimalField(max_digits=10, decimal_places=2) # The current selling price
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # The old price (optional)
    
    # --- Descriptive Information ---
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True) # For the book cover
    
    # --- Auto-managed Fields ---
    created_at = models.DateTimeField(auto_now_add=True) # To calculate "5 days ago"
    is_available = models.BooleanField(default=True)
    
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class BookImage(models.Model):
    book = models.ForeignKey(Book, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='book_images/')

    def __str__(self):
        return f"Image for {self.book.title}"
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    
    class Meta:
        # Ensures a user can only favorite a book once
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.user.username} favorites {self.book.title}'

class Profile(models.Model):
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # --- ADD THIS NEW FIELD ---
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')

    def __str__(self):
        return f'{self.user.username} Profile'

# This is a Django signal. It automatically creates a Profile for a new User.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# This signal saves the profile when the user is saved.
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Review(models.Model):
    book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name='reviews_given', on_delete=models.CASCADE, null=True)
    seller = models.ForeignKey(User, related_name='reviews_received', on_delete=models.CASCADE, null=True)
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Review by {self.reviewer.username} for {self.seller.username}'


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed') # Can only follow once

    def __str__(self):
        return f'{self.follower.username} follows {self.followed.username}'

# =========================================================
# == END: NEW USER PROFILE & INTERACTION MODELS          ==
# =========================================================