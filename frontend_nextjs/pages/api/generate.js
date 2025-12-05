export default async function handler(req, res) {
  const { day } = req.query;

  if (!day) {
    return res.status(400).json({ error: "Dia é obrigatório" });
  }

  const dayNum = parseInt(day);
  if (isNaN(dayNum) || dayNum < 1 || dayNum > 31) {
    return res.status(400).json({ error: "Dia deve estar entre 1 e 31" });
  }

  try {
    // Usar a variável configurada no docker-compose (NEXT_PUBLIC_ML_API_URL)
    const mlServiceUrl = process.env.NEXT_PUBLIC_ML_API_URL || process.env.NEXT_PUBLIC_API_ML || process.env.NEXT_PUBLIC_ML_URL || process.env.NEXT_PUBLIC_API_URL;

    console.log('Env vars:', {
      NEXT_PUBLIC_ML_API_URL: process.env.NEXT_PUBLIC_ML_API_URL,
      NEXT_PUBLIC_API_ML: process.env.NEXT_PUBLIC_API_ML,
      NEXT_PUBLIC_ML_URL: process.env.NEXT_PUBLIC_ML_URL,
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    });

    if (!mlServiceUrl) {
      console.error("NEXT_PUBLIC_ML_API_URL / NEXT_PUBLIC_API_ML não configurada");
      return res.status(500).json({ error: "Serviço ML não configurado" });
    }

    // O serviço ML neste repositório expõe /predict
    console.log(`Chamando ML service: ${mlServiceUrl}/predict`);
    const response = await fetch(`${mlServiceUrl}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dia: dayNum }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Erro do serviço ML: ${response.status}`, errorText);
      return res.status(response.status).json({ error: "Erro ao gerar aposta: " + errorText });
    }

    const data = await response.json();

    // Normalizar resposta para o frontend: usar primeiro jogo sugerido ou combinacoes_geradas
    const generated = Array.isArray(data.jogos_sugeridos) && data.jogos_sugeridos.length > 0
      ? data.jogos_sugeridos[0]
      : (Array.isArray(data.combinacoes_geradas) ? data.combinacoes_geradas : []);

    res.status(200).json({
      generated_numbers: Array.isArray(generated) ? generated : [],
      raw: data,
    });
  } catch (error) {
    console.error("Erro na API Next.js:", error?.message || error);
    res.status(500).json({ error: "Erro ao gerar aposta: " + (error?.message || String(error)) });
  }
}
