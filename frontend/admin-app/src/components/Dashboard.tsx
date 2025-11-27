const kpis = [
  { label: 'Faturamento (hoje)', value: 'R$ 12.340' },
  { label: 'Tickets', value: '248' },
  { label: 'Ticket médio', value: 'R$ 49,76' }
]

export default function Dashboard() {
  return (
    <section className="card">
      <h2>Visão Geral</h2>
      <div className="kpis">
        {kpis.map((item) => (
          <div key={item.label} className="kpi">
            <p>{item.label}</p>
            <strong>{item.value}</strong>
          </div>
        ))}
      </div>
    </section>
  )
}
