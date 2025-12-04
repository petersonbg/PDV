const tasks = [
  { title: 'Fechar caixa 03', owner: 'Ana', status: 'Aguardando', tone: 'warning' },
  { title: 'Enviar remessa fiscal', owner: 'Roberto', status: 'Processando', tone: 'informative' },
  { title: 'Atualizar preços semanais', owner: 'Equipe', status: 'Em andamento', tone: 'positive' },
  { title: 'Conciliar pagamentos cartão', owner: 'Fernanda', status: 'Pendente', tone: 'danger' }
]

export default function TaskBoard() {
  return (
    <section className="card">
      <div className="card-header">
        <h2>Fila operacional</h2>
        <span className="badge">hoje</span>
      </div>
      <ul className="task-list">
        {tasks.map((task) => (
          <li key={task.title}>
            <div>
              <p className="title">{task.title}</p>
              <p className="muted">Responsável: {task.owner}</p>
            </div>
            <span className={`pill ${task.tone}`}>{task.status}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
