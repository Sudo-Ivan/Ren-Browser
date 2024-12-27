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
    literal_mode: bool,
    renderer_type: RendererType,
}

impl MicronRenderer {
    pub fn new() -> Self {
        Self {
            current_style: MicronStyle::default(),
            literal_mode: false,
            renderer_type: RendererType::Micron,
        }
    }

    pub fn get_renderer_type(&self) -> RendererType {
        self.renderer_type.clone()
    }

    pub fn parse(&mut self, content: &str) -> Vec<(String, MicronStyle)> {
        match self.try_parse_micron(content) {
            Ok(styled) => styled,
            Err(_) => vec![(content.to_string(), MicronStyle::default())]
        }
    }

    fn try_parse_micron(
        &mut self,
        content: &str,
    ) -> Result<Vec<(String, MicronStyle)>, ()> {
        let mut styled_content = Vec::new();
        let mut buffer = String::new();

        for line in content.lines() {
            if line.starts_with('`') {
                // Push existing buffer with current style
                if !buffer.is_empty() {
                    styled_content.push((buffer.clone(), self.current_style.clone()));
                    buffer.clear();
                }
                self.handle_tag(line);
            } else {
                buffer.push_str(line);
                buffer.push('\n');
            }
        }

        // Push remaining buffer
        if !buffer.is_empty() {
            styled_content.push((buffer, self.current_style.clone()));
        }

        Ok(styled_content)
    }

    fn handle_tag(&mut self, line: &str) {
        let tag = &line[1..];
        match tag.chars().next() {
            Some('F') => {
                if tag.len() >= 4 {
                    self.current_style.foreground = Some(parse_color(&tag[1..4]));
                }
            }
            Some('f') => {
                self.current_style.foreground = None;
            }
            Some('B') => {
                if tag.len() >= 4 {
                    self.current_style.background = Some(parse_color(&tag[1..4]));
                }
            }
            Some('b') => {
                self.current_style.background = None;
            }
            Some('c') => {
                self.current_style.alignment = TextAlignment::Center;
            }
            Some('r') => {
                self.current_style.alignment = TextAlignment::Right;
            }
            Some('l') => {
                self.current_style.alignment = TextAlignment::Left;
            }
            Some('a') => {
                self.current_style.alignment = TextAlignment::Default;
            }
            Some('!') => {
                self.current_style.bold = true;
            }
            Some('*') => {
                self.current_style.italic = true;
            }
            Some('_') => {
                self.current_style.underline = true;
            }
            Some('`') => {
                self.current_style = MicronStyle::default();
            }
            _ => (), // Ignore unknown tags
        }
    }
}

fn parse_color(hex: &str) -> Color {
    if hex == "default" {
        return Color::from_rgb(0.87, 0.87, 0.87); // Default color
    }

    if hex.len() == 3 {
        if hex.starts_with('g') {
            // Grayscale value (g00 to g99)
            if let Ok(val) = u8::from_str_radix(&hex[1..], 10) {
                let normalized = (val as f32) / 99.0;
                return Color::from_rgb(normalized, normalized, normalized);
            }
        } else {
            // RGB hex shorthand
            let r = u8::from_str_radix(&hex[0..1].repeat(2), 16).unwrap_or(0);
            let g = u8::from_str_radix(&hex[1..2].repeat(2), 16).unwrap_or(0);
            let b = u8::from_str_radix(&hex[2..3].repeat(2), 16).unwrap_or(0);

            // Convert to normalized floats
            let (r, g, b) = (r as f32 / 255.0, g as f32 / 255.0, b as f32 / 255.0);

            // Basic ASCII color approximation
            if r == g && g == b {
                // Grayscale
                if r < 0.2 {
                    return Color::from_rgb(0.0, 0.0, 0.0);
                }
                // Black
                else if r < 0.4 {
                    return Color::from_rgb(0.25, 0.25, 0.25);
                } else if r < 0.6 {
                    return Color::from_rgb(0.5, 0.5, 0.5);
                } else if r < 0.8 {
                    return Color::from_rgb(0.75, 0.75, 0.75);
                } else {
                    return Color::from_rgb(1.0, 1.0, 1.0);
                } // White
            } else {
                // Color approximation
                let threshold = 0.5;

                if r > threshold && g > threshold && b < threshold {
                    return Color::from_rgb(1.0, 1.0, 0.0);
                } // Yellow
                if r > threshold && g < threshold && b < threshold {
                    return Color::from_rgb(1.0, 0.0, 0.0);
                } // Red
                if r < threshold && g > threshold && b < threshold {
                    return Color::from_rgb(0.0, 1.0, 0.0);
                } // Green
                if r < threshold && g < threshold && b > threshold {
                    return Color::from_rgb(0.0, 0.0, 1.0);
                } // Blue
                if r > threshold && g < threshold && b > threshold {
                    return Color::from_rgb(0.8, 0.2, 0.8);
                } // Magenta
                if r < threshold && g > threshold && b > threshold {
                    return Color::from_rgb(0.2, 0.8, 0.8);
                } // Cyan

                return Color::from_rgb(r, g, b);
            }
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
    fn test_color_parsing() {
        let color = parse_color("f00");
        assert_eq!(color, Color::from_rgb(1.0, 0.0, 0.0));
    }

    #[test]
    fn test_basic_parsing() {
        let mut renderer = MicronRenderer::new();
        let content = "`F222This is colored text`f\nThis is normal text";
        let styled = renderer.parse(content);
        assert_eq!(styled.len(), 2);
    }
}
