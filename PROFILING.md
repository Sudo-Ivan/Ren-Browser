# Profiling

## Memory Profiling

```rust
cargo run --features memory-profiling 2>&1 | grep "monitoring"
```

save to file
```rust
cargo run --features memory-profiling > ren-browser-profiling.log 2>&1
```