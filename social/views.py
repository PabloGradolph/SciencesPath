from django.http import HttpRequest, HttpResponse
from typing import Union
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Relationship
from .forms import PostForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def home(request: HttpRequest) -> HttpResponse:
    """
    Renders the home page with all posts and a form to create a new post.
    
    If the request method is POST, it processes the submitted form for a new post.
    Otherwise, it displays a blank form along with existing posts.
    """
    posts = Post.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community_home')
    else:
        form = PostForm()

    context = {'posts': posts, 'form': form}
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

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            username = request.user.username
            profile_url = reverse('profile', kwargs={'username': username})
            return redirect(profile_url)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {'u_form': u_form, 'p_form': p_form}
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