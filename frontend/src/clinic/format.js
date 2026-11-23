export function digits(value = '') {
  return String(value).replace(/\D/g, '')
}

export function validCpf(value) {
  const cpf = digits(value)
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false
  return [9, 10].every((length) => {
    const sum = [...cpf.slice(0, length)].reduce((total, digit, index) => total + Number(digit) * (length + 1 - index), 0)
    return ((sum * 10) % 11) % 10 === Number(cpf[length])
  })
}

export function formatCpf(value) {
  return digits(value).replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4') || '—'
}

export function formatPhone(value) {
  return digits(value).replace(/^(\d{2})(\d{4,5})(\d{4})$/, '($1) $2-$3') || '—'
}

export function formatChip(value) {
  return value ? String(value).replace(/^(?:\d+)$/, (code) => code.replace(/(\d{3})(?=\d)/g, '$1 ')) : 'Não vinculado'
}

export function dayKey(value) {
  return value?.slice(0, 10) ?? ''
}

export function localDate() {
  return new Intl.DateTimeFormat('sv-SE', { timeZone: 'America/Sao_Paulo' }).format(new Date())
}

export function formatDate(value, long = false) {
  if (!value) return '—'
  const date = new Date(`${dayKey(value)}T12:00:00`)
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: long ? 'long' : 'short' }).format(date)
}

export function formatTime(value) {
  if (!value) return '—'
  if (!/(Z|[+-]\d\d:\d\d)$/.test(value)) return value.slice(11, 16)
  return new Intl.DateTimeFormat('pt-BR', {
    timeZone: 'America/Sao_Paulo', hour: '2-digit', minute: '2-digit',
  }).format(new Date(value))
}

export function appointmentDay(value) {
  if (!value || !/(Z|[+-]\d\d:\d\d)$/.test(value)) return dayKey(value)
  return new Intl.DateTimeFormat('sv-SE', { timeZone: 'America/Sao_Paulo' }).format(new Date(value))
}

export function matches(query, ...values) {
  const normalize = (item) => String(item ?? '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
  return normalize(query).trim().split(/\s+/).every((word) => values.some((value) => normalize(value).includes(word)))
}
