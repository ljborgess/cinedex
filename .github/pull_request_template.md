## O que muda

<!-- 2 a 4 linhas. O que passa a funcionar, não a lista de arquivos. -->

## Como testar

<!-- Passo a passo para quem revisa. Normalmente: `rodar.bat`, ou `python manage.py test`. -->

## Checklist de segurança

Marcar só o que a mudança toca, e só depois de conferir. O racional de cada item está em [AUDITORIA.md](../AUDITORIA.md).

- [ ] View nova tem `@login_required` (só `home`, `login` e `cadastro` são públicas)
- [ ] Consulta de `Filme`, `Avaliacao` ou `Elenco` parte de `filmes_do` / `avaliacoes_do` / `elenco_do`
- [ ] Dono do registro vem de `request.user`, nunca do formulário
- [ ] `ModelForm` com `fields` explícito (nada de `__all__`)
- [ ] GET nunca muda estado: excluir, buscar capa e sair são POST
- [ ] Erro esperado do banco (`ProtectedError`, `IntegrityError`) vira mensagem, não página 500
- [ ] Nenhuma chave, senha ou `.env` no diff
- [ ] Model alterado vem com migration

## O que ficou de fora

<!-- O que foi adiado de propósito. "Nada" é resposta válida. -->
