"""Limite de tentativas por IP no login e no cadastro (checklist, itens 11 e 12).

Sem isso, um script testa senhas da conta `demo` sem parar, ou cria contas em
lote. O contador mora no cache do Django e expira sozinho depois da janela.

O IP é o `REMOTE_ADDR`, nunca o `X-Forwarded-For`: esse cabeçalho é escrito por
quem faz a requisição, e confiar nele torna o limite decorativo.

Consequência: rodando local, todo mundo é 127.0.0.1 e divide o mesmo contador.
Reiniciar o servidor zera tudo, porque o contador vive na memória do processo.
"""
from django.core.cache import cache

LIMITE = 5
JANELA = 15 * 60  # segundos
MENSAGEM = 'Muitas tentativas seguidas. Aguarde alguns minutos e tente de novo.'


# ponytail: cache em memória vale por processo; com vários workers em produção,
# trocar CACHES para Redis ou banco e o limite passa a valer para todos. Atrás de
# proxy (Render, Nginx), REMOTE_ADDR é o IP do proxy e um atacante trancaria o
# login de todos: ler o IP real só do cabeçalho que esse proxy garante.
def _chave(request, acao):
    return f'tentativas:{acao}:{request.META.get("REMOTE_ADDR", "")}'


def bloqueado(request, acao):
    return cache.get(_chave(request, acao), 0) >= LIMITE


def contar(request, acao):
    chave = _chave(request, acao)
    cache.add(chave, 0, JANELA)  # só cria; não reinicia a janela de quem já tem contador
    try:
        cache.incr(chave)
    except ValueError:
        # A janela expirou entre o add e o incr: começa uma nova, em vez de página 500.
        cache.set(chave, 1, JANELA)
