from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Perfil


class CadastroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username']
        labels = {'username': 'Usuário'}


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
