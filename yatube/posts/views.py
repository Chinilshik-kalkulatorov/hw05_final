from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from .forms import PostForm
from .models import Group, Post, User


def get_page_obj(request, *args):
    """Получение объекта page_obj для пагинатора"""
    paginator = Paginator(*args, settings.PER_PAGE_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Стартовая страница проекта, выводятся все посты без фильтрации,
    посты представлены в краткой версии"""
    template = 'posts/index.html'
    page_obj = get_page_obj(request, Post.objects.all().select_related(
        'author', 'group'))
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context=context)


def group_posts(request, slug):
    """Вывод постов по группам, применена пагинация по 10"""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    page_obj = get_page_obj(request, group.posts.all().select_related('author')
                            )
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    """Профайл автора со всеми его постами"""
    author = get_object_or_404(User, username=username)
    page_obj = get_page_obj(request, author.posts.all().select_related('group')
                            )
    context = {
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Вывод полной версии поста"""
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Функция обработки формы для создания нового поста"""
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(f'/profile/{post.author.username}/')
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Функция обработки формы для редактирования поста автора"""
    post = get_object_or_404(Post, pk=post_id)
    if request.user.id == post.author.id:
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect(f'/posts/{post_id}')
        return render(request, 'posts/create_post.html',
                      {'form': form,
                       'is_edit': True
                       })
    else:
        return redirect(f'/posts/{post_id}')
