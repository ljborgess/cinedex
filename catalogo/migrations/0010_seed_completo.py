"""Completa o seed para a apresentação, sem apagar nada.

- Todo filme da conta `demo` passa a ter pelo menos três atores no elenco.
- O perfil da conta `demo` ganha apelido, bio e gênero favorito.
- Uma segunda conta, `ana`, tem um catálogo próprio de três filmes. Ela mostra
  na prática que cada usuário só enxerga o que é seu, e que atores e diretores
  são compartilhados (Fernanda Montenegro está no catálogo das duas contas).

Tudo usa get_or_create: rodar de novo, ou rodar sobre um banco que já tem
dados, não duplica nem sobrescreve nada.
"""
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.db.models import Max

SENHA = 'filmes123'

# (filme, ator, nacionalidade do ator, personagem)
ELENCO_DEMO = [
    ('A Origem', 'Joseph Gordon-Levitt', 'Norte-americana', 'Arthur'),
    ('A Origem', 'Tom Hardy', 'Britânica', 'Eames'),
    ('O Poderoso Chefão', 'James Caan', 'Norte-americana', 'Sonny Corleone'),
    ('Interestelar', 'Jessica Chastain', 'Norte-americana', 'Murph'),
    ('Parasita', 'Choi Woo-shik', 'Sul-coreana', 'Kim Ki-woo'),
    ('Parasita', 'Park So-dam', 'Sul-coreana', 'Kim Ki-jeong'),
    ('Parasita', 'Cho Yeo-jeong', 'Sul-coreana', 'Park Yeon-kyo'),
    ('Cidade de Deus', 'Leandro Firmino', 'Brasileira', 'Zé Pequeno'),
    ('Cidade de Deus', 'Phellipe Haagensen', 'Brasileira', 'Bené'),
    ('Pulp Fiction', 'Bruce Willis', 'Norte-americana', 'Butch Coolidge'),
    ('Clube da Luta', 'Helena Bonham Carter', 'Britânica', 'Marla Singer'),
    ('Matrix', 'Hugo Weaving', 'Australiana', 'Agente Smith'),
    ('O Senhor dos Anéis: A Sociedade do Anel', 'Elijah Wood', 'Norte-americana', 'Frodo Bolseiro'),
    ('O Senhor dos Anéis: A Sociedade do Anel', 'Ian McKellen', 'Britânica', 'Gandalf'),
    ('O Senhor dos Anéis: A Sociedade do Anel', 'Viggo Mortensen', 'Norte-americana', 'Aragorn'),
    ('Bacurau', 'Bárbara Colen', 'Brasileira', 'Teresa'),
    ('Central do Brasil', 'Vinícius de Oliveira', 'Brasileira', 'Josué'),
    ('Central do Brasil', 'Marília Pêra', 'Brasileira', 'Irene'),
    ('Tropa de Elite', 'André Ramiro', 'Brasileira', 'André Matias'),
    ('Tropa de Elite', 'Caio Junqueira', 'Brasileira', 'Neto'),
    ('A Viagem de Chihiro', 'Rumi Hiiragi', 'Japonesa', 'Chihiro (voz)'),
    ('A Viagem de Chihiro', 'Miyu Irino', 'Japonesa', 'Haku (voz)'),
    ('A Viagem de Chihiro', 'Mari Natsuki', 'Japonesa', 'Yubaba (voz)'),
    ('O Iluminado', 'Shelley Duvall', 'Norte-americana', 'Wendy Torrance'),
    ('O Iluminado', 'Danny Lloyd', 'Norte-americana', 'Danny Torrance'),
    ('Whiplash: Em Busca da Perfeição', 'Melissa Benoist', 'Norte-americana', 'Nicole'),
    ('Kill Bill: Volume 1', 'Lucy Liu', 'Norte-americana', 'O-Ren Ishii'),
    ('Kill Bill: Volume 1', 'Vivica A. Fox', 'Norte-americana', 'Vernita Green'),
    ('Se7en: Os Sete Crimes Capitais', 'Gwyneth Paltrow', 'Norte-americana', 'Tracy Mills'),
    ('Laranja Mecânica', 'Malcolm McDowell', 'Britânica', 'Alex DeLarge'),
    ('Laranja Mecânica', 'Warren Clarke', 'Britânica', 'Dim'),
    ('Laranja Mecânica', 'Michael Bates', 'Britânica', 'Chefe dos guardas'),
    ('Meu Amigo Totoro', 'Noriko Hidaka', 'Japonesa', 'Satsuki (voz)'),
    ('Meu Amigo Totoro', 'Chika Sakamoto', 'Japonesa', 'Mei (voz)'),
    ('Meu Amigo Totoro', 'Hitoshi Takagi', 'Japonesa', 'Totoro (voz)'),
    ('La La Land: Cantando Estações', 'J. K. Simmons', 'Norte-americana', 'Bill'),
]

