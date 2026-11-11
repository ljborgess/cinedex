"""Mais 24 filmes no catálogo da conta `demo`, cada um com elenco, capa e avaliações.

Só acrescenta: filmes, diretores e atores que já existem são reaproveitados, e
nada é sobrescrito. Os links das capas vieram da API da Wikipédia (página do
filme em inglês), e os nomes de autores das avaliações são fictícios, como no
resto do seed.
"""
from django.conf import settings
from django.db import migrations

W = 'https://upload.wikimedia.org/wikipedia/'

DIRETORES = [
    ('Robert Zemeckis', 'Norte-americana'),
    ('Ridley Scott', 'Britânica'),
    ('James Cameron', 'Canadense'),
    ('Steven Spielberg', 'Norte-americana'),
    ('Pete Docter', 'Norte-americana'),
    ('Roger Allers', 'Norte-americana'),
    ('Jordan Peele', 'Norte-americana'),
    ('George Miller', 'Australiana'),
    ('Martin Scorsese', 'Norte-americana'),
    ('Jonathan Demme', 'Norte-americana'),
    ('Denis Villeneuve', 'Canadense'),
    ('Jean-Pierre Jeunet', 'Francesa'),
    ('Guel Arraes', 'Brasileira'),
    ('Todd Phillips', 'Norte-americana'),
    ('Daniel Kwan', 'Norte-americana'),
    ('Alfred Hitchcock', 'Britânica'),
    ('Frank Darabont', 'Norte-americana'),
]

GENEROS_NOVOS = ['Comédia']

