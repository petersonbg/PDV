import { useMemo, useState } from 'react'

type Item = { sku: string; name: string; qty: number; price: number }

const mockCatalog: Item[] = [
  { sku: '1001', name: 'Arroz 5kg', qty: 1, price: 25.9 },
  { sku: '2002', name: 'Feijão 1kg', qty: 1, price: 8.5 },
  { sku: '3003', name: 'Refrigerante 2L', qty: 1, price: 9.9 }
]

export function SalePanel({ onStatusChange }: { onStatusChange: (status: string) => void }) {
  const [cart, setCart] = useState<Item[]>([])
  const total = useMemo(() => cart.reduce((sum, i) => sum + i.price * i.qty, 0), [cart])

  const addItem = (item: Item) => {
    setCart((prev) => [...prev, item])
    onStatusChange('Em venda')
  }

  const finalize = () => {
    onStatusChange('Finalizada')
    setCart([])
  }

  return (
    <section>
      <h2>Venda rápida</h2>
      <div className="grid">
        <div>
          <h3>Catálogo</h3>
          <ul>
            {mockCatalog.map((item) => (
              <li key={item.sku}>
                <button onClick={() => addItem(item)}>
                  {item.name} - R$ {item.price.toFixed(2)}
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3>Carrinho</h3>
          <ul>
            {cart.map((item, idx) => (
              <li key={idx}>
                {item.name} x{item.qty} — R$ {(item.price * item.qty).toFixed(2)}
              </li>
            ))}
          </ul>
          <p>Total: R$ {total.toFixed(2)}</p>
          <button onClick={finalize} disabled={!cart.length}>
            Finalizar venda
          </button>
        </div>
      </div>
    </section>
  )
}
