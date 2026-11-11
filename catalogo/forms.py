from django import forms

from .models import Ator, Avaliacao, Diretor, Elenco, Filme, Genero


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


class AtorForm(forms.ModelForm):
    class Meta:
        model = Ator
        fields = ['nome', 'nacionalidade']
        labels = {'nome': 'Nome', 'nacionalidade': 'Nacionalidade'}
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Fernanda Montenegro'}),
            'nacionalidade': forms.TextInput(attrs={'placeholder': 'Ex.: Brasileira'}),
        }


class ElencoForm(forms.ModelForm):
    """Coloca um ator no elenco de um filme (uma linha da tabela through)."""

    class Meta:
        model = Elenco
        fields = ['ator', 'personagem', 'ordem']
        labels = {'ator': 'Ator', 'personagem': 'Personagem', 'ordem': 'Ordem nos créditos'}
        widgets = {
            'personagem': forms.TextInput(attrs={'placeholder': 'Ex.: Capitão Nascimento'}),
        }

    def __init__(self, *args, filme=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.filme = filme
        self.fields['ator'].empty_label = 'Selecione um ator'

    def clean_ator(self):
        # O filme não é campo do formulário, então o ModelForm não confere a
        # UniqueConstraint (filme, ator) sozinho. A checagem fica aqui.
        ator = self.cleaned_data['ator']
        if self.filme is not None:
            repetido = Elenco.objects.filter(filme=self.filme, ator=ator).exclude(pk=self.instance.pk)
            if repetido.exists():
                raise forms.ValidationError('Este ator já está no elenco do filme.')
        return ator


class ConsultaForm(forms.Form):
    """Filtros da tela de consultas. É um Form comum (não ModelForm): não
    grava nada, só monta a busca. Todos os campos são opcionais."""

    ORDENACOES = [
        ('titulo', 'Título (A–Z)'),
        ('-media', 'Maior média'),
        ('-total_avaliacoes', 'Mais avaliados'),
    ]

    titulo = forms.CharField(
        label='Título contém', required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Parte do título'}),
    )
    genero = forms.ModelChoiceField(
        label='Gênero', queryset=Genero.objects.all(), required=False, empty_label='Todos',
    )
    diretor = forms.ModelChoiceField(
        label='Diretor', queryset=Diretor.objects.all(), required=False, empty_label='Todos',
    )
    ator = forms.ModelChoiceField(
        label='Ator no elenco', queryset=Ator.objects.all(), required=False, empty_label='Qualquer',
    )
    nota_minima = forms.TypedChoiceField(
        label='Média mínima', required=False, coerce=int, empty_value=None,
        choices=[('', 'Qualquer')] + [(n, f'{n} ou mais') for n in range(1, 6)],
    )
    ordenar = forms.ChoiceField(label='Ordenar por', choices=ORDENACOES, required=False)
