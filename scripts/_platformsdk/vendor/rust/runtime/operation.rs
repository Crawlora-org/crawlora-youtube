use reqwest::{header::HeaderMap, StatusCode};
use serde::de::DeserializeOwned;
use serde_json::Value;
use std::time::Duration;

use crate::Error;

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub enum ResponseMode {
    #[default]
    Auto,
    Json,
    Text,
    Bytes,
}

#[derive(Clone, Debug)]
pub struct RequestOptions {
    pub headers: HeaderMap,
    pub timeout: Option<Duration>,
    pub max_retries: Option<usize>,
    pub response_mode: ResponseMode,
    pub retry_non_idempotent: bool,
}

impl Default for RequestOptions {
    fn default() -> Self {
        Self {
            headers: HeaderMap::new(),
            timeout: None,
            max_retries: None,
            response_mode: ResponseMode::Auto,
            retry_non_idempotent: false,
        }
    }
}

#[derive(Clone, Debug)]
pub enum ResponseBody {
    Json(Value),
    Text(String),
    Bytes(Vec<u8>),
}

impl ResponseBody {
    pub fn as_json(&self) -> Option<&Value> {
        match self {
            Self::Json(value) => Some(value),
            _ => None,
        }
    }

    pub fn into_json(self) -> Result<Value, Error> {
        match self {
            Self::Json(value) => Ok(value),
            Self::Text(text) => Ok(serde_json::from_str(&text)?),
            Self::Bytes(bytes) => Ok(serde_json::from_slice(&bytes)?),
        }
    }
}

#[derive(Clone, Debug)]
pub struct ApiResponse {
    pub status: StatusCode,
    pub headers: HeaderMap,
    pub body: ResponseBody,
}

impl ApiResponse {
    pub fn json<T: DeserializeOwned>(&self) -> Result<T, Error> {
        match &self.body {
            ResponseBody::Json(value) => Ok(serde_json::from_value(value.clone())?),
            ResponseBody::Text(text) => Ok(serde_json::from_str(text)?),
            ResponseBody::Bytes(bytes) => Ok(serde_json::from_slice(bytes)?),
        }
    }

    pub fn into_json<T: DeserializeOwned>(self) -> Result<T, Error> {
        match self.body {
            ResponseBody::Json(value) => Ok(serde_json::from_value(value)?),
            ResponseBody::Text(text) => Ok(serde_json::from_str(&text)?),
            ResponseBody::Bytes(bytes) => Ok(serde_json::from_slice(&bytes)?),
        }
    }

    pub fn request_id(&self) -> Option<&str> {
        self.headers
            .get("x-request-id")
            .or_else(|| self.headers.get("x-crawlora-request-id"))
            .and_then(|value| value.to_str().ok())
    }
}

#[derive(Clone, Copy, Debug)]
pub(crate) struct ParameterDefinition {
    pub name: &'static str,
    pub collection_format: Option<&'static str>,
    pub kind: Option<&'static str>,
    pub required: bool,
    pub enum_values: &'static [&'static str],
}

#[derive(Clone, Copy, Debug)]
pub(crate) struct OperationDefinition {
    pub id: &'static str,
    pub method: &'static str,
    pub path: &'static str,
    pub path_params: &'static [ParameterDefinition],
    pub query_params: &'static [ParameterDefinition],
    pub form_params: &'static [ParameterDefinition],
    pub body_param: Option<&'static str>,
    pub body_required: bool,
    pub consumes: &'static [&'static str],
    pub produces: &'static [&'static str],
    pub security: &'static [&'static str],
}
