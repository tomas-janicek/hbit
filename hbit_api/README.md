# HBIT API

This project is a comprehensive API for managing vulnerabilities, patches, devices, and evaluations. It is built using FastAPI and SQLAlchemy, and follows a domain-driven design approach.

## Overview

The HBIT API provides endpoints for creating, reading, updating, and deleting various entities such as devices, patches, CVEs (Common Vulnerabilities and Exposures), CWEs (Common Weakness Enumerations), and CAPECs (Common Attack Pattern Enumeration and Classification). It also includes functionality for user management and authentication.

## Root Folders

### Domain

The `domain` folder contains the domain models, commands, events, and DTOs (Data Transfer Objects). It follows the domain-driven design principles and encapsulates the business logic of the application. The models represent the entities in the system, while the commands and events are used for handling business operations and domain events.

### Adapters

The `adapters` folder contains the implementation of the repository pattern and ORM (Object-Relational Mapping) configurations. It includes the SQLAlchemy models and table definitions, as well as the repository classes that interact with the database.

### API

The `api` folder contains the FastAPI routes and dependencies. It is responsible for defining the API endpoints and their corresponding request handlers. The routes are organized into different modules based on the entity they manage, such as devices, evaluations, users, and vulnerabilities.

### Core

The `core` folder contains the core configuration and utility functions for the project. This includes the settings configuration, logging setup, and database connection management.

### Service Layer

The `service_layer` folder contains the application services, handlers, and the message bus. It is responsible for coordinating the application's workflow and handling the business logic. The handlers process the commands and events, while the message bus routes them to the appropriate handlers.

### Tests

The `tests` folder contains the test cases for the project. It includes unit tests, integration tests, and end-to-end tests to ensure the correctness and reliability of the application.

### Alembic

The `alembic` folder contains the database migration scripts. Alembic is used to manage database schema changes in a consistent and version-controlled manner. This folder includes the migration scripts and configuration files necessary for applying and rolling back database migrations.


### Email Templates

The `email-templates` folder contains the MJML templates for generating HTML emails. These templates are used for sending various types of emails, such as account creation, password recovery, and notifications.

## 🎲 Design Decision

TBD

## 🚀 Next Steps

## Usage

TBD
