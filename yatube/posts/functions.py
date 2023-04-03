from django.conf import settings  # type: ignore
from django.core.paginator import Paginator  # type: ignore


def get_page(request, post_list):
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
