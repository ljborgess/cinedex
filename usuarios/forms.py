from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from . import limite
from .models import Perfil


class LoginForm(AuthenticationForm):
    """Login com limite de tentativas erradas por IP.

    O bloqueio é checado antes de conferir a senha: quem está bloqueado não
    consegue nem testar se acertou. A mensagem é a mesma para qualquer usuário,
    exista a conta ou não.
    """

    def clean(self):
        if limite.bloqueado(self.request, 'login'):
            raise forms.ValidationError(limite.MENSAGEM, code='muitas_tentativas')
        try:
            return super().clean()
        except forms.ValidationError:
            limite.contar(self.request, 'login')
            raise


class AdminLoginForm(LoginForm, AdminAuthenticationForm):
    """O mesmo limite no login do /admin/, que tem formulário próprio.

    Sem isto, o /admin/ era a porta lateral: tentativas sem fim contra a conta
    `admin`. O contador é o mesmo do site, então errar num lado conta no outro.
    """


class CadastroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username']
        labels = {'username': 'Usuário'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # As ajudas padrão do Django são listas longas; aqui basta uma linha.
        self.fields['username'].help_text = 'Letras, números e @ . + - _'
        self.fields['password1'].help_text = 'Pelo menos 8 caracteres, sem ser só números.'
        self.fields['password2'].help_text = ''


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['apelido', 'bio', 'genero_favorito']
        labels = {
            'apelido': 'Como quer ser chamado',
            'bio': 'Sobre você',
            'genero_favorito': 'Gênero favorito',
        }
        widgets = {
            'apelido': forms.TextInput(attrs={'placeholder': 'Ex.: Lu'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Que tipo de filme você gosta?'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['genero_favorito'].empty_label = 'Nenhum'
