import { useEffect, useState } from 'react'
import { demoDate } from '../clinic/demoData.js'
import { appointmentDay, digits, formatChip, formatCpf, formatDate, formatPhone, formatTime, localDate, matches } from '../clinic/format.js'
import { isDemo, repository } from '../clinic/repository.js'
import { Button, DataTable, DateText, Icon, KeyValues, PageHeader, PetAvatar, Search, Status, Tabs } from './ui.jsx'

const find = (records, id) => records.find((record) => record.id === Number(id))
const activeStatus = (animal) => animal.situacao === 'ativo' ? (animal.sexo === 'F' ? 'Ativa' : 'Ativo') : (animal.sexo === 'F' ? 'Inativa' : 'Inativo')
const animalDescription = (animal) => [animal.especie?.nome, animal.raca?.nome ?? 'Sem raça definida'].filter(Boolean).join(' · ')
const animalPath = (id, tab) => `#/animais/${id}${tab ? `?aba=${tab}` : ''}`
const integrationPath = (id) => `#/integracoes/${id}`

export function TutorsPage({ data, edit, deactivate }) {
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('')
  const [selectedId, select] = useState(null)
  const tutors = data.tutors.filter((tutor) => (
    (!status || tutor.situacao === status) &&
    (matches(query, tutor.nome_completo, formatCpf(tutor.cpf)) || (digits(query) && tutor.cpf.includes(digits(query))))
  ))
  const selected = find(tutors, selectedId) ?? tutors[0]
  const columns = [
    { key: 'name', label: 'Tutor', render: (row) => <strong>{row.nome_completo}</strong> },
    { key: 'cpf', label: 'CPF', render: (row) => formatCpf(row.cpf) },
    { key: 'phone', label: 'Telefone', render: (row) => formatPhone(row.telefone) },
    { key: 'status', label: 'Situação', render: (row) => <Status value={row.situacao} /> },
    { key: 'action', label: '', render: (row) => <button type="button" className="text-link" aria-label={`Ver cadastro de ${row.nome_completo}`} aria-pressed={selected?.id === row.id} onClick={() => select(row.id)}>Ver cadastro</button> },
  ]

  return <>
    <PageHeader title="Tutores" description="Cadastros dos responsáveis pelos animais.">
      <Button icon="plus" onClick={() => edit('tutor')}>Novo tutor</Button>
    </PageHeader>
    <section className="panel directory-panel">
      <div className="toolbar">
        <Search label="Buscar por nome ou CPF" value={query} onChange={setQuery} />
        <select aria-label="Filtrar tutores por situação" value={status} onChange={(event) => setStatus(event.target.value)}>
          <option value="">Todos os status</option><option value="ativo">Ativos</option><option value="inativo">Inativos</option>
        </select>
      </div>
      <DataTable columns={columns} rows={tutors} label="Tutores cadastrados" selected={selected?.id} empty="Nenhum tutor encontrado." />
      {selected && <section className="tutor-detail" aria-labelledby="tutor-detail-title">
        <div className="section-header">
          <div><h2 id="tutor-detail-title">Cadastro de {selected.nome_completo.split(' ')[0]}</h2><p className="muted">{selected.email}</p></div>
          <div className="actions">
            {selected.situacao === 'ativo' && <Button variant="quiet" onClick={() => deactivate('tutors', selected)}>Inativar</Button>}
            <Button variant="secondary" icon="edit" onClick={() => edit('tutor', selected)}>Editar cadastro</Button>
          </div>
        </div>
        <h3>Endereço</h3>
        {selected.endereco ? <KeyValues items={[
          ['CEP', digits(selected.endereco.cep).replace(/^(\d{5})(\d{3})$/, '$1-$2')],
          ['Logradouro', `${selected.endereco.logradouro}, ${selected.endereco.numero}`],
          ['Cidade / UF', `${selected.endereco.cidade} / ${selected.endereco.uf}`],
          ['Bairro', selected.endereco.bairro],
        ]} /> : <p className="muted">Endereço indisponível.</p>}
      </section>}
    </section>
  </>
}

