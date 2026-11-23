import { useCallback, useEffect, useState } from 'react'
import { demoCredentials, demoVeterinarian } from './clinic/demoData.js'
import { emptyData, isDemo, repository } from './clinic/repository.js'
import { ClinicEditor } from './components/forms.jsx'
import { AnimalPage, AnimalsPage, ConsultationsPage, IntegrationsPage, TutorsPage, VaccinesPage } from './components/screens.jsx'
import { Button, Icon, Modal } from './components/ui.jsx'
import './App.css'

const sessionKey = 'sdm:acesso-local'
const modules = [
  ['tutores', 'Tutores', 'people'],
  ['animais', 'Animais', 'paw'],
  ['consultas', 'Consultas', 'calendar'],
  ['vacinas', 'Vacinas', 'syringe'],
  ['integracoes', 'Integrações', 'link'],
]

function readRoute() {
  const [path = '', search = ''] = window.location.hash.slice(1).split('?')
  const [, section, id] = path.split('/')
  return { section: modules.some(([key]) => key === section) ? section : 'animais', id, tab: new URLSearchParams(search).get('aba') }
}

function navigate(href) {
  window.location.hash = href
}

function Login({ onLogin }) {
  const [error, setError] = useState('')
  function submit(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    if (String(form.get('email')).trim().toLowerCase() !== demoCredentials.email || form.get('password') !== demoCredentials.password) {
      setError('E-mail ou senha inválidos para a demonstração.')
      return
    }
    onLogin()
  }

  return <main className="login-layout" id="conteudo">
    <div className="login-panel">
      <div className="login-mark"><Icon name="paw" size={32} /></div>
      <h1>Clínica Veterinária</h1>
      <p className="muted">Acesso veterinário</p>
      <form className="login-form" onSubmit={submit} onChange={() => error && setError('')}>
        <label className="field"><span>E-mail</span><input type="email" name="email" autoComplete="username" autoCapitalize="none" placeholder="nome@clinica.com" required /></label>
        <label className="field"><span>Senha</span><input type="password" name="password" autoComplete="current-password" placeholder="Sua senha de demonstração" required /></label>
        {error && <p className="notice notice--error" role="alert">{error}</p>}
        <Button type="submit">Entrar</Button>
      </form>
      <div className="login-demo">
        <p className="muted">{isDemo ? 'Explore o sistema com dados fictícios.' : 'Acesso local para testar a API. A autenticação do servidor está pendente.'}</p>
        <Button variant="secondary" onClick={onLogin}>{isDemo ? 'Entrar na demonstração' : 'Abrir modo de teste da API'}</Button>
      </div>
    </div>
  </main>
}

function Sidebar({ section, logout }) {
  return <aside className="sidebar">
    <a className="brand" href="#/animais"><Icon name="paw" size={37} /><span>Clínica<br className="desktop-break" /> Veterinária</span></a>
    <nav className="main-nav" aria-label="Menu principal">
      {modules.map(([key, label, icon]) =>
        <a key={key} className="nav-item" href={`#/${key}`} aria-current={section === key ? 'page' : undefined}>
          <Icon name={icon} size={22} /><span>{label}</span>
        </a>,
      )}
    </nav>
    <div className="sidebar-footer">
      <div className="account">
        <span className="account-avatar" aria-hidden="true">AL</span>
        <div className="account-copy"><strong>{isDemo ? demoVeterinarian.nome_completo : 'Acesso local'}</strong><small>{isDemo ? 'Veterinária · Demonstração' : 'Sessão de teste local'}</small></div>
        <button type="button" className="icon-button logout" title="Sair" aria-label="Sair" onClick={logout}><Icon name="logout" size={19} /></button>
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
  tutor: 'saveTutor', animal: 'saveAnimal', consulta: 'saveAppointment', vacina: 'saveVaccine',
}

function ClinicWorkspace({ logout }) {
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
    if (kind === 'microchip') await repository.linkChip(record.id, input)
    else await repository[saveMethods[kind]](input, record?.id)
    await load()
    const messages = { microchip: 'Vínculo de microchip registrado.', consulta: 'Consulta salva.', vacina: 'Vacina salva.' }
    setMessage(messages[kind] ?? 'Registro salvo.')
  }
  async function confirmAction() {
    await confirmation.run()
    await load()
    setMessage(confirmation.success)
  }
  async function retry(id) {
    await repository.retryIntegration(id)
    await load()
    setMessage('Reenvio simulado confirmado.')
  }

  const pages = {
    tutores: <TutorsPage data={data} edit={edit} deactivate={deactivate} />,
    animais: route.id ? <AnimalPage data={data} edit={edit} deactivate={deactivate} cancelAppointment={cancelAppointment} cancelVaccine={cancelVaccine} navigate={navigate} id={route.id} tab={route.tab} /> : <AnimalsPage data={data} edit={edit} />,
    consultas: <ConsultationsPage data={data} edit={edit} cancelAppointment={cancelAppointment} />,
    vacinas: <VaccinesPage data={data} edit={edit} cancelVaccine={cancelVaccine} />,
    integracoes: <IntegrationsPage data={data} selectedId={route.id} navigate={navigate} retry={retry} />,
  }

  return <div className="app-shell">
    <a className="skip-link" href="#conteudo" onClick={(event) => { event.preventDefault(); document.getElementById('conteudo').focus() }}>Pular para o conteúdo</a>
    <Sidebar section={route.section} logout={logout} />
    <main className="workspace" id="conteudo" tabIndex={-1}>
      <div className="workspace-inner">
        <div className="mode-line"><span className="mode-pill">{isDemo ? 'Demonstração · Dados fictícios' : 'API da clínica · Acesso local de teste'}</span></div>
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
  const [signedIn, setSignedIn] = useState(() => sessionStorage.getItem(sessionKey) === '1')
  function login() {
    sessionStorage.setItem(sessionKey, '1')
    setSignedIn(true)
  }
  function logout() {
    sessionStorage.removeItem(sessionKey)
    window.history.replaceState(null, '', window.location.pathname + window.location.search)
    setSignedIn(false)
  }
  return signedIn ? <ClinicWorkspace logout={logout} /> : <Login onLogin={login} />
}
