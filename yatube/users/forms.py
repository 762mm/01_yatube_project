from django.contrib.auth.forms import UserCreationForm  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
