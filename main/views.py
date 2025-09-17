from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q, Avg, Sum, Count
from django.template.loader import render_to_string

from .models import Book, BookImage, Category, Course, Profile, Review, Favorite, Follow
from .forms import BookForm, RegistrationForm, ProfileUpdateForm, ReviewForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout


# ===============================
#  2. CORE PUBLIC VIEWS
# ===============================
def home(request):
    latest_books = Book.objects.filter(status='Available').order_by('-created_at')[:8]
    return render(request, 'index.html', {'latest_books': latest_books})

def listed_books(request):
    search_query = request.GET.get('q', '')
    all_books = Book.objects.filter(status='Available')
    if search_query:
        all_books = all_books.filter(
            Q(title__icontains=search_query) | Q(course__name__icontains=search_query) |
            Q(category__name__icontains=search_query) | Q(seller__username__icontains=search_query)
        ).distinct()
    return render(request, 'listed_books.html', {'books': all_books.order_by('-created_at'), 'search_query': search_query})

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id, status='Available')
    similar_books = Book.objects.filter(category=book.category, status='Available').exclude(id=book.id)[:4]
    reviews = book.reviews.all().order_by('-created_at')
    return render(request, 'book_detail.html', {'book': book, 'similar_books': similar_books, 'reviews': reviews})

def all_categories(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'all_categories.html', {'categories': categories})

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    search_query = request.GET.get('q', '')
    books_in_category = Book.objects.filter(category=category, status='Available')
    if search_query:
        books_in_category = books_in_category.filter(Q(title__icontains=search_query) | Q(course__name__icontains=search_query)).distinct()
    return render(request, 'category_detail.html', {'category': category, 'books': books_in_category.order_by('-created_at'), 'search_query': search_query})

def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    books_for_sale = Book.objects.filter(seller=profile_user, status='Available').order_by('-created_at')
    average_rating = profile_user.reviews_received.aggregate(Avg('rating'))['rating__avg']
    is_following = request.user.is_authenticated and Follow.objects.filter(follower=request.user, followed=profile_user).exists()
    context = {
        'profile_user': profile_user, 'books_for_sale': books_for_sale,
        'average_rating': average_rating, 'follower_count': profile_user.followers.count(),
        'following_count': profile_user.following.count(), 'is_following': is_following
    }
    return render(request, 'profile.html', context)


# ===============================
#  3. AUTHENTICATION & USER ACTIONS
# ===============================
class CustomLoginView(LoginView):
    template_name = 'login.html'

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def my_listings_dashboard(request):
    all_my_books = Book.objects.filter(seller=request.user)
    sold_books = all_my_books.filter(status='Sold')
    available_books = all_my_books.filter(status='Available')
    context = {
        'all_my_books': all_my_books.order_by('-created_at'),
        'total_listings': all_my_books.count(),
        'available_count': available_books.count(),
        'sold_count': sold_books.count(),
        'pending_count': all_my_books.filter(status='Pending').count(),
        'total_revenue_from_sold': sold_books.aggregate(total=Sum('price'))['total'] or 0,
        'potential_revenue_from_available': available_books.aggregate(total=Sum('price'))['total'] or 0,
    }
    return render(request, 'my_listings_dashboard.html', context)


# ===============================
#  4. BOOK LISTING ACTIONS
# ===============================
@login_required
def sell_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        images = request.FILES.getlist('images')
        if form.is_valid() and len(images) > 0:
            book = form.save(commit=False)
            book.seller = request.user
            book.cover_image = images[0]
            book.save()
            for image_file in images:
                BookImage.objects.create(book=book, image=image_file)
            return redirect('my_listings')
        else:
            if len(images) == 0:
                form.add_error(None, "Please upload at least one image.")
            return render(request, 'sell_book.html', {'form': form})
    else:
        form = BookForm()
    return render(request, 'sell_book.html', {'form': form})

@login_required
def edit_listing(request, book_id):
    book = get_object_or_404(Book, id=book_id, seller=request.user)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            updated_book = form.save()
            new_images = request.FILES.getlist('images')
            if new_images:
                if not updated_book.cover_image:
                    updated_book.cover_image = new_images[0]
                    updated_book.save()
                for image_file in new_images:
                    BookImage.objects.create(book=updated_book, image=image_file)
            return redirect('my_listings')
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_listing.html', {'form': form, 'book': book})

