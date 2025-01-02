# Hirule Trading System

A comprehensive trading system with memory integration, risk management, and performance analytics.

## Components

- Event Logging System
- Configuration Management
- Performance Analytics
- Risk Monitoring
- Memory System Integration

## Setup

1. Copy `config/default_config.json` to `config/config.json`
2. Modify configuration values as needed
3. Run `python src/main.py config/config.json`

## Testing

Run integration tests:
```bash
python -m pytest tests/integration
```

## Project Structure

```
├── src/
│   ├── analytics/        # Performance and risk analytics
│   ├── config/           # Configuration management
│   ├── logging/          # Event logging system
│   ├── memory/           # Memory system integration
│   └── main.py           # Main entry point
├── tests/
│   ├── analytics/        # Analytics tests
│   ├── integration/      # System integration tests
│   └── logging/          # Logging tests
└── config/
    └── default_config.json  # Default configuration
```
