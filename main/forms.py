# main/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Book, Profile, Review

# ===============================================
#  1. THE ONE AND ONLY BOOK FORM
# ===============================================
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'category', 'course', 'condition', 
            'price', 'original_price', 'description'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. The Great Gatsby'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-input price-input'}),
            'original_price': forms.NumberInput(attrs={'class': 'form-input price-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Add details about the book...'
            }),
        }
        
        labels = {
            'title': 'Book Title*',
            'category': 'Category*',
            'course': 'Course*',
            'condition': 'Condition*',
            'price': 'Price (Rs)*',
            'original_price': 'Original Price (Optional)',
            'description': 'Description',
        }

    # This function adds the placeholder text to the dropdowns
    # --- THIS IS THE FIX: 'self' was missing ---
    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select a Category"
        self.fields['course'].empty_label = "Select a Course"
        self.fields['condition'].empty_label = "Select the Book's Condition"


# ===============================================
#  2. USER-RELATED FORMS
# ===============================================
class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'location']
        labels = {
            'profile_picture': 'Change Profile Picture',
            'bio': 'About Me',
            'location': 'My City',
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
        }
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        
        # --- THIS IS THE FIX: Add the new address fields to this list ---
        fields = [
            'profile_picture', 'bio', 'location',
            'full_name', 'phone_number', 'address_line_1', 'city'
        ]
        
        # We should also add labels for them
        labels = {
            'profile_picture': 'Change Profile Picture',
            'bio': 'About Me',
            'location': 'Public Location (City)',
            'full_name': 'Full Name (for delivery)',
            'phone_number': 'Contact Number',
            'address_line_1': 'Street Address / Tole',
            'city': 'City / District (for delivery)',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }