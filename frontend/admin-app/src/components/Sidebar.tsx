const menu = [
  { label: 'Painel', active: true },
  { label: 'Vendas e Caixas' },
  { label: 'Produtos e Estoque' },
  { label: 'Clientes e Fidelidade' },
  { label: 'Financeiro' },
  { label: 'Auditoria e Fiscal' }
]

const highlights = [
  { label: 'Caixa aberto', value: '02' },
  { label: 'Usuários online', value: '7' },
  { label: 'Alertas de estoque', value: '5' }
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="dot" />
        <div>
          <strong>PDV Aurora</strong>
          <p>Loja Central</p>
        </div>
      </div>

      <nav>
        <p className="label">Navegação</p>
        <ul className="menu">
          {menu.map((item) => (
            <li key={item.label} className={item.active ? 'active' : ''}>
              <span>{item.label}</span>
            </li>
          ))}
        </ul>
      </nav>

      <div className="summary">
        <p className="label">Estado rápido</p>
        <div className="summary-grid">
          {highlights.map((item) => (
            <div key={item.label} className="summary-card">
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="callout">
        <p>Próxima coleta fiscal em 32 min.</p>
        <button type="button">Ver fila</button>
      </div>
    </aside>
  )
}
