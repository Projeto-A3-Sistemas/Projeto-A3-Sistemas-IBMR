import { useId, useState } from 'react'
import { appointmentDay, digits, formatTime, localDate, validCpf } from '../clinic/format.js'
import { isDemo, repository } from '../clinic/repository.js'
import { Button, Modal } from './ui.jsx'

const ufOptions = 'AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO'.split(' ')
const active = (records) => records.filter((record) => record.situacao === 'ativo')
const options = (records, label) => records.map((record) => [record.id, record[label]])

function Field({ label, ...props }) {
  const id = useId()
  return <div className="field">
    <label htmlFor={id} className={props.required ? 'required' : undefined}>{label}</label>
    <input id={id} {...props} />
  </div>
}

function Select({ label, items, optional, placeholder = 'Selecione', ...props }) {
  const id = useId()
  return <div className="field">
    <label htmlFor={id} className={props.required ? 'required' : undefined}>{label}</label>
    <select id={id} {...props}>
      <option value="" disabled={!optional}>{placeholder}</option>
      {items.map(([value, name]) => <option key={value} value={value}>{name}</option>)}
    </select>
  </div>
}

function Notes({ label, ...props }) {
  const id = useId()
  return <div className="field field--wide"><label htmlFor={id}>{label}</label><textarea id={id} rows="2" {...props} /></div>
}

function Editor({ title, onClose, onSave, read, children }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function submit(event) {
    event.preventDefault()
    if (busy) return
    const fields = Object.fromEntries(new FormData(event.currentTarget))
    setError('')
    setBusy(true)
    try {
      await onSave(read(fields))
      onClose()
    } catch (failure) {
      setError(failure.message)
      setBusy(false)
    }
  }

  return <Modal title={title} onClose={onClose} busy={busy}>
    <form onSubmit={submit} className="editor">
      <fieldset disabled={busy}><div className="fields">{children}</div></fieldset>
      {error && <div className="notice notice--error" role="alert">{error}</div>}
      <div className="modal-actions">
        <Button variant="secondary" onClick={onClose} disabled={busy}>Cancelar</Button>
        <Button type="submit" disabled={busy}>{busy ? 'Salvando…' : 'Salvar'}</Button>
      </div>
    </form>
  </Modal>
}

