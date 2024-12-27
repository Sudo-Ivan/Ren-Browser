use iced::{widget::button, Color, Theme};

pub struct Styles;

impl Styles {
    pub fn status_text(connected: bool) -> Color {
        if connected {
            Color::from_rgb(0.0, 0.8, 0.0)
        } else {
            Color::from_rgb(0.8, 0.0, 0.0)
        }
    }

    pub fn node_button() -> iced::theme::Button {
        iced::theme::Button::Custom(Box::new(NodeButtonStyle))
    }

    pub fn tab_button(active: bool) -> iced::theme::Button {
        iced::theme::Button::Custom(Box::new(TabButtonStyle { active }))
    }

    pub fn content_container() -> iced::Background {
        iced::Background::Color(Color::from_rgb(0.12, 0.12, 0.12))
    }

    pub fn muted_text() -> Color {
        Color::from_rgb(0.5, 0.5, 0.5)
    }
}

struct NodeButtonStyle;
struct TabButtonStyle {
    active: bool,
}

impl button::StyleSheet for TabButtonStyle {
    type Style = Theme;

    fn active(&self, _style: &Self::Style) -> button::Appearance {
        button::Appearance {
            background: Some(iced::Background::Color(if self.active {
                Color::from_rgb(0.2, 0.2, 0.2)
            } else {
                Color::from_rgb(0.15, 0.15, 0.15)
            })),
            border_radius: 4.0.into(),
            border_width: 0.0,
            border_color: Color::TRANSPARENT,
            text_color: if self.active {
                Color::WHITE
            } else {
                Color::from_rgb(0.7, 0.7, 0.7)
            },
            ..Default::default()
        }
    }
}

impl button::StyleSheet for NodeButtonStyle {
    type Style = Theme;

    fn active(&self, _style: &Self::Style) -> button::Appearance {
        button::Appearance {
            background: Some(iced::Background::Color(Color::from_rgb(0.15, 0.15, 0.15))),
            border_radius: 4.0.into(),
            border_width: 0.0,
            border_color: Color::TRANSPARENT,
            ..Default::default()
        }
    }
}

pub const SIDEBAR_WIDTH: f32 = 200.0;
pub const PADDING: u16 = 20;
pub const SPACING: u16 = 10;
pub const TEXT_SIZE: u16 = 14;
pub const HEADING_SIZE: u16 = 20;
pub const TAB_HEIGHT: u16 = 32;
pub const CONTENT_PADDING: u16 = 30;
pub const BORDER_RADIUS: f32 = 8.0;
