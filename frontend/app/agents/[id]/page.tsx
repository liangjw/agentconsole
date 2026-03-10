'use client'
import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { getSkills, getAgent, updateAgent } from '@/lib/api'

interface Skill {
  id: string
  name: string
  description: string
  icon: string
}

interface Agent {
  id: string
  name: string
  description: string
  skills: string[]
  image: string
}

export default function EditAgentPage() {
  const router = useRouter()
  const params = useParams()
  const agentId = params.id as string
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  const [image, setImage] = useState('python:3.11')
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getSkills(),
      getAgent(agentId)
    ]).then(([skillsRes, agentRes]) => {
      setSkills(skillsRes.data)
      const agent: Agent = agentRes.data
      setName(agent.name)
      setDescription(agent.description)
      setSelectedSkills(agent.skills || [])
      setImage(agent.image)
    }).catch(console.error).finally(() => {
      setInitialLoading(false)
    })
  }, [agentId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await updateAgent(agentId, {
        name,
        description,
        skills: selectedSkills,
        image
      })
      router.push('/agents')
    } catch (error) {
      console.error('Failed to update agent', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleSkill = (skillId: string) => {
    setSelectedSkills(prev =>
      prev.includes(skillId)
        ? prev.filter(id => id !== skillId)
        : [...prev, skillId]
    )
  }

  const images = [
    'python:3.11',
    'python:3.10',
    'node:18',
    'node:20',
    'golang:1.21'
  ]

  if (initialLoading) {
    return <div className="container">加载中...</div>
  }

  return (
    <div className="container">
      <h1>编辑智能代理</h1>
      <form onSubmit={handleSubmit} style={{ maxWidth: 600, marginTop: 20 }}>
        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>代理名称</label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            required
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #d1d5db' }}
          />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>描述</label>
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            rows={3}
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #d1d5db' }}
          />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>选择Skills</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
            {skills.map(skill => (
              <button
                key={skill.id}
                type="button"
                onClick={() => toggleSkill(skill.id)}
                style={{
                  padding: '8px 12px',
                  border: selectedSkills.includes(skill.id) ? '2px solid #4f46e5' : '1px solid #d1d5db',
                  borderRadius: 6,
                  background: selectedSkills.includes(skill.id) ? '#eef2ff' : 'white',
                  cursor: 'pointer'
                }}
              >
                {skill.icon} {skill.name}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', marginBottom: 5 }}>沙箱镜像</label>
          <select
            value={image}
            onChange={e => setImage(e.target.value)}
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #d1d5db' }}
          >
            {images.map(img => (
              <option key={img} value={img}>{img}</option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', gap: 10 }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '10px 20px',
              background: '#4f46e5',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1
            }}
          >
            {loading ? '保存中...' : '保存'}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            style={{
              padding: '10px 20px',
              background: '#6b7280',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: 'pointer'
            }}
          >
            取消
          </button>
        </div>
      </form>
    </div>
  )
}
