use actix_cors::Cors;
use actix_web::{get, post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use chrono;
use reqwest;
use rand::Rng;

#[derive(Serialize, Deserialize, Debug)]
struct HealthCheck {
    status: String,
    service: String,
    version: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct GenerateRequest {
    day: i32,
}

#[derive(Serialize, Deserialize, Debug)]
struct Game {
    numbers: Vec<i32>,
    sum: i32,
    high_numbers: i32,
    even_numbers: i32,
    source: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct GenerateResponse {
    success: bool,
    games: Vec<Game>,
    day: i32,
    timestamp: String,
    method: String,
}

#[get("/")]
async fn root() -> impl Responder {
    HttpResponse::Ok().json(HealthCheck {
        status: "ok".to_string(),
        service: "MegaSena AI Backend (Proxy to Python ML)".to_string(),
        version: "2.0.0".to_string(),
    })
}

#[get("/health")]
async fn health() -> impl Responder {
    // Verificar também se Python está respondendo
    let python_ok = match reqwest::get("http://localhost:5000/health").await {
        Ok(resp) => resp.status().is_success(),
        Err(_) => false,
    };
    
    HttpResponse::Ok().json(HealthCheck {
        status: if python_ok { "healthy" } else { "partial" }.to_string(),
        service: "MegaSena AI Backend".to_string(),
        version: "2.0.0".to_string(),
    })
}

#[post("/api/generate")]
async fn generate_game(req: web::Json<GenerateRequest>) -> impl Responder {
    let day = req.day;
    
    println!("📡 Recebido pedido para dia: {}", day);
    println!("🔗 Redirecionando para Python ML Service...");
    
    // Tentar usar Python ML primeiro
    match call_python_ml(day).await {
        Ok(python_game) => {
            println!("✅ Python ML retornou: {:?}", python_game.numbers);
            
            HttpResponse::Ok().json(GenerateResponse {
                success: true,
                games: vec![python_game],
                day,
                timestamp: chrono::Utc::now().to_rfc3339(),
                method: "python_ml".to_string(),
            })
        }
        Err(err) => {
            println!("⚠️  Python ML falhou: {}. Usando fallback Rust.", err);
            
            // Fallback: algoritmo simples (apenas para emergência)
            let fallback_game = generate_fallback();
            
            HttpResponse::Ok().json(GenerateResponse {
                success: true,
                games: vec![fallback_game],
                day,
                timestamp: chrono::Utc::now().to_rfc3339(),
                method: "rust_fallback".to_string(),
            })
        }
    }
}

async fn call_python_ml(day: i32) -> Result<Game, String> {
    let client = reqwest::Client::new();
    
    let response = client.post("http://localhost:5000/api/generate")
        .json(&serde_json::json!({
            "day": day,
            "method": "hybrid"
        }))
        .send()
        .await
        .map_err(|e| format!("Erro de conexão: {}", e))?;
    
    if !response.status().is_success() {
        return Err(format!("Python ML retornou erro: {}", response.status()));
    }
    
    let json: serde_json::Value = response.json().await
        .map_err(|e| format!("Erro ao parsear JSON: {}", e))?;
    
    let game_data = &json["games"][0];
    
    Ok(Game {
        numbers: game_data["numbers"].as_array()
            .unwrap()
            .iter()
            .map(|n| n.as_i64().unwrap() as i32)
            .collect(),
        sum: game_data["sum"].as_i64().unwrap() as i32,
        high_numbers: game_data["high_numbers"].as_i64().unwrap() as i32,
        even_numbers: game_data["even_numbers"].as_i64().unwrap() as i32,
        source: "python_ml".to_string(),
    })
}

fn generate_fallback() -> Game {
    // Apenas fallback simples - NÃO é a IA!
    let mut rng = rand::thread_rng();
    let mut numbers = Vec::new();
    
    // Gerar 6 números únicos (apenas random, sem IA)
    while numbers.len() < 6 {
        let num = rng.gen_range(1..=60);
        if !numbers.contains(&num) {
            numbers.push(num);
        }
    }
    
    numbers.sort();
    
    let sum: i32 = numbers.iter().sum();
    let high_numbers = numbers.iter().filter(|&&n| n >= 35).count() as i32;
    let even_numbers = numbers.iter().filter(|&&n| n % 2 == 0).count() as i32;
    
    Game {
        numbers,
        sum,
        high_numbers,
        even_numbers,
        source: "rust_fallback".to_string(),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    println!("🚀 Iniciando MegaSena Backend Proxy na porta 8080...");
    println!("🔗 Conectando ao Python ML Service (porta 5000)...");
    
    HttpServer::new(|| {
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header()
            .max_age(3600);
        
        App::new()
            .wrap(cors)
            .service(root)
            .service(health)
            .service(generate_game)
    })
    .bind(("0.0.0.0", 8080))?
    .run()
    .await
}
