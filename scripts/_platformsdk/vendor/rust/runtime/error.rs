use reqwest::StatusCode;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum Error {
    #[error("HTTP transport failed: {0}")]
    Transport(#[from] reqwest::Error),
    #[error("failed to encode or decode JSON: {0}")]
    Json(#[from] serde_json::Error),
    #[error("invalid API base URL: {0}")]
    InvalidBaseUrl(String),
    #[error("unknown Crawlora operation `{0}`")]
    UnknownOperation(String),
    #[error("required parameter `{parameter}` is missing for `{operation}`")]
    MissingParameter {
        operation: String,
        parameter: String,
    },
    #[error("operation `{operation}` requires an API key or JWT token")]
    MissingCredentials { operation: String },
    #[error("Crawlora returned HTTP {status}: {body}")]
    Api {
        status: StatusCode,
        body: String,
        request_id: Option<String>,
    },
    #[error("parameter `{parameter}` for `{operation}` has unsupported value `{value}`")]
    InvalidParameterValue {
        operation: String,
        parameter: String,
        value: String,
    },
    #[error("response was not JSON (content type: {content_type:?})")]
    UnexpectedResponse { content_type: Option<String> },
    #[error("pagination parameter `{parameter}` is not declared by operation `{operation}`")]
    InvalidPaginationParameter {
        operation: String,
        parameter: String,
    },
}

impl Error {
    pub fn status(&self) -> Option<StatusCode> {
        match self {
            Self::Api { status, .. } => Some(*status),
            _ => None,
        }
    }

    pub fn request_id(&self) -> Option<&str> {
        match self {
            Self::Api { request_id, .. } => request_id.as_deref(),
            _ => None,
        }
    }
}
