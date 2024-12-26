use iced::{
    executor, theme, time,
    widget::{button, column, row, scrollable, text, text_input, Row},
    Application, Command, Element, Length, Settings, Subscription, Theme,
};

use chrono;
use log::{debug, info, warn, LevelFilter};
use reqwest;
use serde::Deserialize;
use simple_logger::SimpleLogger;
use std::env;

mod styles;
use styles::{Styles, HEADING_SIZE, PADDING, SIDEBAR_WIDTH, SPACING, TAB_HEIGHT, TEXT_SIZE};

pub fn main() -> iced::Result {
    let debug = env::args().any(|arg| arg == "--debug");

    let log_level = if debug {
        LevelFilter::Debug
    } else {
        LevelFilter::Info
    };

    SimpleLogger::new()
        .with_level(log_level)
        .with_module_level("iced", log_level)
        .with_colors(true)
        .with_local_timestamps()
        .init()
        .unwrap();

    debug!("Starting RenBrowser in debug mode");

    // Run the application
    RenBrowser::run(Settings {
        window: iced::window::Settings {
            size: (1280, 720),
            ..Default::default()
        },
        ..Default::default()
    })
}

#[derive(Debug, Clone)]
struct Tab {
    id: usize,
    address: String,
    content: String,
    loading: bool,
    show_address: bool,
}

struct RenBrowser {
    tabs: Vec<Tab>,
    active_tab: usize,
    address_input: String,
    nodes: Vec<Node>,
    api_status: ApiStatus,
    next_tab_id: usize,
}

#[derive(Debug, Clone, Deserialize)]
struct Node {
    destination_hash: String,
    identity_hash: String,
    display_name: Option<String>,
    aspect: String,
    created_at: i64,
    updated_at: i64,
}

#[derive(Debug, Clone, Deserialize)]
struct ApiStatus {
    status: String,
    address: String,
}

#[derive(Debug, Clone)]
enum Message {
    AddTab,
    CloseTab(usize),
    SelectTab(usize),
    AddressInputChanged(String),
    LoadPage,
    ApiStatusReceived(Box<Result<ApiStatus, String>>),
    NodesUpdated(Box<Result<Vec<Node>, String>>),
    PageLoaded(Box<Result<String, String>>),
    ShowAddressBar,
    Tick,
}

impl Application for RenBrowser {
    type Message = Message;
    type Theme = Theme;
    type Executor = executor::Default;
    type Flags = ();

    fn new(_flags: ()) -> (Self, Command<Message>) {
        let initial_tab = Tab {
            id: 0,
            address: String::new(),
            content: String::from("Welcome to Ren Browser"),
            loading: false,
            show_address: true,
        };

        (
            RenBrowser {
                tabs: vec![initial_tab],
                active_tab: 0,
                address_input: String::new(),
                nodes: Vec::new(),
                api_status: ApiStatus {
                    status: String::from("Connecting..."),
                    address: String::new(),
                },
                next_tab_id: 1,
            },
            Command::batch(vec![fetch_api_status(), fetch_nodes()]),
        )
    }

    fn title(&self) -> String {
        String::from("Ren Browser")
    }

    fn update(&mut self, message: Message) -> Command<Message> {
        debug!("Handling message: {:?}", message);
        match message {
            Message::AddTab => {
                self.tabs.push(Tab {
                    id: self.next_tab_id,
                    address: String::new(),
                    content: String::from("New Tab"),
                    loading: false,
                    show_address: true,
                });
                self.active_tab = self.tabs.len() - 1;
                self.next_tab_id += 1;
                Command::none()
            }
            Message::CloseTab(id) => {
                if let Some(index) = self.tabs.iter().position(|tab| tab.id == id) {
                    self.tabs.remove(index);
                    if self.active_tab >= self.tabs.len() {
                        self.active_tab = self.tabs.len().saturating_sub(1);
                    }
                }
                Command::none()
            }
            Message::SelectTab(id) => {
                if let Some(index) = self.tabs.iter().position(|tab| tab.id == id) {
                    self.active_tab = index;
                }
                Command::none()
            }
            Message::AddressInputChanged(address) => {
                debug!("Address input changed: {}", address);
                self.address_input = address;
                Command::none()
            }
            Message::LoadPage => {
                info!("Loading page: {}", self.address_input);
                if let Some(tab) = self.tabs.get_mut(self.active_tab) {
                    tab.loading = true;
                    tab.address = self.address_input.clone();
                    fetch_page(tab.address.clone())
                } else {
                    warn!("No active tab to load page");
                    Command::none()
                }
            }
            Message::ApiStatusReceived(result) => {
                match *result {
                    Ok(status) => {
                        self.api_status = ApiStatus {
                            status: "Connected".to_string(),
                            address: status.address,
                        };
                    }
                    Err(e) => {
                        self.api_status = ApiStatus {
                            status: format!("Error: {}", e),
                            address: String::new(),
                        };
                    }
                }
                Command::none()
            }
            Message::NodesUpdated(result) => {
                match *result {
                    Ok(nodes) => {
                        self.nodes = nodes;
                    }
                    Err(_) => {}
                }
                Command::none()
            }
            Message::PageLoaded(result) => {
                if let Some(tab) = self.tabs.get_mut(self.active_tab) {
                    tab.loading = false;
                    match *result {
                        Ok(content) => {
                            tab.content = content;
                            tab.show_address = false;
                        }
                        Err(e) => {
                            tab.content = format!("Error loading page: {}", e);
                            tab.show_address = true;
                        }
                    }
                }
                Command::none()
            }
            Message::ShowAddressBar => {
                // Implementation for ShowAddressBar message
                Command::none()
            }
            Message::Tick => fetch_nodes(),
        }
    }

