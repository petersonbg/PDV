const events = [
  { title: 'Sincronização concluída', detail: 'Inventário recebido da loja 02', time: '14:12' },
  { title: 'Recebimento de fornecedor', detail: 'Pedido #5534 conferido - 184 unidades', time: '13:48' },
  { title: 'NFC-e autorizada', detail: 'Venda 009381 - Caixa 04', time: '13:21' },
  { title: 'Usuário logado', detail: 'Caixa 05 - operador Rafael', time: '12:57' }
]

export default function ActivityFeed() {
  return (
    <section className="card wide">
      <div className="card-header">
        <h2>Atividades recentes</h2>
        <span className="badge ghost">tempo real</span>
      </div>
      <ul className="timeline">
        {events.map((event) => (
          <li key={event.title}>
            <div className="bullet" />
            <div>
              <p className="title">{event.title}</p>
              <p className="muted">{event.detail}</p>
            </div>
            <span className="muted time">{event.time}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
