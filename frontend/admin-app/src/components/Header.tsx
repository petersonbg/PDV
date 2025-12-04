export default function Header() {
  return (
    <header className="page-header">
      <div>
        <p className="label">Operação</p>
        <h1>Administração e Monitoramento</h1>
        <p className="muted">Controle unificado de vendas, estoque e compliance fiscal.</p>
      </div>
      <div className="header-actions">
        <input type="text" placeholder="Buscar produto, cliente ou nota" />
        <button type="button" className="ghost">Exportar</button>
        <button type="button" className="primary">Nova venda</button>
      </div>
    </header>
  )
}
