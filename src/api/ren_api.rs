use crate::Message;
use log::debug;
use reqwest;
use serde::Deserialize;
use serde_json;

// API constants
pub const API_HOST: &str = "http://localhost:8000";
pub const API_VERSION: &str = "v1";

#[derive(Debug, Clone, Deserialize)]
pub struct Node {
    pub destination_hash: String,
    pub display_name: Option<String>,
    pub updated_at: i64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ApiStatus {
    pub status: String,
    pub address: String,
}

pub fn fetch_api_status() -> iced::Command<Message> {
    iced::Command::perform(
        async {
            match reqwest::get(&format!("{}/api/{}/status", API_HOST, API_VERSION)).await {
                Ok(response) => match response.json::<ApiStatus>().await {
                    Ok(status) => Ok(status),
                    Err(e) => Err(e.to_string()),
                },
                Err(e) => Err(e.to_string()),
            }
        },
        |result| Message::ApiStatusReceived(Box::new(result)),
    )
}

pub fn fetch_nodes() -> iced::Command<Message> {
    iced::Command::perform(
        async {
            match reqwest::get(&format!("{}/api/{}/nodes", API_HOST, API_VERSION)).await {
                Ok(response) => match response.json::<Vec<Node>>().await {
                    Ok(nodes) => Ok(nodes),
                    Err(e) => Err(e.to_string()),
                },
                Err(e) => Err(e.to_string()),
            }
        },
        |result| Message::NodesUpdated(Box::new(result)),
    )
}

pub fn fetch_page(address: String, html_enabled: bool) -> iced::Command<Message> {
    debug!("Fetching page: {}", address);
    iced::Command::perform(
        async move {
            let client = reqwest::Client::new();
            let parts: Vec<&str> = address.split(':').collect();
            if parts.len() != 2 {
                return Err("Invalid address format. Use: hash:/page/path".to_string());
            }

            let hash = parts[0];
            if html_enabled {
                let html_path = "/pages/index.html";
                let html_result = client
                    .post(&format!("{}/api/{}/page", API_HOST, API_VERSION))
                    .json(&serde_json::json!({
                        "destination_hash": hash,
                        "page_path": html_path,
                    }))
                    .send()
                    .await;

                if let Ok(response) = html_result {
                    if response.status().is_success() {
                        return response
                            .json::<serde_json::Value>()
                            .await
                            .map(|json| {
                                json.get("content")
                                    .and_then(|c| c.as_str())
                                    .unwrap_or("Invalid response format")
                                    .to_string()
                            })
                            .map_err(|e| e.to_string());
                    }
                }
            }

            let path = parts[1];
            match client
                .post(&format!("{}/api/{}/page", API_HOST, API_VERSION))
                .json(&serde_json::json!({
                    "destination_hash": hash,
                    "page_path": path,
                }))
                .send()
                .await
            {
                Ok(response) => {
                    if response.status() == 404 {
                        Ok("Requesting path to destination...".to_string())
                    } else if !response.status().is_success() {
                        Err(format!("Server error: {}", response.status()))
                    } else {
                        match response.json::<serde_json::Value>().await {
                            Ok(json) => match json.get("content") {
                                Some(content) => Ok(content
                                    .as_str()
                                    .unwrap_or("Invalid response format")
                                    .to_string()),
                                None => Err("No content in response".to_string()),
                            },
                            Err(e) => Err(e.to_string()),
                        }
                    }
                }
                Err(e) => Err(e.to_string()),
            }
        },
        |result| {
            debug!("Page fetch result: {:?}", result);
            Message::PageLoaded(Box::new(result))
        },
    )
}
