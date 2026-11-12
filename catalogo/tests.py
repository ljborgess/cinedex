from io import StringIO
from unittest import mock

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from usuarios import limite
from usuarios.models import Perfil

from .forms import ElencoForm
from .models import Ator, Avaliacao, Diretor, Elenco, Filme, Genero


class BaseTeste(TestCase):
    """Dois usuários com um filme cada, para testar o isolamento entre eles."""

    @classmethod
    def setUpTestData(cls):
        cls.ana = User.objects.create_user('teste_ana', password='senha-da-ana-123')
        cls.bruno = User.objects.create_user('teste_bruno', password='senha-do-bruno-123')
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


class CapaTeste(BaseTeste):
    URL = 'https://upload.wikimedia.org/exemplo.jpg'

    def setUp(self):
        self.client.force_login(self.ana)

    def test_capa_url_vira_imagem_e_sem_link_fica_a_capa_desenhada(self):
        resposta = self.client.get(reverse('lista_filmes'))
        self.assertNotContains(resposta, 'capa-foto')
        Filme.objects.filter(pk=self.filme_ana.pk).update(capa_url=self.URL)
        resposta = self.client.get(reverse('lista_filmes'))
        self.assertContains(resposta, f'src="{self.URL}"')

    @mock.patch('catalogo.views.buscar_capa', return_value=URL)
    def test_botao_buscar_capa_grava_o_link(self, buscar):
        self.client.post(reverse('buscar_capa', args=[self.filme_ana.pk]))
        self.filme_ana.refresh_from_db()
        self.assertEqual(self.filme_ana.capa_url, self.URL)
        buscar.assert_called_once_with('Filme da Ana', 'Diretora Teste')

    @mock.patch('catalogo.views.buscar_capa', return_value=URL)
    def test_nao_busca_capa_de_filme_de_outro_usuario(self, buscar):
        resposta = self.client.post(reverse('buscar_capa', args=[self.filme_bruno.pk]))
        self.assertEqual(resposta.status_code, 404)
        buscar.assert_not_called()

    @mock.patch('catalogo.management.commands.buscar_capas.buscar_capa', return_value=URL)
    def test_comando_preenche_so_quem_nao_tem_capa(self, buscar):
        Filme.objects.filter(pk=self.filme_bruno.pk).update(capa_url='https://ja-tinha.jpg')
        call_command('buscar_capas', stdout=StringIO())
        self.filme_ana.refresh_from_db()
        self.filme_bruno.refresh_from_db()
        self.assertEqual(self.filme_ana.capa_url, self.URL)
        self.assertEqual(self.filme_bruno.capa_url, 'https://ja-tinha.jpg')
        self.assertEqual(buscar.call_count, 1)


class ProntoParaApresentarTeste(TestCase):
    """O banco criado só com `migrate` já tem tudo que a apresentação usa."""

    def test_seed_cria_conta_demo_com_catalogo(self):
        demo = User.objects.get(username='demo')
        self.assertTrue(demo.check_password('filmes123'))
        self.assertEqual(Filme.objects.filter(usuario=demo).count(), 44)

    def test_seed_da_elenco_a_todo_filme_da_demo(self):
        from django.db.models import Count
        filmes = Filme.objects.filter(usuario__username='demo').annotate(n=Count('elenco'))
        self.assertFalse(filmes.filter(n__lt=3).exists())

    def test_seed_cria_segunda_conta_isolada(self):
        ana = User.objects.get(username='ana')
        self.assertTrue(ana.check_password('filmes123'))
        self.assertEqual(Filme.objects.filter(usuario=ana).count(), 3)
        self.client.force_login(ana)
        resposta = self.client.get(reverse('lista_filmes'))
        self.assertContains(resposta, 'Oppenheimer')
        self.assertNotContains(resposta, 'Matrix')

    def test_seed_cria_admin_que_entra_no_painel_do_django(self):
        admin = User.objects.get(username='admin')
        self.assertTrue(admin.is_superuser and admin.is_staff)
        self.client.force_login(admin)
        self.assertEqual(self.client.get('/admin/').status_code, 200)

    def test_paginas_principais_abrem(self):
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)
        self.assertEqual(self.client.get(reverse('cadastro')).status_code, 200)
        self.client.force_login(User.objects.get(username='demo'))
        filme = Filme.objects.filter(usuario__username='demo').first()
        for url in (reverse('dashboard'), reverse('lista_filmes'),
                    reverse('detalhe_filme', args=[filme.pk]), reverse('consulta')):
            self.assertEqual(self.client.get(url).status_code, 200, url)


    def test_pagina_do_filme_aponta_onde_assistir(self):
        self.client.force_login(User.objects.get(username='demo'))
        filme = Filme.objects.get(titulo='A Origem')
        resposta = self.client.get(reverse('detalhe_filme', args=[filme.pk]))
        self.assertContains(resposta, 'https://www.justwatch.com/br/busca?q=A%20Origem')
        self.assertContains(resposta, 'https://www.netflix.com/search?q=A%20Origem')
        self.assertContains(resposta, 'https://www.primevideo.com/search/?phrase=A%20Origem')

    def test_lista_de_atores_nao_mostra_quem_so_esta_em_outra_conta(self):
        self.client.force_login(User.objects.get(username='demo'))
        resposta = self.client.get(reverse('lista_atores'))
        self.assertContains(resposta, 'Keanu Reeves')
        self.assertNotContains(resposta, 'Cillian Murphy')


