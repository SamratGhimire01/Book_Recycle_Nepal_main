# main/views.py

# ===============================
#  1. IMPORTS
# ===============================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q, Avg, Sum
from django.template.loader import render_to_string
import json
from decimal import Decimal

from .models import Book, BookImage, Category, Course, Profile, Review, Favorite, Follow, Order, OrderItem
from .forms import BookForm, RegistrationForm, ProfileUpdateForm, ReviewForm


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
    
    # --- THIS IS THE NEW LOGIC ---
    # Check if the currently logged-in user is the seller of this book
    is_seller = (request.user == book.seller)

    context = {
        'book': book,
        'similar_books': similar_books,
        'reviews': reviews,
        'is_seller': is_seller, # <-- Pass this boolean to the template
    }
    return render(request, 'book_detail.html', context)

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
#  4. BOOK LISTING ACTIONS & REVIEWS
# ===============================
@login_required
def sell_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('images')
            if len(images) > 0:
                book = form.save(commit=False)
                book.seller = request.user
                book.cover_image = images[0]
                book.save()
                for image_file in images:
                    BookImage.objects.create(book=book, image=image_file)
                return redirect('my_listings')
            else:
                form.add_error(None, "Please upload at least one image.")
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
#  5. CART & CHECKOUT FLOW
# ===============================
def view_cart(request):
    cart = request.session.get('cart', {})
    book_ids = [int(bid) for bid in cart.keys()]
    books_in_cart = Book.objects.filter(id__in=book_ids)
    
    selected_book_ids_str = request.session.get('selected_for_checkout', [str(bid) for bid in book_ids])
    selected_book_ids = [int(bid) for bid in selected_book_ids_str]
    
    # subtotal will be a Decimal because book.price is a DecimalField
    subtotal = sum(book.price for book in books_in_cart if book.id in selected_book_ids)
    delivery_charge = Decimal('100.00')
    voucher_discount = Decimal('0.00')
    grand_total = subtotal + delivery_charge - voucher_discount
    context = {
        'books_in_cart': books_in_cart,
        'selected_book_ids': selected_book_ids,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'voucher_discount': voucher_discount,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)

@login_required
def checkout(request):
    selected_ids = request.session.get('selected_for_checkout', [])
    if not selected_ids: return redirect('view_cart')
    books_for_checkout = Book.objects.filter(id__in=selected_ids)
    total_price = sum(book.price for book in books_for_checkout)
    return render(request, 'checkout.html', {'books_in_cart': books_for_checkout, 'total_price': total_price})

@login_required
def place_order(request):
    selected_ids = request.session.get('selected_for_checkout', [])
    if not selected_ids or request.method != 'POST': return redirect('view_cart')
    books_in_order = Book.objects.filter(id__in=selected_ids)
    total_price = sum(book.price for book in books_in_order)
    profile = request.user.profile
    shipping_address = f"{profile.full_name}\n{profile.address_line_1}\n{profile.city}\nPhone: {profile.phone_number}"
    order = Order.objects.create(buyer=request.user, shipping_address=shipping_address, total_price=total_price, payment_method='COD')
    for book in books_in_order:
        OrderItem.objects.create(order=order, book=book, price=book.price)
        book.status = 'Sold'; book.save()
    request.session['cart'] = {}; request.session['selected_for_checkout'] = []
    return redirect('order_success', order_id=order.id)

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    return render(request, 'order_success.html', {'order': order})

@login_required
def order_tracking(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    return render(request, 'order_tracking.html', {'order': order})


# ===============================
#  6. API-LIKE VIEWS (for JavaScript)
# ===============================
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        cart = request.session.get('cart', {})
        cart[str(book_id)] = 1
        request.session['cart'] = cart
        return JsonResponse({'status': 'ok', 'message': f'"{book.title}" added to cart.', 'cart_item_count': len(cart)})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def remove_from_cart(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        cart = request.session.get('cart', {})
        if str(book_id) in cart:
            del cart[str(book_id)]
            request.session['cart'] = cart
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def update_cart_selection(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids[]')
        request.session['selected_for_checkout'] = selected_ids
        return JsonResponse({'status': 'ok'})
    return HttpResponseBadRequest("Invalid request method")

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
        user_to_follow_id = request.POST.get('user_to_follow_id')
        if user_to_follow_id:
            try:
                user_to_follow = User.objects.get(id=user_to_follow_id)
                if user_to_follow == request.user:
                     return JsonResponse({'status': 'error', 'message': 'You cannot follow yourself.'}, status=400)
                favorite, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
                if not created:
                    favorite.delete()
                return JsonResponse({'status': 'ok', 'is_following': created})
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def my_orders(request):
    """
    Shows a list of all orders placed by the currently logged-in user.
    """
    # Fetch all orders where the 'buyer' is the current user.
    # 'prefetch_related' is a performance optimization to get all related items efficiently.
    orders = Order.objects.filter(buyer=request.user).prefetch_related('items__book').order_by('-created_at')
    
    context = {
        'orders': orders
    }
    return render(request, 'my_orders.html', context)