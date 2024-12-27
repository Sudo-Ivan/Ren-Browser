use iced::{
    alignment::{Alignment, Horizontal},
    event::{self, Event},
    executor, keyboard, theme, time,
    widget::{button, column, container, row, scrollable, text, text_input, Row},
    Application, Command, Element, Length, Settings, Subscription, Theme,
};

use chrono;
use log::{debug, info, warn, LevelFilter};
use simple_logger::SimpleLogger;
use std::env;

mod styles;
use styles::{
    Styles, BORDER_RADIUS, CONTENT_PADDING, HEADING_SIZE, PADDING, SIDEBAR_WIDTH, SPACING,
    TAB_HEIGHT, TEXT_SIZE,
};

mod api;
use api::{fetch_api_status, fetch_nodes, fetch_page, ApiStatus, Node};

mod renderers;
use renderers::mu_renderer::{MicronRenderer, MicronStyle, TextAlignment};

mod shortcuts;
use renderers::mu_renderer::RendererType;
use shortcuts::{handle_shortcut, Shortcut};

use crate::Message as LibMessage;

const VERSION: &str = env!("CARGO_PKG_VERSION");

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

    debug!("Starting Ren Browser in debug mode");

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
    rendered_content: Vec<(String, MicronStyle)>,
    renderer_type: RendererType,
}

impl Tab {
    fn new(id: usize) -> Self {
        Self {
            id,
            address: String::new(),
            content: String::new(),
            loading: false,
            show_address: true,
            rendered_content: Vec::new(),
            renderer_type: RendererType::default(),
        }
    }
}

struct RenBrowser {
    tabs: Vec<Tab>,
    active_tab: usize,
    address_input: String,
    nodes: Vec<Node>,
    api_status: ApiStatus,
    next_tab_id: usize,
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
    ContentLoaded(String),
    Shortcut(Shortcut),
    ReloadPage,
}

impl Message {
    fn from_lib(msg: LibMessage) -> Self {
        match msg {
            LibMessage::ApiStatusReceived(result) => Message::ApiStatusReceived(result),
            LibMessage::NodesUpdated(result) => Message::NodesUpdated(result),
            LibMessage::PageLoaded(result) => Message::PageLoaded(result),
            _ => Message::AddTab,
        }
    }
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
            rendered_content: Vec::new(),
            renderer_type: RendererType::default(),
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
            Command::batch(vec![fetch_api_status().map(Message::from_lib), fetch_nodes().map(Message::from_lib)]),
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
                    rendered_content: Vec::new(),
                    renderer_type: RendererType::default(),
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
                            tab.content = content.clone();
                            tab.show_address = false;

