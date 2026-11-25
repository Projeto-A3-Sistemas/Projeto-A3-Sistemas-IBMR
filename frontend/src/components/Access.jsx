import { useState } from 'react'
import { demoCredentials } from '../clinic/demoData.js'
import { apiAuth, isDemo } from '../clinic/repository.js'
import { Button, Icon } from './ui.jsx'

function PasswordConfirmation({ onClose }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [token, setToken] = useState('')

  async function requestLink(event) {
    event.preventDefault()
    if (busy) return
    const email = String(new FormData(event.currentTarget).get('email')).trim().toLowerCase()
    setBusy(true)
    setError('')
    try {
      const result = await apiAuth.requestPasswordConfirmation(email)
      if (!result?.token_confirmacao_simulado) throw new Error('A API não retornou o link de confirmação.')
      setToken(result.token_confirmacao_simulado)
    } catch (failure) {
      setError(failure.message)
    } finally {
      setBusy(false)
    }
  }

  async function confirm() {
    if (busy) return
    setBusy(true)
    setError('')
    try {
      await apiAuth.confirmPassword(token)
      onClose(true)
    } catch (failure) {
      setError(failure.message)
    } finally {
      setBusy(false)
    }
  }

  return <div className="login-demo">
    <p className="muted">O envio do link é simulado neste projeto acadêmico.</p>
    {token ? <>
      <p role="status">Link simulado recebido. Confirme a senha para liberar o acesso.</p>
      <Button onClick={confirm} disabled={busy}>{busy ? 'Confirmando…' : 'Confirmar senha'}</Button>
    </> : <form className="login-form" onSubmit={requestLink}>
      <label className="field"><span>E-mail cadastrado</span><input type="email" name="email" autoComplete="email" autoCapitalize="none" required disabled={busy} /></label>
      <Button type="submit" disabled={busy}>{busy ? 'Solicitando…' : 'Solicitar link de confirmação'}</Button>
    </form>}
    {error && <p className="notice notice--error" role="alert">{error}</p>}
    <Button variant="quiet" onClick={() => onClose(false)} disabled={busy}>Voltar ao login</Button>
  </div>
}

export function Login({ onLogin, message }) {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [confirmationOpen, setConfirmationOpen] = useState(false)
  const [confirmed, setConfirmed] = useState(false)

  async function submit(event) {
    event.preventDefault()
    if (busy) return
    const form = new FormData(event.currentTarget)
    const email = String(form.get('email')).trim().toLowerCase()
    const password = form.get('password')
    setError('')
    setBusy(true)
    try {
      if (isDemo && (email !== demoCredentials.email || password !== demoCredentials.password)) {
        throw new Error('E-mail ou senha inválidos para a demonstração.')
      }
      await onLogin(email, password)
    } catch (failure) {
      setError(failure.status === 404 ? 'A API em execução ainda não oferece o login deste projeto. Inicie a versão com autenticação.' : failure.message)
    } finally {
      setBusy(false)
    }
  }

  return <main className="login-layout" id="conteudo">
    <div className="login-panel">
      <div className="login-mark"><Icon name="paw" size={32} /></div>
      <h1>Clínica Veterinária</h1>
      <p className="muted">{confirmationOpen ? 'Confirmação de senha' : 'Acesso veterinário'}</p>
      {confirmationOpen ? <PasswordConfirmation onClose={(success) => {
        setConfirmationOpen(false)
        setConfirmed(success)
      }} /> : <>
        {confirmed && <p className="notice notice--success" role="status">Senha confirmada. Já é possível fazer login.</p>}
        {message && !error && <p className="notice notice--warning" role="status">{message}</p>}
        <form className="login-form" onSubmit={submit} onChange={() => error && setError('')}>
          <label className="field"><span>E-mail</span><input type="email" name="email" autoComplete="username" autoCapitalize="none" placeholder="nome@clinica.com" required disabled={busy} /></label>
          <label className="field"><span>Senha</span><input type="password" name="password" autoComplete="current-password" placeholder={isDemo ? 'Sua senha de demonstração' : 'Sua senha'} required disabled={busy} /></label>
          {error && <p className="notice notice--error" role="alert">{error}</p>}
          <Button type="submit" disabled={busy}>{busy ? 'Entrando…' : 'Entrar'}</Button>
        </form>
        <div className="login-demo">
          {isDemo ? <>
            <p className="muted">Explore o sistema com dados fictícios.</p>
            <Button variant="secondary" onClick={() => onLogin()}>Entrar na demonstração</Button>
          </> : <Button variant="quiet" onClick={() => {
            setError('')
            setConfirmed(false)
            setConfirmationOpen(true)
          }} disabled={busy}>Confirmar minha senha</Button>}
        </div>
      </>}
    </div>
  </main>
}