export function AnimalsPage({ data, edit }) {
  const [query, setQuery] = useState('')
  const [species, setSpecies] = useState('')
  const animals = data.animals.filter((animal) => (
    (!species || animal.especie?.id === Number(species)) && matches(query, animal.nome, animal.tutor?.nome_completo)
  ))
  const columns = [
    { key: 'name', label: 'Animal', render: (animal) => <div className="animal-cell"><PetAvatar animal={animal} /><div><strong>{animal.nome}</strong><small>{animalDescription(animal)}</small></div></div> },
    { key: 'tutor', label: 'Tutor', render: (animal) => animal.tutor?.nome_completo ?? '—' },
    { key: 'chip', label: 'Microchip RFID', render: (animal) => isDemo ? formatChip(animal.chips?.find((chip) => chip.atual)?.codigo) :
      data.integrationsAvailable ? <a className="text-link" href={animalPath(animal.id, 'microchip')}>Ver vínculo</a> : 'Indisponível' },
    { key: 'status', label: 'Situação', render: (animal) => <Status value={animal.situacao} label={activeStatus(animal)} /> },
    { key: 'action', label: '', render: (animal) => <a className="button button--secondary" href={animalPath(animal.id)} aria-label={`Abrir ficha de ${animal.nome}`}>Abrir ficha</a> },
  ]
  return <>
    <PageHeader title="Animais"><Button icon="plus" onClick={() => edit('animal')} disabled={!data.species.length || !data.tutors.some((item) => item.situacao === 'ativo')}>Novo animal</Button></PageHeader>
    <section className="panel directory-panel">
      <div className="toolbar">
        <Search label="Buscar por animal ou tutor" value={query} onChange={setQuery} />
        <select aria-label="Filtrar animais por espécie" value={species} onChange={(event) => setSpecies(event.target.value)}>
          <option value="">Todas as espécies</option>
          {data.species.map((item) => <option key={item.id} value={item.id}>{item.nome}</option>)}
        </select>
      </div>
      <DataTable columns={columns} rows={animals} label="Animais cadastrados" empty="Nenhum animal encontrado." />
    </section>
  </>
}

function AppointmentDetails({ record, data, edit, cancelAppointment, showAnimalLink = true }) {
  if (!record) return <p className="empty">Selecione uma consulta para ver os detalhes.</p>
  const animal = find(data.animals, record.animal.id)
  return <>
    <div className="section-header">
      <h2>Consulta de {record.animal.nome}</h2>
      <Status value={record.situacao} />
    </div>
    <div className="detail-person"><strong>{record.veterinario?.nome_completo}</strong>{animal?.tutor && <p className="muted">{animal.tutor.nome_completo} · Tutor responsável</p>}</div>
    <KeyValues items={[
      ['Data e hora', `${formatDate(appointmentDay(record.data_hora))} às ${formatTime(record.data_hora)}`],
      ['Motivo', record.motivo],
      ['Peso', record.peso ? `${Number(record.peso).toLocaleString('pt-BR')} kg` : null],
      ['Temperatura', record.temperatura ? `${Number(record.temperatura).toLocaleString('pt-BR')} °C` : null],
      ['Anamnese', record.anamnese], ['Sintomas', record.sintomas], ['Diagnóstico', record.diagnostico],
      ['Tratamento', record.tratamento], ['Prescrição', record.prescricao], ['Observações', record.observacoes],
    ].filter(([, value]) => value)} />
    <div className="actions">
      {record.situacao === 'agendada' && <Button onClick={() => edit('consulta', record, { completeAppointment: true })}>Registrar atendimento</Button>}
      {showAnimalLink && <a className="button button--secondary" href={animalPath(record.animal.id, 'consultas')}>Abrir ficha do animal</a>}
      <Button variant="quiet" icon="edit" onClick={() => edit('consulta', record)}>Editar consulta</Button>
      {record.situacao === 'agendada' && <Button variant="secondary" onClick={() => cancelAppointment(record)}>Cancelar consulta</Button>}
    </div>
  </>
}

function AppointmentList({ records, selected, select, showDates = false }) {
  if (!records.length) return <p className="empty">Nenhuma consulta encontrada.</p>
  return <div className="queue">
    {records.map((record) => <button key={record.id} type="button" className="queue-row appointment-row" aria-pressed={selected?.id === record.id} onClick={() => select(record.id)}>
      <strong>{showDates ? `${formatDate(appointmentDay(record.data_hora))} · ` : ''}{formatTime(record.data_hora)} · {record.animal.nome}</strong>
      <span>{record.motivo}</span><Status value={record.situacao} />
    </button>)}
  </div>
}

