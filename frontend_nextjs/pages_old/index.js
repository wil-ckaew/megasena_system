import { useState, useEffect } from 'react';

export default function Home() {
  const [day, setDay] = useState(new Date().getDate());
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({ python: '❓', rust: '❓' });

  useEffect(() => {
    checkServices();
  }, []);

  const checkServices = async () => {
    try {
      const rustRes = await fetch('http://localhost:8080/health');
      setStats(s => ({ ...s, rust: rustRes.ok ? '✅' : '❌' }));
    } catch { setStats(s => ({ ...s, rust: '❌' })); }

    try {
      const pythonRes = await fetch('http://localhost:5000/health');
      setStats(s => ({ ...s, python: pythonRes.ok ? '✅' : '❌' }));
    } catch { setStats(s => ({ ...s, python: '❌' })); }
  };

  const generateWithAI = async () => {
    setLoading(true);
    setError('');
    setGame(null);

    try {
      const response = await fetch('http://localhost:8080/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ day: parseInt(day) }),
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
    } catch (err) {
      setError(`Erro: ${err.message}. A IA Python está rodando?`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1>🤖 Mega-Sena com IA Python</h1>
      <p>Análise de 52 sorteios históricos usando Machine Learning</p>
      
      <div style={styles.status}>
        <div>🐍 Python ML: {stats.python} :5000</div>
        <div>🦀 Rust Proxy: {stats.rust} :8080</div>
        <button onClick={checkServices} style={styles.smallBtn}>🔄</button>
      </div>

      <div style={styles.card}>
        <h2>🎯 Gerar com IA</h2>
        
        <div style={styles.inputGroup}>
          <label>Dia para análise (1-31):</label>
          <input
            type="number"
            value={day}
            onChange={(e) => setDay(e.target.value)}
            min="1"
            max="31"
            style={styles.input}
          />
        </div>

        <button onClick={generateWithAI} disabled={loading} style={styles.button}>
          {loading ? '🤖 ANALISANDO DADOS...' : '🧠 GERAR COM IA PYTHON'}
        </button>

        {error && <div style={styles.error}>{error}</div>}

        {game && (
          <div style={styles.result}>
            <h3>✅ JOGO GERADO POR {game.source.toUpperCase()}</h3>
            <div style={styles.numbers}>
              {game.numbers.map((num, i) => (
                <div key={i} style={styles.number}>
                  <div style={styles.numValue}>{num}</div>
                  <div style={styles.numInfo}>
                    {num >= 35 ? 'ALTO' : 'baixo'} • {num % 2 === 0 ? 'PAR' : 'ÍMPAR'}
                  </div>
                </div>
              ))}
            </div>
            
            <div style={styles.stats}>
              <div><strong>Soma:</strong> {game.sum}</div>
              <div><strong>Altos (≥35):</strong> {game.high_numbers}</div>
              <div><strong>Pares:</strong> {game.even_numbers}</div>
            </div>
            
            <p style={styles.note}>
              {game.source === 'python_ml' 
                ? '✨ Gerado por IA Python analisando dados históricos'
                : '⚠️ Usando fallback (IA Python indisponível)'}
            </p>
          </div>
        )}
      </div>

      <div style={styles.info}>
        <h3>📊 Como funciona a IA Python:</h3>
        <ol>
          <li>Carrega 52 sorteios históricos do CSV</li>
          <li>Analisa frequência de cada número</li>
          <li>Identifica números "quentes" (sorteios recentes)</li>
          <li>Considera padrões por posição (n1, n2, ..., n6)</li>
          <li>Combina estatísticas com fator do dia</li>
          <li>Gera números otimizados probabilisticamente</li>
        </ol>
        <p><em>Dados reais analisados: resultados_megasena.csv</em></p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
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
  },
  card: {
    backgroundColor: 'white',
    padding: '30px',
    borderRadius: '15px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
    marginBottom: '30px',
  },
  inputGroup: {
    marginBottom: '20px',
  },
  input: {
    padding: '10px',
    fontSize: '18px',
    marginLeft: '10px',
    width: '80px',
  },
  button: {
    padding: '15px',
    fontSize: '18px',
    backgroundColor: '#306998',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    width: '100%',
    fontWeight: 'bold',
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
};
