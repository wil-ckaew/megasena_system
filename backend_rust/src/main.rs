use actix_web::{get, App, HttpResponse, HttpServer, Responder};

mod handlers;
use handlers::megasena_handler::predict_megasena;

/// Rota raiz para teste do servidor
#[get("/")]
async fn root() -> impl Responder {
    HttpResponse::Ok().body("✅ Backend MegaSena Rust está ativo!")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    println!("🚀 Backend Rust rodando na porta 8080...");

    HttpServer::new(|| {
        App::new()
            .service(root)
            .service(predict_megasena)
    })
    .bind(("0.0.0.0", 8080))?
    .run()
    .await
}