function TutorEditor({ record, data, onClose, onSave }) {
  const [address, setAddress] = useState(record?.endereco ?? {})
  const [cepMessage, setCepMessage] = useState('')
  const [lookingUp, setLookingUp] = useState(false)
  const addresses = [...new Map(data.tutors.filter((tutor) => tutor.endereco).map((tutor) => [tutor.endereco.id, tutor.endereco])).values()]
  const setAddressField = (name, value) => setAddress((current) => ({ ...current, [name]: value }))

  async function lookup() {
    const currentCep = digits(address.cep)
    if (currentCep.length !== 8) {
      setCepMessage('Informe um CEP de 8 dígitos.')
      return
    }
    setLookingUp(true)
    setCepMessage('')
    try {
      const result = await repository.lookupCep(currentCep)
      setAddress((current) => digits(current.cep) === currentCep ? { ...current, ...result } : current)
      setCepMessage('Endereço localizado na demonstração.')
    } catch (error) {
      setCepMessage(error.message)
    } finally {
      setLookingUp(false)
    }
  }

  function read(fields) {
    const cpf = record?.cpf ?? digits(fields.cpf)
    if (fields.nome_completo.trim().length < 3) throw new Error('Informe o nome completo do tutor.')
    if (!validCpf(cpf) && !record) throw new Error('Informe um CPF válido.')
    if (fields.data_nascimento >= localDate()) throw new Error('A data de nascimento deve estar no passado.')
    if (digits(fields.telefone).length < 10) throw new Error('Informe um telefone com DDD.')
    if (isDemo && digits(address.cep).length !== 8) throw new Error('Informe um CEP de 8 dígitos.')
    return {
      nome_completo: fields.nome_completo.trim(), cpf, data_nascimento: fields.data_nascimento,
      email: fields.email.trim(), telefone: digits(fields.telefone),
      ...(isDemo ? { endereco: { ...address, cep: digits(address.cep) } } : { endereco_id: Number(fields.endereco_id) }),
    }
  }

  return <Editor title={record ? 'Editar tutor' : 'Novo tutor'} onClose={onClose} onSave={onSave} read={read}>
    <Field name="nome_completo" label="Nome completo" required minLength={3} maxLength={150} defaultValue={record?.nome_completo} />
    <Field name="cpf" label="CPF" inputMode="numeric" maxLength={14} required={!record} readOnly={Boolean(record)} defaultValue={record?.cpf} />
    <Field name="data_nascimento" label="Nascimento" type="date" max={localDate()} required defaultValue={record?.data_nascimento} />
    <Field name="email" label="E-mail" type="email" required defaultValue={record?.email} />
    <Field name="telefone" label="Telefone" type="tel" required maxLength={20} defaultValue={record?.telefone} />
    <h3 className="field--wide section-label">Endereço</h3>
    {isDemo ? <>
      <div className="field--wide address-lookup">
        <Field label="CEP" name="cep" inputMode="numeric" maxLength={9} required value={address.cep ?? ''} onChange={(event) => { setAddressField('cep', event.target.value); setCepMessage('') }} />
        <Button variant="secondary" disabled={lookingUp} onClick={lookup}>{lookingUp ? 'Consultando…' : 'Consultar CEP'}</Button>
      </div>
      {cepMessage && <p className="field--wide muted" role="status">{cepMessage}</p>}
      {[
        ['logradouro', 'Logradouro', true], ['numero', 'Número', true], ['complemento', 'Complemento', false],
        ['bairro', 'Bairro', true], ['cidade', 'Cidade', true], ['ibge', 'Código IBGE', false],
      ].map(([name, label, required]) => <Field key={name} label={label} name={name} required={required} value={address[name] ?? ''} onChange={(event) => setAddressField(name, event.target.value)} />)}
      <Select label="UF" name="uf" required items={ufOptions.map((uf) => [uf, uf])} value={address.uf ?? ''} onChange={(event) => setAddressField('uf', event.target.value)} />
    </> : <>
      <p className="field--wide muted">A API atual aceita apenas endereços já cadastrados. A consulta de CEP ainda está em desenvolvimento.</p>
      <Select label="Endereço existente" name="endereco_id" required defaultValue={record?.endereco_id ?? ''} items={addresses.map((item) => [item.id, `${item.logradouro}, ${item.numero} · ${item.cidade}/${item.uf}`])} />
    </>}
  </Editor>
}

function AnimalEditor({ record, data, onClose, onSave }) {
  const [species, setSpecies] = useState(String(record?.especie?.id ?? ''))
  const [breed, setBreed] = useState(String(record?.raca?.id ?? ''))

  function read(fields) {
    if (!fields.nome.trim()) throw new Error('Informe o nome do animal.')
    if (!fields.data_nascimento && !fields.idade_estimada_meses) throw new Error('Informe o nascimento ou a idade estimada em meses.')
    return {
      nome: fields.nome.trim(), tutor_id: Number(fields.tutor_id), especie_id: Number(species), raca_id: breed ? Number(breed) : null,
      sexo: fields.sexo, data_nascimento: fields.data_nascimento || null,
      idade_estimada_meses: fields.idade_estimada_meses === '' ? null : Number(fields.idade_estimada_meses),
      cor: fields.cor.trim() || null, peso_atual: fields.peso_atual ? Number(fields.peso_atual) : null,
    }
  }

  return <Editor title={record ? 'Editar ficha' : 'Novo animal'} onClose={onClose} onSave={onSave} read={read}>
    <Field label="Nome do animal" name="nome" required maxLength={100} defaultValue={record?.nome} />
    <Select label="Tutor" name="tutor_id" required defaultValue={record?.tutor?.id ?? ''} items={options(active(data.tutors), 'nome_completo')} />
    <Select label="Espécie" name="especie_id" required value={species} items={options(data.species, 'nome')} onChange={(event) => { setSpecies(event.target.value); setBreed('') }} />
    <Select label="Raça" name="raca_id" optional placeholder="Sem raça definida" value={breed} items={options(data.breeds.filter((item) => item.especie_id === Number(species)), 'nome')} onChange={(event) => setBreed(event.target.value)} />
    <Select label="Sexo" name="sexo" required defaultValue={record?.sexo ?? ''} items={ [['F', 'Fêmea'], ['M', 'Macho']] } />
    <Field label="Pelagem / cor" name="cor" maxLength={50} defaultValue={record?.cor ?? ''} />
    <Field label="Nascimento" name="data_nascimento" type="date" max={localDate()} defaultValue={record?.data_nascimento ?? ''} />
    <Field label="Idade estimada em meses" name="idade_estimada_meses" type="number" min="0" max="600" defaultValue={record?.idade_estimada_meses ?? ''} />
    <Field label="Peso atual (kg)" name="peso_atual" type="number" min="0.01" max="9999.99" step="0.01" defaultValue={record?.peso_atual ?? ''} />
  </Editor>
}

