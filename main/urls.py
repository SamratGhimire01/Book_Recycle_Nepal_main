from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    # --- Core Public Pages ---
    path('', views.home, name='home'),
    path('books/', views.listed_books, name='listed_books'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('categories/', views.all_categories, name='all_categories'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),

    # --- Authentication ---
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # --- User Dashboards & Profiles ---
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('my-listings/', views.my_listings_dashboard, name='my_listings'),

    # --- Book & Listing Actions ---
    path('sell/', views.sell_book, name='sell_book'),
    path('my-listings/edit/<int:book_id>/', views.edit_listing, name='edit_listing'),
    path('my-listings/delete/<int:book_id>/', views.delete_listing, name='delete_listing'),

    # --- Cart Actions ---
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    
    # --- Reviews, Favorites, Follows ---
    path('book/<int:book_id>/review/', views.add_review, name='add_review'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('toggle-follow/', views.toggle_follow, name='toggle_follow'),

    # --- API-like URLs for JavaScript ---
    path('live-search/', views.live_search_books, name='live_search_books'),
    path('update-theme/', views.update_theme, name='update_theme'),
]