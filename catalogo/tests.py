from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Perfil

from .models import Ator, Avaliacao, Diretor, Elenco, Filme, Genero


class BaseTeste(TestCase):
    """Dois usuários com um filme cada, para testar o isolamento entre eles."""

    @classmethod
    def setUpTestData(cls):
        cls.ana = User.objects.create_user('ana', password='senha-da-ana-123')
        cls.bruno = User.objects.create_user('bruno', password='senha-do-bruno-123')
        cls.genero = Genero.objects.create(nome='Teste Drama')
        cls.diretor = Diretor.objects.create(nome='Diretora Teste', nacionalidade='Brasileira')

        cls.filme_ana = Filme.objects.create(
            titulo='Filme da Ana', genero=cls.genero, diretor=cls.diretor,
            sinopse='...', usuario=cls.ana,
        )
        cls.filme_bruno = Filme.objects.create(
            titulo='Filme do Bruno', genero=cls.genero, diretor=cls.diretor,
            sinopse='...', usuario=cls.bruno,
        )
        for nota in (4, 5):
            Avaliacao.objects.create(filme=cls.filme_ana, autor='Ana', nota=nota, usuario=cls.ana)


class AcessoTeste(BaseTeste):

    def test_home_e_publica(self):
        resposta = self.client.get(reverse('home'))
        self.assertEqual(resposta.status_code, 200)

    def test_areas_internas_redirecionam_para_login(self):
        rotas = [
            reverse('dashboard'),
            reverse('consulta'),
            reverse('lista_filmes'),
            reverse('criar_filme'),
            reverse('editar_filme', args=[self.filme_ana.pk]),
            reverse('lista_atores'),
            reverse('perfil'),
        ]
        for rota in rotas:
            with self.subTest(rota=rota):
                resposta = self.client.get(rota)
                self.assertRedirects(resposta, f"{reverse('login')}?next={rota}")


class IsolamentoTeste(BaseTeste):

    def setUp(self):
        self.client.force_login(self.ana)

    def test_lista_mostra_apenas_os_proprios_filmes(self):
        resposta = self.client.get(reverse('lista_filmes'))
        self.assertContains(resposta, 'Filme da Ana')
        self.assertNotContains(resposta, 'Filme do Bruno')

    def test_id_de_outro_usuario_na_url_retorna_404(self):
        for nome in ('detalhe_filme', 'editar_filme', 'excluir_filme'):
            with self.subTest(rota=nome):
                resposta = self.client.get(reverse(nome, args=[self.filme_bruno.pk]))
                self.assertEqual(resposta.status_code, 404)

    def test_post_nao_exclui_filme_de_outro_usuario(self):
        self.client.post(reverse('excluir_filme', args=[self.filme_bruno.pk]))
        self.assertTrue(Filme.objects.filter(pk=self.filme_bruno.pk).exists())

    def test_novo_filme_pertence_ao_usuario_logado(self):
        # Mesmo que alguém injete "usuario" no POST, o dono vem da sessão.
        self.client.post(reverse('criar_filme'), {
            'titulo': 'Novo', 'genero': self.genero.pk, 'diretor': self.diretor.pk,
            'sinopse': 'x', 'usuario': self.bruno.pk,
        })
        self.assertEqual(Filme.objects.get(titulo='Novo').usuario, self.ana)

    def test_nao_avalia_filme_de_outro_usuario(self):
        resposta = self.client.post(reverse('criar_avaliacao'), {
            'filme': self.filme_bruno.pk, 'autor': 'Ana', 'nota': 1,
        })
        self.assertIn('filme', resposta.context['form'].errors)
        self.assertFalse(self.filme_bruno.avaliacoes.exists())

    def test_consulta_e_csv_respeitam_o_usuario(self):
        resposta = self.client.get(reverse('consulta'), {'formato': 'csv'})
        conteudo = resposta.content.decode('utf-8-sig')
        self.assertEqual(resposta['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('Filme da Ana', conteudo)
        self.assertNotIn('Filme do Bruno', conteudo)


class DashboardTeste(BaseTeste):

    def test_indicadores_vem_do_banco(self):
        self.client.force_login(self.ana)
        contexto = self.client.get(reverse('dashboard')).context
        self.assertEqual(contexto['total_filmes'], 1)
        self.assertEqual(contexto['total_avaliacoes'], 2)
        self.assertEqual(contexto['media_geral'], 4.5)
        self.assertEqual(contexto['destaque'], self.filme_ana)


class RelacionamentosTeste(BaseTeste):

    def test_perfil_criado_automaticamente_um_para_um(self):
        self.assertIsInstance(self.ana.perfil, Perfil)
        self.assertEqual(Perfil.objects.filter(usuario=self.ana).count(), 1)

    def test_elenco_liga_filme_e_ator_com_personagem(self):
        ator = Ator.objects.create(nome='Ator Teste')
        Elenco.objects.create(filme=self.filme_ana, ator=ator, personagem='Herói')
        self.assertIn(ator, self.filme_ana.atores.all())
        self.assertEqual(ator.participacoes.get().personagem, 'Herói')

    def test_mesmo_ator_nao_entra_duas_vezes_no_filme(self):
        ator = Ator.objects.create(nome='Ator Repetido')
        Elenco.objects.create(filme=self.filme_ana, ator=ator, personagem='A')
        with self.assertRaises(IntegrityError):
            Elenco.objects.create(filme=self.filme_ana, ator=ator, personagem='B')