    fn view(&self) -> Element<Message> {
        let status_text = text(&self.api_status.status)
            .style(Styles::status_text(self.api_status.status == "Connected"))
            .size(TEXT_SIZE);

        let sidebar = column![
            status_text,
            text(&format!("Address: {}", self.api_status.address)).size(TEXT_SIZE),
            text("Nodes").size(HEADING_SIZE),
            scrollable(
                column(
                    self.nodes
                        .iter()
                        .map(|node| {
                            let name = node.display_name.as_deref().unwrap_or("Unknown");
                            let hash = &node.destination_hash[0..8];
                            let last_seen = chrono::DateTime::from_timestamp(node.updated_at, 0)
                                .map(|dt| dt.format("%Y-%m-%d %H:%M").to_string())
                                .unwrap_or_else(|| "Unknown".to_string());

                            button(
                                column![
                                    text(name).size(TEXT_SIZE),
                                    text(hash).size(TEXT_SIZE - 2),
                                    text(last_seen).size(TEXT_SIZE - 4)
                                ]
                                .spacing(SPACING / 2),
                            )
                            .style(Styles::node_button())
                            .width(Length::Fill)
                            .on_press(Message::AddressInputChanged(node.destination_hash.clone()))
                            .into()
                        })
                        .collect()
                )
                .spacing(SPACING)
            )
            .height(Length::Fill)
        ]
        .width(Length::Fixed(SIDEBAR_WIDTH))
        .spacing(SPACING)
        .padding(PADDING);

        let tab_bar = Row::with_children(
            self.tabs
                .iter()
                .map(|tab| {
                    let tab_text = if self.tabs.len() > 1 && !tab.address.is_empty() {
                        if self.active_tab
                            == self.tabs.iter().position(|t| t.id == tab.id).unwrap_or(0)
                        {
                            &tab.address
                        } else {
                            tab.address.split('/').last().unwrap_or("New Tab")
                        }
                    } else {
                        if tab.address.is_empty() {
                            "New Tab"
                        } else {
                            &tab.address
                        }
                    };

                    button(
                        row![
                            text(tab_text).size(TEXT_SIZE),
                            button(text("×"))
                                .on_press(Message::CloseTab(tab.id))
                                .style(theme::Button::Text)
                        ]
                        .spacing(5),
                    )
                    .on_press(Message::SelectTab(tab.id))
                    .style(Styles::tab_button(
                        self.active_tab
                            == self.tabs.iter().position(|t| t.id == tab.id).unwrap_or(0),
                    ))
                    .height(Length::Fixed(TAB_HEIGHT as f32))
                    .padding([2, 8])
                    .into()
                })
                .chain(std::iter::once(
                    button(text("+"))
                        .on_press(Message::AddTab)
                        .style(theme::Button::Secondary)
                        .padding([2, 8])
                        .height(Length::Fixed(TAB_HEIGHT as f32))
                        .into(),
                ))
                .collect(),
        )
        .spacing(2)
        .padding(2);

        let address_bar = if let Some(tab) = self.tabs.get(self.active_tab) {
            if tab.show_address {
                row![
                    text_input("Enter address...", &self.address_input)
                        .on_input(Message::AddressInputChanged)
                        .padding(8),
                    button("Go")
                        .on_press(Message::LoadPage)
                        .padding(8)
                        .style(theme::Button::Primary)
                ]
                .spacing(8)
                .padding(8)
            } else {
                row![]
            }
        } else {
            row![]
        };

        let content = if let Some(tab) = self.tabs.get(self.active_tab) {
            scrollable(column![text(&tab.content).size(14)].padding(20)).height(Length::Fill)
        } else {
            scrollable(column![text("No tab selected")].padding(20)).height(Length::Fill)
        };

        let main_content = column![tab_bar, address_bar, content]
            .width(Length::Fill)
            .height(Length::Fill);

        row![sidebar, main_content]
            .width(Length::Fill)
            .height(Length::Fill)
            .into()
    }

    fn theme(&self) -> Theme {
        Theme::Dark
    }

    fn subscription(&self) -> Subscription<Message> {
        time::every(std::time::Duration::from_secs(30)).map(|_| Message::Tick)
    }
}

fn fetch_api_status() -> Command<Message> {
    Command::perform(
        async {
            match reqwest::get("http://localhost:8000/status").await {
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

fn fetch_nodes() -> Command<Message> {
    Command::perform(
        async {
            match reqwest::get("http://localhost:8000/nodes").await {
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

fn fetch_page(address: String) -> Command<Message> {
    debug!("Fetching page: {}", address);
    Command::perform(
        async move {
            let client = reqwest::Client::new();

            // Extract page path from address (format: hash:/page/path)
            let parts: Vec<&str> = address.split(':').collect();
            if parts.len() != 2 {
                return Err("Invalid address format. Use: hash:/page/path".to_string());
            }

            let hash = parts[0];
            let path = parts[1];

            match client
                .post("http://localhost:8000/page")
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
