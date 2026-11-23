import { demoAddresses, demoVeterinarian, seed } from './demoData.js'
import { digits, localDate } from './format.js'

const storageKey = 'clinica-veterinaria:demo:v1'
const nextId = (items) => Math.max(0, ...items.map(({ id }) => id)) + 1
const byId = (items, id) => items.find((item) => item.id === Number(id))
const ref = (item) => ({ id: item.id, nome: item.nome })
const personRef = (item) => ({ id: item.id, nome_completo: item.nome_completo })

function read() {
  try {
    const saved = localStorage.getItem(storageKey)
    if (saved) return JSON.parse(saved)
  } catch {
    // A fresh copy keeps the demo available when storage cannot be read.
  }
  return structuredClone(seed)
}

function commit(data, result) {
  localStorage.setItem(storageKey, JSON.stringify(data))
  return result
}

function put(items, entry) {
  const index = items.findIndex(({ id }) => id === entry.id)
  if (index < 0) items.push(entry)
  else items[index] = entry
}

function enqueue(data, animal, tipo, vacinaId = null) {
  if (vacinaId && data.integrations.some((item) => item.vacina_id === vacinaId)) return
  data.integrations.unshift({
    id: nextId(data.integrations),
    animal: ref(animal),
    vacina_id: vacinaId,
    tipo,
    situacao: 'pendente',
    data: localDate(),
    tentativas: 0,
    erro: null,
    protocolo: null,
  })
}

export const demoRepository = {
  async load() {
    return { ...read(), errors: [] }
  },

  async lookupCep(cep) {
    const result = demoAddresses[digits(cep)]
    if (!result) throw new Error('CEP indisponível na demonstração. Preencha o endereço manualmente.')
    const { logradouro, bairro, cidade, uf, ibge } = result
    return { logradouro, bairro, cidade, uf, ibge }
  },

  async saveTutor(input, id) {
    const data = read()
    const current = byId(data.tutors, id)
    if (data.tutors.some((item) => item.id !== id && item.cpf === input.cpf)) {
      throw new Error('Já existe um tutor com este CPF.')
    }
    const addressId = current?.endereco_id ?? nextId(data.tutors.map((item) => ({ id: item.endereco_id })))
    const tutor = { ...input, id: id ?? nextId(data.tutors), cpf: current?.cpf ?? input.cpf, endereco_id: addressId, endereco: { ...input.endereco, id: addressId }, situacao: current?.situacao ?? 'ativo' }
    put(data.tutors, tutor)
    for (const animal of data.animals) {
      if (animal.tutor.id === tutor.id) animal.tutor = personRef(tutor)
    }
    return commit(data, tutor)
  },

  async saveAnimal(input, id) {
    const data = read()
    const current = byId(data.animals, id)
    const { tutor_id, especie_id, raca_id, ...fields } = input
    const tutor = byId(data.tutors, tutor_id)
    const species = byId(data.species, especie_id)
    const breed = byId(data.breeds, raca_id)
    if (!tutor || tutor.situacao !== 'ativo') throw new Error('Selecione um tutor ativo.')
    if (!species || (raca_id && breed?.especie_id !== species.id)) throw new Error('Selecione uma espécie e uma raça compatíveis.')
    const animal = {
      ...current, ...fields, id: id ?? nextId(data.animals), tutor: personRef(tutor),
      especie: ref(species), raca: breed ? ref(breed) : null, situacao: current?.situacao ?? 'ativo', chips: current?.chips ?? [],
    }
    put(data.animals, animal)
    for (const item of [...data.appointments, ...data.vaccines, ...data.integrations]) {
      if (item.animal.id === animal.id) item.animal = ref(animal)
    }
    return commit(data, animal)
  },

  async saveAppointment(input, id) {
    const data = read()
    const { animal_id, veterinario_id, ...fields } = input
    const animal = byId(data.animals, animal_id)
    const veterinarian = byId(data.vets, veterinario_id)
    if (animal?.situacao !== 'ativo' || veterinarian?.situacao !== 'ativo') throw new Error('Selecione um animal e um veterinário ativos.')
    const record = { ...fields, id: id ?? nextId(data.appointments), animal: ref(animal), veterinario: personRef(veterinarian) }
    put(data.appointments, record)
    return commit(data, record)
  },

  async saveVaccine(input, id) {
    const data = read()
    const { animal_id, veterinario_id, ...fields } = input
    const animal = byId(data.animals, animal_id)
    const veterinarian = byId(data.vets, veterinario_id)
    if (animal?.situacao !== 'ativo' || veterinarian?.situacao !== 'ativo') throw new Error('Selecione um animal e um veterinário ativos.')
    if (byId(data.vaccines, id)?.situacao === 'aplicada' && fields.situacao === 'cancelada') {
      throw new Error('Uma vacina já aplicada não pode ser cancelada.')
    }
    const record = { ...fields, id: id ?? nextId(data.vaccines), animal: ref(animal), veterinario: personRef(veterinarian) }
    put(data.vaccines, record)
    if (record.antirrabica && record.situacao === 'aplicada') enqueue(data, animal, 'Vacina antirrábica', record.id)
    return commit(data, record)
  },

  async deactivate(resource, id) {
    const data = read()
    const record = byId(data[resource], id)
    record.situacao = 'inativo'
    return commit(data, record)
  },

  async linkChip(id, codigo) {
    const data = read()
    const animal = byId(data.animals, id)
    if (animal?.situacao !== 'ativo') throw new Error('Selecione um animal ativo.')
    if (data.animals.some((item) => item.chips.some((chip) => chip.codigo === codigo))) {
      throw new Error('Este código de microchip já está registrado.')
    }
    const type = animal.chips.length ? 'Atualização de animal' : 'Cadastro de animal'
    for (const chip of animal.chips) chip.atual = false
    animal.chips.unshift({ codigo, data_vinculo: localDate(), veterinario: demoVeterinarian.nome_completo, atual: true })
    enqueue(data, animal, type)
    return commit(data, animal)
  },

  async retryIntegration(id) {
    const data = read()
    const record = byId(data.integrations, id)
    if (record.situacao === 'confirmada') return record
    const animal = byId(data.animals, record.animal.id)
    if (!animal?.chips.some((chip) => chip.atual)) throw new Error('Vincule um microchip antes de reenviar a comunicação.')
    record.tentativas += 1
    record.situacao = 'confirmada'
    record.protocolo = `SIM-${record.data.slice(0, 4)}-${String(record.id).padStart(4, '0')}`
    record.erro = null
    return commit(data, record)
  },
}
