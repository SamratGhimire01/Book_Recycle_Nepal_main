# main/admin.py

from django.contrib import admin
from .models import Category, Course, Book, BookImage, Profile, Follow
# --- ADD 'Review' TO THIS IMPORT ---
from .models import Review

# --- (Your existing BookAdmin class is here) ---
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'status', 'created_at', 'rejection_reason')
    list_filter = ('status', 'category')
    search_fields = ('title', 'seller__username')
    list_editable = ('status', 'rejection_reason')
    actions = ['approve_books']

    def approve_books(self, request, queryset):
        queryset.update(status='Available')
    approve_books.short_description = "Mark selected books as Available"

# --- (Your existing CourseAdmin and CategoryAdmin can be here) ---
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

# --- Register your models here ---
admin.site.register(Category, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookImage)
admin.site.register(Profile)
admin.site.register(Follow)

# ===============================================
# == THIS IS THE LINE THAT WAS MISSING         ==
# ===============================================
admin.site.register(Review)