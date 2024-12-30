# Ren Browser TODO

## Core Features
- [x] Basic browsing functionality
- [x] Node discovery and listing
- [x] Page loading
- [x] Page Caching
- [x] Micron (.mu) renderer (very barebones)
  - [ ] Full 1:1 with Micron Parser JS
  - [ ] Render background window black
- [ ] HTML + CSS renderer (search for at address:/pages/index.html)
- [ ] File downloading from nodes (:/files/) (Ren-API)

## UI/UX Improvements
- [ ] Bookmarks system
  - [ ] Save bookmarks to JSON
  - [ ] Import/export bookmarks
  - [ ] Bookmark categories/folders
  - [ ] Quick bookmark current page (Ctrl+D)
- [ ] Browsing history
  - [ ] Save history to SQLite (setting: disable/enable)
  - [ ] History search
  - [ ] Clear history option
  - [ ] History view with filters
- [x] Tab management
  - [x] Basic tabs
  - [x] Tab switching
  - [ ] Tab persistence between sessions (setting: disable/enable)
  - [ ] Tab drag-and-drop reordering
  - [ ] Tab groups
  - [ ] Tab preview on hover (setting: disable/enable)
- [x] Sidebar
  - [x] Node listing
  - [x] Status display
  - [ ] Minimize sidebar
  - [ ] Resizable width

## Settings & Configuration
- [ ] Settings panel
  - [ ] Theme customization
  - [ ] Font settings
  - [ ] Privacy settings
  - [ ] Network settings
- [ ] Identity management
  - [ ] Create/import identities
  - [ ] Erase identity on exit option
  - [ ] Identity backup/restore
- [x] Keyboard shortcuts
  - [x] Reload page (Ctrl+R)
  - [x] New tab (Ctrl+T)
  - [x] Close tab (Ctrl+W)
  - [ ] Next tab (Ctrl+Tab)
  - [ ] Previous tab (Ctrl+Shift+Tab)

## Network Features
- [x] Connection status indicators
- [ ] Network statistics view
- [ ] Bandwidth usage monitoring
- [ ] Node health monitoring
- [ ] Connection retry/fallback

## Security & Privacy 
- [ ] Private browsing mode (Ren-API)

## Developer Tools
- [ ] Page source viewer
- [ ] Error console
- [x] Debug mode (--debug flag)
- [ ] Performance metrics
  - [ ] Render time
  - [ ] Network RTT
  - [ ] Memory usage
- [ ] Export node page
- [ ] Network inspector

## Documentation
- [ ] User manual
- [ ] Developer documentation
- [ ] API documentation
- [ ] Contribution guidelines
- [ ] Architecture diagrams

## Optimization
- [ ] Performance improvements
  - [ ] Renderer optimization
  - [ ] Network caching
  - [ ] Asset preloading
- [ ] Memory usage optimization
- [ ] Cache management
  - [ ] Cache size limits
  - [ ] Cache clearing
  - [ ] Cache persistence

## Testing
- [x] Basic unit tests
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] Cross-platform testing
- [ ] Network reliability tests
- [ ] UI/UX testing

## Packaging & Distribution
- [ ] Release builds
- [ ] Package for different platforms
  - [ ] Linux
  - [ ] macOS
  - [ ] Windows