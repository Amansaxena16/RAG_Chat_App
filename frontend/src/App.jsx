import { useState } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000/api/chat/ask/'

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
}

function App() {
  const [input, setInput] = useState('')
  const [history, setHistory] = useState([])
  const [times, setTimes] = useState([])
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const startNewChat = () => {
    setHistory([])
    setTimes([])
    setSources([])
    setError('')
    setInput('')
  }

  const sendQuestion = async (e) => {
    e.preventDefault()
    const question = input.trim()
    if (!question || loading) return

    setInput('')
    setError('')
    setLoading(true)
    const askedAt = new Date()

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, history }),
      })

      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`)
      }

      const data = await res.json()
      setHistory(data.history)
      setTimes((prev) => [...prev, askedAt, new Date()])
      setSources(data.sources)
    } catch (err) {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-app">
      <header>
        <h1>NovaTech Assistant</h1>
        <button className="btn btn-secondary" onClick={startNewChat}>
          New chat
        </button>
      </header>

      <main>
        <div className="container">
          {history.length === 0 ? (
            <div className="empty-state">
              <h2>NovaTech Assistant</h2>
              <p>Ask a question to begin.</p>
            </div>
          ) : (
            <div className="messages">
              {history.map((msg, i) => (
                <div key={i} className={`message-row ${msg.role}`}>
                  <div className="card">
                    <div className="card-kicker">
                      <span className="role-label">
                        {msg.role === 'user' ? 'You' : 'NovaTech'}
                      </span>
                      <span className="timestamp">
                        {times[i] ? formatTime(times[i]) : ''}
                      </span>
                    </div>
                    <p className="message-text">{msg.content}</p>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message-row assistant">
                  <div className="card">
                    <div className="card-kicker">
                      <span className="role-label">NovaTech</span>
                    </div>
                    <p className="message-text">Thinking...</p>
                  </div>
                </div>
              )}

              {error && (
                <div className="message-row assistant">
                  <div className="card card-error">
                    <p className="message-text">{error}</p>
                  </div>
                </div>
              )}

              {sources.length > 0 && (
                <div className="sources">
                  <span className="role-label">Sources</span>
                  <ul>
                    {sources.map((s, i) => (
                      <li key={i}>
                        <strong>{s.doc_type}</strong> — {s.content.slice(0, 120)}...
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <footer>
        <form className="composer" onSubmit={sendQuestion}>
          <textarea
            className="input composer-input"
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                sendQuestion(e)
              }
            }}
            placeholder="Message NovaTech Assistant..."
            disabled={loading}
          />
          <button className="btn btn-primary" type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </footer>
    </div>
  )
}

export default App
