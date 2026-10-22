use crate::operation::{
    ApiResponse, OperationDefinition, RequestOptions, ResponseBody, ResponseMode,
};
use crate::operations_generated;
use crate::{Error, Services};
use percent_encoding::{utf8_percent_encode, NON_ALPHANUMERIC};
use reqwest::header::{
    HeaderMap, HeaderValue, ACCEPT, AUTHORIZATION, CONTENT_TYPE, RETRY_AFTER, USER_AGENT,
};
use reqwest::{Method, StatusCode, Url};
use serde::Serialize;
use serde_json::{json, Map, Value};
use std::ops::Deref;
use std::sync::Arc;
use std::time::Duration;

pub const DEFAULT_BASE_URL: &str = "https://api.crawlora.net/api/v1";
const DEFAULT_TIMEOUT: Duration = Duration::from_secs(30);
const DEFAULT_RETRIES: usize = 3;
const MAX_RETRY_DELAY: Duration = Duration::from_secs(8);

#[derive(Clone)]
pub struct CrawloraClient {
    pub(crate) inner: Arc<ClientInner>,
    services: Services,
}

impl CrawloraClient {
    pub fn new(api_key: impl Into<String>) -> Result<Self, Error> {
        Self::builder().api_key(api_key).build()
    }

    pub fn builder() -> CrawloraClientBuilder {
        CrawloraClientBuilder::default()
    }

    pub async fn call<P: Serialize>(
        &self,
        operation_id: &str,
        params: P,
    ) -> Result<ApiResponse, Error> {
        self.call_with_options(operation_id, params, RequestOptions::default())
            .await
    }

    pub async fn call_with_options<P: Serialize>(
        &self,
        operation_id: &str,
        params: P,
        options: RequestOptions,
    ) -> Result<ApiResponse, Error> {
        self.inner.call(operation_id, &params, options).await
    }

    pub fn paginate_offset<'a, P: Serialize>(
        &'a self,
        operation_id: impl Into<String>,
        params: P,
        page_parameter: impl Into<String>,
        first_page: u64,
        max_pages: usize,
    ) -> Result<OffsetPaginator<'a>, Error> {
        let operation_id = operation_id.into();
        let page_parameter = page_parameter.into();
        require_query_parameter(&operation_id, &page_parameter)?;
        Ok(OffsetPaginator {
            client: self,
            operation_id,
            params: serde_json::to_value(params)?,
            page_parameter,
            next_page: first_page,
            remaining: max_pages,
        })
    }

    pub fn paginate_cursor<'a, P: Serialize>(
        &'a self,
        operation_id: impl Into<String>,
        params: P,
        cursor_parameter: impl Into<String>,
        next_cursor_pointer: impl Into<String>,
        max_pages: usize,
    ) -> Result<CursorPaginator<'a>, Error> {
        let operation_id = operation_id.into();
        let cursor_parameter = cursor_parameter.into();
        require_query_parameter(&operation_id, &cursor_parameter)?;
        Ok(CursorPaginator {
            client: self,
            operation_id,
            params: serde_json::to_value(params)?,
            cursor_parameter,
            next_cursor_pointer: next_cursor_pointer.into(),
            next_cursor: None,
            remaining: max_pages,
            finished: false,
        })
    }
}

impl Deref for CrawloraClient {
    type Target = Services;

    fn deref(&self) -> &Self::Target {
        &self.services
    }
}

#[derive(Default)]
pub struct CrawloraClientBuilder {
    api_key: Option<String>,
    jwt_token: Option<String>,
    base_url: Option<String>,
    timeout: Option<Duration>,
    max_retries: Option<usize>,
    user_agent: Option<String>,
    default_headers: HeaderMap,
    http_client: Option<reqwest::Client>,
}

impl CrawloraClientBuilder {
    pub fn api_key(mut self, api_key: impl Into<String>) -> Self {
        self.api_key = Some(api_key.into());
        self
    }

    pub fn jwt_token(mut self, jwt_token: impl Into<String>) -> Self {
        self.jwt_token = Some(jwt_token.into());
        self
    }

    pub fn base_url(mut self, base_url: impl Into<String>) -> Self {
        self.base_url = Some(base_url.into());
        self
    }

    pub fn timeout(mut self, timeout: Duration) -> Self {
        self.timeout = Some(timeout);
        self
    }

