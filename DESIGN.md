# Ren Browser Design Document

## Overview
Ren Browser is a lightweight browser designed using Iced framework for browsing Reticulum nodes and rendering Micron markup text and possible more types of content, with a focus on simplicity.

## Architecture

### Core Components

1. **Main Application (src/main.rs)**
   - Handles the core application state
   - Manages tabs and navigation
   - Coordinates between UI and renderers
   - Implements keyboard shortcuts from (src/shortcuts.rs)

2. **Renderers (src/renderers/)**
   - `mu_renderer.rs`: Micron markup renderer
   - Extensible design for future renderers
   - Fallback to plain text renderer when needed

3. **API Layer (src/api/)**
   - Handles communication with backend services
   - Manages page fetching and status updates
   - Asynchronous operations

4. **Styles (src/styles.rs)**
   - Centralized styling system
   - Theme management
   - Consistent color schemes

### Key Features

1. **Tab Management**
   - Multiple tabs support
   - Individual tab state tracking
   - Tab-specific renderer selection

2. **Micron Markup Support**
   - Text formatting (bold, italic, underline)
   - Color support (RGB, grayscale)
   - Section headings
   - Literal mode
   - Comments

3. **Keyboard Shortcuts**
   - Ctrl+R: Reload page
   - Extensible shortcut system

## Design Decisions

### Renderer Architecture
- Renderers implement fallback mechanisms
- Clear separation between parsing and rendering
- Support for multiple renderer types
- Easy to add new renderers

### UI Design
- Clean, minimal interface
- Dark theme by default
- Status indicators
- Renderer type display
- Responsive layout

### State Management
- Centralized application state
- Tab-specific states
- Clear message passing system
- Predictable update flow

## Future Considerations

1. **Planned Features**
   - Link support
   - Form elements
   - Additional keyboard shortcuts
   - Theme switching
   - More renderer types

2. **Performance Optimizations**
   - Lazy loading for large documents
   - Caching mechanisms
   - Renderer optimizations

3. **Extensions**
   - Plugin system
   - Custom renderer support
   - Theme customization

See [TODO.md](TODO.md) for more details.

## Contributing
When contributing to Ren Browser, please:
1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Maintain consistent styling
5. Consider backwards compatibility

## Code Style
- Minimal comments
- Clear function names
- Consistent formatting
- Type safety
- Error handling
- Unit tests for critical components 