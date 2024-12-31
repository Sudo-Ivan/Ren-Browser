use iced::{
    alignment::{Horizontal, Vertical},
    theme,
    widget::{button, container, row, text, Row},
    Alignment, Color, Element, Length,
};

use crate::Message;
use ren_browser::renderers::mu_renderer::{
    MicronRenderer, MicronStyle, RendererType, TextAlignment,
};
use ren_browser::styles::{Styles, CLOSE_BUTTON_SIZE, NEW_TAB_BUTTON_SIZE, TAB_HEIGHT, TEXT_SIZE};

#[derive(Debug, Clone)]
pub struct Tab {
    pub id: usize,
    pub address: String,
    pub content: String,
    pub loading: bool,
    pub show_address: bool,
    pub rendered_content: Vec<(String, MicronStyle)>,
    pub renderer_type: RendererType,
    pub display_name: Option<String>,
}

impl Tab {
    pub fn new(id: usize) -> Self {
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

    pub fn settings() -> Self {
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

    pub fn view(&self, active: bool) -> Element<Message> {
        let tab_text = if self.address.is_empty() {
            "New Tab"
        } else {
            self.display_name.as_deref().unwrap_or_else(|| {
                if active {
                    &self.address
                } else {
                    self.address.split('/').last().unwrap_or("New Tab")
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
                        .on_press(Message::CloseTab(self.id))
                        .style(Styles::close_button())
                        .padding(0)
                )
                .width(Length::Fixed(CLOSE_BUTTON_SIZE as f32))
                .height(Length::Fixed(CLOSE_BUTTON_SIZE as f32))
                .center_y()
                .center_x()
                .padding([0, 0, 0, 0])
            ]
            .spacing(5)
            .width(Length::Fill)
            .height(Length::Fill)
            .align_items(Alignment::Center),
        )
        .on_press(Message::SelectTab(self.id))
        .style(Styles::tab_button(active))
        .width(Length::Fixed(150.0))
        .height(Length::Fixed(TAB_HEIGHT as f32))
        .padding([2, 8])
        .into()
    }
}

pub fn tab_bar(tabs: &[Tab], active_tab: usize) -> Element<Message> {
    Row::with_children(
        tabs.iter()
            .map(|tab| {
                tab.view(active_tab == tabs.iter().position(|t| t.id == tab.id).unwrap_or(0))
            })
            .chain(std::iter::once(
                container(
                    button(text("+").size(NEW_TAB_BUTTON_SIZE))
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
    .padding(2)
    .into()
}
