"""Busca automática do pôster de um filme na Wikipédia.

Não precisa de chave de API nem de biblioteca extra (só `urllib`).

Como funciona:
1. procura o título na Wikipédia em português;
2. segue o link para o artigo equivalente em inglês, que é onde os pôsteres
   oficiais ficam hospedados;
3. só aceita a página se ela for de um filme e citar o diretor cadastrado.
   Isso evita trazer o livro de mesmo nome ou a continuação do filme.

Devolve só o endereço da imagem; o arquivo não é baixado. A capa é exibida
direto de upload.wikimedia.org.
"""
import difflib
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

# A Wikimedia pede um User-Agent que identifique o cliente.
USER_AGENT = 'crud-filmes/1.0 (projeto academico Django)'
PAUSA = 1.0  # segundos entre chamadas, para não ser bloqueado (HTTP 429)


class ErroDeBusca(Exception):
    pass


def _api(idioma, **parametros):
    parametros.update(format='json', formatversion=2)
    url = f'https://{idioma}.wikipedia.org/w/api.php?' + urllib.parse.urlencode(parametros)
    requisicao = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    for _ in range(4):
        time.sleep(PAUSA)
        try:
            with urllib.request.urlopen(requisicao, timeout=15) as resposta:
                return json.load(resposta)
        except urllib.error.HTTPError as erro:
            if erro.code != 429:
                raise ErroDeBusca(f'Wikipédia respondeu HTTP {erro.code}') from erro
            time.sleep(int(erro.headers.get('Retry-After') or 10))
        except (urllib.error.URLError, TimeoutError) as erro:
            raise ErroDeBusca(f'Sem conexão com a Wikipédia ({erro})') from erro
    raise ErroDeBusca('Wikipédia limitou as requisições; tente de novo em alguns minutos')


def _normalizar(texto):
    sem_acento = unicodedata.normalize('NFKD', texto.lower())
    return ''.join(c for c in sem_acento if not unicodedata.combining(c)).replace('-', ' ')


def _sem_parenteses(titulo):
    return re.sub(r'\s*\(.*?\)\s*', ' ', titulo).strip()


def _cita_o_diretor(texto, diretor):
    nomes = [n for n in _normalizar(diretor).split() if len(n) >= 4]
    return any(nome in texto for nome in nomes)


def buscar_capa(titulo, diretor):
    """Endereço do pôster do filme, ou None se nenhum resultado for confiável."""
    resultado = _api(
        'pt', action='query', generator='search', gsrsearch=f'{titulo} filme', gsrlimit=6,
        prop='langlinks', lllang='en', redirects=1,
    )
    paginas_pt = [p for p in resultado.get('query', {}).get('pages', []) if p.get('langlinks')]
    if not paginas_pt:
        return None

    # O resultado cujo título em português mais se parece com o cadastrado vem
    # primeiro: "O Poderoso Chefão" antes de "O Poderoso Chefão: Parte II".
    alvo = _normalizar(titulo)
    paginas_pt.sort(key=lambda p: (
        -difflib.SequenceMatcher(None, alvo, _normalizar(_sem_parenteses(p['title']))).ratio(),
        p.get('index', 99),
    ))
    titulos_en = [p['langlinks'][0]['title'] for p in paginas_pt]

    resultado = _api(
        'en', action='query', titles='|'.join(titulos_en), redirects=1,
        prop='pageimages|description|extracts', piprop='thumbnail', pithumbsize=500,
        pilicense='any', exintro=1, explaintext=1, exlimit='max',
    )
    consulta = resultado.get('query', {})
    por_titulo = {p['title']: p for p in consulta.get('pages', [])}
    for redirecionamento in consulta.get('redirects', []):
        if redirecionamento['to'] in por_titulo:
            por_titulo[redirecionamento['from']] = por_titulo[redirecionamento['to']]

    for titulo_en in titulos_en:
        pagina = por_titulo.get(titulo_en)
        if not pagina or 'thumbnail' not in pagina:
            continue
        descricao = _normalizar(pagina.get('description', ''))
        texto = descricao + ' ' + _normalizar(pagina.get('extract', '')[:1500])
        if 'film' in descricao and _cita_o_diretor(texto, diretor):
            # Tira os parâmetros de rastreio (?utm_...) que a API acrescenta.
            return pagina['thumbnail']['source'].split('?')[0]
    return None
