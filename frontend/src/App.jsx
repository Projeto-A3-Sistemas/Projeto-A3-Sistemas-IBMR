import { useCallback, useEffect, useState } from 'react'
import { demoVeterinarian } from './clinic/demoData.js'
import { apiAuth, emptyData, isDemo, repository, sessionEndedEvent } from './clinic/repository.js'
import { Login } from './components/Access.jsx'
import { ClinicEditor } from './components/forms.jsx'
import { AnimalPage, AnimalsPage, ConsultationsPage, IntegrationsPage, TutorsPage, VaccinesPage, VeterinariansPage } from './components/screens.jsx'
import { Button, Icon, Modal } from './components/ui.jsx'
import './App.css'

const sessionKey = 'sdm:acesso-local'
const modules = [
  ['tutores', 'Tutores', 'people'],
  ['animais', 'Animais', 'paw'],
  ['consultas', 'Consultas', 'calendar'],
  ['vacinas', 'Vacinas', 'syringe'],
  ['integracoes', 'Integrações', 'link'],
  ...(!isDemo ? [['veterinarios', 'Veterinários', 'people']] : []),
]

function readRoute() {
  const [path = '', search = ''] = window.location.hash.slice(1).split('?')
  const [, section, id] = path.split('/')
  return { section: modules.some(([key]) => key === section) ? section : 'animais', id, tab: new URLSearchParams(search).get('aba') }
}

function navigate(href) {
  window.location.hash = href
}

function Sidebar({ section, profile, logout, signingOut }) {
  const names = profile.nome_completo.trim().split(/\s+/)
  const initials = `${names[0]?.[0] ?? ''}${names.length > 1 ? names.at(-1)[0] : ''}`.toUpperCase()
  return <aside className="sidebar">
    <a className="brand" href="#/animais"><Icon name="paw" size={37} /><span>Clínica<br className="desktop-break" /> Veterinária</span></a>
    <nav className={isDemo ? 'main-nav' : 'main-nav main-nav--veterinarios'} aria-label="Menu principal">
      {modules.map(([key, label, icon]) =>
        <a key={key} className="nav-item" href={`#/${key}`} aria-current={section === key ? 'page' : undefined}>
          <Icon name={icon} size={22} /><span>{label}</span>
        </a>,
      )}
    </nav>
    <div className="sidebar-footer">
      <div className="account">
        <span className="account-avatar" aria-hidden="true">{initials}</span>
        <div className="account-copy"><strong>{profile.nome_completo}</strong><small>{isDemo ? 'Veterinária · Demonstração' : `CRMV-${profile.crmv_uf} ${profile.crmv_numero}`}</small></div>
        <button type="button" className="icon-button logout" title="Sair" aria-label="Sair" onClick={logout} disabled={signingOut}><Icon name="logout" size={19} /></button>
      </div>
    </div>
  </aside>
}

function ConfirmationDialog({ title, description, actionLabel, onClose, onConfirm }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function confirm() {
    setBusy(true)
    try {
      await onConfirm()
      onClose()
    } catch (failure) {
      setError(failure.message)
      setBusy(false)
    }
  }
  return <Modal title={title} onClose={onClose} busy={busy}>
    <div className="editor">
      <p>{description}</p>
      {error && <p className="notice notice--error" role="alert">{error}</p>}
      <div className="modal-actions">
        <Button variant="secondary" disabled={busy} onClick={onClose}>Voltar</Button>
        <Button variant="danger" disabled={busy} onClick={confirm}>{busy ? 'Processando…' : actionLabel}</Button>
      </div>
    </div>
  </Modal>
}

const saveMethods = {
  tutor: 'saveTutor', animal: 'saveAnimal', veterinario: 'saveVeterinarian', consulta: 'saveAppointment', vacina: 'saveVaccine',
}