    pub fn max_retries(mut self, max_retries: usize) -> Self {
        self.max_retries = Some(max_retries);
        self
    }

    pub fn user_agent(mut self, user_agent: impl Into<String>) -> Self {
        self.user_agent = Some(user_agent.into());
        self
    }

    pub fn default_headers(mut self, headers: HeaderMap) -> Self {
        self.default_headers = headers;
        self
    }

    pub fn http_client(mut self, http_client: reqwest::Client) -> Self {
        self.http_client = Some(http_client);
        self
    }

    pub fn build(self) -> Result<CrawloraClient, Error> {
        let base_url_text = self.base_url.unwrap_or_else(|| DEFAULT_BASE_URL.to_owned());
        let base_url = Url::parse(base_url_text.trim_end_matches('/'))
            .map_err(|error| Error::InvalidBaseUrl(error.to_string()))?;
        if !matches!(base_url.scheme(), "http" | "https") || base_url.host_str().is_none() {
            return Err(Error::InvalidBaseUrl(base_url_text));
        }

        let timeout = self.timeout.unwrap_or(DEFAULT_TIMEOUT);
        let user_agent = self
            .user_agent
            .unwrap_or_else(|| format!("crawlora-rust-sdk/{}", env!("CARGO_PKG_VERSION")));
        let mut headers = self.default_headers;
        if let Ok(value) = HeaderValue::from_str(&user_agent) {
            headers.insert(USER_AGENT, value);
        }
        let http = match self.http_client {
            Some(client) => client,
            None => reqwest::Client::builder()
                .default_headers(headers.clone())
                .timeout(timeout)
                .build()?,
        };
        let inner = Arc::new(ClientInner {
            http,
            base_url,
            api_key: self.api_key,
            jwt_token: self.jwt_token,
            default_headers: headers,
            timeout,
            max_retries: self.max_retries.unwrap_or(DEFAULT_RETRIES),
        });
        let services = Services::new(Arc::clone(&inner));
        Ok(CrawloraClient { inner, services })
    }
}

pub(crate) struct ClientInner {
    http: reqwest::Client,
    base_url: Url,
    api_key: Option<String>,
    jwt_token: Option<String>,
    default_headers: HeaderMap,
    timeout: Duration,
    max_retries: usize,
}

impl ClientInner {
    pub(crate) async fn call<P: Serialize>(
        &self,
        operation_id: &str,
        params: &P,
        options: RequestOptions,
    ) -> Result<ApiResponse, Error> {
        let operation = operations_generated::get(operation_id)
            .ok_or_else(|| Error::UnknownOperation(operation_id.to_owned()))?;
        let params = serde_json::to_value(params)?;
        validate_required(operation, &params)?;
        self.validate_auth(operation)?;

        let retries = options.max_retries.unwrap_or(self.max_retries);
        let mut attempt = 0usize;
        loop {
            let request = self.build_request(operation, &params, &options)?;
            match request.send().await {
                Ok(response) => {
                    let status = response.status();
                    let retry_after = response
                        .headers()
                        .get(RETRY_AFTER)
                        .and_then(|value| value.to_str().ok())
                        .and_then(|value| value.parse::<u64>().ok())
                        .map(Duration::from_secs);
                    if should_retry_status(status, operation.method, options.retry_non_idempotent)
                        && attempt < retries
                    {
                        let delay = retry_after
                            .map(|delay| delay.min(MAX_RETRY_DELAY))
                            .unwrap_or_else(|| backoff(attempt));
                        tokio::time::sleep(delay).await;
                        attempt += 1;
                        continue;
                    }

                    let headers = response.headers().clone();
                    let bytes = response.bytes().await?;
                    if !status.is_success() {
                        let request_id = header_string(&headers, "x-request-id")
                            .or_else(|| header_string(&headers, "x-crawlora-request-id"));
                        return Err(Error::Api {
                            status,
                            body: String::from_utf8_lossy(&bytes).into_owned(),
                            request_id,
                        });
                    }
                    let body = decode_body(bytes.to_vec(), &headers, options.response_mode)?;
                    return Ok(ApiResponse {
                        status,
                        headers,
                        body,
                    });
                }
                Err(error)
                    if attempt < retries
                        && (is_safe_to_retry(operation.method) || options.retry_non_idempotent) =>
                {
                    let _ = error;
                    tokio::time::sleep(backoff(attempt)).await;
                    attempt += 1;
                }
                Err(error) => return Err(Error::Transport(error)),
            }
        }
    }

