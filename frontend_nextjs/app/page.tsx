'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

// Configuração da API - ajuste conforme seu ambiente
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface GameResult {
  numbers: number[];
  sum: number;
  high_numbers: number;
  even_numbers: number;
  source: string;
  method?: string;
}

export default function Home() {
  const [day, setDay] = useState(new Date().getDate());
  const [game, setGame] = useState<GameResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({ python: '❓', rust: '❓' });
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    checkServices();
  }, []);

  const checkServices = async () => {
    setBackendStatus('checking');
    
    try {
      const rustRes = await fetch(`${API_BASE_URL}/health`);
      const rustOk = rustRes.ok;
      setStats(s => ({ ...s, rust: rustOk ? '✅' : '❌' }));
      
      try {
        const pythonRes = await fetch('http://localhost:5000/health');
        setStats(s => ({ ...s, python: pythonRes.ok ? '✅' : '❌' }));
      } catch { 
        setStats(s => ({ ...s, python: '❌' }));
      }
      
      setBackendStatus(rustOk ? 'online' : 'offline');
    } catch { 
      setStats(s => ({ ...s, rust: '❌' }));
      setBackendStatus('offline');
    }
  };

  const generateWithAI = async () => {
    setLoading(true);
    setError('');
    setGame(null);

    try {
      const dayNumber = Number(day);
      
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ day: dayNumber }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      if (data.success && data.games[0]) {
        setGame({
          ...data.games[0],
          method: data.method,
          source: data.games[0].source
        });
      }
    } catch (err: any) {
      setError(`Backend não disponível. Iniciando modo de demonstração...`);
      
      // Modo de demonstração - gera um jogo simulado
      setTimeout(() => {
        const demoGame = generateDemoGame();
        setGame(demoGame);
        setError('');
      }, 1000);
    } finally {
      setLoading(false);
    }
  };

  // Gera um jogo de demonstração quando o backend está offline
  const generateDemoGame = (): GameResult => {
    // Números baseados em estatísticas reais
    const commonNumbers = [5, 10, 23, 33, 37, 53];
    const shuffled = [...commonNumbers].sort(() => Math.random() - 0.5);
    const selected = shuffled.slice(0, 6).sort((a, b) => a - b);
    
    const sum = selected.reduce((a, b) => a + b, 0);
    const highNumbers = selected.filter(n => n >= 35).length;
    const evenNumbers = selected.filter(n => n % 2 === 0).length;
    
    return {
      numbers: selected,
      sum,
      high_numbers: highNumbers,
      even_numbers: evenNumbers,
      source: 'demo_mode',
      //method: 'demo'
    };
  };

  const getStatusColor = () => {
    switch (backendStatus) {
      case 'online': return '#4caf50';
      case 'offline': return '#f44336';
      case 'checking': return '#ff9800';
      default: return '#9e9e9e';
    }
  };

  const getStatusText = () => {
    switch (backendStatus) {
      case 'online': return 'CONECTADO';
      case 'offline': return 'MODO DEMO';
      case 'checking': return 'VERIFICANDO';
      default: return 'DESCONHECIDO';
    }
  };

  return (
    <div style={styles.container}>
      <nav style={styles.nav}>
        <Link href="/" style={styles.navLink}>🏠 Home</Link>
        <Link href="/bolao" style={styles.navLink}>🎯 Bolão</Link>
        <Link href="/chatbot" style={styles.navLink}>🤖 ChatBot</Link>
      </nav>
      
      <div style={styles.header}>
        <h1>🤖 Mega-Sena com IA Python</h1>
        <p>Análise de 52 sorteios históricos usando Machine Learning</p>
        <div style={{
          ...styles.statusBadge,
          backgroundColor: getStatusColor()
        }}>
          {getStatusText()}
        </div>
      </div>
      
      <div style={styles.status}>
        <div>🐍 Python ML: {stats.python} :5000</div>
        <div>🦀 Rust Proxy: {stats.rust} :8080</div>
        <button onClick={checkServices} style={styles.smallBtn}>🔄</button>
      </div>

      <div style={styles.card}>
        <h2>🎯 Gerar com IA</h2>
        <p style={styles.subtitle}>
          {backendStatus === 'online' 
            ? 'Usando IA Python em tempo real' 
            : '⚠️ Modo Demonstração - Backend offline'}
        </p>
        
        <div style={styles.inputGroup}>
          <label>Dia para análise (1-31):</label>
          <input
            type="number"
            value={day}
            onChange={(e) => setDay(Number(e.target.value))}
            min="1"
            max="31"
            style={styles.input}
          />
        </div>

        <button 
          onClick={generateWithAI} 
          disabled={loading} 
          style={{
            ...styles.button,
            backgroundColor: backendStatus === 'online' ? '#306998' : '#757575'
          }}
        >
          {loading ? '🤖 ANALISANDO DADOS...' : 
           backendStatus === 'online' ? '🧠 GERAR COM IA PYTHON' : '🎲 GERAR DEMONSTRAÇÃO'}
        </button>

        {error && <div style={styles.error}>{error}</div>}

        {game && (
          <div style={styles.result}>
            <h3>
              {game.source === 'python_ml' ? '✅ JOGO GERADO POR IA PYTHON' : 
               game.source === 'rust_fallback' ? '⚠️ JOGO GERADO POR FALLBACK' : 
               '🎲 JOGO DE DEMONSTRAÇÃO'}
            </h3>
            <div style={styles.numbers}>
              {game.numbers.map((num: number, i: number) => (
                <div key={i} style={styles.number}>
                  <div style={styles.numValue}>{num}</div>
                  <div style={styles.numInfo}>
                    {num >= 35 ? 'ALTO' : 'baixo'} • {num % 2 === 0 ? 'PAR' : 'ÍMPAR'}
                  </div>
                </div>
              ))}
            </div>
            
            <div style={styles.stats}>
              <div>
                <strong>Soma:</strong> {game.sum}
                <div style={styles.statNote}>
                  {game.sum >= 180 && game.sum <= 240 ? '✅ Ideal' : '⚠️ Fora do ideal'}
                </div>
              </div>
              <div>
                <strong>Altos (≥35):</strong> {game.high_numbers}
                <div style={styles.statNote}>
                  {game.high_numbers >= 2 && game.high_numbers <= 3 ? '✅ Ideal' : '⚠️ Fora do ideal'}
                </div>
              </div>
              <div>
                <strong>Pares:</strong> {game.even_numbers}
                <div style={styles.statNote}>
                  {game.even_numbers >= 2 && game.even_numbers <= 4 ? '✅ Balanceado' : '⚠️ Desbalanceado'}
                </div>
              </div>
            </div>
            
            <p style={styles.note}>
              {game.source === 'python_ml' 
                ? '✨ Gerado por IA Python analisando dados históricos'
                : game.source === 'rust_fallback'
                ? '⚠️ Usando fallback (IA Python indisponível)'
                : '🎲 Modo demonstração - Backend offline'}
            </p>
          </div>
        )}
      </div>

      <div style={styles.info}>
        <h3>📊 Como funciona o sistema:</h3>
        <div style={styles.systemInfo}>
          <div style={styles.systemItem}>
            <h4>🤖 IA Python (ML)</h4>
            <ul>
              <li>Analisa 52 sorteios históricos</li>
              <li>Machine Learning com scikit-learn</li>
              <li>Identifica padrões e tendências</li>
              <li>Status: {stats.python === '✅' ? 'Online' : 'Offline'}</li>
            </ul>
          </div>
          <div style={styles.systemItem}>
            <h4>🦀 Backend Rust</h4>
            <ul>
              <li>API de alta performance</li>
              <li>Integra Python ML + Frontend</li>
              <li>Cache inteligente</li>
              <li>Status: {stats.rust === '✅' ? 'Online' : 'Offline'}</li>
            </ul>
          </div>
          <div style={styles.systemItem}>
            <h4>⚛️ Frontend Next.js</h4>
            <ul>
              <li>Interface moderna React</li>
              <li>Geração de bolões</li>
              <li>Chatbot inteligente</li>
              <li>Status: ✅ Sempre online</li>
            </ul>
          </div>
        </div>
        
        <div style={styles.demoNote}>
          <p><strong>💡 Nota:</strong> Quando o backend está offline, o sistema entra em modo de demonstração, mostrando dados baseados em estatísticas reais dos sorteios.</p>
        </div>
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    maxWidth: '1000px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  header: {
    textAlign: 'center',
    marginBottom: '30px',
    position: 'relative',
  },
  statusBadge: {
    position: 'absolute',
    top: '0',
    right: '0',
    padding: '5px 15px',
    borderRadius: '20px',
    color: 'white',
    fontSize: '12px',
    fontWeight: 'bold',
  },
  nav: {
    display: 'flex',
    gap: '20px',
    marginBottom: '30px',
    padding: '15px',
    backgroundColor: '#f0f0f0',
    borderRadius: '10px',
  },
  navLink: {
    textDecoration: 'none',
    color: '#306998',
    fontWeight: 'bold',
    padding: '10px 20px',
    borderRadius: '5px',
    backgroundColor: 'white',
    border: '2px solid #306998',
    transition: 'all 0.3s',
  },
  status: {
    backgroundColor: '#e3f2fd',
    padding: '15px',
    borderRadius: '10px',
    margin: '20px 0',
    display: 'flex',
    gap: '20px',
    alignItems: 'center',
  },
  smallBtn: {
    padding: '5px 10px',
    marginLeft: 'auto',
    cursor: 'pointer',
    backgroundColor: '#306998',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
  },
  card: {
    backgroundColor: 'white',
    padding: '30px',
    borderRadius: '15px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
    marginBottom: '30px',
  },
  subtitle: {
    color: '#666',
    marginBottom: '20px',
    fontStyle: 'italic',
  },
  inputGroup: {
    marginBottom: '20px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  input: {
    padding: '10px',
    fontSize: '18px',
    width: '80px',
    border: '2px solid #ddd',
    borderRadius: '5px',
  },
  button: {
    padding: '15px',
    fontSize: '18px',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    width: '100%',
    fontWeight: 'bold',
    transition: 'all 0.3s',
  },
  error: {
    backgroundColor: '#ffebee',
    color: '#c62828',
    padding: '15px',
    borderRadius: '5px',
    marginTop: '20px',
  },
  result: {
    backgroundColor: '#e8f5e9',
    padding: '25px',
    borderRadius: '10px',
    marginTop: '25px',
    textAlign: 'center',
  },
  numbers: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '15px',
    margin: '25px 0',
  },
  number: {
    backgroundColor: 'white',
    padding: '15px',
    borderRadius: '10px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  numValue: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#1a237e',
  },
  numInfo: {
    fontSize: '12px',
    color: '#666',
    marginTop: '5px',
  },
  stats: {
    display: 'flex',
    justifyContent: 'center',
    gap: '30px',
    margin: '20px 0',
  },
  statNote: {
    fontSize: '12px',
    color: '#666',
    marginTop: '5px',
  },
  note: {
    fontStyle: 'italic',
    color: '#666',
    marginTop: '15px',
  },
  info: {
    backgroundColor: '#f5f5f5',
    padding: '20px',
    borderRadius: '10px',
  },
  systemInfo: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '20px',
    marginTop: '20px',
  },
  systemItem: {
    backgroundColor: 'white',
    padding: '15px',
    borderRadius: '10px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  demoNote: {
    backgroundColor: '#fff3e0',
    padding: '15px',
    borderRadius: '10px',
    marginTop: '20px',
    borderLeft: '4px solid #ff9800',
  },
};