function ClinicWorkspace({ profile, logout, signingOut }) {
  const [route, setRoute] = useState(readRoute)
  const [data, setData] = useState(emptyData)
  const [loading, setLoading] = useState(true)
  const [editor, setEditor] = useState(null)
  const [confirmation, setConfirmation] = useState(null)
  const [message, setMessage] = useState('')

  const load = useCallback(async () => {
    const result = await repository.load()
    setData(result)
  }, [])

  useEffect(() => {
    let mounted = true
    repository.load().then((result) => {
      if (mounted) setData(result)
    }).catch((error) => {
      if (mounted) setData({ ...emptyData, errors: [error.message] })
    }).finally(() => {
      if (mounted) setLoading(false)
    })
    return () => { mounted = false }
  }, [])

  useEffect(() => {
    const update = () => {
      setRoute(readRoute())
      setMessage('')
      setEditor(null)
      setConfirmation(null)
    }
    window.addEventListener('hashchange', update)
    return () => window.removeEventListener('hashchange', update)
  }, [])

  const edit = (kind, record, options = {}) => {
    setMessage('')
    setEditor({ kind, record, ...options })
  }
  const deactivate = (resource, record) => {
    setMessage('')
    setConfirmation({
      title: 'Inativar cadastro', actionLabel: 'Inativar cadastro',
      description: <>Inativar o cadastro de <strong>{record.nome ?? record.nome_completo}</strong>? O histórico será preservado.</>,
      run: () => repository.deactivate(resource, record.id),
      success: 'Cadastro inativado.',
    })
  }
  const cancelAppointment = (record) => {
    setMessage('')
    setConfirmation({
      title: 'Cancelar consulta', actionLabel: 'Confirmar cancelamento',
      description: <>Cancelar a consulta de <strong>{record.animal.nome}</strong>? Ela continuará no histórico como cancelada.</>,
      run: () => repository.cancelAppointment(record.id),
      success: 'Consulta cancelada.',
    })
  }
  const cancelVaccine = (record) => {
    setMessage('')
    setConfirmation({
      title: 'Cancelar agendamento de vacina', actionLabel: 'Confirmar cancelamento',
      description: <>Cancelar o agendamento de <strong>{record.nome_vacina}</strong> para <strong>{record.animal.nome}</strong>? O registro continuará no histórico como cancelado.</>,
      run: () => repository.cancelVaccine(record.id),
      success: 'Agendamento de vacina cancelado.',
    })
  }
  async function save(input) {
    const { kind, record } = editor
    if (kind === 'microchip') await repository.linkChip(record.id, input, editor.replaceChip)
    else await repository[saveMethods[kind]](input, record?.id)
    await load()
    const messages = {
      microchip: 'Vínculo de microchip registrado.', consulta: 'Consulta salva.', vacina: 'Vacina salva.',
      veterinario: 'Veterinário cadastrado. A pessoa pode usar “Confirmar minha senha” na tela de login para liberar o acesso.',
    }
    setMessage(messages[kind] ?? 'Registro salvo.')
  }
  async function confirmAction() {
    await confirmation.run()
    await load()
    setMessage(confirmation.success)
  }
  async function retry(id) {
    const result = await repository.retryIntegration(id)
    await load()
    if (result.situacao === 'confirmada') {
      setMessage(isDemo ? 'Reenvio simulado confirmado.' : 'Comunicação confirmada pelo governo simulado.')
    }
  }

  const pages = {
    tutores: <TutorsPage data={data} edit={edit} deactivate={deactivate} />,
    animais: route.id ? <AnimalPage key={route.id} data={data} edit={edit} deactivate={deactivate} cancelAppointment={cancelAppointment} cancelVaccine={cancelVaccine} navigate={navigate} id={route.id} tab={route.tab} /> : <AnimalsPage data={data} edit={edit} />,
    consultas: <ConsultationsPage data={data} edit={edit} cancelAppointment={cancelAppointment} />,
    vacinas: <VaccinesPage data={data} edit={edit} cancelVaccine={cancelVaccine} />,
    veterinarios: <VeterinariansPage data={data} edit={edit} />,
    integracoes: <IntegrationsPage data={data} selectedId={route.id} navigate={navigate} retry={retry} refresh={load} />,
  }

  return <div className="app-shell">
    <a className="skip-link" href="#conteudo" onClick={(event) => { event.preventDefault(); document.getElementById('conteudo').focus() }}>Pular para o conteúdo</a>
    <Sidebar section={route.section} profile={profile} logout={logout} signingOut={signingOut} />
    <main className="workspace" id="conteudo" tabIndex={-1}>
      <div className="workspace-inner">
        <div className="mode-line"><span className="mode-pill">{isDemo ? 'Demonstração · Dados fictícios' : 'API da clínica'}</span></div>
        {message && <p className="notice notice--success" role="status">{message}</p>}
        {data.errors.length > 0 && <div className="notice notice--error" role="alert">
          <div><strong>Alguns dados da clínica estão indisponíveis.</strong><ul>{data.errors.map((error) => <li key={error}>{error}</li>)}</ul></div>
          <Button variant="secondary" onClick={load}>Tentar novamente</Button>
        </div>}
        {loading ? <section className="panel work-panel" role="status">Carregando dados da clínica…</section> : pages[route.section]}
      </div>
    </main>
    {editor && <ClinicEditor editor={editor} data={data} onClose={() => setEditor(null)} onSave={save} />}
    {confirmation && <ConfirmationDialog title={confirmation.title} description={confirmation.description} actionLabel={confirmation.actionLabel} onClose={() => setConfirmation(null)} onConfirm={confirmAction} />}
  </div>
}

export default function App() {
  const [profile, setProfile] = useState(() => isDemo && sessionStorage.getItem(sessionKey) === '1' ? demoVeterinarian : null)
  const [checking, setChecking] = useState(() => !isDemo && apiAuth.hasSession())
  const [signingOut, setSigningOut] = useState(false)
  const [accessMessage, setAccessMessage] = useState('')

  useEffect(() => {
    if (isDemo) return
    let current = true
    const endSession = (event) => {
      setProfile(null)
      setAccessMessage(event.detail)
    }
    window.addEventListener(sessionEndedEvent, endSession)
    if (apiAuth.hasSession()) {
      apiAuth.profile().then((user) => {
        if (current) setProfile(user)
      }).catch((error) => {
        if (current) setAccessMessage(error.message)
      }).finally(() => {
        if (current) setChecking(false)
      })
    }
    return () => {
      current = false
      window.removeEventListener(sessionEndedEvent, endSession)
    }
  }, [])

  async function login(email, password) {
    if (isDemo) {
      sessionStorage.setItem(sessionKey, '1')
      setProfile(demoVeterinarian)
    } else {
      setProfile(await apiAuth.login(email, password))
    }
    setAccessMessage('')
  }
  async function logout() {
    if (signingOut) return
    setSigningOut(true)
    let message = ''
    try {
      if (isDemo) sessionStorage.removeItem(sessionKey)
      else await apiAuth.logout()
    } catch (error) {
      if (![401, 403].includes(error.status)) {
        message = 'Sessão encerrada neste navegador. A API não confirmou a revogação.'
      }
    } finally {
      window.history.replaceState(null, '', window.location.pathname + window.location.search)
      setProfile(null)
      setSigningOut(false)
      setAccessMessage(message)
    }
  }
  if (checking) return <main className="login-layout"><p role="status">Verificando sessão…</p></main>
  return profile ? <ClinicWorkspace profile={profile} logout={logout} signingOut={signingOut} /> : <Login onLogin={login} message={accessMessage} />
}