# titulo, genero, diretor, sinopse, capa, elenco [(ator, nacionalidade, personagem)],
# avaliacoes [(autor, nota, comentario)]
FILMES = [
    ('O Cavaleiro das Trevas', 'Ação', 'Christopher Nolan',
     'Batman enfrenta o Coringa, um criminoso que quer provar que qualquer pessoa pode ser levada ao caos.',
     W + 'en/1/1c/The_Dark_Knight_%282008_film%29.jpg',
     [('Christian Bale', 'Britânica', 'Bruce Wayne'), ('Heath Ledger', 'Australiana', 'Coringa'),
      ('Aaron Eckhart', 'Norte-americana', 'Harvey Dent')],
     [('Marina', 5, 'O Coringa mais assustador do cinema.'), ('Diego', 5, 'Filme de herói que é filme policial.'),
      ('Lucas', 4, 'Longo, mas não sobra cena.')]),
    ('Forrest Gump: O Contador de Histórias', 'Drama', 'Robert Zemeckis',
     'Um homem de bom coração atravessa, quase sem perceber, décadas da história dos Estados Unidos.',
     W + 'en/6/67/Forrest_Gump_poster.jpg',
     [('Tom Hanks', 'Norte-americana', 'Forrest Gump'), ('Robin Wright', 'Norte-americana', 'Jenny Curran'),
      ('Gary Sinise', 'Norte-americana', 'Tenente Dan')],
     [('Bia', 5, 'Chorei no banco da praça.'), ('Rafael', 4, 'Emociona mesmo sendo previsível.')]),
    ('De Volta para o Futuro', 'Ficção Científica', 'Robert Zemeckis',
     'Marty McFly volta acidentalmente a 1955 num carro-máquina do tempo e precisa garantir que os pais se conheçam.',
     W + 'en/d/d2/Back_to_the_Future.jpg',
     [('Michael J. Fox', 'Canadense', 'Marty McFly'), ('Christopher Lloyd', 'Norte-americana', 'Doc Brown'),
      ('Lea Thompson', 'Norte-americana', 'Lorraine Baines')],
     [('Caio', 5, 'Roteiro de relojoeiro.'), ('Marina', 5, 'Não envelhece nunca.')]),
    ('Gladiador', 'Ação', 'Ridley Scott',
     'Traído pelo novo imperador, o general Maximus vira escravo e gladiador para buscar vingança em Roma.',
     W + 'en/f/fb/Gladiator_%282000_film_poster%29.png',
     [('Russell Crowe', 'Neozelandesa', 'Maximus'), ('Joaquin Phoenix', 'Norte-americana', 'Commodus'),
      ('Connie Nielsen', 'Dinamarquesa', 'Lucilla')],
     [('Lucas', 5, 'A trilha sonora sozinha já valeria.'), ('Bia', 4, 'Épico do jeito antigo.')]),
    ('Alien, o 8º Passageiro', 'Terror', 'Ridley Scott',
     'A tripulação de uma nave cargueira atende a um sinal de socorro e leva a bordo uma criatura mortal.',
     W + 'en/c/c3/Alien_movie_poster.jpg',
     [('Sigourney Weaver', 'Norte-americana', 'Ellen Ripley'), ('Tom Skerritt', 'Norte-americana', 'Dallas'),
      ('John Hurt', 'Britânica', 'Kane')],
     [('Diego', 5, 'Silêncio e corredor escuro: terror perfeito.'), ('Rafael', 4, 'Lento no começo, sufocante no fim.')]),
    ('Titanic', 'Romance', 'James Cameron',
     'A bordo do navio inaufragável, uma jovem da alta sociedade e um artista pobre vivem um romance improvável.',
     W + 'en/1/18/Titanic_%281997_film%29_poster.png',
     [('Leonardo DiCaprio', 'Norte-americana', 'Jack Dawson'), ('Kate Winslet', 'Britânica', 'Rose DeWitt Bukater'),
      ('Billy Zane', 'Norte-americana', 'Cal Hockley')],
     [('Bia', 4, 'Cabia os dois na porta, sim.'), ('Marina', 4, 'A segunda metade é um filme-catástrofe impecável.')]),
    ('O Exterminador do Futuro 2: O Julgamento Final', 'Ação', 'James Cameron',
     'Um ciborgue reprogramado volta no tempo para proteger o jovem John Connor de um exterminador mais avançado.',
     W + 'en/5/5e/Terminator_2-Judgment_Day.png',
     [('Arnold Schwarzenegger', 'Austríaca', 'T-800'), ('Linda Hamilton', 'Norte-americana', 'Sarah Connor'),
      ('Edward Furlong', 'Norte-americana', 'John Connor')],
     [('Caio', 5, 'Efeitos que ainda impressionam.'), ('Lucas', 5, 'Continuação melhor que o original.')]),
    ('Jurassic Park: O Parque dos Dinossauros', 'Aventura', 'Steven Spielberg',
     'Um parque com dinossauros clonados é testado por cientistas antes da inauguração, até que tudo sai do controle.',
     W + 'en/e/e7/Jurassic_Park_poster.jpg',
     [('Sam Neill', 'Neozelandesa', 'Alan Grant'), ('Laura Dern', 'Norte-americana', 'Ellie Sattler'),
      ('Jeff Goldblum', 'Norte-americana', 'Ian Malcolm')],
     [('Rafael', 5, 'O copo d’água tremendo é cinema puro.'), ('Bia', 4, 'Ainda dá medo do velociraptor.')]),
    ('O Resgate do Soldado Ryan', 'Drama', 'Steven Spielberg',
     'Depois do Dia D, um pelotão atravessa a Normandia para encontrar e mandar para casa um único soldado.',
     W + 'en/a/ac/Saving_Private_Ryan_poster.jpg',
     [('Tom Hanks', 'Norte-americana', 'Capitão Miller'), ('Matt Damon', 'Norte-americana', 'James Ryan'),
      ('Tom Sizemore', 'Norte-americana', 'Sargento Horvath')],
     [('Diego', 5, 'Os primeiros vinte minutos são inesquecíveis.'), ('Marina', 4, 'Pesado e necessário.')]),
    ('Up: Altas Aventuras', 'Animação', 'Pete Docter',
     'Um viúvo amarra milhares de balões à própria casa para cumprir a promessa de viajar à América do Sul.',
     W + 'en/0/05/Up_%282009_film%29.jpg',
     [('Ed Asner', 'Norte-americana', 'Carl Fredricksen (voz)'), ('Jordan Nagai', 'Norte-americana', 'Russell (voz)'),
      ('Christopher Plummer', 'Canadense', 'Charles Muntz (voz)')],
     [('Bia', 5, 'Os primeiros minutos acabam com qualquer um.'), ('Caio', 4, 'Aventura linda, final um pouco corrido.')]),
    ('O Rei Leão', 'Animação', 'Roger Allers',
     'O jovem leão Simba foge depois da morte do pai e precisa voltar para assumir o lugar que é dele.',
     W + 'en/3/3d/The_Lion_King_poster.jpg',
     [('Matthew Broderick', 'Norte-americana', 'Simba adulto (voz)'), ('James Earl Jones', 'Norte-americana', 'Mufasa (voz)'),
      ('Jeremy Irons', 'Britânica', 'Scar (voz)')],
     [('Lucas', 5, 'Infância inteira em 90 minutos.'), ('Marina', 5, 'A abertura ainda arrepia.')]),
    ('Corra!', 'Terror', 'Jordan Peele',
     'Um jovem negro visita a família da namorada branca e percebe que a recepção calorosa esconde algo terrível.',
     W + 'en/a/a3/Get_Out_poster.png',
     [('Daniel Kaluuya', 'Britânica', 'Chris Washington'), ('Allison Williams', 'Norte-americana', 'Rose Armitage'),
      ('Bradley Whitford', 'Norte-americana', 'Dean Armitage')],
     [('Rafael', 5, 'Terror com coisa para dizer.'), ('Diego', 4, 'A cena da xícara não sai da cabeça.')]),
    ('Mad Max: Estrada da Fúria', 'Ação', 'George Miller',
     'Num deserto pós-apocalíptico, Max e a imperatriz Furiosa fogem de um tirano numa perseguição sem trégua.',
     W + 'en/6/6e/Mad_Max_Fury_Road.jpg',
     [('Tom Hardy', 'Britânica', 'Max Rockatansky'), ('Charlize Theron', 'Sul-africana', 'Furiosa'),
      ('Nicholas Hoult', 'Britânica', 'Nux')],
     [('Caio', 5, 'Duas horas de perseguição e nenhum minuto cansa.'), ('Lucas', 5, 'Ação feita à mão, sem preguiça.')]),
    ('Os Bons Companheiros', 'Crime', 'Martin Scorsese',
     'A ascensão e a queda de Henry Hill, que desde garoto sonhava em fazer parte da máfia de Nova York.',
     W + 'en/7/7b/Goodfellas.jpg',
     [('Ray Liotta', 'Norte-americana', 'Henry Hill'), ('Robert De Niro', 'Norte-americana', 'Jimmy Conway'),
      ('Joe Pesci', 'Norte-americana', 'Tommy DeVito')],
     [('Diego', 5, 'O plano-sequência do restaurante é aula.'), ('Rafael', 4, 'Ritmo de metralhadora.')]),
    ('Taxi Driver', 'Crime', 'Martin Scorsese',
     'Um veterano insone dirige táxi pelas noites de Nova York e afunda numa solidão cada vez mais violenta.',
     W + 'en/3/33/Taxi_Driver_%281976_film_poster%29.jpg',
     [('Robert De Niro', 'Norte-americana', 'Travis Bickle'), ('Jodie Foster', 'Norte-americana', 'Iris'),
      ('Harvey Keitel', 'Norte-americana', 'Sport')],
     [('Marina', 4, 'Desconfortável do jeito certo.'), ('Caio', 3, 'Admiro mais do que gosto.')]),
    ('O Silêncio dos Inocentes', 'Suspense', 'Jonathan Demme',
     'A agente do FBI Clarice Starling pede ajuda ao canibal Hannibal Lecter para capturar outro assassino.',
     W + 'en/8/86/The_Silence_of_the_Lambs_poster.jpg',
     [('Jodie Foster', 'Norte-americana', 'Clarice Starling'), ('Anthony Hopkins', 'Britânica', 'Hannibal Lecter'),
      ('Scott Glenn', 'Norte-americana', 'Jack Crawford')],
     [('Bia', 5, 'Hopkins aparece pouco e domina tudo.'), ('Diego', 5, 'Suspense sem um segundo de folga.')]),
    ('Duna', 'Ficção Científica', 'Denis Villeneuve',
     'Herdeiro de uma casa nobre, Paul Atreides chega ao planeta desértico Arrakis, disputado por toda a galáxia.',
     W + 'en/8/8e/Dune_%282021_film%29.jpg',
     [('Timothée Chalamet', 'Norte-americana', 'Paul Atreides'), ('Rebecca Ferguson', 'Sueca', 'Lady Jessica'),
      ('Oscar Isaac', 'Norte-americana', 'Duque Leto Atreides')],
     [('Lucas', 5, 'Escala que só o cinema dá.'), ('Rafael', 4, 'Lindo, mas termina no meio.')]),
    ('A Chegada', 'Ficção Científica', 'Denis Villeneuve',
     'Uma linguista tenta se comunicar com visitantes alienígenas enquanto o mundo se aproxima de uma guerra.',
     W + 'en/d/df/Arrival%2C_Movie_Poster.jpg',
     [('Amy Adams', 'Norte-americana', 'Louise Banks'), ('Jeremy Renner', 'Norte-americana', 'Ian Donnelly'),
      ('Forest Whitaker', 'Norte-americana', 'Coronel Weber')],
     [('Marina', 5, 'Ficção científica sobre linguagem e luto.'), ('Bia', 5, 'A virada final muda o filme inteiro.')]),
    ('O Fabuloso Destino de Amélie Poulain', 'Romance', 'Jean-Pierre Jeunet',
     'Em Montmartre, uma garçonete tímida decide mudar em segredo a vida das pessoas ao seu redor.',
     W + 'en/5/53/Amelie_poster.jpg',
     [('Audrey Tautou', 'Francesa', 'Amélie Poulain'), ('Mathieu Kassovitz', 'Francesa', 'Nino Quincampoix'),
      ('Rufus', 'Francesa', 'Raphaël Poulain')],
     [('Bia', 5, 'Dá vontade de morar dentro do filme.'), ('Caio', 3, 'Encantador, mas doce demais para mim.')]),
    ('O Auto da Compadecida', 'Comédia', 'Guel Arraes',
     'No sertão da Paraíba, João Grilo e Chicó vivem de pequenos golpes até enfrentarem o próprio julgamento final.',
     W + 'en/d/d1/O_Auto_da_Compadecida.jpg',
     [('Matheus Nachtergaele', 'Brasileira', 'João Grilo'), ('Selton Mello', 'Brasileira', 'Chicó'),
      ('Fernanda Montenegro', 'Brasileira', 'Nossa Senhora (a Compadecida)')],
     [('Lucas', 5, '“Não sei, só sei que foi assim.”'), ('Marina', 5, 'Comédia brasileira no auge.'),
      ('Diego', 5, 'Revejo todo ano.')]),
    ('Coringa', 'Drama', 'Todd Phillips',
     'Em Gotham, um comediante fracassado e ignorado pela sociedade começa a se transformar no Coringa.',
     W + 'en/e/e1/Joker_%282019_film%29_poster.jpg',
     [('Joaquin Phoenix', 'Norte-americana', 'Arthur Fleck'), ('Robert De Niro', 'Norte-americana', 'Murray Franklin'),
      ('Zazie Beetz', 'Norte-americana', 'Sophie Dumond')],
     [('Rafael', 4, 'Atuação gigante do Phoenix.'), ('Caio', 3, 'Bem feito, mas vazio por dentro.')]),
    ('Tudo em Todo o Lugar ao Mesmo Tempo', 'Ficção Científica', 'Daniel Kwan',
     'Uma dona de lavanderia descobre que precisa atravessar universos paralelos para salvar o multiverso e a família.',
     W + 'en/1/1e/Everything_Everywhere_All_at_Once.jpg',
     [('Michelle Yeoh', 'Malaia', 'Evelyn Wang'), ('Ke Huy Quan', 'Norte-americana', 'Waymond Wang'),
      ('Jamie Lee Curtis', 'Norte-americana', 'Deirdre Beaubeirdre')],
     [('Bia', 5, 'Caótico e comovente ao mesmo tempo.'), ('Lucas', 4, 'Cansa um pouco, mas vale.')]),
    ('Psicose', 'Suspense', 'Alfred Hitchcock',
     'Depois de roubar dinheiro do patrão, uma secretária se hospeda num motel isolado administrado por Norman Bates.',
     W + 'commons/7/76/Psycho_%281960%29_theatrical_poster_%28retouched%29.jpg',
     [('Anthony Perkins', 'Norte-americana', 'Norman Bates'), ('Janet Leigh', 'Norte-americana', 'Marion Crane'),
      ('Vera Miles', 'Norte-americana', 'Lila Crane')],
     [('Diego', 5, 'Mudou o cinema de suspense.'), ('Marina', 4, 'A cena do chuveiro ainda funciona.')]),
    ('Um Sonho de Liberdade', 'Drama', 'Frank Darabont',
     'Condenado injustamente, o banqueiro Andy Dufresne passa décadas na prisão de Shawshank sem perder a esperança.',
     W + 'en/8/81/ShawshankRedemptionMoviePoster.jpg',
     [('Tim Robbins', 'Norte-americana', 'Andy Dufresne'), ('Morgan Freeman', 'Norte-americana', 'Red'),
      ('Bob Gunton', 'Norte-americana', 'Diretor Norton')],
     [('Caio', 5, 'O final mais satisfatório que conheço.'), ('Rafael', 5, 'A narração do Morgan Freeman é tudo.'),
      ('Bia', 5, 'Esperança como tema, sem pieguice.')]),
]