export function ConsultationsPage({ data, edit, cancelAppointment }) {
  const [day, setDay] = useState(isDemo ? demoDate : localDate())
  const [selectedId, select] = useState(null)
  const records = data.appointments.filter((record) => appointmentDay(record.data_hora) === day)
    .sort((a, b) => formatTime(a.data_hora).localeCompare(formatTime(b.data_hora)))
  const selected = find(records, selectedId) ?? records[0]
  return <>
    <PageHeader title="Consultas"><Button icon="plus" onClick={() => edit('consulta', null, { day })} disabled={!data.animals.some((item) => item.situacao === 'ativo') || !data.vets.length}>Nova consulta</Button></PageHeader>
    <div className="date-strip"><div><Icon name="calendar" /><strong>{formatDate(day, true)}</strong></div>
      <input type="date" aria-label="Data da agenda" value={day} onChange={(event) => { if (event.target.value) setDay(event.target.value) }} />
    </div>
    <div className="split split--agenda">
      <section className="panel work-panel"><h2>Atendimentos do dia</h2><AppointmentList records={records} selected={selected} select={select} /></section>
      <section className="panel work-panel"><AppointmentDetails record={selected} data={data} edit={edit} cancelAppointment={cancelAppointment} /></section>
    </div>
  </>
}

function VaccineTable({ records, edit, cancelVaccine, showAnimal = true, empty = 'Nenhum registro de vacinação encontrado.' }) {
  const columns = [
    ...(showAnimal ? [{ key: 'animal', label: 'Animal', render: (record) => <a className="text-link" href={animalPath(record.animal.id, 'vacinas')}>{record.animal.nome}</a> }] : []),
    { key: 'name', label: 'Vacina', render: (record) => <strong>{record.nome_vacina}</strong> },
    { key: 'applied', label: 'Aplicação', render: (record) => <DateText value={record.data_aplicacao} /> },
    { key: 'next', label: 'Próxima dose', render: (record) => <DateText value={record.data_proxima_dose} /> },
    { key: 'status', label: 'Situação', render: (record) => <Status value={record.situacao} /> },
    { key: 'action', label: '', render: (record) => <div className="actions vaccine-actions">
      {record.situacao === 'agendada' && <button type="button" className="text-link" onClick={() => edit('vacina', record, { applyVaccine: true })}>Registrar aplicação</button>}
      <button type="button" className="text-link" onClick={() => edit('vacina', record)} aria-label={`Editar vacina ${record.nome_vacina} de ${record.animal.nome}`}>Editar</button>
      {record.situacao === 'agendada' && <button type="button" className="text-link" onClick={() => cancelVaccine(record)}>Cancelar agendamento</button>}
    </div> },
  ]
  return <DataTable columns={columns} rows={records} label="Registros de vacinação" empty={empty} />
}

export function VaccinesPage({ data, edit, cancelVaccine }) {
  const [tab, setTab] = useState('records')
  const [query, setQuery] = useState('')
  const records = data.vaccines.filter((record) => (
    matches(query, record.animal.nome, record.nome_vacina) &&
    (tab === 'records' || (record.situacao !== 'cancelada' && record.data_proxima_dose && record.data_proxima_dose >= localDate()))
  )).sort((a, b) => tab === 'records'
    ? (b.data_aplicacao ?? '').localeCompare(a.data_aplicacao ?? '') || b.id - a.id
    : a.data_proxima_dose.localeCompare(b.data_proxima_dose))
  const pending = data.integrations.find((item) => item.situacao === 'pendente' && records.some((vaccine) => vaccine.id === item.vacina_id))
  return <>
    <PageHeader title="Vacinas"><Button icon="plus" onClick={() => edit('vacina')} disabled={!data.animals.some((item) => item.situacao === 'ativo') || !data.vets.length}>Registrar vacina</Button></PageHeader>
    <section className="panel directory-panel vaccine-panel">
      <Tabs label="Visão de vacinação" value={tab} onChange={setTab} items={ [['records', 'Aplicações'], ['next', 'Próximas doses']] } />
      <Search label="Buscar por animal ou vacina" value={query} onChange={setQuery} />
      <VaccineTable records={records} edit={edit} cancelVaccine={cancelVaccine} empty={tab === 'next' ? 'Nenhuma próxima dose encontrada.' : undefined} />
      {pending && <div className="notice notice--warning vaccine-notice">
        <div><strong>{pending.animal.nome} · Comunicação antirrábica</strong><Status value={pending.situacao} /></div>
        <a className="button button--secondary" href={integrationPath(pending.id)}>Ver integração</a>
      </div>}
    </section>
  </>
}

