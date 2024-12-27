use iced::Color;
use log::{debug, warn};

#[derive(Debug, Clone, PartialEq, Copy)]
pub enum TextAlignment {
    Left,
    Center,
    Right,
    Default,
}

// Separate style for links to avoid recursion
#[derive(Debug, Clone)]
pub struct LinkStyle {
    pub bold: bool,
    pub italic: bool,
    pub underline: bool,
    pub foreground: Option<Color>,
    pub background: Option<Color>,
    pub section_depth: u8,
    pub alignment: TextAlignment,
    pub selectable: bool,
}

#[derive(Debug, Clone)]
pub struct Link {
    pub label: String,
    pub url: String,
    pub style: LinkStyle,
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
    pub selectable: bool,
    pub link: Option<Box<Link>>, // Use Box to break the recursion
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
            selectable: true,
            link: None,
        }
    }
}

#[derive(Debug, Clone)]
pub struct ParserState {
    pub literal: bool,
    pub style: MicronStyle,
    pub default_align: TextAlignment,
}

impl Default for ParserState {
    fn default() -> Self {
        Self {
            literal: false,
            style: MicronStyle::default(),
            default_align: TextAlignment::Left,
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
            renderer_type: RendererType::default(),
        }
    }

    pub fn get_renderer_type(&self) -> RendererType {
        self.renderer_type.clone()
    }

    pub fn parse(&mut self, content: &str) -> Vec<(String, MicronStyle)> {
        // Check if we should use Micron renderer based on content
        if content.contains('`') {
            self.renderer_type = RendererType::Micron;
            match self.try_parse_micron(content) {
                Ok(styled) => styled,
                Err(_) => {
                    debug!("Failed to parse Micron content, falling back to plain text");
                    vec![(content.to_string(), MicronStyle::default())]
                }
            }
        } else {
            self.renderer_type = RendererType::Plain;
            vec![(content.to_string(), MicronStyle::default())]
        }
    }

    fn try_parse_micron(&mut self, content: &str) -> Result<Vec<(String, MicronStyle)>, ()> {
        let mut styled_content = Vec::new();
        let mut state = ParserState::default();
        let mut preserve_whitespace = false;

        for line in content.split('\n') {
            // Handle literal mode toggle
            if line == "`=" {
                state.literal = !state.literal;
                preserve_whitespace = state.literal; // Preserve whitespace in literal mode
                continue;
            }

            if state.literal {
                // In literal mode, preserve all whitespace and characters exactly
                styled_content.push((format!("{}\n", line), state.style.clone()));
                continue;
            }

            if line.is_empty() {
                styled_content.push(("\n".to_string(), state.style.clone()));
                continue;
            }

            if !state.literal {
                // Handle comments
                if line.starts_with('#') {
                    continue;
                }

                // Handle section depth reset
                if line.starts_with('<') {
                    state.style.section_depth = 0;
                    self.parse_line(
                        &line[1..],
                        &mut state,
                        &mut styled_content,
                        preserve_whitespace,
                    )?;
                    continue;
                }

                // Handle section headings
                if line.starts_with('>') {
                    let depth = line.chars().take_while(|&c| c == '>').count();
                    state.style.section_depth = depth as u8;

                    // Apply heading style
                    let prev_style = state.style.clone();
                    state.style.background = Some(match depth {
                        1 => Color::from_rgb(0.73, 0.73, 0.73),
                        2 => Color::from_rgb(0.60, 0.60, 0.60),
                        3 => Color::from_rgb(0.47, 0.47, 0.47),
                        _ => Color::from_rgb(0.33, 0.33, 0.33),
                    });

                    self.parse_line(
                        &line[depth..],
                        &mut state,
                        &mut styled_content,
                        preserve_whitespace,
                    )?;
                    state.style = prev_style;
                    continue;
                }

                // Handle horizontal dividers with custom characters
                if line.starts_with('-') {
                    let divider = if line.len() > 1 {
                        line.chars().nth(1).unwrap_or('─')
                    } else {
                        '─'
                    };

                    // Support custom width dividers
                    let width = if line.len() > 2 {
                        line[2..].parse::<usize>().unwrap_or(80)
                    } else {
                        80
                    };

                    let line = divider.to_string().repeat(width);
                    styled_content.push((format!("{}\n", line), state.style.clone()));
                    continue;
                }

                // Handle ASCII art blocks
                if line.starts_with('|') {
                    preserve_whitespace = true;
                    let content = &line[1..];
                    styled_content.push((format!("{}\n", content), state.style.clone()));
                    continue;
                }
            }

            self.parse_line(line, &mut state, &mut styled_content, preserve_whitespace)?;
            preserve_whitespace = false;
        }

        Ok(styled_content)
    }