def acrescentar(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    Genero = apps.get_model('catalogo', 'Genero')
    Diretor = apps.get_model('catalogo', 'Diretor')
    Ator = apps.get_model('catalogo', 'Ator')
    Filme = apps.get_model('catalogo', 'Filme')
    Elenco = apps.get_model('catalogo', 'Elenco')
    Avaliacao = apps.get_model('catalogo', 'Avaliacao')

    demo = User.objects.filter(username='demo').first()
    if demo is None:
        return

    for nome in GENEROS_NOVOS:
        Genero.objects.get_or_create(nome=nome)
    for nome, nacionalidade in DIRETORES:
        if not Diretor.objects.filter(nome=nome).exists():
            Diretor.objects.create(nome=nome, nacionalidade=nacionalidade)

    for titulo, genero, diretor, sinopse, capa, elenco, avaliacoes in FILMES:
        if Filme.objects.filter(usuario=demo, titulo=titulo).exists():
            continue
        filme = Filme.objects.create(
            usuario=demo, titulo=titulo, sinopse=sinopse, capa_url=capa,
            genero=Genero.objects.get(nome=genero),
            diretor=Diretor.objects.filter(nome=diretor).order_by('pk').first(),
        )
        for ordem, (nome, nacionalidade, personagem) in enumerate(elenco, start=1):
            ator = Ator.objects.filter(nome=nome).order_by('pk').first()
            if ator is None:
                ator = Ator.objects.create(nome=nome, nacionalidade=nacionalidade)
            Elenco.objects.create(filme=filme, ator=ator, personagem=personagem, ordem=ordem)
        for autor, nota, comentario in avaliacoes:
            Avaliacao.objects.create(
                filme=filme, autor=autor, nota=nota, comentario=comentario, usuario=demo,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0010_seed_completo'),
    ]

    operations = [
        # Sem desfazer, pelo mesmo motivo da 0010: apagar poderia levar junto
        # o que o usuário criou depois em cima destes filmes.
        migrations.RunPython(acrescentar, migrations.RunPython.noop),
    ]
