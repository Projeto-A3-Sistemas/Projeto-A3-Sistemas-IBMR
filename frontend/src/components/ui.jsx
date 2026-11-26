import { useEffect, useRef } from 'react'
import demoPortraits from '../assets/pacientes-demo.webp'
import { formatDate } from '../clinic/format.js'

const iconPaths = {
  paw: <><path d="M11.9 11.8c-2.4 0-3.3 2.6-5.6 4.3-2.8 2.1-1.6 5.8 1.7 5.4 1.4-.2 2.5-1 4-1s2.6.8 4 1c3.3.4 4.5-3.3 1.7-5.4-2.3-1.7-3.2-4.3-5.8-4.3Z"/><ellipse cx="4.8" cy="9.5" rx="2.2" ry="3" transform="rotate(-26 4.8 9.5)"/><ellipse cx="9.5" cy="5.4" rx="2.1" ry="3" transform="rotate(-10 9.5 5.4)"/><ellipse cx="14.8" cy="5.4" rx="2.1" ry="3" transform="rotate(10 14.8 5.4)"/><ellipse cx="19.4" cy="9.5" rx="2.2" ry="3" transform="rotate(26 19.4 9.5)"/></>,
  people: <><circle cx="10" cy="8" r="3.5"/><path d="M3 21v-2a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v2M16 5a3.5 3.5 0 0 1 0 6.7m2 2.8a5 5 0 0 1 3 4.5v2"/></>,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/></>,
  syringe: <><path d="m18 2 4 4M17 7l4-4M19 9l-9 9H6v-4l9-9m-2-2 8 8m-9-3 2 2m-5 1 2 2m-5 5-4 4"/></>,
  link: <path d="M10 13a4 4 0 0 0 6 0l4-4a4 4 0 0 0-6-6l-2 2m2 6a4 4 0 0 0-6 0l-4 4a4 4 0 0 0 6 6l2-2"/>,
  plus: <path d="M12 5v14M5 12h14"/>,
  search: <><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/></>,
  close: <path d="m6 6 12 12M18 6 6 18"/>,
  edit: <path d="m13 6 5 5M4 20l4-1 12-12a2 2 0 0 0-3-3L5 16l-1 4Z"/>,
  clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
  logout: <path d="M10 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h5m5-13 5 5-5 5m-7-5h12"/>,
  chip: <><rect x="6" y="6" width="12" height="12" rx="2"/><rect x="10" y="10" width="4" height="4" rx="1"/><path d="M9 3v3m6-3v3M9 18v3m6-3v3M3 9h3m-3 6h3m12-6h3m-3 6h3"/></>,
}

export function Icon({ name, size = 20 }) {
  return <svg className="icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{iconPaths[name]}</svg>
}

const statuses = {
  ativo: 'Ativo', inativo: 'Inativo', realizada: 'Realizada', agendada: 'Agendada',
  cancelada: 'Cancelada', nao_compareceu: 'Não compareceu', aplicada: 'Aplicada',
  pendente: 'Pendente', enviada: 'Enviada', enviado: 'Enviado', confirmada: 'Confirmada', falha: 'Falha',
}
const statusTones = {
  ativo: 'good', realizada: 'good', aplicada: 'good', confirmada: 'good',
  pendente: 'warning', cancelada: 'alert', falha: 'alert',
}

export function Status({ value, label }) {
  return <span className={`status status--${statusTones[value] ?? 'neutral'}`}>
    {value === 'pendente' ? <Icon name="clock" size={15} /> : value === 'ativo' ? <span className="status-dot" /> : null}
    {label ?? statuses[value] ?? value}
  </span>
}

export function Button({ children, icon, variant = 'primary', ...props }) {
  return <button type="button" className={`button button--${variant}`} {...props}>{icon && <Icon name={icon} size={18} />}{children}</button>
}

export function PageHeader({ title, description, children }) {
  return <header className="page-header">
    <div><h1>{title}</h1>{description && <p className="muted">{description}</p>}</div>
    {children && <div className="page-actions">{children}</div>}
  </header>
}

export function Search({ label, value, onChange }) {
  return <label className="search-field">
    <Icon name="search" />
    <input type="search" aria-label={label} placeholder={label} value={value} onChange={(event) => onChange(event.target.value)} />
  </label>
}

export function Tabs({ items, value, onChange, label }) {
  return <div className="tabs" aria-label={label} role="group">
    {items.map(([id, name]) =>
      <button key={id} type="button" aria-pressed={value === id} onClick={() => onChange(id)}>{name}</button>,
    )}
  </div>
}

export function DataTable({ columns, rows, rowKey = 'id', empty = 'Nenhum registro encontrado.', selected, label }) {
  if (!rows.length) return <p className="empty">{empty}</p>
  return <table className="data-table" aria-label={label}>
    <thead><tr>{columns.map(({ key, label }) => <th key={key} scope="col">{label || <span className="sr-only">Ações</span>}</th>)}</tr></thead>
    <tbody>{rows.map((row) => <tr key={row[rowKey]} className={selected === row[rowKey] ? 'selected-row' : undefined}>
      {columns.map(({ key, label, render }) => <td key={key} data-label={label}>{render(row)}</td>)}
    </tr>)}</tbody>
  </table>
}

export function KeyValues({ items }) {
  return <dl className="key-values">
    {items.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value ?? '—'}</dd></div>)}
  </dl>
}

export function PetAvatar({ animal, large = false }) {
  return <span
    className={`pet-avatar ${large ? 'pet-avatar--large' : ''} ${animal.portrait ? `pet-avatar--${animal.portrait}` : ''}`}
    style={animal.portrait ? { backgroundImage: `url("${demoPortraits}")` } : undefined}
    aria-hidden="true"
  >
    {!animal.portrait && <Icon name="paw" size={large ? 35 : 21} />}
  </span>
}

export function DateText({ value }) {
  return value ? <time dateTime={value}>{formatDate(value)}</time> : '—'
}

export function Modal({ title, onClose, busy = false, children }) {
  const ref = useRef(null)
  useEffect(() => {
    const dialog = ref.current
    dialog.showModal()
    return () => dialog.close()
  }, [])
  return <dialog ref={ref} className="modal" aria-labelledby="modal-title" onCancel={(event) => {
    event.preventDefault()
    if (!busy) onClose()
  }}>
    <div className="modal-header"><h2 id="modal-title">{title}</h2>
      <button className="icon-button" type="button" aria-label="Fechar" disabled={busy} onClick={onClose}><Icon name="close" /></button>
    </div>
    {children}
  </dialog>
}
