import { demoRepository } from './demoRepository.js'

export const isDemo = import.meta.env.VITE_CLINIC_MODE !== 'api'
const apiBase = (import.meta.env.VITE_CLINIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '')

const endpoints = {
  tutors: ['/api/tutores', 'tutores'],
  animals: ['/api/animais', 'animais'],
  vets: ['/api/veterinarios', 'veterinários'],
  appointments: ['/api/consultas', 'consultas'],
  vaccines: ['/api/vacinas', 'vacinas'],
  species: ['/api/especies', 'espécies'],
  breeds: ['/api/racas', 'raças'],
}

export const emptyData = {
  tutors: [], animals: [], appointments: [], vaccines: [], vets: [], integrations: [],
  species: [], breeds: [], errors: [],
}

async function request(path, { method = 'GET', body } = {}) {
  let response
  try {
    response = await fetch(`${apiBase}${path}`, {
      method,
      headers: { Accept: 'application/json', ...(body ? { 'Content-Type': 'application/json' } : {}) },
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(8000),
    })
  } catch (error) {
    if (error.name === 'TimeoutError') throw new Error('A API da clínica demorou para responder.')
    throw new Error('Não foi possível conectar à API da clínica.')
  }
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    if (typeof data?.detail === 'string') throw new Error(data.detail)
    if (Array.isArray(data?.detail)) {
      throw new Error(data.detail.map(({ loc, msg }) => `${loc?.slice(1).join('.') || 'Dados'}: ${msg}`).join(' · '))
    }
    throw new Error(`A API respondeu com HTTP ${response.status}.`)
  }
  return data
}

function save(resource, body, id) {
  const [path] = endpoints[resource]
  return request(id ? `${path}/${id}` : path, { method: id ? 'PUT' : 'POST', body })
}

async function listAnimalRecords(resource, animalId) {
  const [path] = endpoints[resource]
  const history = await request(`${path}?animal_id=${animalId}`)
  if (!Array.isArray(history)) throw new Error('A API retornou um histórico inválido.')
  return history
}

const apiRepository = {
  async lookupCep(cep) {
    const { logradouro, complemento, bairro, cidade, uf, codigo_ibge } = await request(`/api/cep/${cep}`)
    return { logradouro, complemento, bairro, cidade, uf, ibge: codigo_ibge }
  },

  async load() {
    const resources = Object.entries(endpoints)
    const results = await Promise.allSettled(resources.map(([key, [path]]) =>
      request(['tutors', 'animals'].includes(key) ? `${path}?incluir_inativos=true` : path),
    ))
    const data = { ...emptyData, errors: [] }
    results.forEach((result, index) => {
      const [key, [, label]] = resources[index]
      if (result.status === 'fulfilled' && Array.isArray(result.value)) data[key] = result.value
      else data.errors.push(`Não foi possível carregar ${label}. ${result.reason?.message ?? 'Resposta inesperada.'}`)
    })
    return data
  },
  saveTutor({ endereco, ...body }, id) {
    if (id) delete body.cpf
    return save('tutors', body, id)
  },
  createAddress({ ibge, ...address }) {
    return request('/api/enderecos', { method: 'POST', body: { ...address, codigo_ibge: ibge || null } })
  },
  saveAnimal: (body, id) => save('animals', body, id),
  saveAppointment: (body, id) => save('appointments', body, id),
  listAnimalAppointments: (id) => listAnimalRecords('appointments', id),
  cancelAppointment: (id) => request(`/api/consultas/${id}`, { method: 'DELETE' }),
  saveVaccine: (body, id) => save('vaccines', body, id),
  listAnimalVaccines: (id) => listAnimalRecords('vaccines', id),
  cancelVaccine: (id) => request(`/api/vacinas/${id}`, { method: 'DELETE' }),
  deactivate: (name, id) => request(`${endpoints[name][0]}/${id}`, { method: 'DELETE' }),
}

export const repository = isDemo ? demoRepository : apiRepository
