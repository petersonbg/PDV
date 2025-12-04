import { useMemo, useState } from 'react'

type CatalogItem = {
  sku: string
  name: string
  price: number
  barcode: string
  stock: number
}

type CartItem = CatalogItem & { qty: number }

const mockCatalog: CatalogItem[] = [
  { sku: '1001', name: 'Arroz 5kg Premium', price: 25.9, barcode: '789100001', stock: 34 },
  { sku: '1002', name: 'Feijão Carioca 1kg', price: 8.5, barcode: '789100002', stock: 52 },
  { sku: '1003', name: 'Macarrão Espaguete 500g', price: 5.2, barcode: '789100003', stock: 41 },
  { sku: '1004', name: 'Óleo de Soja 900ml', price: 6.9, barcode: '789100004', stock: 63 },
  { sku: '1005', name: 'Refrigerante 2L Cola', price: 9.9, barcode: '789100005', stock: 22 },
  { sku: '1006', name: 'Biscoito Recheado 140g', price: 3.5, barcode: '789100006', stock: 88 },
  { sku: '1007', name: 'Café Torrado 500g', price: 16.4, barcode: '789100007', stock: 19 },
  { sku: '1008', name: 'Sabão em Pó 1,6kg', price: 24.8, barcode: '789100008', stock: 27 }
]

const paymentMethods = ['Dinheiro', 'Crédito', 'Débito', 'Pix', 'Voucher']

