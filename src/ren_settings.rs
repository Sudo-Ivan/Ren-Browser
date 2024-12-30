use iced::widget::{checkbox, column, container, row, text, text_input};
use iced::{Element, Length};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

use ren_browser::styles::Styles;

const SETTINGS_FILE: &str = "ren_browser.toml";

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct RenSettings {
    pub window: WindowSettings,
    pub appearance: AppearanceSettings,
    pub features: FeatureSettings,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct WindowSettings {
    pub width: u32,
    pub height: u32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AppearanceSettings {
    pub text_size: u16,
    pub sidebar_width: u16,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct FeatureSettings {
    pub html_renderer: bool,
}

#[derive(Debug, Clone)]
pub enum SettingUpdate {
    WindowWidth(u32),
    WindowHeight(u32),
    TextSize(u16),
    SidebarWidth(u16),
    HtmlRenderer(bool),
}

impl Default for RenSettings {
    fn default() -> Self {
        Self {
            window: WindowSettings {
                width: 1280,
                height: 720,
            },
            appearance: AppearanceSettings {
                text_size: 14,
                sidebar_width: 250,
            },
            features: FeatureSettings {
                html_renderer: false,
            },
        }
    }
}

impl RenSettings {
    pub fn load() -> Self {
        let config_path = Self::config_path();

        if let Ok(content) = fs::read_to_string(config_path) {
            toml::from_str(&content).unwrap_or_default()
        } else {
            let default = Self::default();
            default.save();
            default
        }
    }

    pub fn save(&self) {
        if let Ok(content) = toml::to_string_pretty(self) {
            let _ = fs::write(Self::config_path(), content);
        }
    }

    fn config_path() -> PathBuf {
        let mut path = dirs::config_dir().unwrap_or_else(|| PathBuf::from("."));
        path.push("ren-browser");
        fs::create_dir_all(&path).unwrap_or_default();
        path.push(SETTINGS_FILE);
        path
    }

    pub fn view(&self) -> Element<SettingUpdate> {
        let window_section = container(
            column![
                text("Window Settings").size(20),
                row![
                    text("Width: ").width(Length::Fixed(100.0)),
                    text_input("width", &self.window.width.to_string())
                        .on_input(|s| s
                            .parse()
                            .map(SettingUpdate::WindowWidth)
                            .unwrap_or_else(|_| SettingUpdate::WindowWidth(1280)))
                        .style(Styles::settings_input())
                        .width(Length::Fixed(100.0))
                ],
                row![
                    text("Height: ").width(Length::Fixed(100.0)),
                    text_input("height", &self.window.height.to_string())
                        .on_input(|s| s
                            .parse()
                            .map(SettingUpdate::WindowHeight)
                            .unwrap_or_else(|_| SettingUpdate::WindowHeight(720)))
                        .style(Styles::settings_input())
                        .width(Length::Fixed(100.0))
                ]
            ]
            .spacing(10)
            .padding(15),
        )
        .style(Styles::settings_section())
        .width(Length::Fill);

        let appearance_section = container(
            column![
                text("Appearance").size(20),
                row![
                    text("Text Size: ").width(Length::Fixed(100.0)),
                    text_input("text size", &self.appearance.text_size.to_string())
                        .on_input(|s| s
                            .parse()
                            .map(SettingUpdate::TextSize)
                            .unwrap_or_else(|_| SettingUpdate::TextSize(14)))
                        .style(Styles::settings_input())
                        .width(Length::Fixed(100.0))
                ],
                row![
                    text("Sidebar Width: ").width(Length::Fixed(100.0)),
                    text_input("sidebar width", &self.appearance.sidebar_width.to_string())
                        .on_input(|s| s
                            .parse()
                            .map(SettingUpdate::SidebarWidth)
                            .unwrap_or_else(|_| SettingUpdate::SidebarWidth(250)))
                        .style(Styles::settings_input())
                        .width(Length::Fixed(100.0))
                ]
            ]
            .spacing(10)
            .padding(15),
        )
        .style(Styles::settings_section())
        .width(Length::Fill);

        let features_section = container(
            column![
                text("Features").size(20),
                row![
                    text("HTML Renderer: ").width(Length::Fixed(100.0)),
                    checkbox("", self.features.html_renderer, |checked| {
                        SettingUpdate::HtmlRenderer(checked)
                    })
                ]
            ]
            .spacing(10)
            .padding(15),
        )
        .style(Styles::settings_section())
        .width(Length::Fill);

        container(
            column![window_section, appearance_section, features_section]
                .spacing(20)
                .padding(20)
                .width(Length::Fill)
                .max_width(400),
        )
        .style(Styles::settings_container())
        .width(Length::Fill)
        .center_x()
        .into()
    }
}