    fn validate_auth(&self, operation: &OperationDefinition) -> Result<(), Error> {
        let needs_key = operation.security.contains(&"ApiKeyAuth");
        let needs_jwt = operation.security.contains(&"JWTAuth");
        if (needs_key || needs_jwt) && self.api_key.is_none() && self.jwt_token.is_none() {
            return Err(Error::MissingCredentials {
                operation: operation.id.to_owned(),
            });
        }
        if needs_key && !needs_jwt && self.api_key.is_none() {
            return Err(Error::MissingCredentials {
                operation: operation.id.to_owned(),
            });
        }
        if needs_jwt && !needs_key && self.jwt_token.is_none() {
            return Err(Error::MissingCredentials {
                operation: operation.id.to_owned(),
            });
        }
        Ok(())
    }

    fn build_request(
        &self,
        operation: &OperationDefinition,
        params: &Value,
        options: &RequestOptions,
    ) -> Result<reqwest::RequestBuilder, Error> {
        let mut path = operation.path.to_owned();
        for parameter in operation.path_params {
            let value = required_value(operation, params, parameter.name)?;
            validate_enum(operation, parameter, value)?;
            let raw_value = value_to_string(value);
            let encoded = utf8_percent_encode(&raw_value, NON_ALPHANUMERIC).to_string();
            path = path.replace(&format!("{{{}}}", parameter.name), &encoded);
        }
        let url_text = format!("{}{}", self.base_url.as_str().trim_end_matches('/'), path);
        let mut url =
            Url::parse(&url_text).map_err(|error| Error::InvalidBaseUrl(error.to_string()))?;
        let mut query = Vec::<(String, String)>::new();
        for parameter in operation.query_params {
            let Some(value) = value_at(params, parameter.name) else {
                if parameter.required {
                    return Err(missing_parameter(operation, parameter.name));
                }
                continue;
            };
            if value.is_null() {
                if parameter.required {
                    return Err(missing_parameter(operation, parameter.name));
                }
                continue;
            }
            append_query_values(&mut query, parameter, value);
        }
        url.query_pairs_mut().extend_pairs(query.iter());

        let method = Method::from_bytes(operation.method.as_bytes())
            .map_err(|_| Error::UnknownOperation(operation.id.to_owned()))?;
        let mut request = self.http.request(method.clone(), url);
        request = request.timeout(options.timeout.unwrap_or(self.timeout));

        for (name, value) in &self.default_headers {
            request = request.header(name, value);
        }
        for (name, value) in &options.headers {
            request = request.header(name, value);
        }
        if operation.security.contains(&"ApiKeyAuth") {
            if let Some(api_key) = &self.api_key {
                request = request.header("x-api-key", api_key);
            }
        }
        if operation.security.contains(&"JWTAuth") {
            if let Some(token) = &self.jwt_token {
                request = request.header(AUTHORIZATION, format!("Bearer {token}"));
            }
        }
        if !operation.produces.is_empty() {
            request = request.header(ACCEPT, operation.produces.join(", "));
        }

        if !operation.form_params.is_empty() {
            if operation
                .consumes
                .iter()
                .any(|content_type| content_type.contains("multipart/form-data"))
            {
                let mut form = reqwest::multipart::Form::new();
                for parameter in operation.form_params {
                    let Some(value) = value_at(params, parameter.name) else {
                        if parameter.required {
                            return Err(missing_parameter(operation, parameter.name));
                        }
                        continue;
                    };
                    if value.is_null() {
                        continue;
                    }
                    if parameter.kind == Some("file") {
                        form = form.part(
                            parameter.name,
                            reqwest::multipart::Part::bytes(value_to_bytes(value)),
                        );
                    } else {
                        form = form.text(parameter.name, value_to_string(value));
                    }
                }
                request = request.multipart(form);
            } else {
                let mut form = Vec::<(String, String)>::new();
                for parameter in operation.form_params {
                    let Some(value) = value_at(params, parameter.name) else {
                        if parameter.required {
                            return Err(missing_parameter(operation, parameter.name));
                        }
                        continue;
                    };
                    if !value.is_null() {
                        form.push((parameter.name.to_owned(), value_to_string(value)));
                    }
                }
                request = request.form(&form);
            }
        } else if let Some(body_name) = operation.body_param {
            if let Some(body) = value_at(params, body_name) {
                if !body.is_null() {
                    request = request.json(body);
                }
            } else if operation.body_required {
                return Err(missing_parameter(operation, body_name));
            }
        }

        Ok(request)
    }
}

