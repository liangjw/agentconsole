'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { getTemplates, createAgent } from '@/lib/api'

interface Template {
  id: string
  name: string
  description: string
  skills: string[]
  image: string
  icon: string
  category: string
}

export default function TemplatesPage() {
  const router = useRouter()
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  useEffect(() => {
    getTemplates().then(res => {
      setTemplates(res.data)
    }).catch(console.error).finally(() => {
      setLoading(false)
    })
  }, [])

  const categories = [...new Set(templates.map(t => t.category))]

  const filteredTemplates = selectedCategory
    ? templates.filter(t => t.category === selectedCategory)
    : templates

  const handleUseTemplate = async (template: Template) => {
    try {
      await createAgent({
        name: template.name,
        description: template.description,
        skills: template.skills,
        image: template.image
      })
      router.push('/agents')
    } catch (error) {
      console.error('Failed to create agent from template', error)
    }
  }

  if (loading) return <div className="container">加载中...</div>

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>代理模板</h1>
        <Link href="/agents">
          <button style={{
            padding: '8px 16px',
            background: '#6b7280',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer'
          }}>
            返回
          </button>
        </Link>
      </div>

      <p style={{ color: '#6b7280', marginBottom: 20 }}>
        选择一个模板快速创建智能代理
      </p>

      {/* 分类筛选 */}
      <div style={{ marginBottom: 20, display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        <button
          onClick={() => setSelectedCategory(null)}
          style={{
            padding: '6px 12px',
            background: selectedCategory === null ? '#4f46e5' : '#e5e7eb',
            color: selectedCategory === null ? 'white' : 'black',
            border: 'none',
            borderRadius: 20,
            cursor: 'pointer'
          }}
        >
          全部
        </button>
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            style={{
              padding: '6px 12px',
              background: selectedCategory === cat ? '#4f46e5' : '#e5e7eb',
              color: selectedCategory === cat ? 'white' : 'black',
              border: 'none',
              borderRadius: 20,
              cursor: 'pointer'
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* 模板卡片 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
        {filteredTemplates.map(template => (
          <div key={template.id} style={{
            border: '1px solid #e5e7eb',
            borderRadius: 12,
            padding: 20,
            display: 'flex',
            flexDirection: 'column'
          }}>
            <div style={{ fontSize: 40, marginBottom: 10 }}>{template.icon}</div>
            <h3 style={{ margin: '0 0 8px 0' }}>{template.name}</h3>
            <span style={{
              display: 'inline-block',
              padding: '2px 8px',
              background: '#eef2ff',
              color: '#4f46e5',
              borderRadius: 12,
              fontSize: 12,
              marginBottom: 8,
              alignSelf: 'flex-start'
            }}>
              {template.category}
            </span>
            <p style={{ color: '#6b7280', fontSize: 14, flex: 1 }}>
              {template.description}
            </p>
            <div style={{ fontSize: 12, color: '#9ca3af', marginBottom: 12 }}>
              Skills: {template.skills.length} 个
            </div>
            <button
              onClick={() => handleUseTemplate(template)}
              style={{
                padding: '10px 20px',
                background: '#4f46e5',
                color: 'white',
                border: 'none',
                borderRadius: 6,
                cursor: 'pointer',
                width: '100%'
              }}
            >
              使用此模板
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
