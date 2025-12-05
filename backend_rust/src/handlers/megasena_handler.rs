use actix_web::{post, web, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use reqwest::Client;
use std::env;

#[derive(Serialize, Deserialize)]
pub struct PredictRequest {
    pub dia: i32,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct PredictResponse {
    pub combinacoes_geradas: Vec<i32>,
    pub dia: i32,
    pub jogos_sugeridos: Vec<Vec<i32>>,
    pub previsao_modelo: Vec<i32>,
    pub probabilidades: Vec<f64>,
    pub grafico_base64: Option<String>,
}

#[post("/api/megasena/predict")]
pub async fn predict_megasena(req: web::Json<PredictRequest>) -> impl Responder {
    let flask_url = env::var("FLASK_URL").unwrap_or_else(|_| "http://127.0.0.1:5000/predict".into());
    let client = Client::new();

    match client.post(&flask_url).json(&*req).send().await {
        Ok(resp) => {
            if resp.status().is_success() {
                match resp.json::<PredictResponse>().await {
                    Ok(data) => HttpResponse::Ok().json(data),
                    Err(e) => HttpResponse::InternalServerError().json(
                        serde_json::json!({ "erro": format!("Falha ao interpretar resposta do Flask: {}", e) })
                    ),
                }
            } else {
                let status = resp.status();
                HttpResponse::BadGateway().json(
                    serde_json::json!({ "erro": format!("Flask retornou status {}", status) })
                )
            }
        }
        Err(e) => HttpResponse::InternalServerError().json(
            serde_json::json!({ "erro": format!("Erro ao conectar com o Flask: {}", e) })
        ),
    }
}