export function IntegrationsPage({ data, selectedId, navigate, retry, refresh }) {
  const [status, setStatus] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const records = data.integrations.filter((record) => !status || record.situacao === status)
  const selected = find(records, selectedId) ?? records[0]
  const vaccine = selected ? find(data.vaccines, selected.vacina_id) : null
  async function confirmRetry() {
    if (busy) return
    setBusy(true)
    setError('')
    try {
      await retry(selected.id)
      setStatus('')
    } catch (failure) {
      setError(failure.message)
      if (failure.status === 409) await refresh()
    } finally {
      setBusy(false)
    }
  }
  return <>
    <PageHeader title="Integrações" description="API governamental simulada">
      {!isDemo && data.integrationsAvailable && <Button variant="secondary" disabled={busy} onClick={() => { setError(''); refresh() }}>Atualizar comunicações</Button>}
    </PageHeader>
    {!isDemo && !data.integrationsAvailable ? <section className="panel work-panel"><h2>Comunicações</h2><p className="muted">A versão da API em execução ainda não expõe as rotas de integração.</p></section> :
      <div className="split split--integrations">
        <section className="panel work-panel">
          <h2>Comunicações</h2>
          <Tabs label="Filtrar comunicações" value={status} onChange={(value) => { setStatus(value); setError('') }} items={ [['', 'Todas'], ['pendente', 'Pendentes'], ['enviada', 'Enviadas'], ['confirmada', 'Confirmadas'], ['falha', 'Com falha']] } />
          {records.length ? <div className="queue integration-queue">
            {records.map((record) => <button className="queue-row" key={record.id} type="button" aria-pressed={record.id === selected?.id} onClick={() => { navigate(integrationPath(record.id)); setError('') }}>
              <span><strong>{record.animal.nome}</strong><small>{record.tipo}</small></span><span><Status value={record.situacao} /><small>{formatDate(record.data)}</small></span>
            </button>)}
          </div> : <p className="empty">Nenhuma comunicação nesta situação.</p>}
        </section>
        <section className="panel work-panel integration-details" aria-label="Detalhes da comunicação">
          {selected ? <>
            <div className="section-header"><h2>{selected.vacina_id ? `Vacinação de ${selected.animal.nome}` : `${selected.tipo} · ${selected.animal.nome}`}</h2><Status value={selected.situacao} /></div>
            <KeyValues items={[
              ['Registro na clínica', vaccine ? `Aplicada em ${formatDate(vaccine.data_aplicacao)}` : `Registrado em ${formatDate(selected.data)}`],
              ['Protocolo', selected.protocolo ?? (selected.situacao === 'pendente' || selected.situacao === 'enviada' ? 'Aguardando confirmação' : 'Sem protocolo')],
              ['Tentativas', selected.tentativas],
              ...(selected.resposta ? [['Última resposta', formatDate(selected.resposta)]] : []),
            ]} />
            {selected.erro && <p className="notice notice--warning"><Icon name="clock" />{selected.erro}</p>}
            {error && <p className="notice notice--error" role="alert">{error}</p>}
            {['pendente', 'falha'].includes(selected.situacao) && <Button onClick={confirmRetry} disabled={busy}>{busy ? 'Reenviando…' : 'Reenviar comunicação'}</Button>}
            <a className="text-link" href={animalPath(selected.animal.id, selected.vacina_id ? 'vacinas' : 'microchip')}>Abrir ficha do animal</a>
          </> : <p className="empty">Selecione uma comunicação para ver os detalhes.</p>}
        </section>
      </div>}
  </>
}

