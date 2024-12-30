use iced::Color;

// Default colors
pub const DEFAULT_FG_DARK: Color = Color {
    r: 0.87,
    g: 0.87,
    b: 0.87,
    a: 1.0,
};
pub const DEFAULT_FG_LIGHT: Color = Color {
    r: 0.13,
    g: 0.13,
    b: 0.13,
    a: 1.0,
};
pub const DEFAULT_BG: Color = Color {
    r: 0.0,
    g: 0.0,
    b: 0.0,
    a: 1.0,
};

// Styles for dark theme
pub const STYLES_DARK: [(&str, Color, Color, bool, bool, bool); 4] = [
    ("plain", DEFAULT_FG_DARK, DEFAULT_BG, false, false, false),
    (
        "heading1",
        Color {
            r: 0.13,
            g: 0.13,
            b: 0.13,
            a: 1.0,
        },
        Color {
            r: 0.73,
            g: 0.73,
            b: 0.73,
            a: 1.0,
        },
        false,
        false,
        false,
    ),
    (
        "heading2",
        Color {
            r: 0.07,
            g: 0.07,
            b: 0.07,
            a: 1.0,
        },
        Color {
            r: 0.60,
            g: 0.60,
            b: 0.60,
            a: 1.0,
        },
        false,
        false,
        false,
    ),
    (
        "heading3",
        Color {
            r: 0.0,
            g: 0.0,
            b: 0.0,
            a: 1.0,
        },
        Color {
            r: 0.47,
            g: 0.47,
            b: 0.47,
            a: 1.0,
        },
        false,
        false,
        false,
    ),
];

// Styles for light theme
pub const STYLES_LIGHT: [(&str, Color, Color, bool, bool, bool); 4] = [
    ("plain", DEFAULT_FG_LIGHT, DEFAULT_BG, false, false, false),
    (
        "heading1",
        Color {
            r: 0.0,
            g: 0.0,
            b: 0.0,
            a: 1.0,
        },
        Color {
            r: 0.47,
            g: 0.47,
            b: 0.47,
            a: 1.0,
        },
        false,
        false,
        false,
    ),
    (
        "heading2",
        Color {
            r: 0.07,
            g: 0.07,
            b: 0.07,
            a: 1.0,
        },
        Color {
            r: 0.66,
            g: 0.66,
            b: 0.66,
            a: 1.0,
        },
        false,
        false,
        false,
    ),
    (
        "heading3",
        Color {
            r: 0.13,
            g: 0.13,
            b: 0.13,
            a: 1.0,
        },
        Color {
            r: 0.80,
            g: 0.80,
            b: 0.80,
            a: 1.0,
        },
        false,
        false,
        false,
    ),
];

// Formatting constants
pub const DEFAULT_DIVIDER_WIDTH: usize = 80;
pub const DEFAULT_DIVIDER_CHAR: char = '─';

// Parser constants
pub const LINK_START: char = '[';
pub const LINK_END: char = ']';
pub const STYLE_MARKER: char = '`';
pub const ESCAPE_CHAR: char = '\\';
pub const LITERAL_TOGGLE: &str = "`=";
pub const SECTION_MARKER: char = '>';
pub const COMMENT_MARKER: char = '#';
pub const DIVIDER_MARKER: char = '-';
pub const ASCII_ART_MARKER: char = '|';
pub const DEFAULT_TEXT_COLOR: Color = Color {
    r: 0.87,
    g: 0.87,
    b: 0.87,
    a: 1.0,
};
pub const DEFAULT_LINK_COLOR: Color = Color {
    r: 0.4,
    g: 0.6,
    b: 1.0,
    a: 1.0,
};
pub const SECTION_COLORS: [Color; 4] = [
    Color {
        r: 0.73,
        g: 0.73,
        b: 0.73,
        a: 1.0,
    },
    Color {
        r: 0.60,
        g: 0.60,
        b: 0.60,
        a: 1.0,
    },
    Color {
        r: 0.47,
        g: 0.47,
        b: 0.47,
        a: 1.0,
    },
    Color {
        r: 0.33,
        g: 0.33,
        b: 0.33,
        a: 1.0,
    },
];
pub const NAMED_COLORS: &[(&str, Color)] = &[
    (
        "red",
        Color {
            r: 1.0,
            g: 0.0,
            b: 0.0,
            a: 1.0,
        },
    ),
    (
        "green",
        Color {
            r: 0.0,
            g: 1.0,
            b: 0.0,
            a: 1.0,
        },
    ),
    (
        "blue",
        Color {
            r: 0.0,
            g: 0.0,
            b: 1.0,
            a: 1.0,
        },
    ),
];
