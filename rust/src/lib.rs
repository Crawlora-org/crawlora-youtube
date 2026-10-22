mod client;
mod error;
pub mod models;
mod operation;
mod operations_generated;
pub mod services_generated;

pub use client::{
    CrawloraClient, CrawloraClientBuilder, CursorPaginator, OffsetPaginator, DEFAULT_BASE_URL,
};
pub use error::Error;
pub use models::*;
pub use operation::{ApiResponse, RequestOptions, ResponseBody, ResponseMode};
pub use serde_json;
pub use services_generated::*;

pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub type Client = CrawloraClient;
pub type YouTubeClient = CrawloraClient;