function ChipHistory({ animal, edit, history, available, vets }) {
  const chip = history.items.find((item) => item.atual)
  const columns = [
    { key: 'codigo', label: 'Microchip RFID', render: (row) => <strong>{formatChip(row.codigo)}</strong> },
    { key: 'implantacao', label: 'Implantação', render: (row) => <DateText value={row.data_implantacao} /> },
    { key: 'date', label: 'Vínculo', render: (row) => <DateText value={row.data_vinculo} /> },
    { key: 'vet', label: 'Veterinário', render: (row) => row.veterinario },
    { key: 'status', label: 'Situação', render: (row) => <Status value={row.atual ? 'ativo' : 'inativo'} label={row.atual ? 'Atual' : 'Substituído'} /> },
  ]
  return <section className="panel work-panel">
    <div className="section-header"><h2>Histórico de microchip</h2>{available && <Button icon="chip" disabled={animal.situacao !== 'ativo' || !vets.some((vet) => vet.situacao === 'ativo') || history.loading || Boolean(history.error)} onClick={() => edit('microchip', animal, { replaceChip: Boolean(chip) })}>{chip ? 'Substituir microchip' : 'Vincular microchip'}</Button>}</div>
    {!available ? <p className="muted">A versão da API em execução ainda não expõe o vínculo de microchip.</p> :
      history.loading || history.error ? <HistoryFeedback history={history} /> :
      <DataTable rows={history.items} columns={columns} rowKey="codigo" label="Vínculos de microchip" empty="Nenhum microchip vinculado." />}
  </section>
}

function useAnimalHistory(animalId, records, list, enabled = !isDemo, demoItems = []) {
  const [history, setHistory] = useState(null)
  const [error, setError] = useState('')
  const [reload, setReload] = useState(0)

  useEffect(() => {
    if (!enabled || !animalId) return
    let current = true
    setError('')
    list(animalId).then((result) => {
      if (current) setHistory(result)
    }).catch((error) => {
      if (current) setError(error.message)
    })
    return () => { current = false }
  }, [animalId, records, list, reload, enabled])

  return {
    items: enabled ? history ?? [] : demoItems,
    loading: enabled && !history,
    error,
    retry: () => setReload((value) => value + 1),
  }
}

function HistoryFeedback({ history }) {
  if (history.error) return <div className="notice notice--error" role="alert">
    <p>Não foi possível carregar o histórico. {history.error}</p>
    <Button variant="secondary" onClick={history.retry}>Tentar novamente</Button>
  </div>
  return <p className="empty" role="status">Carregando histórico…</p>
}

function AnimalConsultations({ animal, data, edit, cancelAppointment }) {
  const [selectedId, select] = useState(null)
  const history = useAnimalHistory(animal.id, data.appointments, repository.listAnimalAppointments, !isDemo,
    isDemo ? data.appointments.filter((record) => record.animal.id === animal.id) : [])
  const records = [...history.items].sort((a, b) => new Date(b.data_hora) - new Date(a.data_hora))
  const selected = find(records, selectedId) ?? records[0]
  return <div className="split split--agenda">
    <section className="panel work-panel">
      <div className="section-header"><h2>Histórico de consultas</h2><Button icon="plus" disabled={animal.situacao !== 'ativo' || !data.vets.length} onClick={() => edit('consulta', null, { animalId: animal.id, day: isDemo ? demoDate : localDate() })}>Nova consulta</Button></div>
      {history.error || history.loading ? <HistoryFeedback history={history} /> :
        <AppointmentList records={records} selected={selected} select={select} showDates />}
    </section>
    <section className="panel work-panel"><AppointmentDetails record={history.error ? null : selected} data={data} edit={edit} cancelAppointment={cancelAppointment} showAnimalLink={false} /></section>
  </div>
}