@login_required
def delete_listing(request, book_id):
    book = get_object_or_404(Book, id=book_id, seller=request.user)
    if request.method == 'POST':
        book.delete()
        return redirect('my_listings')
    return render(request, 'delete_listing_confirm.html', {'book': book})

@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.reviewer = request.user
            review.seller = book.seller
            review.save()
            return redirect('profile_view', username=book.seller.username)
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form, 'book': book})


# ===============================
#  5. API-LIKE VIEWS (for JavaScript)
# ===============================
def live_search_books(request):
    search_query = request.GET.get('q', '')
    if len(search_query) > 2:
        books = Book.objects.filter(status='Available').filter(
            Q(title__icontains=search_query) | Q(category__name__icontains=search_query)
        ).distinct()[:5]
        results = [{'title': b.title, 'url': f'/book/{b.id}/', 'image_url': b.cover_image.url if b.cover_image else ''} for b in books]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

@login_required
def toggle_favorite(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)
        if not created:
            favorite.delete()
        return JsonResponse({'status': 'favorited' if created else 'unfavorited'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def update_theme(request):
    if request.method == 'POST':
        theme = request.POST.get('theme')
        if theme in ['light', 'dark']:
            profile = request.user.profile
            profile.theme = theme
            profile.save()
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)
@login_required
def toggle_follow(request):
    if request.method == 'POST':
        # Get the ID of the user to be followed from the form data
        user_to_follow_id = request.POST.get('user_to_follow_id')
        
        if user_to_follow_id:
            try:
                # Find the user object that the current user wants to follow
                user_to_follow = User.objects.get(id=user_to_follow_id)
                
                # Prevent users from following themselves
                if user_to_follow == request.user:
                     return JsonResponse({'status': 'error', 'message': 'You cannot follow yourself.'}, status=400)

                # Check if the current user is already following them
                follow_instance, created = Follow.objects.get_or_create(
                    follower=request.user,
                    followed=user_to_follow
                )

                if created:
                    # If the instance was just created, it means they are now following
                    is_following = True
                else:
                    # If the instance already existed, it means they want to unfollow
                    follow_instance.delete()
                    is_following = False
                
                # Send a success response back to the JavaScript
                return JsonResponse({'status': 'ok', 'is_following': is_following})

            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# main/views.py
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        book_id_str = request.POST.get('book_id')
        if book_id_str:
            book = get_object_or_404(Book, id=int(book_id_str))
            cart = request.session.get('cart', {})
            
            cart[book_id_str] = 1 
            request.session['cart'] = cart
            
            # --- THIS IS THE CRITICAL IMPROVEMENT ---
            # Return the new number of items in the cart directly in the response.
            return JsonResponse({
                'status': 'ok',
                'message': f'"{book.title}" was added to your cart.',
                'cart_item_count': len(cart) # <-- ADD THIS
            })
            
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def remove_from_cart(request):
    if request.method == 'POST':
        book_id_str = request.POST.get('book_id')
        if book_id_str:
            cart = request.session.get('cart', {})
            if book_id_str in cart:
                del cart[book_id_str]
                request.session['cart'] = cart
            return JsonResponse({'status': 'ok', 'message': 'Book removed from cart.'})
    return JsonResponse({'status': 'error'}, status=400)

# main/views.py

def view_cart(request):
    """
    Displays the user's shopping cart with delivery charges.
    """
    cart = request.session.get('cart', {})
    book_ids = cart.keys()
    books_in_cart = Book.objects.filter(id__in=book_ids)
    
    subtotal = sum(book.price for book in books_in_cart)
    
    # --- NEW LOGIC: DELIVERY CHARGES ---
    delivery_charge = 0
    if books_in_cart.exists(): # Only add delivery charge if the cart is not empty
        delivery_charge = 100 
    
    # --- NEW LOGIC: VOUCHER (Placeholder) ---
    # For now, we'll simulate a voucher. A real system would be more complex.
    voucher_discount = 0
    voucher_code = request.GET.get('voucher', '') # Check if a voucher was submitted
    if voucher_code.upper() == 'RECYCLE10':
        voucher_discount = subtotal * 0.10 # 10% discount
    
    grand_total = (subtotal - voucher_discount) + delivery_charge
        
    context = {
        'books_in_cart': books_in_cart,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'voucher_discount': voucher_discount,
        'grand_total': grand_total,
        'voucher_code': voucher_code,
    }
    return render(request, 'cart.html', context)
