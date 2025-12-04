const channels = [
  { name: 'Balcão / PDV', gross: 'R$ 14.120', tickets: 396, avg: 'R$ 35,66', target: 82 },
  { name: 'Delivery', gross: 'R$ 2.480', tickets: 68, avg: 'R$ 36,47', target: 64 },
  { name: 'Retirada', gross: 'R$ 1.640', tickets: 48, avg: 'R$ 34,16', target: 72 }
]

export default function SalesPerformance() {
  return (
    <section className="card wide">
      <div className="card-header">
        <h2>Performance de vendas</h2>
        <span className="badge ghost">filial loja central</span>
      </div>
      <div className="table">
        <div className="table-head">
          <span>Canal</span>
          <span>Bruto</span>
          <span>Tickets</span>
          <span>Ticket médio</span>
          <span>Meta</span>
        </div>
        {channels.map((channel) => (
          <div key={channel.name} className="table-row">
            <span className="title">{channel.name}</span>
            <span>{channel.gross}</span>
            <span>{channel.tickets}</span>
            <span>{channel.avg}</span>
            <div className="progress">
              <div className="bar" style={{ width: `${channel.target}%` }} />
              <span>{channel.target}%</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