function AnimalVaccines({ animal, data, edit, cancelVaccine }) {
  const history = useAnimalHistory(animal.id, data.vaccines, repository.listAnimalVaccines, !isDemo,
    isDemo ? data.vaccines.filter((record) => record.animal.id === animal.id) : [])
  const records = [...history.items]
    .sort((a, b) => (b.data_aplicacao ?? '').localeCompare(a.data_aplicacao ?? ''))
  const communication = data.integrations.find((record) => record.animal.id === animal.id && record.vacina_id && record.situacao === 'pendente')
    ?? data.integrations.find((record) => record.animal.id === animal.id && record.vacina_id)
  return <div className="split split--vaccine">
    <section className="panel work-panel">
      <div className="section-header"><h2>Histórico de vacinação</h2><Button icon="plus" disabled={animal.situacao !== 'ativo' || !data.vets.length} onClick={() => edit('vacina', null, { animalId: animal.id })}>Nova vacina</Button></div>
      {history.error || history.loading ? <HistoryFeedback history={history} /> :
        <VaccineTable records={records} edit={edit} cancelVaccine={cancelVaccine} showAnimal={false} />}
    </section>
    <section className="panel work-panel">
      <h2>Comunicação governamental</h2>
      {communication ? <>
        <div className="section-header"><strong>{communication.tipo}</strong><Status value={communication.situacao} /></div>
        {communication.erro && <p className="muted">{communication.erro}</p>}
        <KeyValues items={ [['Protocolo', communication.protocolo ?? 'Aguardando confirmação']] } />
        <a className="button button--secondary" href={integrationPath(communication.id)}>Ver comunicação</a>
      </> : <p className="muted">{isDemo || data.integrationsAvailable ? 'Nenhuma comunicação de vacina registrada.' : 'Consulta de comunicações indisponível na API.'}</p>}
    </section>
  </div>
}

const animalTabs = [['resumo', 'Resumo'], ['consultas', 'Consultas'], ['vacinas', 'Vacinas'], ['microchip', 'Microchip']]

export function AnimalPage({ id, tab, data, edit, navigate, deactivate, cancelAppointment, cancelVaccine }) {
  const animal = find(data.animals, id)
  const chips = useAnimalHistory(animal?.id, data.animals, repository.listMicrochips, !isDemo && data.integrationsAvailable, animal?.chips)
  if (!animal) return <><PageHeader title="Ficha do animal" /><section className="panel work-panel"><p>Animal não encontrado.</p><a className="text-link" href="#/animais">Voltar para animais</a></section></>
  const current = animalTabs.some(([key]) => key === tab) ? tab : 'resumo'
  const chip = chips.items.find((record) => record.atual)
  const chipAvailable = isDemo || data.integrationsAvailable
  return <>
    <nav className="breadcrumb" aria-label="Localização"><a href="#/animais">Animais</a><span aria-hidden="true">/</span><span>Ficha do animal</span></nav>
    <section className="panel patient">
      <PetAvatar animal={animal} large />
      <div className="patient-description">
        <div className="patient-name"><h1>{animal.nome}</h1><Status value={animal.situacao} label={activeStatus(animal)} /></div>
        <p className="muted">{animalDescription(animal)}</p>
        <KeyValues items={[
          ['Tutor', animal.tutor?.nome_completo],
          ['Microchip RFID', !chipAvailable || chips.error ? 'Indisponível' : chips.loading ? 'Consultando…' : formatChip(chip?.codigo)],
        ]} />
      </div>
      <Button variant="secondary" icon="edit" onClick={() => edit('animal', animal)}>Editar ficha</Button>
    </section>
    <Tabs label="Áreas da ficha" items={animalTabs} value={current} onChange={(value) => navigate(animalPath(id, value))} />
    {current === 'resumo' && <section className="panel work-panel">
      <div className="section-header"><h2>Dados do animal</h2>{animal.situacao === 'ativo' && <Button variant="quiet" onClick={() => deactivate('animals', animal)}>Inativar animal</Button>}</div>
      <KeyValues items={[
        ['Sexo', animal.sexo === 'F' ? 'Fêmea' : 'Macho'],
        ['Nascimento', animal.data_nascimento ? formatDate(animal.data_nascimento) : null],
        ['Idade estimada', animal.idade_estimada_meses == null ? null : `${animal.idade_estimada_meses} meses`],
        ['Pelagem / cor', animal.cor],
        ['Peso atual', animal.peso_atual ? `${Number(animal.peso_atual).toLocaleString('pt-BR')} kg` : null],
      ]} />
    </section>}
    {current === 'consultas' && <AnimalConsultations key={animal.id} animal={animal} data={data} edit={edit} cancelAppointment={cancelAppointment} />}
    {current === 'vacinas' && <AnimalVaccines key={animal.id} animal={animal} data={data} edit={edit} cancelVaccine={cancelVaccine} />}
    {current === 'microchip' && <ChipHistory animal={animal} edit={edit} history={chips} available={chipAvailable} vets={data.vets} />}
  </>
}
