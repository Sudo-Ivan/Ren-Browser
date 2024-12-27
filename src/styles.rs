use iced::widget::{container, text_input};
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

    pub fn text_color() -> Color {
        Color::WHITE
    }

    pub fn text_color_muted() -> Color {
        Color::from_rgb(0.7, 0.7, 0.7)
    }

    pub fn renderer_text() -> Color {
        Color::from_rgb(0.4, 0.4, 0.4)
    }

    pub fn spinner() -> iced::theme::Container {
        iced::theme::Container::Custom(Box::new(SpinnerStyle))
    }

    pub fn close_button() -> iced::theme::Button {
        iced::theme::Button::Custom(Box::new(CloseButtonStyle))
    }

    pub fn new_tab_button() -> iced::theme::Button {
        iced::theme::Button::Custom(Box::new(NewTabButtonStyle))
    }

    pub fn search_input() -> iced::theme::TextInput {
        iced::theme::TextInput::Custom(Box::new(SearchInputStyle))
    }

    pub fn settings_container() -> iced::theme::Container {
        iced::theme::Container::Custom(Box::new(SettingsContainerStyle))
    }

    pub fn settings_section() -> iced::theme::Container {
        iced::theme::Container::Custom(Box::new(SettingsSectionStyle))
    }

    pub fn settings_input() -> iced::theme::TextInput {
        iced::theme::TextInput::Custom(Box::new(SettingsInputStyle))
    }

    pub fn save_notification() -> iced::theme::Container {
        iced::theme::Container::Custom(Box::new(SaveNotificationStyle))
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
            border_radius: 6.0.into(),
            border_width: 0.0,
            border_color: Color::TRANSPARENT,
            text_color: Color::WHITE,
            ..Default::default()
        }
    }

    fn hovered(&self, style: &Self::Style) -> button::Appearance {
        let active = self.active(style);
        button::Appearance {
            background: Some(iced::Background::Color(Color::from_rgb(0.2, 0.2, 0.2))),
            ..active
        }
    }
}

pub const SIDEBAR_WIDTH: f32 = 300.0;
pub const PADDING: u16 = 20;
pub const SPACING: u16 = 12;
pub const TEXT_SIZE: u16 = 14;
pub const HEADING_SIZE: u16 = 20;
pub const TAB_HEIGHT: u16 = 32;
pub const CONTENT_PADDING: u16 = 35;
pub const BORDER_RADIUS: f32 = 8.0;
pub const SPINNER_SIZE: f32 = 24.0;
pub const SPINNER_BORDER: f32 = 2.5;
pub const CLOSE_BUTTON_SIZE: u16 = TEXT_SIZE + 4;

pub struct SpinnerStyle;

impl container::StyleSheet for SpinnerStyle {
    type Style = Theme;

    fn appearance(&self, _style: &Self::Style) -> container::Appearance {
        container::Appearance {
            border_width: SPINNER_BORDER,
            border_color: Color::from_rgb(0.7, 0.7, 0.7),
            border_radius: (SPINNER_SIZE / 2.0).into(),
            background: Some(iced::Background::Color(Color::from_rgba(
                0.0, 0.0, 0.0, 0.2,
            ))),
            ..Default::default()
        }
    }
}

struct CloseButtonStyle;
struct NewTabButtonStyle;

impl button::StyleSheet for CloseButtonStyle {
    type Style = Theme;

    fn active(&self, _style: &Self::Style) -> button::Appearance {
        button::Appearance {
            background: None,
            border_radius: 0.0.into(),
            border_width: 0.0,
            border_color: Color::TRANSPARENT,
            text_color: Color::from_rgb(0.7, 0.7, 0.7),
            ..Default::default()
        }
    }

    fn hovered(&self, style: &Self::Style) -> button::Appearance {
        let active = self.active(style);
        button::Appearance {
            text_color: Color::WHITE,
            ..active
        }
    }
}

impl button::StyleSheet for NewTabButtonStyle {
    type Style = Theme;

    fn active(&self, _style: &Self::Style) -> button::Appearance {
        button::Appearance {
            background: None,
            border_radius: 0.0.into(),
            border_width: 0.0,
            border_color: Color::TRANSPARENT,
            text_color: Color::from_rgb(0.7, 0.7, 0.7),
            ..Default::default()
        }
    }

    fn hovered(&self, style: &Self::Style) -> button::Appearance {
        let active = self.active(style);
        button::Appearance {
            text_color: Color::WHITE,
            ..active
        }
    }
}

struct SearchInputStyle;

