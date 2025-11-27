const lowStock = [
  { sku: '1001', name: 'Arroz 5kg', qty: 8 },
  { sku: '2002', name: 'Feijão 1kg', qty: 12 }
]

export default function InventoryWidget() {
  return (
    <section className="card">
      <h2>Estoque crítico</h2>
      <ul>
        {lowStock.map((item) => (
          <li key={item.sku}>
            <strong>{item.name}</strong> — {item.qty} un
          </li>
        ))}
      </ul>
    </section>
  )
}
