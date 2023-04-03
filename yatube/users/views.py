from django.views.generic import CreateView  # type: ignore

from django.urls import reverse_lazy  # type: ignore

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
