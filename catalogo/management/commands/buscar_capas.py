from django.core.management.base import BaseCommand, CommandError

from catalogo.capas import ErroDeBusca, buscar_capa
from catalogo.models import Filme


class Command(BaseCommand):
    help = 'Busca na Wikipédia o pôster dos filmes que ainda não têm capa.'

    def add_arguments(self, parser):
        parser.add_argument('--usuario', help='só os filmes deste usuário (username)')
        parser.add_argument('--todos', action='store_true',
                            help='refaz a busca também nos filmes que já têm capa')

    def handle(self, *args, usuario=None, todos=False, **options):
        filmes = Filme.objects.select_related('diretor').order_by('titulo')
        if usuario:
            filmes = filmes.filter(usuario__username=usuario)
        if not todos:
            filmes = filmes.filter(capa_url='')

        total = filmes.count()
        if not total:
            self.stdout.write('Nenhum filme sem capa.')
            return

        encontradas = 0
        for numero, filme in enumerate(filmes, start=1):
            prefixo = f'[{numero}/{total}] {filme.titulo}'
            try:
                url = buscar_capa(filme.titulo, filme.diretor.nome)
            except ErroDeBusca as erro:
                raise CommandError(f'{prefixo}: {erro}') from erro
            if url:
                filme.capa_url = url
                filme.save(update_fields=['capa_url'])
                encontradas += 1
                self.stdout.write(self.style.SUCCESS(f'{prefixo}: ok'))
            else:
                self.stdout.write(self.style.WARNING(f'{prefixo}: não encontrada'))

        self.stdout.write(f'{encontradas} de {total} capas preenchidas.')
