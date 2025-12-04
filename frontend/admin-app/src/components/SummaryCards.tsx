const cards = [
  { title: 'Faturamento do dia', value: 'R$ 18.240', detail: '+12% vs ontem', tone: 'positive' },
  { title: 'Tickets emitidos', value: '512', detail: '87 em atendimento', tone: 'informative' },
  { title: 'Caixas ativos', value: '5/7', detail: '2 aguardando fechamento', tone: 'warning' },
  { title: 'Notas fiscais', value: '96%', detail: 'Fila limpa (2 pendências)', tone: 'positive' }
]

export default function SummaryCards() {
  return (
    <section className="card wide">
      <div className="card-header">
        <h2>Resumo do dia</h2>
        <span className="badge">tempo real</span>
      </div>
      <div className="summary-cards">
        {cards.map((card) => (
          <div key={card.title} className={`stat ${card.tone}`}>
            <p className="muted">{card.title}</p>
            <div className="stat-value">
              <strong>{card.value}</strong>
              <span>{card.detail}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
