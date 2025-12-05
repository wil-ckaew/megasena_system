import { useState } from "react";
import ApostasTable from "../components/ApostasTable";

export default function Home() {
  const [day, setDay] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function gerarAposta() {
    if (!day) {
      setError("Por favor, digite um dia");
      return;
    }

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const res = await fetch(`/api/generate?day=${day}`);
      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Erro ao gerar aposta");
        return;
      }

      if (data.generated_numbers && Array.isArray(data.generated_numbers)) {
        setResults(data.generated_numbers);
      } else {
        setError("Resposta inválida do servidor");
      }
    } catch (err) {
      setError(`Erro: ${err.message}`);
      console.error("Erro completo:", err);
    } finally {
      setLoading(false);
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      gerarAposta();
    }
  };

  return (
    <div className="min-h-screen p-6" style={{ background: 'linear-gradient(135deg, #e0f2ff 0%, #e9e6ff 50%, #f8fafc 100%)' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
        * { font-family: 'Poppins', sans-serif; }

        .card {
          background: linear-gradient(180deg, rgba(255,255,255,0.85), rgba(255,255,255,0.78));
          border-radius: 18px;
          padding: 28px;
          box-shadow: 0 10px 30px rgba(16,24,40,0.06);
          border: 1px solid rgba(99,102,241,0.06);
        }

        .label-center {
          text-align: center;
          color: #0f172a;
          font-weight: 600;
          margin-bottom: 10px;
        }

        .controls-row {
          display: flex;
          gap: 16px;
          align-items: center;
          justify-content: center;
          flex-wrap: wrap;
        }

        .input-elegant {
          background: rgba(255,255,255,0.98);
          border: 1px solid rgba(15,23,42,0.08);
          color: #0f172a;
          padding: 12px 16px;
          border-radius: 12px;
          min-width: 180px;
          font-weight: 600;
          box-shadow: 0 6px 18px rgba(2,6,23,0.04);
          outline: none;
        }

        .input-elegant::placeholder { color: #94a3b8; }

        .input-elegant:focus {
          box-shadow: 0 8px 24px rgba(99,102,241,0.12);
          border-color: rgba(99,102,241,0.6);
        }

        .btn-elegant {
          background: linear-gradient(135deg, #fde68a 0%, #fbbf24 100%);
          color: #0f172a;
          border: none;
          padding: 12px 20px;
          font-weight: 700;
          border-radius: 12px;
          cursor: pointer;
          transition: transform 0.18s ease, box-shadow 0.18s ease;
          box-shadow: 0 8px 22px rgba(251,191,36,0.12);
        }

        .btn-elegant:hover:not(:disabled) {
          transform: translateY(-3px);
          box-shadow: 0 18px 40px rgba(251,191,36,0.18);
        }

        .btn-elegant:disabled { opacity: 0.6; cursor: not-allowed; }

        .hint {
          text-align: center;
          color: #475569;
          margin-top: 14px;
          font-size: 14px;
        }
      `}</style>

      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 style={{ fontSize: 40, fontWeight: 800, color: '#0f172a' }}>MegaSena AI</h1>
          <p style={{ color: '#374151', marginTop: 6 }}>Gerador Inteligente de Apostas</p>
        </div>

        <div className="card">
          <div className="label-center">Selecione um dia (1–31)</div>

          <div className="controls-row">
            <input
              type="number"
              min="1"
              max="31"
              value={day}
              onChange={(e) => setDay(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Digite o dia"
              className="input-elegant"
            />

            <button
              onClick={gerarAposta}
              disabled={loading}
              className="btn-elegant"
            >
              {loading ? 'Gerando...' : 'Gerar Aposta'}
            </button>
          </div>

          {error && (
            <div style={{ marginTop: 16, textAlign: 'center', color: '#b91c1c', fontWeight: 700 }}>{error}</div>
          )}

          {Array.isArray(results) && results.length > 0 && (
            <div style={{ marginTop: 22 }}>
              <ApostasTable results={results} />
            </div>
          )}

          {!loading && results.length === 0 && !error && (
            <div className="hint">Digite um dia e pressione <strong>Gerar Aposta</strong></div>
          )}
        </div>

      </div>
    </div>
  );
}
