const dailySales = [
  { date: '09/05', total: 18430.5, quantity: 482, trend: '+8%' },
  { date: '08/05', total: 16980.75, quantity: 451, trend: '+3%' },
  { date: '07/05', total: 15214.0, quantity: 420, trend: '-2%' },
  { date: '06/05', total: 14892.3, quantity: 405, trend: '+1%' }
]

const cashFlow = [
  { method: 'Cartão crédito', paid: true, total: 11240 },
  { method: 'Cartão débito', paid: true, total: 6840 },
  { method: 'Dinheiro', paid: true, total: 4320 },
  { method: 'Pix', paid: true, total: 5180 },
  { method: 'Fiado', paid: false, total: 2890 }
]

const bestSellers = [
  { product: 'Café gourmet 500g', quantity: 128, revenue: 6144 },
  { product: 'Pão de fermentação natural', quantity: 102, revenue: 3468 },
  { product: 'Capuccino pronto 300ml', quantity: 96, revenue: 3360 },
  { product: 'Combo café + pão de queijo', quantity: 84, revenue: 3192 }
]

const stockTurns = [
  { product: 'Café gourmet 500g', entries: 210, exits: 198, balance: 12 },
  { product: 'Leite vegetal 1L', entries: 160, exits: 124, balance: 36 },
  { product: 'Xícara térmica', entries: 75, exits: 54, balance: 21 },
  { product: 'Filtro de papel', entries: 320, exits: 308, balance: 12 }
]

const creditCustomers = [
  { customer: 'Maria Clara', pending: 840.5 },
  { customer: 'Gabriel Souza', pending: 624.0 },
  { customer: 'Loja Parceira Centro', pending: 512.3 },
  { customer: 'Paulo Ferreira', pending: 403.0 }
]

export default function Reports() {
  const grossTotal = cashFlow.filter((item) => item.paid).reduce((sum, item) => sum + item.total, 0)
  const pendingTotal = cashFlow.filter((item) => !item.paid).reduce((sum, item) => sum + item.total, 0)
  const averageTicket = dailySales[0] ? dailySales[0].total / dailySales[0].quantity : 0

  return (
    <section className="card wide reports">
      <div className="card-header">
        <div>
          <p className="badge">Relatórios</p>
          <h2>Análise consolidada</h2>
          <p className="muted">Visão rápida de vendas, fluxo de caixa e saúde do estoque</p>
        </div>
        <div className="report-actions">
          <button type="button" className="ghost">
            Exportar CSV
          </button>
          <button type="button" className="primary">
            Últimos 7 dias
          </button>
        </div>
      </div>

      <div className="report-summary">
        <div className="stat positive">
          <span className="label">Faturamento pago</span>
          <div className="stat-value">
            <strong>R$ {grossTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</strong>
            <span className="pill positive">+5% vs. semana anterior</span>
          </div>
        </div>
        <div className="stat warning">
          <span className="label">A receber / fiado</span>
          <div className="stat-value">
            <strong>R$ {pendingTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</strong>
            <span className="pill warning">monitorar clientes</span>
          </div>
        </div>
        <div className="stat informative">
          <span className="label">Ticket médio (hoje)</span>
          <div className="stat-value">
            <strong>R$ {averageTicket.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</strong>
            <span className="pill informative">{dailySales[0]?.trend ?? ''}</span>
          </div>
        </div>
        <div className="stat">
          <span className="label">Clientes fiados</span>
          <div className="stat-value">
            <strong>{creditCustomers.length} contas</strong>
            <span className="pill">acompanhando quitação</span>
          </div>
        </div>
      </div>

      <div className="report-grid">
        <div className="report-section">
          <div className="section-header">
            <h3>Vendas diárias</h3>
            <span className="badge ghost">rolando 4 dias</span>
          </div>
          <div className="report-table columns-4">
            <div className="report-row head">
              <span>Data</span>
              <span>Pedidos</span>
              <span>Faturamento</span>
              <span>Tendência</span>
            </div>
            {dailySales.map((sale) => (
              <div key={sale.date} className="report-row">
                <span className="title">{sale.date}</span>
                <span>{sale.quantity} pedidos</span>
                <span>R$ {sale.total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
                <span className={`trend ${sale.trend.startsWith('-') ? 'down' : 'up'}`}>{sale.trend}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="report-section">
          <div className="section-header">
            <h3>Fluxo de caixa</h3>
            <span className="badge ghost">por método</span>
          </div>
          <div className="report-table columns-3">
            <div className="report-row head">
              <span>Método</span>
              <span>Status</span>
              <span>Total</span>
            </div>
            {cashFlow.map((flow) => (
              <div key={flow.method} className="report-row">
                <span className="title">{flow.method}</span>
                <span>
                  <span className={`pill ${flow.paid ? 'positive' : 'warning'}`}>
                    {flow.paid ? 'Pago' : 'Pendente'}
                  </span>
                </span>
                <span>R$ {flow.total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="report-section">
          <div className="section-header">
            <h3>Produtos mais vendidos</h3>
            <span className="badge ghost">ranking</span>
          </div>
          <div className="report-table columns-3">
            <div className="report-row head">
              <span>Produto</span>
              <span>Qtd.</span>
              <span>Faturamento</span>
            </div>
            {bestSellers.map((item) => (
              <div key={item.product} className="report-row">
                <span className="title">{item.product}</span>
                <span>{item.quantity} un.</span>
                <span>R$ {item.revenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="report-section">
          <div className="section-header">
            <h3>Giro e saldo de estoque</h3>
            <span className="badge ghost">última semana</span>
          </div>
          <div className="report-table columns-4">
            <div className="report-row head">
              <span>Produto</span>
              <span>Entradas</span>
              <span>Saídas</span>
              <span>Saldo</span>
            </div>
            {stockTurns.map((item) => (
              <div key={item.product} className="report-row">
                <span className="title">{item.product}</span>
                <span>{item.entries}</span>
                <span>{item.exits}</span>
                <span className={item.balance < 0 ? 'trend down' : 'trend up'}>{item.balance}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="report-section">
          <div className="section-header">
            <h3>Clientes fiados</h3>
            <span className="badge ghost">bloqueio de crédito</span>
          </div>
          <div className="report-table columns-3">
            <div className="report-row head">
              <span>Cliente</span>
              <span>Pendente</span>
              <span>Ação</span>
            </div>
            {creditCustomers.map((customer) => (
              <div key={customer.customer} className="report-row">
                <span className="title">{customer.customer}</span>
                <span>R$ {customer.pending.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
                <span className="pill warning">acompanhar</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
