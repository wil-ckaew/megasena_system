
import React, { useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function App() {
  const [dia, setDia] = useState("");
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState("");

  const gerarJogos = async () => {
    if (!dia) {
      alert("Informe o dia!");
      return;
    }

    setLoading(true);
    setErro("");
    try {
      const res = await axios.post("http://127.0.0.1:5000/predict", { dia: Number(dia) });
      setResultado(res.data);
    } catch (err) {
      console.error(err);
      setErro("❌ Erro ao conectar com o servidor Flask!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white p-6">
      <h1 className="text-3xl font-bold mb-6 text-green-400">
        MegaSena AI — Teoria da Bola + Aprendizado de Máquina
      </h1>

      <div className="mb-6 flex gap-3">
        <input
          type="number"
          value={dia}
          onChange={(e) => setDia(e.target.value)}
          placeholder="Informe o dia"
          className="p-2 rounded bg-gray-700 border border-gray-600 text-white"
        />
        <button
          onClick={gerarJogos}
          className="bg-green-500 hover:bg-green-600 px-4 py-2 rounded font-bold"
        >
          {loading ? "Gerando..." : "Gerar Jogos"}
        </button>
      </div>

      {erro && <p className="text-red-400 font-semibold">{erro}</p>}

      {resultado && (
        <div className="w-full max-w-3xl bg-gray-800 rounded-lg p-6 shadow-lg mt-6">
          <h2 className="text-xl font-bold mb-4 text-green-300">
            🎲 Jogos Sugeridos
          </h2>
          <ul className="grid grid-cols-2 gap-3">
            {resultado.jogos_sugeridos.map((jogo, i) => (
              <li
                key={i}
                className="bg-gray-700 rounded-lg p-3 text-center text-lg tracking-wider"
              >
                {jogo.join(" - ")}
              </li>
            ))}
          </ul>

          <h2 className="text-xl font-bold mt-8 text-blue-400">
            📊 Probabilidades
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={resultado.probabilidades}>
              <XAxis dataKey="numero" stroke="#aaa" />
              <YAxis stroke="#aaa" />
              <Tooltip />
              <Bar dataKey="chance" fill="#4ade80" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <footer className="mt-10 text-sm text-gray-400">
        Desenvolvido por Wilson & GPT-5 🤖
      </footer>
    </div>
  );
}
