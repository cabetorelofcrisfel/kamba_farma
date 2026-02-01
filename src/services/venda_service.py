def processar_venda(itens, usuario_id):
    """Processa uma venda: calcula total e regista."""
    total = sum(i['quantidade'] * i['preco_unitario'] for i in itens)
    return {'total': total, 'itens': itens, 'usuario_id': usuario_id}
