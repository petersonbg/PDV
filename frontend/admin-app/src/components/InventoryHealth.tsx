const items = [
  { sku: '1001', name: 'Arroz 5kg', status: 'Crítico', qty: 8, action: 'Gerar pedido' },
  { sku: '2044', name: 'Queijo muçarela', status: 'Reposição', qty: 19, action: 'Separar inventário' },
  { sku: '3012', name: 'Refrigerante 2L', status: 'OK', qty: 64, action: 'Monitorar venda' },
  { sku: '4409', name: 'Café 500g', status: 'Crítico', qty: 12, action: 'Negociar fornecedor' }
]

const statusTone: Record<string, string> = {
  Crítico: 'danger',
  Reposição: 'warning',
  OK: 'positive'
}

export default function InventoryHealth() {
  return (
    <section className="card">
      <div className="card-header">
        <h2>Estoque e reposição</h2>
        <span className="badge ghost">última contagem 15:40</span>
      </div>
      <div className="table compact">
        <div className="table-head">
          <span>SKU</span>
          <span>Item</span>
          <span>Status</span>
          <span>Qtd</span>
          <span>Ação rápida</span>
        </div>
        {items.map((item) => (
          <div key={item.sku} className="table-row">
            <span className="muted">{item.sku}</span>
            <span className="title">{item.name}</span>
            <span className={`pill ${statusTone[item.status]}`}>{item.status}</span>
            <span>{item.qty} un</span>
            <button type="button" className="ghost">{item.action}</button>
          </div>
        ))}
      </div>
    </section>
  )
}
