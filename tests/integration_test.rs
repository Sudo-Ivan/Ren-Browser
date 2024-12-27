use ren_browser::{
    api::{ApiStatus, Node},
    renderers::mu_renderer::{MicronRenderer, RendererType, TextAlignment},
};

#[test]
fn test_micron_renderer_basic() {
    let mut renderer = MicronRenderer::new();
    let content = "Hello World";
    let result = renderer.parse(content);

    assert_eq!(result.len(), 1);
    assert_eq!(result[0].0, "Hello World");
    assert_eq!(renderer.get_renderer_type(), RendererType::Plain);
}

#[test]
fn test_micron_renderer_formatting() {
    let mut renderer = MicronRenderer::new();
    let content = "`BHello`b World";
    let result = renderer.parse(content);

    assert_eq!(result.len(), 2);
    assert_eq!(result[0].0, "Hello");
    assert!(result[0].1.bold);
    assert_eq!(result[1].0, " World");
    assert!(!result[1].1.bold);
    assert_eq!(renderer.get_renderer_type(), RendererType::Micron);
}

#[test]
fn test_micron_renderer_colors() {
    let mut renderer = MicronRenderer::new();
    let content = "`F900Red Text`f Normal Text";
    let result = renderer.parse(content);

    assert_eq!(result.len(), 2);
    assert_eq!(result[0].0, "Red Text");
    assert!(result[0].1.foreground.is_some());
    assert_eq!(result[1].0, " Normal Text");
    assert_eq!(renderer.get_renderer_type(), RendererType::Micron);
}

#[test]
fn test_micron_renderer_alignment() {
    let mut renderer = MicronRenderer::new();
    let content = "`CCenter Text`c\nLeft Text";
    let result = renderer.parse(content);

    assert_eq!(result.len(), 2);
    assert_eq!(result[0].0, "Center Text");
    assert_eq!(result[0].1.alignment, TextAlignment::Center);
    assert_eq!(result[1].0, "Left Text");
    assert_eq!(result[1].1.alignment, TextAlignment::Default);
}

#[test]
fn test_api_status() {
    let status = ApiStatus {
        status: "Connected".to_string(),
        address: "test.address".to_string(),
    };

    assert_eq!(status.status, "Connected");
    assert!(!status.address.is_empty());
}

#[test]
fn test_node_creation() {
    let node = Node {
        destination_hash: "test_hash".to_string(),
        identity_hash: "id_hash".to_string(),
        display_name: Some("Test Node".to_string()),
        aspect: "test".to_string(),
        created_at: 0,
        updated_at: 0,
    };

    assert_eq!(node.destination_hash, "test_hash");
    assert_eq!(node.display_name.as_deref().unwrap(), "Test Node");
}
