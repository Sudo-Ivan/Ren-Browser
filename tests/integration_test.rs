use ren_browser::api::{ApiStatus, Node};

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