# O catálogo da segunda conta: filmes que a conta demo não tem.
FILMES_ANA = [
    {
        'titulo': 'Oppenheimer',
        'genero': 'Drama',
        'diretor': 'Christopher Nolan',
        'sinopse': 'A trajetória do físico J. Robert Oppenheimer e o desenvolvimento '
                   'da bomba atômica durante a Segunda Guerra Mundial.',
        'capa_url': 'https://upload.wikimedia.org/wikipedia/en/4/4a/Oppenheimer_%28film%29.jpg',
        'elenco': [
            ('Cillian Murphy', 'Irlandesa', 'J. Robert Oppenheimer'),
            ('Emily Blunt', 'Britânica', 'Kitty Oppenheimer'),
            ('Robert Downey Jr.', 'Norte-americana', 'Lewis Strauss'),
        ],
        'avaliacoes': [
            ('Ana', 5, 'Três horas que passam voando.'),
            ('Caio', 4, 'A montagem é o grande trunfo.'),
        ],
    },
    {
        'titulo': 'Ainda Estou Aqui',
        'genero': 'Drama',
        'diretor': 'Walter Salles',
        'sinopse': 'No Rio de Janeiro de 1971, Eunice Paiva reconstrói a vida da família '
                   'depois que o marido é levado pela ditadura militar.',
        'capa_url': 'https://upload.wikimedia.org/wikipedia/en/0/0a/I%27m_Still_Here_%282024_film%29_poster.jpg',
        'elenco': [
            ('Fernanda Torres', 'Brasileira', 'Eunice Paiva'),
            ('Selton Mello', 'Brasileira', 'Rubens Paiva'),
            ('Fernanda Montenegro', 'Brasileira', 'Eunice Paiva (idosa)'),
        ],
        'avaliacoes': [
            ('Ana', 5, 'Fernanda Torres carrega o filme no olhar.'),
            ('Caio', 5, 'Saí do cinema em silêncio.'),
        ],
    },
    {
        'titulo': 'O Menino e a Garça',
        'genero': 'Animação',
        'diretor': 'Hayao Miyazaki',
        'sinopse': 'Depois de perder a mãe, o jovem Mahito segue uma garça misteriosa '
                   'até um mundo onde vivos e mortos se encontram.',
        'capa_url': 'https://upload.wikimedia.org/wikipedia/en/4/41/How_Do_You_Live_poster.jpg',
        'elenco': [
            ('Soma Santoki', 'Japonesa', 'Mahito Maki (voz)'),
            ('Masaki Suda', 'Japonesa', 'Garça-cinzenta (voz)'),
        ],
        'avaliacoes': [
            ('Ana', 4, 'Lindo, mas pede uma segunda sessão.'),
        ],
    },
]


def _ator(Ator, nome, nacionalidade):
    ator = Ator.objects.filter(nome=nome).order_by('pk').first()
    if ator is None:
        return Ator.objects.create(nome=nome, nacionalidade=nacionalidade)
    if not ator.nacionalidade:
        ator.nacionalidade = nacionalidade
        ator.save(update_fields=['nacionalidade'])
    return ator


def _escalar(Elenco, filme, ator, personagem):
    if Elenco.objects.filter(filme=filme, ator=ator).exists():
        return
    ultima = Elenco.objects.filter(filme=filme).aggregate(m=Max('ordem'))['m'] or 0
    Elenco.objects.create(filme=filme, ator=ator, personagem=personagem, ordem=ultima + 1)


def completar(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    Perfil = apps.get_model('usuarios', 'Perfil')
    Genero = apps.get_model('catalogo', 'Genero')
    Diretor = apps.get_model('catalogo', 'Diretor')
    Ator = apps.get_model('catalogo', 'Ator')
    Filme = apps.get_model('catalogo', 'Filme')
    Elenco = apps.get_model('catalogo', 'Elenco')
    Avaliacao = apps.get_model('catalogo', 'Avaliacao')

    # --- conta demo: elenco completo e perfil preenchido -------------------
    demo = User.objects.filter(username='demo').first()
    if demo:
        for titulo, nome, nacionalidade, personagem in ELENCO_DEMO:
            filme = Filme.objects.filter(usuario=demo, titulo=titulo).first()
            if filme:
                _escalar(Elenco, filme, _ator(Ator, nome, nacionalidade), personagem)

        perfil, _ = Perfil.objects.get_or_create(usuario=demo)
        if not perfil.apelido or perfil.apelido == 'Demo':
            perfil.apelido = 'Demo'
        if not perfil.bio:
            perfil.bio = 'Ficção científica, cinema brasileiro e tudo que o Miyazaki fizer.'
        if not perfil.genero_favorito_id:
            perfil.genero_favorito = Genero.objects.filter(nome='Ficção Científica').first()
        perfil.save()

    # --- segunda conta: catálogo próprio --------------------------------
    ana, _ = User.objects.get_or_create(
        username='ana', defaults={'password': make_password(SENHA)},
    )
    Perfil.objects.get_or_create(
        usuario=ana,
        defaults={
            'apelido': 'Ana',
            'bio': 'Drama primeiro, animação depois.',
            'genero_favorito': Genero.objects.filter(nome='Drama').first(),
        },
    )
    for dados in FILMES_ANA:
        genero = Genero.objects.filter(nome=dados['genero']).first()
        diretor = Diretor.objects.filter(nome=dados['diretor']).first()
        if not (genero and diretor):
            continue
        filme, criado = Filme.objects.get_or_create(
            usuario=ana, titulo=dados['titulo'],
            defaults={
                'genero': genero,
                'diretor': diretor,
                'sinopse': dados['sinopse'],
                'capa_url': dados['capa_url'],
            },
        )
        for nome, nacionalidade, personagem in dados['elenco']:
            _escalar(Elenco, filme, _ator(Ator, nome, nacionalidade), personagem)
        if criado:
            for autor, nota, comentario in dados['avaliacoes']:
                Avaliacao.objects.create(
                    filme=filme, autor=autor, nota=nota, comentario=comentario, usuario=ana,
                )


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0009_conta_admin'),
        ('usuarios', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Sem desfazer: o seed só acrescenta, e apagar poderia levar junto
        # registros que o usuário criou depois em cima destes.
        migrations.RunPython(completar, migrations.RunPython.noop),
    ]
