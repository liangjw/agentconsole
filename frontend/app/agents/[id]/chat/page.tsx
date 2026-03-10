'use client'
import { useState, useEffect, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { createConversation, sendMessage, endConversation, getSandboxFiles } from '@/lib/api'

interface ToolCall {
  tool: string
  input: Record<string, any>
  result: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  tool_calls?: ToolCall[]
}

interface FileNode {
  name: string
  type: 'file' | 'directory'
  path: string
}

export default function ChatPage() {
  const router = useRouter()
  const params = useParams()
  const agentId = params.id as string
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [files, setFiles] = useState<FileNode[]>([])
  const [showFiles, setShowFiles] = useState(true)
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

  // 定期刷新文件列表
  useEffect(() => {
    if (!conversationId) return

    const fetchFiles = async () => {
      try {
        const res = await getSandboxFiles(conversationId)
        setFiles(res.data.files || [])
      } catch (e) {
        // 忽略文件获取错误
      }
    }

    fetchFiles()
    const interval = setInterval(fetchFiles, 5000)

    return () => clearInterval(interval)
  }, [conversationId])

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

      // 刷新文件列表
      const filesRes = await getSandboxFiles(conversationId)
      setFiles(filesRes.data.files || [])
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
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'row',
      background: '#f9fafb'
    }}>
      {/* 左侧目录树 */}
      <div style={{
        width: showFiles ? 250 : 0,
        background: 'white',
        borderRight: '1px solid #e5e7eb',
        overflow: 'hidden',
        transition: 'width 0.3s'
      }}>
        <div style={{
          padding: '12px',
          borderBottom: '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span style={{ fontWeight: 600, fontSize: 14 }}>📁 文件目录</span>
          <button
            onClick={() => setShowFiles(false)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: 18
            }}
          >
            ×
          </button>
        </div>
        <div style={{ padding: 12, fontSize: 13 }}>
          {files.length === 0 ? (
            <div style={{ color: '#9ca3af', textAlign: 'center', padding: 20 }}>
              暂无文件
            </div>
          ) : (
            files.map((file, idx) => (
              <div key={idx} style={{
                padding: '4px 8px',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                borderRadius: 4,
                cursor: 'pointer'
              }}>
                <span>{file.type === 'directory' ? '📁' : '📄'}</span>
                <span style={{ color: '#374151' }}>{file.name}</span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 右侧聊天区域 */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* 头部 */}
        <div style={{
          padding: '12px 20px',
          background: 'white',
          borderBottom: '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {!showFiles && (
              <button
                onClick={() => setShowFiles(true)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: 18,
                  marginRight: 8
                }}
              >
                📁
              </button>
            )}
            <Link href="/agents" style={{ textDecoration: 'none', color: '#6b7280' }}>
              ← 返回
            </Link>
            <h2 style={{ margin: 0, fontSize: 18 }}>会话聊天</h2>
          </div>
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

        {/* 消息区域 */}
        <div style={{ flex: 1, overflow: 'auto', padding: 20 }}>
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', paddingTop: 100, color: '#9ca3af' }}>
              <div style={{ fontSize: 48, marginBottom: 16 }}>🤖</div>
              <p>开始发送消息与智能代理对话...</p>
              <p style={{ fontSize: 12 }}>代理将在沙箱中执行任务并返回结果</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={msg.id || idx} style={{
                marginBottom: 20,
                display: 'flex',
                flexDirection: 'column',
                alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start'
              }}>
                <div style={{
                  maxWidth: '70%',
                  padding: '12px 16px',
                  borderRadius: 12,
                  background: msg.role === 'user' ? '#4f46e5' : 'white',
                  color: msg.role === 'user' ? 'white' : '#1f2937',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                  whiteSpace: 'pre-wrap',
                  lineHeight: 1.5
                }}>
                  {msg.content}
                </div>

                {/* 工具调用结果 */}
                {msg.tool_calls && msg.tool_calls.length > 0 && (
                  <div style={{ maxWidth: '70%', marginTop: 8 }}>
                    {msg.tool_calls.map((tool, tIdx) => (
                      <div key={tIdx} style={{
                        background: '#f3f4f6',
                        borderRadius: 8,
                        padding: 12,
                        fontSize: 12,
                        marginTop: 8,
                        borderLeft: '3px solid #4f46e5'
                      }}>
                        <div style={{ fontWeight: 600, color: '#4f46e5', marginBottom: 4 }}>
                          🔧 工具: {tool.tool}
                        </div>
                        <div style={{
                          background: '#1f2937',
                          color: '#10b981',
                          padding: 8,
                          borderRadius: 4,
                          fontFamily: 'monospace',
                          maxHeight: 150,
                          overflow: 'auto',
                          whiteSpace: 'pre-wrap'
                        }}>
                          {tool.result.substring(0, 500)}
                          {tool.result.length > 500 && '...'}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#9ca3af' }}>
              <div style={{
                width: 8,
                height: 8,
                background: '#4f46e5',
                borderRadius: '50%',
                animation: 'pulse 1s infinite'
              }}>
                <style>{`@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }`}</style>
              </div>
              代理正在思考...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div style={{ padding: 20, background: 'white', borderTop: '1px solid #e5e7eb' }}>
          <div style={{ display: 'flex', gap: 10, maxWidth: 800, margin: '0 auto' }}>
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="描述你想完成的任务..."
              disabled={loading}
              style={{
                flex: 1,
                padding: 12,
                borderRadius: 8,
                border: '1px solid #d1d5db',
                fontSize: 14
              }}
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
                opacity: loading ? 0.7 : 1,
                fontWeight: 500
              }}
            >
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
