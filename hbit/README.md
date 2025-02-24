# HBIT

This project is a comprehensive evaluation and extraction tool for 
analyzing the security status of devices, particularly focusing on 
iOS devices. It includes various modules for bootstrapping services, 
handling CLI commands, managing configurations, and evaluating device security.

## Project Structure

```
.
├── bootstrap/
├── cli.py
├── clients.py
├── config.py
├── core.py
├── dto.py
├── endpoints/
├── enums.py
├── evaluations/
├── extractors/
├── notebooks/
├── prompting/
├── services/
├── summaries.py
├── tools.py
├── types.py
├── ui/
└── utils.py
```

## Modules

### Core

- **core.py**: Core functionalities and utilities.
- **config.py**: Configuration management.
- **dto.py**: Data transfer objects.
- **enums.py**: Enumerations used across the project.
- **summaries.py**: Logic for generating summaries.
- **tools.py**: TBD
- **types.py**: Type definitions.
- **utils.py**: General utilities.

### Bootstrap

Initializes and configures the services.

### CLI

Command-line interface for interacting with the tool.

### Endpoints

Endpoint for agent-related operations, chain-related operations, and sequence-related operations.

### Evaluations

TBD

### Extractors

TBD

### Notebooks

TBD

### Services

Directory for service-related modules.

## 🎲 Design Decision

TBD

## 🚀 Next Steps

TBD
- Add search API tool (like [Tavily](https://python.langchain.com/docs/integrations/tools/tavily_search/)) that can be used as fallback if our data are not enough.
- Add email evaluation service and tool that communicates with [HIBP API](https://haveibeenpwned.com/API/v3).
- Look into async evaluation and execution. It's certainly not required for this use case but it might be useful to know how it works.

## Usage & UI

Directory for user interface-related modules.

