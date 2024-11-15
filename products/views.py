from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import UserRegisterForm, ReviewForm
from .models import Product, Review

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'products/register.html', {'form': form})

def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.review_set.all().order_by('-created_at')
    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
    })

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, 'You have already reviewed this product')
        return redirect('product_detail', pk=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, 'Review added successfully!')
            return redirect('product_detail', pk=product_id)
    else:
        form = ReviewForm()
    
    return render(request, 'products/add_review.html', {
        'form': form,
        'product': product
    })

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    
    if review.user != request.user:
        return HttpResponseForbidden("You cannot edit this review.")
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('product_detail', pk=review.product.pk)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'products/edit_review.html', {
        'form': form,
        'review': review,
        'product': review.product
    })

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    
    if review.user != request.user:
        return HttpResponseForbidden("You cannot delete this review.")
    
    if request.method == 'POST':
        product_id = review.product.id
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return redirect('product_detail', pk=product_id)
    
    return render(request, 'products/delete_review.html', {
        'review': review
    })

@login_required
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'products/my_reviews.html', {'reviews': reviews})