                            let mut renderer = MicronRenderer::new();
                            tab.rendered_content = renderer.parse(&content);
                            debug!("Content rendered");
                        }
                        Err(e) => {
                            let error_msg = format!("Error loading page: {}", e);
                            tab.content = error_msg.clone();
                            tab.show_address = true;
                            tab.rendered_content = vec![(error_msg, MicronStyle::default())];
                        }
                    }
                }
                Command::none()
            }
            Message::ShowAddressBar => Command::none(),
            Message::Tick => Command::none(),
            Message::ContentLoaded(content) => {
                if let Some(tab) = self.tabs.get_mut(self.active_tab) {
                    tab.content = content.clone();
                    let mut renderer = MicronRenderer::new();
                    tab.rendered_content = renderer.parse(&content);
                    tab.loading = false;
                }
                Command::none()
            }
            Message::Shortcut(Shortcut::Reload) => {
                if let Some(tab) = self.tabs.get(self.active_tab) {
                    return fetch_page(tab.address.clone());
                }
                Command::none()
            }
            Message::ReloadPage => {
                if let Some(tab) = self.tabs.get(self.active_tab) {
                    return fetch_page(tab.address.clone());
                }
                Command::none()
            }
        }
    }

    fn view(&self) -> Element<Message> {
        let status_text = text(&self.api_status.status)
            .style(Styles::status_text(self.api_status.status == "Connected"))
            .size(TEXT_SIZE);

        let sidebar = column![
            // Top section with status and nodes
            column![
                status_text,
                text("Nodes").size(HEADING_SIZE),
                scrollable(
                    column(
                        self.nodes
                            .iter()
                            .map(|node| {
                                let name = node.display_name.as_deref().unwrap_or("Unknown");
                                let hash = &node.destination_hash[0..8];
                                let last_seen =
                                    chrono::DateTime::from_timestamp(node.updated_at, 0)
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
                                .on_press(Message::AddressInputChanged(
                                    node.destination_hash.clone(),
                                ))
                                .into()
                            })
                            .collect()
                    )
                    .spacing(SPACING)
                )
                .height(Length::Fill)
            ],
            column![
                // Version display
                text(&format!("v{}", VERSION))
                    .size(TEXT_SIZE - 2)
                    .style(theme::Text::Color(Styles::muted_text())),
                // Address display
                text(if !self.api_status.address.is_empty() {
                    &self.api_status.address[0..16]
                } else {
                    "Not connected"
                })
                .size(TEXT_SIZE - 2)
            ]
            .spacing(SPACING / 2)
            .width(Length::Fill)
            .align_items(Alignment::End)
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
            container(column![
                scrollable(
                    column(
                        tab.rendered_content
                            .iter()
                            .map(|(content, style)| {
                                let mut text_el = text(content);
                                text_el = text_el.size(TEXT_SIZE);

                                if let Some(color) = style.foreground {
                                    text_el = text_el.style(color);
                                } else {
                                    text_el = text_el.style(Styles::text_color());
                                }

                                let container = container(text_el);

                                match style.alignment {
                                    TextAlignment::Center => container.align_x(Horizontal::Center),
                                    TextAlignment::Right => container.align_x(Horizontal::Right),
                                    TextAlignment::Left => container.align_x(Horizontal::Left),
                                    TextAlignment::Default => container,
                                }
                                .width(Length::Fill)
                                .into()
                            })
                            .collect(),
                    )
                    .spacing(SPACING)
                    .padding(CONTENT_PADDING)
                    .width(Length::Fill),
                )
                .height(Length::Fill),
                container(
                    text(if let Some(tab) = self.tabs.get(self.active_tab) {
                        match tab.renderer_type {
                            RendererType::Micron => "Micron Renderer",
                            RendererType::Plain => "Plain Text Renderer",
                        }
                    } else {
                        "No Renderer"
                    })
                    .size(TEXT_SIZE - 2)
                    .style(Styles::renderer_text())
                )
                .width(Length::Fill)
                .align_x(Horizontal::Right)
                .padding([0, CONTENT_PADDING])
            ])
            .style(|_theme: &Theme| container::Appearance {
                background: Some(Styles::content_container()),
                border_radius: BORDER_RADIUS.into(),
                ..Default::default()
            })
            .padding(PADDING)
        } else {
            container(
                scrollable(column![text("No tab selected")].padding(CONTENT_PADDING))
                    .height(Length::Fill),
            )
            .style(|_theme: &Theme| container::Appearance {
                background: Some(Styles::content_container()),
                border_radius: BORDER_RADIUS.into(),
                ..Default::default()
            })
            .padding(PADDING)
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
        Subscription::batch(vec![
            iced::subscription::events_with(|event, status| {
                if let event::Status::Captured = status {
                    return None;
                }

                if let Event::Keyboard(keyboard::Event::KeyPressed { .. }) = event {
                    if let Some(shortcut) = handle_shortcut(event, keyboard::Modifiers::empty()) {
                        Some(Message::Shortcut(shortcut))
                    } else {
                        None
                    }
                } else {
                    None
                }
            }),
            time::every(std::time::Duration::from_secs(30)).map(|_| Message::Tick),
        ])
    }
}
