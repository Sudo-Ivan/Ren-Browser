use iced::{
    alignment::{Alignment, Horizontal},
    executor,
    keyboard::{self, KeyCode},
    theme::{self, Theme},
    time,
    widget::{button, column, container, row, scrollable, text, text_input, Column, Row},
    Application, Color, Command, Element, Length, Settings, Subscription,
};

use log::{debug, info, warn, LevelFilter};
use simple_logger::SimpleLogger;
use std::env;

use ren_browser::styles::{
    Styles, CLOSE_BUTTON_SIZE, CONTENT_PADDING, PADDING, SIDEBAR_WIDTH, SPACING, TAB_HEIGHT,
    TEXT_SIZE,
};

mod api;
use api::{fetch_api_status, fetch_nodes, fetch_page, ApiStatus, Node};

mod renderers;
use renderers::mu_renderer::{MicronRenderer, MicronStyle, RendererType, TextAlignment};

mod ren_settings;
use ren_settings::{RenSettings, SettingUpdate};

use itertools::Itertools;

use crate::Message as LibMessage;

mod caching;
use caching::PageCache;

mod monitoring;

use monitoring::AppMonitor;
use std::time::Duration;

pub fn main() -> iced::Result {
    let debug = env::args().any(|arg| arg == "--debug");
    let settings = RenSettings::load();

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

    // Initialize monitoring
    let mut monitor = AppMonitor::new();

    // Start a monitoring thread
    std::thread::spawn(move || {
        loop {
            monitor.log_usage();
            std::thread::sleep(Duration::from_secs(5)); // Log every 5 seconds
        }
    });

    RenBrowser::run(Settings {
        window: iced::window::Settings {
            size: (settings.window.width, settings.window.height),
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
    display_name: Option<String>,
}

impl Tab {
    fn new(id: usize) -> Self {
        Self {
            id,
            address: String::new(),
            content: String::from("Welcome to Ren Browser"),
            loading: false,
            show_address: true,
            rendered_content: Vec::new(),
            renderer_type: RendererType::default(),
            display_name: Some("New Tab".to_string()),
        }
    }

    fn settings() -> Self {
        Self {
            id: 0,
            address: String::from("settings"),
            content: String::new(),
            loading: false,
            show_address: false,
            rendered_content: vec![
                (
                    "Settings".to_string(),
                    MicronStyle {
                        alignment: TextAlignment::Center,
                        foreground: None,
                        link: None,
                        background: None,
                        bold: false,
                        italic: false,
                        underline: false,
                        section_depth: 0,
                        selectable: true,
                    },
                ),
                ("\nKeyboard Shortcuts:".to_string(), MicronStyle::default()),
                ("F11: Open Settings".to_string(), MicronStyle::default()),
                ("Ctrl+R: Reload Page".to_string(), MicronStyle::default()),
                ("Ctrl+T: New Tab".to_string(), MicronStyle::default()),
                ("Ctrl+W: Close Tab".to_string(), MicronStyle::default()),
            ],
            renderer_type: RendererType::Plain,
            display_name: Some("Settings".to_string()),
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
    page_cache: PageCache,
    node_search: String,
    settings: RenSettings,
    show_save_notification: bool,
    save_notification_timer: Option<std::time::Instant>,
}

#[derive(Debug, Clone)]
enum Message {
    AddTab,
    CloseTab(usize),
    SelectTab(usize),
    AddressInputChanged(String),
    LoadPage,
    ReloadPage,
    ApiStatusReceived(Box<Result<ApiStatus, String>>),
    NodesUpdated(Box<Result<Vec<Node>, String>>),
    PageLoaded(Box<Result<String, String>>),
    ShowAddressBar,
    Tick,
    ContentLoaded(String),
    LinkClicked(String),
    NodeSearchChanged(String),
    OpenSettings,
    UpdateSetting(SettingUpdate),
    SaveSettings,
    FetchNodes,
}

impl Message {
    fn from_lib(msg: LibMessage) -> Self {
        match msg {
            LibMessage::ApiStatusReceived(result) => Message::ApiStatusReceived(Box::new(*result)),
            LibMessage::NodesUpdated(result) => Message::NodesUpdated(Box::new(*result)),
            LibMessage::PageLoaded(result) => Message::PageLoaded(Box::new(*result)),
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
        let initial_tab = Tab::new(0);
        let settings = RenSettings::load();

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
                page_cache: PageCache::new(300),
                node_search: String::new(),
                settings,
                show_save_notification: false,
                save_notification_timer: None,
            },
            Command::batch(vec![
                fetch_api_status().map(Message::from_lib),
                fetch_nodes().map(Message::from_lib),
            ]),
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
                    display_name: None,
                });
                self.active_tab = self.tabs.len() - 1;
                self.next_tab_id += 1;
                Command::none()
            }
            Message::CloseTab(id) => {
                if id == 0 {
                    if let Some(tab) = self.tabs.get(self.active_tab) {
                        let real_id = tab.id;
                        if let Some(index) = self.tabs.iter().position(|t| t.id == real_id) {
                            self.tabs.remove(index);
                            if self.active_tab >= self.tabs.len() {
                                self.active_tab = self.tabs.len().saturating_sub(1);
                            }
                        }
                    }
                } else {
                    if let Some(index) = self.tabs.iter().position(|t| t.id == id) {
                        self.tabs.remove(index);
                        if self.active_tab >= self.tabs.len() {
                            self.active_tab = self.tabs.len().saturating_sub(1);
                        }
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
                self.address_input = address.clone();
                if address.ends_with("/index.mu") {
                    // Automatically load the page if it's a node click
                    return Command::batch(vec![Command::perform(async {}, |_| Message::LoadPage)]);
                }
                Command::none()
            }
            Message::LoadPage => {
                info!("Loading page: {}", self.address_input);
                // Check if it's the settings page
                if self.address_input.to_lowercase() == "settings" {
                    return self.update(Message::OpenSettings);
                }

                if let Some(tab) = self.tabs.get_mut(self.active_tab) {
                    tab.loading = true;
                    tab.address = self.address_input.clone();

                    // Check cache first
                    if let Some(cached_content) = self.page_cache.get(&tab.address) {
                        tab.loading = false;
                        tab.content = cached_content.clone();
                        tab.show_address = false;

                        let mut renderer = MicronRenderer::new();
                        if tab.address.ends_with(".mu") {
                            tab.rendered_content = renderer.parse(&tab.content);
                            tab.renderer_type = renderer.get_renderer_type();
                        } else {
                            tab.rendered_content =
                                vec![(tab.content.clone(), MicronStyle::default())];
                            tab.renderer_type = RendererType::Plain;
                        }
                        Command::none()
                    } else {
                        fetch_page(tab.address.clone(), self.settings.features.html_renderer)
                    }
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
                            // Cache the content
                            self.page_cache.set(tab.address.clone(), content.clone());

                            tab.content = content.clone();
                            tab.show_address = false;

                            // Try to find node info to get display name
                            if let Some(node) = self.nodes.iter().find(|n| {
                                n.destination_hash == tab.address.split(':').next().unwrap_or("")
                            }) {
                                tab.display_name = node.display_name.clone();
                            }

                            let mut renderer = MicronRenderer::new();

                            // Check if it's a .mu file
                            if tab.address.ends_with(".mu") {
                                debug!("Processing .mu file content");
                                tab.rendered_content = renderer.parse(&content);
                                tab.renderer_type = renderer.get_renderer_type();
                            } else {
                                debug!("Processing plain text content");
                                tab.rendered_content = vec![(content, MicronStyle::default())];
                                tab.renderer_type = RendererType::Plain;
                            }
                        }
                        Err(e) => {
                            // Remove from cache if there was an error
                            self.page_cache.remove(&tab.address);

                            let error_msg = format!("Error loading page: {}", e);
                            debug!("Page load error: {}", error_msg);
                            tab.content = error_msg.clone();
                            tab.show_address = true;
                            tab.rendered_content = vec![(error_msg, MicronStyle::default())];
                        }
                    }
                }
                Command::none()
            }
            Message::ShowAddressBar => Command::none(),
            Message::Tick => {
                if let Some(timer) = self.save_notification_timer {
                    if timer.elapsed() > std::time::Duration::from_secs(2) {
                        self.show_save_notification = false;
                        self.save_notification_timer = None;
                    }
                }
                Command::none()
            }
            Message::ContentLoaded(content) => {
                if let Some(tab) = self.tabs.get_mut(self.active_tab) {
                    tab.content = content.clone();
                    let mut renderer = MicronRenderer::new();
                    tab.rendered_content = renderer.parse(&content);
                    tab.loading = false;
                }
                Command::none()
            }
            Message::LinkClicked(url) => {
                if let Some(tab) = self.tabs.get_mut(self.active_tab) {
                    tab.loading = true;
                    tab.address = url;
                    return fetch_page(tab.address.clone(), self.settings.features.html_renderer);
                }
                Command::none()
            }
            Message::NodeSearchChanged(search) => {
                self.node_search = search;
                Command::none()
            }
            Message::OpenSettings => {
                // Check if settings tab already exists
                if let Some(index) = self.tabs.iter().position(|tab| tab.address == "settings") {
                    self.active_tab = index;
                } else {
                    let settings_tab = Tab::settings();
                    self.tabs.push(settings_tab);
                    self.active_tab = self.tabs.len() - 1;
                }
                Command::none()
            }
            Message::UpdateSetting(update) => {
                match update {
                    SettingUpdate::WindowWidth(w) => self.settings.window.width = w,
                    SettingUpdate::WindowHeight(h) => self.settings.window.height = h,
                    SettingUpdate::TextSize(s) => self.settings.appearance.text_size = s,
                    SettingUpdate::SidebarWidth(w) => self.settings.appearance.sidebar_width = w,
                    SettingUpdate::HtmlRenderer(enabled) => {
                        self.settings.features.html_renderer = enabled
                    }
                }
                self.settings.save();
                self.show_save_notification = true;
                self.save_notification_timer = Some(std::time::Instant::now());
                Command::none()
            }
            Message::SaveSettings => {
                self.settings.save();
                Command::none()
            }
            Message::ReloadPage => {
                if let Some(tab) = self.tabs.get_mut(self.active_tab) {
                    self.page_cache.remove(&tab.address);
                    tab.loading = true;
                    return fetch_page(tab.address.clone(), self.settings.features.html_renderer);
                }
                Command::none()
            }
            Message::FetchNodes => fetch_nodes().map(Message::from_lib),
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
                container(
                    text_input(
                        &format!("Search {} nodes...", self.nodes.len()),
                        &self.node_search
                    )
                    .on_input(Message::NodeSearchChanged)
                    .padding(8)
                    .style(Styles::search_input())
                    .width(Length::Fill)
                )
                .width(Length::Fill)
                .padding([0, 0, 5, 0])
                .style(theme::Container::Transparent),
                scrollable(
                    column(
                        self.nodes
                            .iter()
                            .sorted_by(|a, b| b.updated_at.cmp(&a.updated_at))
                            .filter(|node| {
                                let search = self.node_search.to_lowercase();
                                if search.is_empty() {
                                    return true;
                                }
                                let name = node
                                    .display_name
                                    .as_deref()
                                    .unwrap_or("Anonymous")
                                    .to_lowercase();
                                let hash = &node.destination_hash[0..8].to_lowercase();
                                name.contains(&search) || hash.contains(&search)
                            })
                            .map(|node| {
                                let name = node.display_name.as_deref().unwrap_or("Anonymous");
                                let hash = &node.destination_hash[0..8];
                                let last_seen = format_relative_time(node.updated_at);

                                button(
                                    column![
                                        text(name).size(TEXT_SIZE),
                                        text(hash).size(TEXT_SIZE - 2),
                                        text(last_seen)
                                            .size(TEXT_SIZE - 4)
                                            .style(theme::Text::Color(Styles::text_color_muted()))
                                    ]
                                    .spacing(SPACING / 2),
                                )
                                .style(Styles::node_button())
                                .width(Length::Fill)
                                .on_press(Message::AddressInputChanged(format!(
                                    "{}:/page/index.mu",
                                    node.destination_hash
                                )))
                                .into()
                            })
                            .collect()
                    )
                    .spacing(SPACING)
                )
                .height(Length::Fill)
            ],
            // Bottom section with version and address
            column![
                text("Ren Browser - v0.4.0")
                    .size(TEXT_SIZE - 2)
                    .style(theme::Text::Color(Styles::muted_text())),
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
                    let tab_text = if tab.address.is_empty() {
                        "New Tab"
                    } else {
                        tab.display_name.as_deref().unwrap_or_else(|| {
                            if self.active_tab
                                == self.tabs.iter().position(|t| t.id == tab.id).unwrap_or(0)
                            {
                                &tab.address
                            } else {
                                tab.address.split('/').last().unwrap_or("New Tab")
                            }
                        })
                    };

                    button(
                        row![
                            container(text(tab_text).size(TEXT_SIZE))
                                .width(Length::Fill)
                                .center_x()
                                .center_y(),
                            container(
                                button(text("×").size(CLOSE_BUTTON_SIZE))
                                    .on_press(Message::CloseTab(tab.id))
                                    .style(Styles::close_button())
                                    .padding(0)
                            )
                            .width(Length::Shrink)
                            .height(Length::Fill)
                            .center_y()
                            .padding([0, 5])
                        ]
                        .spacing(5)
                        .width(Length::Fill)
                        .height(Length::Fill)
                        .align_items(Alignment::Center),
                    )
                    .on_press(Message::SelectTab(tab.id))
                    .style(Styles::tab_button(
                        self.active_tab
                            == self.tabs.iter().position(|t| t.id == tab.id).unwrap_or(0),
                    ))
                    .width(Length::Fixed(150.0))
                    .height(Length::Fixed(TAB_HEIGHT as f32))
                    .padding([2, 8])
                    .into()
                })
                .chain(std::iter::once(
                    container(
                        button(text("+").size(TEXT_SIZE + 2))
                            .on_press(Message::AddTab)
                            .style(Styles::new_tab_button())
                            .padding([2, 8]),
                    )
                    .center_y()
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
            if tab.loading {
                // Replace spinner with Loading... text for now
                container(
                    text("Loading...")
                        .size(TEXT_SIZE)
                        .style(theme::Text::Color(Color::from_rgb(0.7, 0.7, 0.7))),
                )
                .width(Length::Fill)
                .height(Length::Fill)
                .center_x()
                .center_y()
            } else if tab.address == "settings" {
                // Render settings page
                container(self.settings.view().map(Message::UpdateSetting))
                    .width(Length::Fill)
                    .height(Length::Fill)
                    .into()
            } else {
                container(
                    scrollable(
                        Column::with_children(
                            tab.rendered_content
                                .iter()
                                .map(|(content, style)| {
                                    let text_el = text(content).size(TEXT_SIZE);

                                    if let Some(link) = &style.link {
                                        button(text_el.style(theme::Text::Color(Color::from_rgb(
                                            0.4, 0.6, 1.0,
                                        ))))
                                        .on_press(Message::LinkClicked(link.url.clone()))
                                        .style(theme::Button::Text)
                                        .into()
                                    } else {
                                        let styled_text = if let Some(color) = style.foreground {
                                            text_el.style(theme::Text::Color(color))
                                        } else {
                                            text_el
                                        };

                                        let aligned_container =
                                            match style.alignment {
                                                TextAlignment::Center => container(styled_text)
                                                    .align_x(Horizontal::Center),
                                                TextAlignment::Right => container(styled_text)
                                                    .align_x(Horizontal::Right),
                                                TextAlignment::Left => {
                                                    container(styled_text).align_x(Horizontal::Left)
                                                }
                                                TextAlignment::Default => container(styled_text),
                                            };

                                        aligned_container.width(Length::Fill).into()
                                    }
                                })
                                .collect(),
                        )
                        .spacing(SPACING)
                        .padding(CONTENT_PADDING)
                        .width(Length::Fill),
                    )
                    .height(Length::Fill),
                )
                .width(Length::Fill)
                .into()
            }
        } else {
            container(text("No tab selected"))
                .width(Length::Fill)
                .center_x()
                .into()
        };

        let main_content = column![
            tab_bar,
            address_bar,
            container(
                text(match self.tabs.get(self.active_tab) {
                    Some(tab) => match tab.renderer_type {
                        RendererType::Micron => "Micron Renderer",
                        RendererType::Plain => "Plain Text",
                    },
                    None => "",
                })
                .size(TEXT_SIZE - 2)
                .style(theme::Text::Color(Styles::renderer_text()))
            )
            .width(Length::Fill)
            .padding([2, PADDING])
            .align_x(Horizontal::Right),
            content,
        ]
        .width(Length::Fill)
        .height(Length::Fill);

        let content = column![
            main_content,
            if self.show_save_notification {
                let notification: Element<_> = container(
                    text("Settings saved")
                        .size(12)
                        .style(theme::Text::Color(Color::WHITE)),
                )
                .style(Styles::save_notification())
                .padding(8)
                .align_x(Horizontal::Right)
                .into();
                notification
            } else {
                container(text("")).width(Length::Fill).into()
            }
        ]
        .width(Length::Fill)
        .height(Length::Fill);

        row![sidebar, content]
            .width(Length::Fill)
            .height(Length::Fill)
            .into()
    }

    fn theme(&self) -> Theme {
        Theme::Dark
    }

    fn subscription(&self) -> Subscription<Message> {
        Subscription::batch([
            iced::subscription::events_with(|event, status| {
                if let iced::event::Status::Captured = status {
                    return None;
                }

                if let iced::Event::Keyboard(keyboard::Event::KeyPressed {
                    key_code,
                    modifiers,
                    ..
                }) = event
                {
                    match (key_code, modifiers.command()) {
                        (KeyCode::R, true) => Some(Message::ReloadPage),
                        (KeyCode::T, true) => Some(Message::AddTab),
                        (KeyCode::W, true) => Some(Message::CloseTab(0)),
                        _ => None,
                    }
                } else {
                    None
                }
            }),
            time::every(std::time::Duration::from_secs(30)).map(|_| Message::Tick),
            time::every(std::time::Duration::from_secs(5)).map(|_| Message::FetchNodes),
        ])
    }
}

fn format_relative_time(timestamp: i64) -> String {
    let now = chrono::Utc::now().timestamp();
    let diff = now - timestamp;

    if diff < 60 {
        return "just now".to_string();
    }
    if diff < 3600 {
        let mins = diff / 60;
        return format!("{} min{} ago", mins, if mins == 1 { "" } else { "s" });
    }
    if diff < 86400 {
        let hours = diff / 3600;
        return format!("{} hour{} ago", hours, if hours == 1 { "" } else { "s" });
    }
    if diff < 2592000 {
        let days = diff / 86400;
        return format!("{} day{} ago", days, if days == 1 { "" } else { "s" });
    }
    if diff < 31536000 {
        let months = diff / 2592000;
        return format!("{} month{} ago", months, if months == 1 { "" } else { "s" });
    }
    let years = diff / 31536000;
    format!("{} year{} ago", years, if years == 1 { "" } else { "s" })
}
