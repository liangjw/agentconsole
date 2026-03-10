import Link from 'next/link'

export default function Home() {
  return (
    <main className="container">
      <h1>AgentConsole</h1>
      <p>基于OpenSandbox的智能代理系统</p>
      <div style={{ marginTop: 20 }}>
        <Link href="/agents">
          <button style={{
            padding: '10px 20px',
            background: '#4f46e5',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer',
            marginRight: 10
          }}>
            管理智能代理
          </button>
        </Link>
      </div>
    </main>
  )
}
