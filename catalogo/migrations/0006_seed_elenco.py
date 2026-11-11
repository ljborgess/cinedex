from django.db import migrations

# (filme, ator, nacionalidade do ator, personagem)
ELENCO = [
    ('Pulp Fiction', 'John Travolta', 'Norte-americana', 'Vincent Vega'),
    ('Pulp Fiction', 'Samuel L. Jackson', 'Norte-americana', 'Jules Winnfield'),
    ('Pulp Fiction', 'Uma Thurman', 'Norte-americana', 'Mia Wallace'),
    ('Kill Bill: Volume 1', 'Uma Thurman', 'Norte-americana', 'A Noiva'),
    ('Clube da Luta', 'Edward Norton', 'Norte-americana', 'Narrador'),
    ('Clube da Luta', 'Brad Pitt', 'Norte-americana', 'Tyler Durden'),
    ('Se7en: Os Sete Crimes Capitais', 'Brad Pitt', 'Norte-americana', 'Detetive Mills'),
    ('Se7en: Os Sete Crimes Capitais', 'Morgan Freeman', 'Norte-americana', 'Detetive Somerset'),
    ('Matrix', 'Keanu Reeves', 'Canadense', 'Neo'),
    ('Matrix', 'Laurence Fishburne', 'Norte-americana', 'Morpheus'),
    ('Matrix', 'Carrie-Anne Moss', 'Canadense', 'Trinity'),
    ('A Origem', 'Leonardo DiCaprio', 'Norte-americana', 'Dom Cobb'),
    ('A Origem', 'Elliot Page', 'Canadense', 'Ariadne'),
    ('Interestelar', 'Matthew McConaughey', 'Norte-americana', 'Cooper'),
    ('Interestelar', 'Anne Hathaway', 'Norte-americana', 'Amelia Brand'),
    ('O Poderoso Chefão', 'Marlon Brando', 'Norte-americana', 'Vito Corleone'),
    ('O Poderoso Chefão', 'Al Pacino', 'Norte-americana', 'Michael Corleone'),
    ('Bacurau', 'Sônia Braga', 'Brasileira', 'Domingas'),
    ('Bacurau', 'Udo Kier', 'Alemã', 'Michael'),
    ('Central do Brasil', 'Fernanda Montenegro', 'Brasileira', 'Dora'),
    ('Tropa de Elite', 'Wagner Moura', 'Brasileira', 'Capitão Nascimento'),
    ('Cidade de Deus', 'Alexandre Rodrigues', 'Brasileira', 'Buscapé'),
    ('Parasita', 'Song Kang-ho', 'Sul-coreana', 'Kim Ki-taek'),
    ('O Iluminado', 'Jack Nicholson', 'Norte-americana', 'Jack Torrance'),
    ('Whiplash: Em Busca da Perfeição', 'Miles Teller', 'Norte-americana', 'Andrew Neiman'),
    ('Whiplash: Em Busca da Perfeição', 'J. K. Simmons', 'Norte-americana', 'Terence Fletcher'),
    ('La La Land: Cantando Estações', 'Ryan Gosling', 'Canadense', 'Sebastian'),
    ('La La Land: Cantando Estações', 'Emma Stone', 'Norte-americana', 'Mia'),
]


def criar_elenco(apps, schema_editor):
    Ator = apps.get_model('catalogo', 'Ator')
    Filme = apps.get_model('catalogo', 'Filme')
    Elenco = apps.get_model('catalogo', 'Elenco')

    ordem_por_filme = {}
    for titulo, nome, nacionalidade, personagem in ELENCO:
        filme = Filme.objects.filter(titulo=titulo).first()
        if filme is None:
            continue
        ator, _ = Ator.objects.get_or_create(nome=nome, defaults={'nacionalidade': nacionalidade})
        ordem = ordem_por_filme[titulo] = ordem_por_filme.get(titulo, 0) + 1
        Elenco.objects.get_or_create(
            filme=filme, ator=ator,
            defaults={'personagem': personagem, 'ordem': ordem},
        )


def remover_elenco(apps, schema_editor):
    Ator = apps.get_model('catalogo', 'Ator')
    Elenco = apps.get_model('catalogo', 'Elenco')
    nomes = {nome for _, nome, _, _ in ELENCO}
    Elenco.objects.filter(ator__nome__in=nomes).delete()
    Ator.objects.filter(nome__in=nomes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0005_ator_elenco'),
    ]

    operations = [
        migrations.RunPython(criar_elenco, remover_elenco),
    ]
