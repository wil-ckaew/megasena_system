pub mod handlers;

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
    pub timestamp: String,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        ApiResponse {
            success: true,
            data: Some(data),
            error: None,
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
    }
    
    pub fn error(message: &str) -> Self {
        ApiResponse {
            success: false,
            data: None,
            error: Some(message.to_string()),
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
    }
}
