from django.contrib.auth.decorators import login_required  # type: ignore
from django.shortcuts import (  # type: ignore
    get_object_or_404,
    redirect,
    render
)

from .forms import CommentForm, PostForm
from .functions import get_page
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = get_page(request, post_list)
    return render(request, 'posts/index.html', {'page_obj': page_obj})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('author').filter(group=group)
    page_obj = get_page(request, post_list)
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': page_obj,
        },
    )


def profile(request, username):
    author = User.objects.get(username=username)
    post_list = author.posts.all()
    page_obj = get_page(request, post_list)
    following = (
        Follow.objects.filter(
            user=User.objects.filter(username=request.user).first(),
            author=author
        )
    ).exists()
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': page_obj,
            'following': following
        },
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form
        }

    )


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if not form.is_valid():
            return render(
                request,
                'posts/create_post.html',
                {
                    'post': post,
                    'form': form,
                    'is_edit': True
                }
            )
        form.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.select_related("author").filter(
        author__following__user=request.user
    )
    page_obj = get_page(request, post_list)
    return render(request, 'posts/follow.html', {'page_obj': page_obj})


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', author)
