from django import forms

from .models import Avaliacao, Diretor, Filme, Genero


class GeneroForm(forms.ModelForm):
    class Meta:
        model = Genero
        fields = ['nome']
        labels = {'nome': 'Nome do gênero'}
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Ficção Científica'}),
        }


class DiretorForm(forms.ModelForm):
    class Meta:
        model = Diretor
        fields = ['nome', 'nacionalidade']
        labels = {'nome': 'Nome', 'nacionalidade': 'Nacionalidade'}
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Christopher Nolan'}),
            'nacionalidade': forms.TextInput(attrs={'placeholder': 'Ex.: Britânica'}),
        }


class FilmeForm(forms.ModelForm):
    class Meta:
        model = Filme
        fields = ['titulo', 'genero', 'diretor', 'sinopse']
        labels = {
            'titulo': 'Título',
            'genero': 'Gênero',
            'diretor': 'Diretor',
            'sinopse': 'Sinopse',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Título do filme'}),
            'sinopse': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Escreva uma breve sinopse...'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['genero'].empty_label = 'Selecione um gênero'
        self.fields['diretor'].empty_label = 'Selecione um diretor'


class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['filme', 'autor', 'nota', 'comentario']
        labels = {
            'filme': 'Filme',
            'autor': 'Seu nome',
            'nota': 'Nota',
            'comentario': 'Comentário',
        }
        widgets = {
            'autor': forms.TextInput(attrs={'placeholder': 'Quem está avaliando'}),
            'nota': forms.Select(
                choices=[(n, f'{n} {"estrela" if n == 1 else "estrelas"}') for n in range(1, 6)]
            ),
            'comentario': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'O que você achou do filme?'}
            ),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['filme'].empty_label = 'Selecione um filme'
        # Só os filmes do próprio usuário aparecem e são aceitos: um id de
        # filme alheio enviado à mão no POST falha na validação do campo.
        if usuario is not None:
            self.fields['filme'].queryset = Filme.objects.filter(usuario=usuario)
