use iced::Color;

#[derive(Debug, Clone, PartialEq)]
pub enum TextAlignment {
    Left,
    Center,
    Right,
    Default,
}

#[derive(Debug, Clone)]
pub struct MicronStyle {
    pub bold: bool,
    pub italic: bool,
    pub underline: bool,
    pub foreground: Option<Color>,
    pub background: Option<Color>,
    pub section_depth: u8,
    pub alignment: TextAlignment,
}

impl Default for MicronStyle {
    fn default() -> Self {
        Self {
            bold: false,
            italic: false,
            underline: false,
            foreground: Some(Color::from_rgb(0.87, 0.87, 0.87)),
            background: None,
            section_depth: 0,
            alignment: TextAlignment::Default,
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum RendererType {
    Micron,
    Plain,
}

impl Default for RendererType {
    fn default() -> Self {
        Self::Plain
    }
}

pub struct MicronRenderer {
    current_style: MicronStyle,
    renderer_type: RendererType,
}

impl MicronRenderer {
    pub fn new() -> Self {
        Self {
            current_style: MicronStyle::default(),
            renderer_type: RendererType::Plain,
        }
    }

    pub fn get_renderer_type(&self) -> RendererType {
        self.renderer_type.clone()
    }

    pub fn parse(&mut self, content: &str) -> Vec<(String, MicronStyle)> {
        match self.try_parse_micron(content) {
            Ok(styled) => styled,
            Err(_) => vec![(content.to_string(), MicronStyle::default())],
        }
    }

    fn try_parse_micron(&mut self, content: &str) -> Result<Vec<(String, MicronStyle)>, ()> {
        let mut styled_content = Vec::new();
        let mut current_text = String::new();
        let mut chars = content.chars().peekable();

        while let Some(c) = chars.next() {
            if c == '`' {
                self.renderer_type = RendererType::Micron;

                // Push current text if any
                if !current_text.is_empty() {
                    styled_content.push((current_text.clone(), self.current_style.clone()));
                    current_text.clear();
                }

                // Collect tag content
                let mut tag = String::new();
                while let Some(&next_c) = chars.peek() {
                    if next_c == '`' {
                        chars.next(); // consume closing backtick
                        break;
                    }
                    tag.push(chars.next().unwrap());
                }

                // Handle the tag
                if let Some(first_char) = tag.chars().next() {
                    match first_char {
                        'F' => {
                            if tag.len() >= 3 {
                                self.current_style.foreground = Some(parse_color(&tag[1..4]));
                                if tag.len() > 4 {
                                    current_text = tag[4..].to_string();
                                }
                            }
                        }
                        'f' => {
                            self.current_style.foreground = None;
                            // Don't include the 'f' character in the output text
                            if tag.len() > 1 {
                                current_text = tag[1..].to_string();
                            }
                        }
                        _ => current_text = tag,
                    }
                }

                // Push text from tag if any
                if !current_text.is_empty() {
                    styled_content.push((current_text.clone(), self.current_style.clone()));
                    current_text.clear();
                }
            } else {
                current_text.push(c);
            }
        }

        // Push remaining text if any
        if !current_text.is_empty() {
            styled_content.push((current_text, self.current_style.clone()));
        }

        // If no segments were created, create one with the entire content
        if styled_content.is_empty() && !content.is_empty() {
            styled_content.push((content.to_string(), MicronStyle::default()));
        }

        Ok(styled_content)
    }
}

fn parse_color(hex: &str) -> Color {
    if hex == "default" {
        return Color::from_rgb(0.87, 0.87, 0.87);
    }

    if hex.len() == 3 {
        if hex.starts_with('g') {
            if let Ok(val) = u8::from_str_radix(&hex[1..], 10) {
                let normalized = (val as f32) / 99.0;
                return Color::from_rgb(normalized, normalized, normalized);
            }
        } else {
            // RGB hex shorthand - fixed conversion
            let r = u8::from_str_radix(&hex[0..1], 16).unwrap_or(0);
            let g = u8::from_str_radix(&hex[1..2], 16).unwrap_or(0);
            let b = u8::from_str_radix(&hex[2..3], 16).unwrap_or(0);

            // Convert to normalized floats (multiply by 17 to expand single digit)
            return Color::from_rgb(
                (r * 17) as f32 / 255.0,
                (g * 17) as f32 / 255.0,
                (b * 17) as f32 / 255.0,
            );
        }
    } else if hex.len() == 6 {
        // Full RGB hex
        let r = u8::from_str_radix(&hex[0..2], 16).unwrap_or(0);
        let g = u8::from_str_radix(&hex[2..4], 16).unwrap_or(0);
        let b = u8::from_str_radix(&hex[4..6], 16).unwrap_or(0);
        return Color::from_rgb(r as f32 / 255.0, g as f32 / 255.0, b as f32 / 255.0);
    }

    Color::from_rgb(0.87, 0.87, 0.87) // Fallback to default
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_parsing() {
        let mut renderer = MicronRenderer::new();
        let content = "`F222This is colored text`f\nThis is normal text";
        let styled = renderer.parse(content);

        assert_eq!(styled.len(), 2, "Expected 2 segments, got {}", styled.len());
        assert_eq!(
            styled[0].0, "This is colored text",
            "First segment text mismatch"
        );
        assert_eq!(
            styled[1].0, "\nThis is normal text",
            "Second segment text mismatch"
        );

        assert!(
            styled[0].1.foreground.is_some(),
            "First segment should have color"
        );
        assert!(
            styled[1].1.foreground.is_none(),
            "Second segment should not have color"
        );
    }

    #[test]
    fn test_color_parsing() {
        let color = parse_color("222");
        assert_eq!(
            color,
            Color::from_rgb(
                0x22 as f32 / 255.0,
                0x22 as f32 / 255.0,
                0x22 as f32 / 255.0
            )
        );
    }
}
