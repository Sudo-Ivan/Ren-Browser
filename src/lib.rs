pub mod api;
pub mod renderers {
    pub mod micron_constants;
    pub mod mu_renderer;
}
pub mod shortcuts;
pub mod styles;

pub use api::{ApiStatus, Node};
pub use renderers::mu_renderer::{MicronRenderer, MicronStyle, RendererType, TextAlignment};

#[derive(Debug, Clone)]
pub enum Message {
    ApiStatusReceived(Box<Result<ApiStatus, String>>),
    NodesUpdated(Box<Result<Vec<Node>, String>>),
    PageLoaded(Box<Result<String, String>>),
    OpenSettings,
    LinkClicked(String),
    ToggleHtmlRenderer(bool),
}
