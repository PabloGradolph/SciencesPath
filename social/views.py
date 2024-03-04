from django.http import HttpRequest, HttpResponse
from typing import Union
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, Relationship, Like
from .forms import PostForm, UserUpdateForm, ProfileUpdateForm, AddressUpdateForm
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def home(request: HttpRequest) -> HttpResponse:
    """
    Renders the home page with all posts and a form to create a new post.
    
    If the request method is POST, it processes the submitted form for a new post.
    Otherwise, it displays a blank form along with existing posts.
    """

    # Gets the IDs of the users that the current user is following.
    followed_users_ids = request.user.profile.following().values_list('id', flat=True)

    # Filter posts to include only those from followed users.
    posts = Post.objects.filter(Q(user_id__in=followed_users_ids) | Q(user=request.user)).distinct().order_by('-timestamp')

    # Create a dictionary to track which posts the user has liked
    likes = {like.post_id: True for like in Like.objects.filter(user=request.user)}

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community_home')
    else:
        form = PostForm()

    # Find the 3 users with the most publications.
    top_users = User.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:8]

    context = {'posts': posts, 'form': form, 'top_users': top_users, 'likes': likes}
    return render(request, 'social/communityhome.html', context)


@login_required(login_url='login')
def delete(request: HttpRequest, post_id: int) -> HttpResponse:
    """
    Deletes a post by its ID and redirects to the previous page or community home.
    
    The function retrieves the post by its ID and deletes it. Then, it checks the referer URL to decide where to redirect the user.
    """
    post = Post.objects.get(id=post_id)
    post.delete()
    
    # Obtén la URL de la página anterior
    referer = request.META.get('HTTP_REFERER')
        
    if 'profile' in referer:
        username = request.user.username
        profile_url = reverse('profile', kwargs={'username': username})
        return redirect(profile_url)
    else:
        return redirect('community_home')


@login_required(login_url='login')
def edit(request: HttpRequest) -> HttpResponse:
    """
    Renders a page for editing user and profile information.
    
    On POST request, it updates the user and profile information if the submitted forms are valid.
    On GET request, it displays the forms for editing with the current information.
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        a_form = AddressUpdateForm(request.POST, instance=request.user.profile.address if hasattr(request.user.profile, 'address') else None)

        if u_form.is_valid() and p_form.is_valid() and a_form.is_valid():
            u_form.save()
            p_form.save()
            address = a_form.save(commit=False)
            if not address.pk:
                address.save()
                request.user.profile.address = address
                request.user.profile.save()
            username = request.user.username
            profile_url = reverse('profile', kwargs={'username': username})
            return redirect(profile_url)
        else:
            print(u_form.errors)
            print(p_form.errors)
            print(a_form.errors)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        a_form = AddressUpdateForm(instance=request.user.profile.address if hasattr(request.user.profile, 'address') else None)
        
    context = {'u_form': u_form, 'p_form': p_form, 'a_form': a_form}
    return render(request, 'social/edit.html', context)

@login_required(login_url='login')
def follow(request: HttpRequest, username: str) -> HttpResponse:
    """
    Creates a follow relationship between the current user and another user.
    
    Redirects to the followed user's profile page upon completion.
    """
    current_user = request.user
    to_user = User.objects.get(username=username)
    to_user_id = to_user
    rel = Relationship(from_user=current_user, to_user=to_user_id)
    rel.save()
    profile_url = reverse('profile', kwargs={'username': username})
    return redirect(profile_url)


@login_required(login_url='login')
def unfollow(request: HttpRequest, username: str) -> HttpResponse:
    """
    Deletes a follow relationship between the current user and another user.
    
    Redirects to the unfollowed user's profile page upon completion.
    """
    current_user = request.user
    to_user = User.objects.get(username=username)
    rel = Relationship.objects.get(from_user=current_user.id, to_user=to_user.id)
    rel.delete()
    profile_url = reverse('profile', kwargs={'username': username})
    return redirect(profile_url)


@login_required(login_url='login')
@require_POST
def post_like(request):
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    
    if post_id and action:
        try:
            post = Post.objects.get(id=post_id)
            if action == 'like':
                Like.objects.get_or_create(post=post, user=request.user)
            else:
                Like.objects.filter(post=post, user=request.user).delete()
            return JsonResponse({'status': 'ok'})
        except Post.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Post not found.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})