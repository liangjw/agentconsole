'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { getAgents, deleteAgent } from '@/lib/api'

interface Agent {
  id: string
  name: string
  description: string
  skills: string[]
  image: string
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      const res = await getAgents()
      setAgents(res.data)
    } catch (error) {
      console.error('Failed to load agents', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个代理吗？')) return
    try {
      await deleteAgent(id)
      setAgents(agents.filter(a => a.id !== id))
    } catch (error) {
      console.error('Failed to delete agent', error)
    }
  }

  if (loading) return <div className="container">加载中...</div>

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>智能代理管理</h1>
        <div style={{ display: 'flex', gap: 10 }}>
          <Link href="/templates">
            <button style={{
              padding: '10px 20px',
              background: '#7c3aed',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: 'pointer'
            }}>
              模板市场
            </button>
          </Link>
          <Link href="/agents/new">
            <button style={{
              padding: '10px 20px',
              background: '#4f46e5',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: 'pointer'
            }}>
              + 创建代理
            </button>
          </Link>
        </div>
      </div>

      <div style={{ marginTop: 20 }}>
        {agents.length === 0 ? (
          <p>还没有创建任何代理</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 20 }}>
            {agents.map(agent => (
              <div key={agent.id} style={{
                border: '1px solid #e5e7eb',
                borderRadius: 8,
                padding: 16
              }}>
                <h3>{agent.name}</h3>
                <p style={{ color: '#6b7280', fontSize: 14 }}>{agent.description || '暂无描述'}</p>
                <div style={{ marginTop: 10, fontSize: 12, color: '#9ca3af' }}>
                  Skills: {agent.skills?.length || 0} 个
                </div>
                <div style={{ marginTop: 10, display: 'flex', gap: 10 }}>
                  <Link href={`/agents/${agent.id}/chat`}>
                    <button style={{
                      padding: '6px 12px',
                      background: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: 4,
                      cursor: 'pointer'
                    }}>
                      启动
                    </button>
                  </Link>
                  <Link href={`/agents/${agent.id}`}>
                    <button style={{
                      padding: '6px 12px',
                      background: '#f59e0b',
                      color: 'white',
                      border: 'none',
                      borderRadius: 4,
                      cursor: 'pointer'
                    }}>
                      编辑
                    </button>
                  </Link>
                  <button
                    onClick={() => handleDelete(agent.id)}
                    style={{
                      padding: '6px 12px',
                      background: '#ef4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: 4,
                      cursor: 'pointer'
                    }}
                  >
                    删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