    fn parse_line(
        &self,
        line: &str,
        state: &mut ParserState,
        styled_content: &mut Vec<(String, MicronStyle)>,
        preserve_whitespace: bool,
    ) -> Result<(), ()> {
        let mut current_text = String::new();
        let mut chars = line.chars().peekable();

        // Preserve leading whitespace if in preserve mode
        if preserve_whitespace {
            while let Some(&c) = chars.peek() {
                if c.is_whitespace() {
                    current_text.push(c);
                    chars.next();
                } else {
                    break;
                }
            }
        }

        while let Some(c) = chars.next() {
            if state.literal {
                current_text.push(c);
                continue;
            }

            match c {
                '\\' => {
                    if let Some(&next) = chars.peek() {
                        chars.next();
                        current_text.push(next);
                    }
                }
                '[' => {
                    // Handle link parsing
                    if !current_text.is_empty() {
                        styled_content.push((current_text.clone(), state.style.clone()));
                        current_text.clear();
                    }

                    let mut link_text = String::new();
                    let mut link_url = String::new();
                    let mut in_url = false;

                    while let Some(lc) = chars.next() {
                        match lc {
                            '`' => {
                                in_url = true;
                                continue;
                            }
                            ']' => {
                                break;
                            }
                            _ => {
                                if in_url {
                                    link_url.push(lc);
                                } else {
                                    link_text.push(lc);
                                }
                            }
                        }
                    }

                    // Create link style
                    let mut link_style = state.style.clone();
                    link_style.foreground = Some(Color::from_rgb(0.4, 0.6, 1.0));
                    link_style.underline = true;
                    link_style.link = Some(Box::new(Link {
                        label: link_text.clone(),
                        url: link_url,
                        style: LinkStyle {
                            // Convert MicronStyle to LinkStyle
                            bold: state.style.bold,
                            italic: state.style.italic,
                            underline: state.style.underline,
                            foreground: state.style.foreground,
                            background: state.style.background,
                            section_depth: state.style.section_depth,
                            alignment: state.style.alignment,
                            selectable: state.style.selectable,
                        },
                    }));

                    styled_content.push((link_text, link_style));
                }
                '`' => {
                    if !current_text.is_empty() {
                        styled_content.push((current_text.clone(), state.style.clone()));
                        current_text.clear();
                    }

                    // Parse formatting command
                    if let Some(cmd) = chars.next() {
                        match cmd {
                            'F' => {
                                // Parse color code
                                let color = chars.by_ref().take(3).collect::<String>();
                                state.style.foreground = Some(parse_color(&color));
                            }
                            'f' => state.style.foreground = None,
                            'B' => {
                                let color = chars.by_ref().take(3).collect::<String>();
                                state.style.background = Some(parse_color(&color));
                            }
                            'b' => state.style.background = None,
                            '!' => state.style.bold = !state.style.bold,
                            '_' => state.style.underline = !state.style.underline,
                            '*' => state.style.italic = !state.style.italic,
                            'c' => state.style.alignment = TextAlignment::Center,
                            'l' => state.style.alignment = TextAlignment::Left,
                            'r' => state.style.alignment = TextAlignment::Right,
                            'a' => state.style.alignment = state.default_align,
                            '`' => {
                                // Reset all formatting
                                state.style = MicronStyle::default();
                                state.style.section_depth = 0;
                            }
                            _ => current_text.push(cmd),
                        }
                    }
                }
                _ => current_text.push(c),
            }
        }

        if !current_text.is_empty() {
            styled_content.push((format!("{}\n", current_text), state.style.clone()));
        } else {
            styled_content.push(("\n".to_string(), state.style.clone()));
        }

        Ok(())
    }

    // Helper method to check if a string is a valid node path
    fn is_node_path(url: &str) -> bool {
        url.ends_with(".mu") || url.starts_with(":/")
    }

    // Helper method to format node URLs
    fn format_node_url(url: &str) -> String {
        if url.starts_with(":/") {
            format!("{}", &url[2..])
        } else if !url.contains(":/") {
            format!("page/{}", url)
        } else {
            url.to_string()
        }
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
