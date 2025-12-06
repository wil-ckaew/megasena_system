use actix_web::{HttpResponse, Responder};
use crate::ApiResponse;

pub async fn not_found() -> impl Responder {
    HttpResponse::NotFound().json(ApiResponse::<()>::error("Endpoint não encontrado"))
}
