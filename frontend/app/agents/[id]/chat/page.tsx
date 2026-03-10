'use client'
import { useState, useEffect, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { createConversation, sendMessage, endConversation } from '@/lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

export default function ChatPage() {
  const router = useRouter()
  const params = useParams()
  const agentId = params.id as string
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    startConversation()
    return () => {
      if (conversationId) {
        endConversation(conversationId).catch(console.error)
      }
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startConversation = async () => {
    try {
      const res = await createConversation(agentId)
      setConversationId(res.data.id)
    } catch (error) {
      console.error('Failed to start conversation', error)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || !conversationId) return
    const userMessage = input.trim()
    setInput('')
    setLoading(true)

    try {
      setMessages(prev => [...prev, { id: 'temp', role: 'user', content: userMessage }])

      const res = await sendMessage(conversationId, userMessage)
      setMessages(prev => [...prev, res.data])
    } catch (error) {
      console.error('Failed to send message', error)
    } finally {
      setLoading(false)
    }
  }

  const handleEnd = async () => {
    if (!conversationId) return
    try {
      await endConversation(conversationId)
      router.push('/agents')
    } catch (error) {
      console.error('Failed to end conversation', error)
    }
  }

  return (
    <div className="container" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 10 }}>
        <h2>会话聊天</h2>
        <button
          onClick={handleEnd}
          style={{
            padding: '8px 16px',
            background: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer'
          }}
        >
          结束会话
        </button>
      </div>

      <div style={{ flex: 1, overflow: 'auto', border: '1px solid #e5e7eb', borderRadius: 8, padding: 20, margin }}>
        {messagesBottom: 20.length === 0 ? (
          <p style={{ color: '#9ca3af', textAlign: 'center' }}>开始发送消息与智能代理对话...</p>
        ) : (
          messages.map(msg => (
            <div key={msg.id} style={{
              marginBottom: 16,
              textAlign: msg.role === 'user' ? 'right' : 'left'
            }}>
              <div style={{
                display: 'inline-block',
                maxWidth: '70%',
                padding: '10px 16px',
                borderRadius: 12,
                background: msg.role === 'user' ? '#4f46e5' : '#f3f4f6',
                color: msg.role === 'user' ? 'white' : 'black',
                whiteSpace: 'pre-wrap'
              }}>
                {msg.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div style={{ color: '#9ca3af' }}>代理正在思考...</div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="输入您想完成的任务..."
          disabled={loading}
          style={{ flex: 1, padding: 12, borderRadius: 8, border: '1px solid #d1d5db' }}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          style={{
            padding: '12px 24px',
            background: '#4f46e5',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1
          }}
        >
          发送
        </button>
      </div>
    </div>
  )
}