fn value_at<'a>(value: &'a Value, key: &str) -> Option<&'a Value> {
    value.as_object()?.get(key)
}

fn required_value<'a>(
    operation: &OperationDefinition,
    params: &'a Value,
    key: &str,
) -> Result<&'a Value, Error> {
    value_at(params, key)
        .filter(|value| !value.is_null())
        .ok_or_else(|| missing_parameter(operation, key))
}

fn validate_required(operation: &OperationDefinition, params: &Value) -> Result<(), Error> {
    for parameter in operation.path_params {
        let value = required_value(operation, params, parameter.name)?;
        validate_enum(operation, parameter, value)?;
    }
    for parameter in operation.query_params.iter().chain(operation.form_params) {
        if let Some(value) = value_at(params, parameter.name).filter(|value| !value.is_null()) {
            if parameter.required {
                required_value(operation, params, parameter.name)?;
            }
            validate_enum(operation, parameter, value)?;
        } else if parameter.required {
            return Err(missing_parameter(operation, parameter.name));
        }
    }
    if operation.body_required {
        let name = operation.body_param.unwrap_or("body");
        required_value(operation, params, name)?;
    }
    Ok(())
}

fn validate_enum(
    operation: &OperationDefinition,
    parameter: &crate::operation::ParameterDefinition,
    value: &Value,
) -> Result<(), Error> {
    if parameter.enum_values.is_empty() {
        return Ok(());
    }
    let allowed = parameter.enum_values;
    let values = value
        .as_array()
        .map(|items| items.as_slice())
        .unwrap_or(std::slice::from_ref(value));
    for item in values {
        let candidate = value_to_string(item);
        if !allowed.iter().any(|expected| *expected == candidate) {
            return Err(Error::InvalidParameterValue {
                operation: operation.id.to_owned(),
                parameter: parameter.name.to_owned(),
                value: candidate,
            });
        }
    }
    Ok(())
}

fn missing_parameter(operation: &OperationDefinition, parameter: &str) -> Error {
    Error::MissingParameter {
        operation: operation.id.to_owned(),
        parameter: parameter.to_owned(),
    }
}

fn value_to_string(value: &Value) -> String {
    match value {
        Value::String(text) => text.clone(),
        Value::Null => String::new(),
        Value::Array(_) | Value::Object(_) => value.to_string(),
        _ => value.to_string(),
    }
}

fn value_to_bytes(value: &Value) -> Vec<u8> {
    match value {
        Value::String(text) => text.as_bytes().to_vec(),
        Value::Array(items) => items
            .iter()
            .filter_map(Value::as_u64)
            .map(|value| value as u8)
            .collect(),
        _ => value.to_string().into_bytes(),
    }
}

fn append_query_values(
    query: &mut Vec<(String, String)>,
    parameter: &crate::operation::ParameterDefinition,
    value: &Value,
) {
    if let Some(values) = value.as_array() {
        let format = parameter.collection_format.unwrap_or("csv");
        if format == "multi" {
            for item in values {
                query.push((parameter.name.to_owned(), value_to_string(item)));
            }
            return;
        }
        let separator = match format {
            "ssv" => " ",
            "tsv" => "\t",
            "pipes" => "|",
            _ => ",",
        };
        query.push((
            parameter.name.to_owned(),
            values
                .iter()
                .map(value_to_string)
                .collect::<Vec<_>>()
                .join(separator),
        ));
    } else {
        query.push((parameter.name.to_owned(), value_to_string(value)));
    }
}

fn should_retry_status(status: StatusCode, method: &str, retry_non_idempotent: bool) -> bool {
    if status == StatusCode::TOO_MANY_REQUESTS {
        return true;
    }
    let retryable_server_error = matches!(
        status,
        StatusCode::INTERNAL_SERVER_ERROR
            | StatusCode::BAD_GATEWAY
            | StatusCode::SERVICE_UNAVAILABLE
            | StatusCode::GATEWAY_TIMEOUT
    );
    retryable_server_error && (is_safe_to_retry(method) || retry_non_idempotent)
}

