"""Capas dos filmes do seed.

Endereços obtidos com `python manage.py buscar_capas` e conferidos um a um
(a busca automática trouxe a capa errada em Kill Bill e O Senhor dos Anéis,
corrigidas aqui). Só os links ficam no banco; as imagens são exibidas direto
da Wikimedia.
"""
from django.db import migrations

CAPAS = {
    'A Origem': 'https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_%282010%29_theatrical_poster.jpg',
    'A Viagem de Chihiro': 'https://upload.wikimedia.org/wikipedia/en/d/db/Spirited_Away_Japanese_poster.png',
    'Bacurau': 'https://upload.wikimedia.org/wikipedia/en/9/92/Bacurau_poster.jpg',
    'Central do Brasil': 'https://upload.wikimedia.org/wikipedia/en/1/12/Central-do-brasil-poster04.jpg',
    'Cidade de Deus': 'https://upload.wikimedia.org/wikipedia/en/1/10/CidadedeDeus.jpg',
    'Clube da Luta': 'https://upload.wikimedia.org/wikipedia/en/f/fc/Fight_Club_poster.jpg',
    'Interestelar': 'https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg',
    'Kill Bill: Volume 1': 'https://upload.wikimedia.org/wikipedia/en/2/2c/Kill_Bill_Volume_1.png',
    'La La Land: Cantando Estações': 'https://upload.wikimedia.org/wikipedia/en/a/ab/La_La_Land_%28film%29.png',
    'Laranja Mecânica': 'https://upload.wikimedia.org/wikipedia/en/7/73/A_Clockwork_Orange_%281971%29.png',
    'Matrix': 'https://upload.wikimedia.org/wikipedia/en/d/db/The_Matrix.png',
    'Meu Amigo Totoro': 'https://upload.wikimedia.org/wikipedia/en/0/02/My_Neighbor_Totoro_-_Tonari_no_Totoro_%28Movie_Poster%29.jpg',
    'O Iluminado': 'https://upload.wikimedia.org/wikipedia/en/1/1d/The_Shining_%281980%29_U.K._release_poster_-_The_tide_of_terror_that_swept_America_IS_HERE.jpg',
    'O Poderoso Chefão': 'https://upload.wikimedia.org/wikipedia/en/1/1c/Godfather_ver1.jpg',
    'O Senhor dos Anéis: A Sociedade do Anel': 'https://upload.wikimedia.org/wikipedia/en/f/fb/Lord_Rings_Fellowship_Ring.jpg',
    'Parasita': 'https://upload.wikimedia.org/wikipedia/en/5/53/Parasite_%282019_film%29.png',
    'Pulp Fiction': 'https://upload.wikimedia.org/wikipedia/en/3/3b/Pulp_Fiction_%281994%29_poster.jpg',
    'Se7en: Os Sete Crimes Capitais': 'https://upload.wikimedia.org/wikipedia/en/6/68/Seven_%28movie%29_poster.jpg',
    'Tropa de Elite': 'https://upload.wikimedia.org/wikipedia/en/d/d7/Elite_Squad.png',
    'Whiplash: Em Busca da Perfeição': 'https://upload.wikimedia.org/wikipedia/en/0/01/Whiplash_poster.jpg',
}


def preencher(apps, schema_editor):
    Filme = apps.get_model('catalogo', 'Filme')
    for titulo, url in CAPAS.items():
        Filme.objects.filter(titulo=titulo, capa_url='').update(capa_url=url)


def limpar(apps, schema_editor):
    Filme = apps.get_model('catalogo', 'Filme')
    for titulo, url in CAPAS.items():
        Filme.objects.filter(titulo=titulo, capa_url=url).update(capa_url='')


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0007_filme_capa_url'),
    ]

    operations = [
        migrations.RunPython(preencher, limpar),
    ]
