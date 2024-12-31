pub mod api {
    pub mod ren_api;
}
pub mod renderers {
    pub mod html_renderer;
    pub mod mu_renderer;
    pub mod parsers;
}
pub mod styles;

pub use api::ren_api::{ApiStatus, Node};
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
