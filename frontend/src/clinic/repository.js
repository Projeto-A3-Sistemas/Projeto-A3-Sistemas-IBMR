import { demoRepository } from './demoRepository.js'

export const isDemo = import.meta.env.VITE_CLINIC_MODE !== 'api'
const apiBase = (import.meta.env.VITE_CLINIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '')
const accessTokenKey = `sdm:api-session:${apiBase}`
export const sessionEndedEvent = 'sdm:api-session-ended'

function storedToken() {
  return sessionStorage.getItem(accessTokenKey)
}

function clearToken() {
  sessionStorage.removeItem(accessTokenKey)
}

const endpoints = {
  tutors: ['/api/tutores', 'tutores'],
  animals: ['/api/animais', 'animais'],
  vets: ['/api/veterinarios', 'veterinários'],
  appointments: ['/api/consultas', 'consultas'],
  vaccines: ['/api/vacinas', 'vacinas'],
  species: ['/api/especies', 'espécies'],
  breeds: ['/api/racas', 'raças'],
  integrations: ['/api/integracoes', 'comunicações governamentais'],
}

export const emptyData = {
  tutors: [], animals: [], appointments: [], vaccines: [], vets: [], integrations: [],
  species: [], breeds: [], errors: [], integrationsAvailable: false,
}

async function request(path, { method = 'GET', body, timeout = 8000, token = storedToken() } = {}) {
  let response
  try {
    response = await fetch(`${apiBase}${path}`, {
      method,
      headers: {
        Accept: 'application/json',
        ...(body ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(timeout),
    })
  } catch (error) {
    if (error.name === 'TimeoutError') throw new Error('A API da clínica demorou para responder.')
    throw new Error('Não foi possível conectar à API da clínica.')
  }
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    let message = `A API respondeu com HTTP ${response.status}.`
    if (typeof data?.detail === 'string') message = data.detail
    if (Array.isArray(data?.detail)) {
      message = data.detail.map(({ loc, msg }) => `${loc?.slice(1).join('.') || 'Dados'}: ${msg}`).join(' · ')
    }
    if (token && token === storedToken() && [401, 403].includes(response.status)) {
      clearToken()
      window.dispatchEvent(new CustomEvent(sessionEndedEvent, { detail: message }))
    }
    throw Object.assign(new Error(message), { status: response.status })
  }
  return data
}

export const apiAuth = {
  hasSession: () => Boolean(storedToken()),
  profile: () => request('/api/auth/me'),
  async login(email, senha) {
    const result = await request('/api/auth/login', { method: 'POST', body: { email, senha }, token: null })
    const token = result?.access_token
    if (typeof token !== 'string' || !token) throw new Error('A API não retornou um token de acesso.')
    const profile = await request('/api/auth/me', { token })
    sessionStorage.setItem(accessTokenKey, token)
    return profile
  },
  async logout() {
    try {
      await request('/api/auth/logout', { method: 'POST' })
    } finally {
      clearToken()
    }
  },
  requestPasswordConfirmation: (email) => request('/api/auth/solicitar-confirmacao', { method: 'POST', body: { email }, token: null }),
  confirmPassword: (token) => request('/api/auth/confirmar-senha', { method: 'POST', body: { token }, token: null }),
}

const operationNames = {
  cadastro_animal: 'Cadastro de animal',
  atualizacao_animal: 'Atualização de animal',
  vacina_antirrabica: 'Vacina antirrábica',
}

function integrationRecord(item) {
  return {
    id: item.id, animal: item.animal, vacina_id: item.vacina_id,
    tipo: operationNames[item.tipo_operacao] ?? item.tipo_operacao,
    situacao: item.situacao, tentativas: item.tentativas, protocolo: item.protocolo_externo,
    data: item.data_solicitacao, resposta: item.data_resposta, erro: item.mensagem_erro,
  }
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
      if (key === 'integrations') {
        // Releases before PR #3 do not expose this router.
        if (result.reason?.status === 404) return
        data.integrationsAvailable = true
      }
      if (result.status === 'fulfilled' && Array.isArray(result.value)) {
        data[key] = key === 'integrations' ? result.value.map(integrationRecord) : result.value
      } else {
        data.errors.push(`Não foi possível carregar ${label}. ${result.reason?.message ?? 'Resposta inesperada.'}`)
      }
    })
    return data
  },
  saveTutor({ endereco: _endereco, ...body }, id) {
    if (id) delete body.cpf
    return save('tutors', body, id)
  },
  createAddress({ ibge, ...address }) {
    return request('/api/enderecos', { method: 'POST', body: { ...address, codigo_ibge: ibge || null } })
  },
  saveAnimal: (body, id) => save('animals', body, id),
  saveVeterinarian: (body) => save('vets', body),
  saveAppointment: (body, id) => save('appointments', body, id),
  listAnimalAppointments: (id) => listAnimalRecords('appointments', id),
  cancelAppointment: (id) => request(`/api/consultas/${id}`, { method: 'DELETE' }),
  saveVaccine: (body, id) => save('vaccines', body, id),
  listAnimalVaccines: (id) => listAnimalRecords('vaccines', id),
  cancelVaccine: (id) => request(`/api/vacinas/${id}`, { method: 'DELETE' }),
  async listMicrochips(animalId) {
    const records = await request(`/api/animais/${animalId}/microchip/historico`)
    if (!Array.isArray(records)) throw new Error('A API retornou um histórico de microchip inválido.')
    return records.map((record) => ({
      codigo: record.codigo_microchip, data_implantacao: record.data_implantacao,
      data_vinculo: record.data_vinculo, veterinario: record.veterinario?.nome_completo,
      atual: record.situacao === 'ativo',
    }))
  },
  linkChip: (id, input, replace) => request(`/api/animais/${id}/microchip${replace ? '/substituir' : ''}`, { method: 'POST', body: input }),
  async retryIntegration(id) {
    return integrationRecord(await request(`/api/integracoes/${id}/reenviar`, { method: 'POST', timeout: 20000 }))
  },
  deactivate: (name, id) => request(`${endpoints[name][0]}/${id}`, { method: 'DELETE' }),
}

export const repository = isDemo ? demoRepository : apiRepository
