"""Content-Security-Policy (checklist de segurança, item 18).

O Django 5.2 ainda não tem CSP nativo, então ela entra aqui.

`'unsafe-inline'` em script e estilo é concessão consciente: a página usa o
`onerror` das capas, um script curto no `base.html` e `style="--matiz: ..."`
nas capas desenhadas. Mesmo assim a política fecha o que mais importa: script
de outro domínio, `<object>`, `<base>` trocado, formulário postando para fora e
o site dentro de iframe alheio.
"""

POLITICA = '; '.join([
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src https://fonts.gstatic.com",
    # As capas vêm de qualquer endereço https que o usuário colar.
    "img-src 'self' https: data:",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
])


def politica_de_conteudo(get_response):
    def aplicar(request):
        resposta = get_response(request)
        resposta.setdefault('Content-Security-Policy', POLITICA)
        return resposta
    return aplicar
