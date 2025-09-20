import React, { useState, useRef, useEffect } from 'react'

const LEVEL_HINT = {
  1: "Indice léger",
  2: "Méthode",
  3: "Diagnostic",
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [level, setLevel] = useState(2)
  const [userId] = useState(() => crypto.randomUUID())
  const [loading, setLoading] = useState(false)
  const scroller = useRef(null)

  useEffect(() => {
    scroller.current?.scrollTo(0, scroller.current.scrollHeight)
  }, [messages])

  async function send() {
    if (!input.trim()) return
    const newMessages = [...messages, { role: 'user', content: input }]
    setMessages(newMessages)
    setInput("")
    setLoading(true)
    try {
      const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          level,
          messages: newMessages,
        })
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || 'Erreur serveur')
      }
      const data = await res.json()
      setMessages(m => [...m, { role: 'assistant', content: data.answer }])
    } catch (e) {
      setMessages(m => [...m, { role: 'assistant', content: '⚠️ ' + e.message }])
    } finally {
      setLoading(false)
    }
  }

  function onKeyDown(e){
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div style={{maxWidth: 820, margin: '20px auto', fontFamily: 'Inter, system-ui, sans-serif'}}>
      <h1 style={{fontSize: 24, marginBottom: 8}}>Tuteur IA — Indices guidés</h1>
      <p style={{marginTop: 0, color: '#555'}}>L'IA ne donne pas la solution, elle guide par paliers d'aide.</p>

      <div style={{display: 'flex', gap: 12, alignItems: 'center', margin: '12px 0'}}>
        <label>Niveau d'aide :</label>
        <select value={level} onChange={e => setLevel(Number(e.target.value))}>
          <option value={1}>1 — {LEVEL_HINT[1]}</option>
          <option value={2}>2 — {LEVEL_HINT[2]}</option>
          <option value={3}>3 — {LEVEL_HINT[3]}</option>
        </select>
        <span style={{color:'#777'}}>Quota raisonnable ; formule des questions précises.</span>
      </div>

      <div ref={scroller} style={{border: '1px solid #ddd', borderRadius: 8, padding: 12, height: 420, overflowY: 'auto'}}>
        {messages.map((m, i) => (
          <div key={i} style={{
            margin: '10px 0',
            background: m.role === 'user' ? '#eef6ff' : '#f7f7f7',
            padding: '10px 12px',
            borderRadius: 8
          }}>
            <div style={{fontSize: 12, color: '#666', marginBottom: 6}}>
              {m.role === 'user' ? 'Élève' : 'Tuteur'}
            </div>
            <div style={{whiteSpace: 'pre-wrap'}}>{m.content}</div>
          </div>
        ))}
        {loading && <div style={{opacity: .7}}>… génération de l'indice …</div>}
      </div>

      <div style={{marginTop: 12}}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Explique où tu bloques, montre ton idée ou ton message d'erreur…"
          rows={4}
          style={{width: '100%', padding: 10, borderRadius: 8, border: '1px solid #ddd'}}
        />
        <div style={{display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 8}}>
          <button onClick={() => setLevel(1)}>Indice 1</button>
          <button onClick={() => setLevel(2)}>Indice 2</button>
          <button onClick={() => setLevel(3)}>Indice 3</button>
          <button onClick={send} disabled={loading} style={{padding: '8px 14px'}}>Envoyer</button>
        </div>
      </div>
    </div>
  )
}