class SegurancaTeste(BaseTeste):
    """Itens do checklist de segurança aplicados ao projeto (ver AUDITORIA.md)."""

    def setUp(self):
        cache.clear()  # o contador de tentativas vive no cache e não pode vazar entre testes

    def test_login_bloqueia_depois_de_cinco_senhas_erradas(self):
        for _ in range(limite.LIMITE):
            self.client.post(reverse('login'), {'username': 'teste_ana', 'password': 'errada'})
        # Bloqueado: nem a senha certa entra, e a mensagem não diz se a conta existe.
        resposta = self.client.post(
            reverse('login'), {'username': 'teste_ana', 'password': 'senha-da-ana-123'}
        )
        self.assertContains(resposta, 'Muitas tentativas')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_certo_nao_gasta_tentativa(self):
        for _ in range(limite.LIMITE + 1):
            self.client.post(reverse('logout'))
            self.client.post(reverse('login'), {'username': 'teste_ana', 'password': 'senha-da-ana-123'})
        self.assertIn('_auth_user_id', self.client.session)

    def test_cadastro_limita_contas_por_ip(self):
        for indice in range(limite.LIMITE + 1):
            self.client.post(reverse('cadastro'), {
                'username': f'robo{indice}', 'password1': 'Senha-forte-123', 'password2': 'Senha-forte-123',
            })
            self.client.post(reverse('logout'))
        self.assertEqual(User.objects.filter(username__startswith='robo').count(), limite.LIMITE)

    def test_login_do_admin_tambem_tem_limite(self):
        User.objects.create_superuser('teste_admin', password='senha-do-admin-123')
        for _ in range(limite.LIMITE):
            self.client.post(reverse('admin:login'), {'username': 'teste_admin', 'password': 'errada'})
        resposta = self.client.post(
            reverse('admin:login'), {'username': 'teste_admin', 'password': 'senha-do-admin-123'}
        )
        self.assertContains(resposta, 'Muitas tentativas')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_filtros_da_consulta_nao_mostram_ator_de_outra_conta(self):
        so_do_bruno = Ator.objects.create(nome='Ator Só do Bruno')
        Elenco.objects.create(filme=self.filme_bruno, ator=so_do_bruno, personagem='X')
        self.client.force_login(self.ana)
        opcoes = self.client.get(reverse('consulta')).context['form'].fields['ator'].queryset
        self.assertNotIn(so_do_bruno, opcoes)

    def test_vitrine_so_usa_capas_da_wikimedia(self):
        # A `demo` do seed já tem capas da Wikimedia; o intruso é um link qualquer.
        demo = User.objects.get(username='demo')
        Filme.objects.create(
            titulo='Intruso', genero=self.genero, diretor=self.diretor,
            sinopse='...', usuario=demo, capa_url='https://exemplo.com/qualquer.jpg',
        )
        self.assertNotContains(self.client.get(reverse('home')), 'exemplo.com')

    def test_csv_neutraliza_formula_no_titulo(self):
        Filme.objects.filter(pk=self.filme_ana.pk).update(titulo='=HYPERLINK("http://x")')
        self.client.force_login(self.ana)
        conteudo = self.client.get(reverse('consulta'), {'formato': 'csv'}).content.decode('utf-8-sig')
        self.assertIn('\'=HYPERLINK(""http://x"")', conteudo)

    def test_resposta_traz_content_security_policy(self):
        politica = self.client.get(reverse('home'))['Content-Security-Policy']
        self.assertIn("frame-ancestors 'none'", politica)
        self.assertIn("object-src 'none'", politica)

    def test_elenco_repetido_por_corrida_vira_erro_e_nao_500(self):
        # Simula dois envios simultâneos: a checagem do formulário deixa passar,
        # e quem barra é a UniqueConstraint do banco.
        ator = Ator.objects.create(nome='Ator Corrida')
        Elenco.objects.create(filme=self.filme_ana, ator=ator, personagem='A')
        self.client.force_login(self.ana)
        with mock.patch.object(ElencoForm, 'clean_ator', lambda form: form.cleaned_data['ator']):
            resposta = self.client.post(
                reverse('criar_elenco', args=[self.filme_ana.pk]),
                {'ator': ator.pk, 'personagem': 'B', 'ordem': 2},
            )
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('ator', resposta.context['form'].errors)
        self.assertEqual(self.filme_ana.elenco.count(), 1)

    def test_exclusao_barrada_pelo_protect_volta_para_a_confirmacao(self):
        # Outra conta liga um filme ao diretor entre a contagem e o delete.
        livre = Diretor.objects.create(nome='Sem Filmes', nacionalidade='X')
        self.client.force_login(self.ana)
        with mock.patch.object(Diretor, 'delete', side_effect=ProtectedError('vinculado', set())):
            resposta = self.client.post(reverse('excluir_diretor', args=[livre.pk]))
        self.assertRedirects(resposta, reverse('excluir_diretor', args=[livre.pk]))
        self.assertTrue(Diretor.objects.filter(pk=livre.pk).exists())
