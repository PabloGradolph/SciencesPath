from django.shortcuts import render, redirect
from .models import Profile, Post
from .forms import PostForm

def home(request):
    posts = Post.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community_home')
    else:
        form = PostForm()

    context = {'posts': posts, 'form': form}
    return render(request, 'social/newsfeed.html', context)


def delete(request, post_id):
    post = Post.objects.get(id=post_id)
    post.delete()
    return redirect('community_home')