impl text_input::StyleSheet for SearchInputStyle {
    type Style = Theme;

    fn active(&self, _style: &Self::Style) -> text_input::Appearance {
        text_input::Appearance {
            background: iced::Background::Color(Color::TRANSPARENT),
            border_radius: 4.0.into(),
            border_width: 1.0,
            border_color: Color::from_rgb(0.3, 0.3, 0.3),
            icon_color: Color::from_rgb(0.7, 0.7, 0.7),
        }
    }

    fn focused(&self, style: &Self::Style) -> text_input::Appearance {
        let active = self.active(style);
        text_input::Appearance {
            border_color: Color::from_rgb(0.4, 0.4, 0.4),
            ..active
        }
    }

    fn placeholder_color(&self, _style: &Self::Style) -> Color {
        Color::from_rgb(0.5, 0.5, 0.5)
    }

    fn value_color(&self, _style: &Self::Style) -> Color {
        Color::WHITE
    }

    fn selection_color(&self, _style: &Self::Style) -> Color {
        Color::from_rgb(0.3, 0.4, 0.9)
    }

    fn disabled_color(&self, _style: &Self::Style) -> Color {
        Color::from_rgb(0.3, 0.3, 0.3)
    }

    fn disabled(&self, style: &Self::Style) -> text_input::Appearance {
        let active = self.active(style);
        text_input::Appearance {
            background: iced::Background::Color(Color::from_rgb(0.15, 0.15, 0.15)),
            border_color: Color::from_rgb(0.2, 0.2, 0.2),
            ..active
        }
    }
}

struct SettingsContainerStyle;
struct SettingsSectionStyle;
struct SettingsInputStyle;
struct SaveNotificationStyle;

impl container::StyleSheet for SettingsContainerStyle {
    type Style = Theme;

    fn appearance(&self, _style: &Self::Style) -> container::Appearance {
        container::Appearance {
            background: Some(iced::Background::Color(Color::from_rgb(0.15, 0.15, 0.15))),
            border_radius: 8.0.into(),
            border_width: 1.0,
            border_color: Color::from_rgb(0.3, 0.3, 0.3),
            ..Default::default()
        }
    }
}

impl container::StyleSheet for SettingsSectionStyle {
    type Style = Theme;

    fn appearance(&self, _style: &Self::Style) -> container::Appearance {
        container::Appearance {
            background: Some(iced::Background::Color(Color::from_rgb(0.18, 0.18, 0.18))),
            border_radius: 6.0.into(),
            border_width: 0.0,
            ..Default::default()
        }
    }
}

impl text_input::StyleSheet for SettingsInputStyle {
    type Style = Theme;

    fn active(&self, _style: &Self::Style) -> text_input::Appearance {
        text_input::Appearance {
            background: iced::Background::Color(Color::from_rgb(0.2, 0.2, 0.2)),
            border_radius: 4.0.into(),
            border_width: 1.0,
            border_color: Color::from_rgb(0.3, 0.3, 0.3),
            icon_color: Color::from_rgb(0.7, 0.7, 0.7),
        }
    }

    fn focused(&self, style: &Self::Style) -> text_input::Appearance {
        let active = self.active(style);
        text_input::Appearance {
            border_color: Color::from_rgb(0.5, 0.5, 0.5),
            ..active
        }
    }

    fn value_color(&self, _style: &Self::Style) -> Color {
        Color::WHITE
    }

    fn placeholder_color(&self, _style: &Self::Style) -> Color {
        Color::from_rgb(0.5, 0.5, 0.5)
    }

    fn selection_color(&self, _style: &Self::Style) -> Color {
        Color::from_rgb(0.3, 0.4, 0.9)
    }

    fn disabled_color(&self, _style: &Self::Style) -> Color {
        Color::from_rgb(0.3, 0.3, 0.3)
    }

    fn disabled(&self, style: &Self::Style) -> text_input::Appearance {
        let active = self.active(style);
        text_input::Appearance {
            background: iced::Background::Color(Color::from_rgb(0.15, 0.15, 0.15)),
            border_color: Color::from_rgb(0.2, 0.2, 0.2),
            ..active
        }
    }
}

impl container::StyleSheet for SaveNotificationStyle {
    type Style = Theme;

    fn appearance(&self, _style: &Self::Style) -> container::Appearance {
        container::Appearance {
            background: Some(iced::Background::Color(Color::from_rgba(
                0.0, 0.0, 0.0, 0.8,
            ))),
            border_radius: 4.0.into(),
            border_width: 0.0,
            ..Default::default()
        }
    }
}
