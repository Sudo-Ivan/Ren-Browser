#!/bin/bash

function show_help() {
    echo "Usage: ./run.sh [OPTIONS]"
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -d, --debug       Run in debug mode"
    echo "  -s, --server      Run only the FastAPI server"
    echo "  -g, --gui         Run only the Rust GUI"
    echo "  -b, --both        Run both server and GUI (default)"
    echo "  -r, --release     Run in release mode"
}

# Check for required tools
function check_dependencies() {
    # Check for cargo
    if ! command -v cargo &> /dev/null; then
        echo "Cargo not found. Installing Rust..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
        source "$HOME/.cargo/env"
    fi

    # Check for poetry
    if ! command -v poetry &> /dev/null; then
        echo "Poetry not found. Installing..."
        curl -sSL https://install.python-poetry.org | python3 -
    fi

    # Install Python dependencies
    echo "Installing Python dependencies..."
    poetry install

    # Build Rust project
    echo "Building Rust project..."
    if [ -n "$RELEASE" ]; then
        cargo build --release
    else
        cargo build
    fi
}

DEBUG=""
RUN_SERVER=0
RUN_GUI=0
RELEASE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--debug)
            DEBUG="--debug"
            shift
            ;;
        -s|--server)
            RUN_SERVER=1
            shift
            ;;
        -g|--gui)
            RUN_GUI=1
            shift
            ;;
        -b|--both)
            RUN_SERVER=1
            RUN_GUI=1
            shift
            ;;
        -r|--release)
            RELEASE="--release"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

if [ $RUN_SERVER -eq 0 ] && [ $RUN_GUI -eq 0 ]; then
    RUN_SERVER=1
    RUN_GUI=1
fi

# Check dependencies before running
check_dependencies

API_PID=""

if [ $RUN_SERVER -eq 1 ]; then
    echo "Starting FastAPI server..."
    if [ -n "$DEBUG" ]; then
        poetry run python -m ren_api.main --debug &
    else
        poetry run uvicorn ren_api.main:app &
    fi
    API_PID=$!

    sleep 2
fi

if [ $RUN_GUI -eq 1 ]; then
    if [ -n "$RELEASE" ]; then
        echo "Running in release mode..."
        cargo run --release
    else
        echo "Running in debug mode..."
        cargo run
    fi
fi

if [ -n "$API_PID" ]; then
    kill $API_PID
fi 