function ClinicalFields({ data, animalId, record, fixedAnimal = false }) {
  return <>
    {fixedAnimal ? <>
      <Field label="Animal" readOnly value={record.animal.nome} />
      <input type="hidden" name="animal_id" value={record.animal.id} />
    </> : <Select label="Animal" name="animal_id" required defaultValue={record?.animal?.id ?? animalId ?? ''} items={options(active(data.animals), 'nome')} />}
    <Select label="Veterinário" name="veterinario_id" required defaultValue={record?.veterinario?.id ?? (data.vets.length === 1 ? data.vets[0].id : '')} items={options(active(data.vets), 'nome_completo')} />
  </>
}

function AppointmentEditor({ record, animalId, day, data, onClose, onSave }) {
  function read(fields) {
    if (fields.motivo.trim().length < 3) throw new Error('Informe o motivo do atendimento.')
    return {
      ...fields, motivo: fields.motivo.trim(), data_hora: `${fields.data_hora}:00`,
      animal_id: Number(fields.animal_id), veterinario_id: Number(fields.veterinario_id),
      peso: fields.peso ? Number(fields.peso) : null, temperatura: fields.temperatura ? Number(fields.temperatura) : null,
    }
  }
  const dateTime = record?.data_hora ? `${appointmentDay(record.data_hora)}T${formatTime(record.data_hora)}` : (day ? `${day}T09:00` : undefined)

  return <Editor title={record ? 'Editar consulta' : 'Nova consulta'} onClose={onClose} onSave={onSave} read={read}>
    <ClinicalFields data={data} record={record} animalId={animalId} />
    <Field label="Data e hora" name="data_hora" type="datetime-local" required defaultValue={dateTime} />
    <Select label="Situação" name="situacao" required defaultValue={record?.situacao ?? 'agendada'} items={ [['agendada', 'Agendada'], ['realizada', 'Realizada'], ['cancelada', 'Cancelada'], ['nao_compareceu', 'Não compareceu']] } />
    <Field label="Motivo" name="motivo" required minLength={3} maxLength={200} defaultValue={record?.motivo} />
    <Field label="Peso (kg)" name="peso" type="number" min="0.01" max="9999.99" step="0.01" defaultValue={record?.peso ?? ''} />
    <Field label="Temperatura (°C)" name="temperatura" type="number" min="30" max="45" step="0.1" defaultValue={record?.temperatura ?? ''} />
    {[
      ['anamnese', 'Anamnese'], ['sintomas', 'Sintomas'], ['diagnostico', 'Diagnóstico'],
      ['tratamento', 'Tratamento'], ['prescricao', 'Prescrição'], ['observacoes', 'Observações'],
    ].map(([name, label]) => <Notes key={name} label={label} name={name} defaultValue={record?.[name] ?? ''} />)}
  </Editor>
}

