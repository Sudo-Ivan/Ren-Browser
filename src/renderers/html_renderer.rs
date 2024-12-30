use iced::{
    widget::{button, container, text, Column},
    Color, Element, Length,
};
use log::debug;

use crate::Message;

#[derive(Debug, Clone, PartialEq)]
pub enum TextAlignment {
    Left,
    Center,
    Right,
}

#[derive(Debug, Clone)]
pub struct HTMLStyle {
    pub color: Option<Color>,
    pub background_color: Option<Color>,
    pub font_size: Option<f32>,
    pub font_weight: Option<u16>,
    pub text_align: TextAlignment,
    pub margin: [f32; 4],
    pub padding: [f32; 4],
    pub width: Option<Length>,
    pub height: Option<Length>,
}

#[derive(Debug, Clone)]
pub enum HTMLNode {
    Element {
        tag: String,
        attributes: Vec<(String, String)>,
        children: Vec<HTMLNode>,
        style: HTMLStyle,
    },
    Text(String),
}

pub struct HTMLRenderer {
    current_style: HTMLStyle,
}

impl HTMLRenderer {
    pub fn new() -> Self {
        Self {
            current_style: HTMLStyle::default(),
        }
    }

    pub fn parse(&mut self, content: &str, _css: Option<&str>) -> Vec<Element<Message>> {
        let nodes = self.parse_html(content);
        let mut elements = Vec::new();

        for node in nodes {
            self.render_node(node, &mut elements);
        }

        elements
    }

    fn parse_html(&self, content: &str) -> Vec<HTMLNode> {
        let mut nodes = Vec::new();
        let mut current_text = String::new();
        let mut chars = content.chars().peekable();

        while let Some(c) = chars.next() {
            match c {
                '<' => {
                    // Handle text content before tag
                    if !current_text.trim().is_empty() {
                        nodes.push(HTMLNode::Text(current_text.trim().to_string()));
                        current_text.clear();
                    }

                    // Parse tag
                    let mut tag = String::new();
                    while let Some(&c) = chars.peek() {
                        if c == '>' {
                            chars.next();
                            break;
                        }
                        tag.push(chars.next().unwrap());
                    }

                    if tag.starts_with('/') {
                        // Closing tag
                        continue;
                    }

                    // Parse attributes
                    let (tag_name, attributes) = self.parse_attributes(&tag);

                    // Create element node
                    nodes.push(HTMLNode::Element {
                        tag: tag_name,
                        attributes,
                        children: Vec::new(),
                        style: HTMLStyle::default(),
                    });
                }
                _ => current_text.push(c),
            }
        }

        // Handle any remaining text
        if !current_text.trim().is_empty() {
            nodes.push(HTMLNode::Text(current_text.trim().to_string()));
        }

        nodes
    }

    fn parse_attributes(&self, tag: &str) -> (String, Vec<(String, String)>) {
        let parts: Vec<&str> = tag.split_whitespace().collect();
        let tag_name = parts[0].to_string();
        let mut attributes = Vec::new();

        for part in &parts[1..] {
            if let Some((key, value)) = part.split_once('=') {
                let value = value.trim_matches('"');
                attributes.push((key.to_string(), value.to_string()));
            }
        }

        (tag_name, attributes)
    }

    fn render_node(&mut self, node: HTMLNode, elements: &mut Vec<Element<Message>>) {
        match node {
            HTMLNode::Element {
                tag,
                attributes,
                children,
                style,
            } => match tag.as_str() {
                "div" => {
                    let mut column = Column::new();
                    let mut child_elements = Vec::new();

                    for child in children {
                        self.render_node(child, &mut child_elements);
                    }

                    for element in child_elements {
                        column = column.push(element);
                    }

                    elements.push(container(column).into());
                }
                "p" => {
                    let mut child_elements = Vec::new();
                    for child in children {
                        self.render_node(child, &mut child_elements);
                    }
                    elements.extend(child_elements);
                }
                "a" => {
                    let href = attributes
                        .iter()
                        .find(|(k, _)| k == "href")
                        .map(|(_, v)| v.clone())
                        .unwrap_or_default();

                    let mut child_elements = Vec::new();
                    for child in children {
                        self.render_node(child, &mut child_elements);
                    }

                    elements.push(
                        button(text("Link"))
                            .on_press(Message::LinkClicked(href))
                            .into(),
                    );
                }
                _ => debug!("Unsupported tag: {}", tag),
            },
            HTMLNode::Text(content) => {
                elements.push(text(content).into());
            }
        }
    }
}

impl Default for HTMLStyle {
    fn default() -> Self {
        Self {
            color: Some(Color::from_rgb(0.87, 0.87, 0.87)),
            background_color: None,
            font_size: Some(16.0),
            font_weight: Some(400),
            text_align: TextAlignment::Left,
            margin: [0.0; 4],
            padding: [0.0; 4],
            width: None,
            height: None,
        }
    }
}