fn is_safe_to_retry(method: &str) -> bool {
    matches!(method, "GET" | "HEAD" | "OPTIONS" | "PUT" | "DELETE")
}

fn backoff(attempt: usize) -> Duration {
    let multiplier = 1u32.checked_shl(attempt.min(5) as u32).unwrap_or(32);
    Duration::from_millis(250 * u64::from(multiplier)).min(MAX_RETRY_DELAY)
}

fn header_string(headers: &HeaderMap, name: &str) -> Option<String> {
    headers
        .get(name)
        .and_then(|value| value.to_str().ok())
        .map(str::to_owned)
}

fn decode_body(
    bytes: Vec<u8>,
    headers: &HeaderMap,
    mode: ResponseMode,
) -> Result<ResponseBody, Error> {
    let content_type = headers
        .get(CONTENT_TYPE)
        .and_then(|value| value.to_str().ok())
        .map(str::to_owned);
    match mode {
        ResponseMode::Json => Ok(ResponseBody::Json(serde_json::from_slice(&bytes)?)),
        ResponseMode::Text => Ok(ResponseBody::Text(
            String::from_utf8_lossy(&bytes).into_owned(),
        )),
        ResponseMode::Bytes => Ok(ResponseBody::Bytes(bytes)),
        ResponseMode::Auto => {
            let is_json = content_type
                .as_deref()
                .map(|value| value.contains("application/json") || value.contains("+json"))
                .unwrap_or(false);
            let is_text = content_type
                .as_deref()
                .map(|value| value.starts_with("text/"))
                .unwrap_or(false);
            if is_json {
                Ok(ResponseBody::Json(serde_json::from_slice(&bytes)?))
            } else if is_text {
                Ok(ResponseBody::Text(
                    String::from_utf8_lossy(&bytes).into_owned(),
                ))
            } else {
                Ok(ResponseBody::Bytes(bytes))
            }
        }
    }
}

fn require_query_parameter(operation_id: &str, parameter: &str) -> Result<(), Error> {
    let operation = operations_generated::get(operation_id)
        .ok_or_else(|| Error::UnknownOperation(operation_id.to_owned()))?;
    if operation
        .query_params
        .iter()
        .any(|item| item.name == parameter)
    {
        Ok(())
    } else {
        Err(Error::InvalidPaginationParameter {
            operation: operation_id.to_owned(),
            parameter: parameter.to_owned(),
        })
    }
}

pub struct OffsetPaginator<'a> {
    client: &'a CrawloraClient,
    operation_id: String,
    params: Value,
    page_parameter: String,
    next_page: u64,
    remaining: usize,
}

impl OffsetPaginator<'_> {
    pub async fn next(&mut self) -> Result<Option<ApiResponse>, Error> {
        if self.remaining == 0 {
            return Ok(None);
        }
        ensure_object(&mut self.params).insert(self.page_parameter.clone(), json!(self.next_page));
        self.next_page += 1;
        self.remaining -= 1;
        self.client
            .call(&self.operation_id, &self.params)
            .await
            .map(Some)
    }
}

pub struct CursorPaginator<'a> {
    client: &'a CrawloraClient,
    operation_id: String,
    params: Value,
    cursor_parameter: String,
    next_cursor_pointer: String,
    next_cursor: Option<Value>,
    remaining: usize,
    finished: bool,
}

impl CursorPaginator<'_> {
    pub async fn next(&mut self) -> Result<Option<ApiResponse>, Error> {
        if self.finished || self.remaining == 0 {
            return Ok(None);
        }
        if let Some(cursor) = self.next_cursor.take() {
            ensure_object(&mut self.params).insert(self.cursor_parameter.clone(), cursor);
        }
        self.remaining -= 1;
        let response = self.client.call(&self.operation_id, &self.params).await?;
        let next = response
            .body
            .as_json()
            .and_then(|body| body.pointer(&self.next_cursor_pointer))
            .filter(|value| {
                !value.is_null() && value.as_str().map(|text| !text.is_empty()).unwrap_or(true)
            })
            .cloned();
        if next.is_some() {
            self.next_cursor = next;
        } else {
            self.finished = true;
        }
        Ok(Some(response))
    }
}

fn ensure_object(value: &mut Value) -> &mut Map<String, Value> {
    if !value.is_object() {
        *value = Value::Object(Map::new());
    }
    value.as_object_mut().expect("object was initialized")
}
