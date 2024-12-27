use iced::event::Event;
use iced::keyboard::{self, KeyCode};

pub fn handle_shortcut(event: Event, modifiers: keyboard::Modifiers) -> Option<Shortcut> {
    match event {
        Event::Keyboard(keyboard::Event::KeyPressed { key_code, .. }) => {
            if modifiers.control() {
                match key_code {
                    KeyCode::R => Some(Shortcut::Reload),
                    _ => None,
                }
            } else {
                None
            }
        }
        _ => None,
    }
}

#[derive(Debug, Clone)]
pub enum Shortcut {
    Reload,
}