export function SalePanel({ onStatusChange }: { onStatusChange: (status: string) => void }) {
  const [cart, setCart] = useState<CartItem[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [discount, setDiscount] = useState(0)
  const [selectedPayment, setSelectedPayment] = useState(paymentMethods[0])

  const filteredCatalog = useMemo(() => {
    const term = searchTerm.toLowerCase()
    if (!term) return mockCatalog

    return mockCatalog.filter((item) =>
      `${item.name} ${item.barcode} ${item.sku}`.toLowerCase().includes(term)
    )
  }, [searchTerm])

  const subtotal = useMemo(
    () => cart.reduce((sum, item) => sum + item.price * item.qty, 0),
    [cart]
  )
  const total = useMemo(() => Math.max(0, subtotal - discount), [discount, subtotal])

  const addItem = (item: CatalogItem) => {
    setCart((prev) => {
      const existing = prev.find((line) => line.sku === item.sku)
      if (existing) {
        return prev.map((line) =>
          line.sku === item.sku ? { ...line, qty: line.qty + 1 } : line
        )
      }

      return [...prev, { ...item, qty: 1 }]
    })
    onStatusChange('Em venda')
  }

  const adjustQuantity = (sku: string, delta: number) => {
    setCart((prev) =>
      prev
        .map((line) => (line.sku === sku ? { ...line, qty: line.qty + delta } : line))
        .filter((line) => line.qty > 0)
    )
  }

  const removeItem = (sku: string) => {
    setCart((prev) => prev.filter((line) => line.sku !== sku))
  }

  const clearSale = () => {
    setCart([])
    setDiscount(0)
    setSelectedPayment(paymentMethods[0])
    onStatusChange('Aberto')
  }

  const finalizeSale = () => {
    if (!cart.length) return
    onStatusChange('Finalizada')
    setCart([])
    setDiscount(0)
    setSelectedPayment(paymentMethods[0])
  }

  return (
    <section className="panel">
      <div className="panel__header">
        <div>
          <p className="eyebrow">Frente de caixa</p>
          <h2>Venda rápida</h2>
          <p className="muted">Simulação do fluxo de PDV com atalhos e visibilidade de totais.</p>
        </div>
        <div className="header__meta">
          <span className="badge">Caixa 02</span>
          <span className="badge badge--live">Status: {cart.length ? 'Em venda' : 'Livre'}</span>
          <span className="chip">Itens no carrinho: {cart.length}</span>
        </div>
      </div>

      <div className="panel__filters">
        <label className="input-group">
          <span>Buscar por nome, SKU ou código de barras</span>
          <input
            type="search"
            placeholder="ex: 1004 ou refrigerante"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </label>
        <div className="shortcuts">
          <span>F2 - Inserir item</span>
          <span>F4 - Quantidade</span>
          <span>F7 - Pagamento</span>
          <span>F9 - Finalizar</span>
        </div>
      </div>

      <div className="panel__layout">
        <div className="card">
          <div className="card__title">
            <div>
              <p className="eyebrow">Catálogo</p>
              <h3>Itens disponíveis</h3>
            </div>
            <span className="chip chip--ghost">{filteredCatalog.length} resultados</span>
          </div>
          <div className="catalog-grid">
            {filteredCatalog.map((item) => (
              <button key={item.sku} className="catalog-item" onClick={() => addItem(item)}>
                <div>
                  <p className="muted">SKU {item.sku}</p>
                  <strong>{item.name}</strong>
                  <p className="muted">Estoque: {item.stock} • Código: {item.barcode}</p>
                </div>
                <div className="price">R$ {item.price.toFixed(2)}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card__title">
            <div>
              <p className="eyebrow">Carrinho</p>
              <h3>Itens da venda</h3>
            </div>
            <span className="chip chip--ghost">Subtotal R$ {subtotal.toFixed(2)}</span>
          </div>
          <div className="cart-table">
            <div className="cart-table__head">
              <span>Item</span>
              <span className="center">Qtd</span>
              <span className="right">Unitário</span>
              <span className="right">Total</span>
              <span className="right">Ações</span>
            </div>
            <div className="cart-table__body">
              {cart.length === 0 && <p className="muted">Nenhum produto lançado.</p>}
              {cart.map((line) => (
                <div key={line.sku} className="cart-row">
                  <div>
                    <strong>{line.name}</strong>
                    <p className="muted">SKU {line.sku}</p>
                  </div>
                  <div className="center qty-control">
                    <button onClick={() => adjustQuantity(line.sku, -1)}>-</button>
                    <span>{line.qty}</span>
                    <button onClick={() => adjustQuantity(line.sku, 1)}>+</button>
                  </div>
                  <div className="right">R$ {line.price.toFixed(2)}</div>
                  <div className="right">R$ {(line.price * line.qty).toFixed(2)}</div>
                  <div className="right">
                    <button className="ghost" onClick={() => removeItem(line.sku)}>
                      Remover
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card summary">
          <div className="card__title">
            <div>
              <p className="eyebrow">Pagamento</p>
              <h3>Resumo da venda</h3>
            </div>
            <span className="badge">PDV Desktop</span>
          </div>

          <dl className="totals">
            <div>
              <dt>Subtotal</dt>
              <dd>R$ {subtotal.toFixed(2)}</dd>
            </div>
            <div>
              <dt>Desconto</dt>
              <dd>
                <input
                  type="number"
                  min={0}
                  value={discount}
                  onChange={(event) => setDiscount(Number(event.target.value))}
                />
              </dd>
            </div>
            <div className="totals__highlight">
              <dt>Total a receber</dt>
              <dd>R$ {total.toFixed(2)}</dd>
            </div>
          </dl>

          <div className="payment-methods">
            {paymentMethods.map((method) => (
              <button
                key={method}
                className={selectedPayment === method ? 'active' : ''}
                onClick={() => setSelectedPayment(method)}
              >
                {method}
              </button>
            ))}
          </div>

          <div className="summary__actions">
            <button onClick={finalizeSale} disabled={!cart.length}>
              Receber pagamento ({selectedPayment})
            </button>
            <button className="ghost" onClick={clearSale}>
              Cancelar venda
            </button>
          </div>
        </div>
      </div>

      <div className="panel__footer">
        <div>
          <p className="muted">Operador: Joana Lima • Turno manhã</p>
          <p className="muted">Última sincronização: 2 min atrás</p>
        </div>
        <div className="footer__actions">
          <button className="ghost">Suspender venda</button>
          <button className="ghost">Abrir gaveta</button>
          <button className="primary" onClick={finalizeSale} disabled={!cart.length}>
            Finalizar (F9)
          </button>
        </div>
      </div>
    </section>
  )
}