function VaccineEditor({ record, animalId, data, onClose, onSave }) {
  const [status, setStatus] = useState(record?.situacao ?? 'aplicada')
  const [rabies, setRabies] = useState(record?.antirrabica ? '1' : '0')
  const alreadyApplied = record?.situacao === 'aplicada'

  function read(fields) {
    const applicationDate = status === 'aplicada' ? fields.data_aplicacao : null
    if (rabies === '0' && /antirr/i.test(fields.tipo_vacina)) throw new Error('Selecione a classificação antirrábica para este tipo de vacina.')
    if (applicationDate && fields.validade_lote < applicationDate) throw new Error('O lote estava vencido na data da aplicação.')
    if (applicationDate && fields.data_proxima_dose && fields.data_proxima_dose <= applicationDate) {
      throw new Error('A próxima dose deve ser posterior à aplicação.')
    }
    return {
      animal_id: Number(fields.animal_id), veterinario_id: Number(fields.veterinario_id),
      nome_vacina: fields.nome_vacina.trim(), fabricante: fields.fabricante.trim(),
      numero_lote: fields.numero_lote.trim(), dose: fields.dose.trim(), validade_lote: fields.validade_lote, situacao: status,
      antirrabica: rabies === '1', tipo_vacina: rabies === '1' ? 'Antirrábica' : fields.tipo_vacina.trim(),
      data_aplicacao: applicationDate, data_proxima_dose: fields.data_proxima_dose || null,
      via_aplicacao: fields.via_aplicacao || null, observacoes: fields.observacoes || null,
    }
  }

  return <Editor title={record ? 'Editar vacina' : 'Registrar vacina'} onClose={onClose} onSave={onSave} read={read}>
    <ClinicalFields data={data} record={record} animalId={animalId} fixedAnimal={alreadyApplied} />
    <Field label="Nome da vacina" name="nome_vacina" required minLength={2} maxLength={100} defaultValue={record?.nome_vacina} />
    {alreadyApplied ? <Field label="Classificação" readOnly value={rabies === '1' ? 'Antirrábica' : 'Não antirrábica'} /> :
      <Select label="Classificação" name="classificacao" required value={rabies} items={ [['0', 'Não antirrábica'], ['1', 'Antirrábica']] } onChange={(event) => setRabies(event.target.value)} />}
    {rabies === '0' && <Field label="Tipo da vacina" name="tipo_vacina" required minLength={2} maxLength={50} defaultValue={record?.antirrabica ? '' : record?.tipo_vacina} />}
    <Field label="Fabricante" name="fabricante" required minLength={2} maxLength={100} defaultValue={record?.fabricante} />
    <Field label="Lote" name="numero_lote" required maxLength={50} defaultValue={record?.numero_lote} />
    <Field label="Validade do lote" name="validade_lote" type="date" required defaultValue={record?.validade_lote} />
    <Field label="Dose" name="dose" required maxLength={30} defaultValue={record?.dose} />
    <Field label="Via de aplicação" name="via_aplicacao" maxLength={30} defaultValue={record?.via_aplicacao ?? ''} />
    <Select label="Situação" name="situacao" required value={status} items={alreadyApplied ? [['aplicada', 'Aplicada']] : [['aplicada', 'Aplicada'], ['agendada', 'Agendada'], ['cancelada', 'Cancelada']]} onChange={(event) => setStatus(event.target.value)} />
    {status === 'aplicada' && <Field label="Data da aplicação" name="data_aplicacao" type="date" required max={localDate()} defaultValue={record?.data_aplicacao ?? localDate()} />}
    <Field label="Próxima dose" name="data_proxima_dose" type="date" defaultValue={record?.data_proxima_dose ?? ''} />
    <Notes label="Observações" name="observacoes" defaultValue={record?.observacoes ?? ''} />
  </Editor>
}

function ChipEditor({ record, onClose, onSave }) {
  return <Editor title={record.chips?.length ? 'Substituir microchip' : 'Vincular microchip'} onClose={onClose} onSave={onSave} read={({ codigo }) => {
    const value = digits(codigo)
    if (value.length !== 15) throw new Error('Informe os 15 dígitos do microchip.')
    return value
  }}>
    <Field label="Código RFID" name="codigo" required inputMode="numeric" maxLength={19} placeholder="000 000 000 000 000" />
    <p className="field--wide muted">O histórico de vínculos fica disponível na ficha de {record.nome}.</p>
  </Editor>
}

const editors = { tutor: TutorEditor, animal: AnimalEditor, consulta: AppointmentEditor, vacina: VaccineEditor, microchip: ChipEditor }

export function ClinicEditor({ editor, data, onClose, onSave }) {
  const Form = editors[editor.kind]
  return <Form record={editor.record} animalId={editor.animalId} day={editor.day} data={data} onClose={onClose} onSave={onSave} />
}
