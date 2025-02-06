# HBIT API

This project is a comprehensive API for managing *vulnerabilities*, *patches*, *devices*, 
and *evaluations*. It is built using *FastAPI* and *SQLAlchemy*, and follows a *domain-driven 
design* approach.

## 🌐 Overview

The HBIT API provides endpoints for creating, reading, updating, and deleting various 
entities such as *devices*, *patches*, *CVEs* (Common Vulnerabilities and Exposures), 
*CWEs* (Common Weakness Enumerations), and *CAPECs* (Common Attack Pattern Enumeration 
and Classification). It also includes functionality for *user management* and *authentication*.

## 📁 Directory Structure

### 📂 Domain

The `domain` folder contains the *domain models*, *commands*, *events*, and *DTOs* (Data Transfer Objects). 
It follows the *domain-driven design* principles and encapsulates the *business logic* of the application. 
The models represent the entities in the system, while the commands and events are used for handling 
business operations and domain events.

### 📂 Adapters

The `adapters` folder contains the implementation of the *repository pattern* and 
*ORM* (Object-Relational Mapping) configurations. It includes the *SQLAlchemy models* 
and table definitions, as well as the *repository classes* that interact with the database.

### 📂 API

The `api` folder contains the *FastAPI routes* and *dependencies*. It is responsible 
for defining the *API endpoints* and their corresponding request handlers. 
The routes are organized into different modules based on the entity they manage, 
such as *devices*, *evaluations*, *users*, and *vulnerabilities*.

### 📂 Core

The `core` folder contains the *core configuration* and *utility functions* 
for the project. This includes the *settings configuration*, *logging setup*, 
and *database connection management*.

### 📂 Service Layer

The `service_layer` folder contains the *application services*, *handlers*, 
and the *message bus*. It is responsible for coordinating the application's workflow 
and handling the *business logic*. The handlers process the commands and events, 
while the message bus routes them to the appropriate handlers.

### 📂 Tests

The `tests` folder contains the *test cases* for the project. It includes *unit tests*, 
*integration tests*, and *end-to-end tests* to ensure the correctness and reliability of the application.

### 📂 Alembic

The `alembic` folder contains the *database migration scripts*. *Alembic* is used to manage 
*database schema changes* in a consistent and version-controlled manner. This folder 
includes the migration scripts and configuration files necessary for applying and 
rolling back database migrations.

### 📂 Email Templates

The `email-templates` folder contains the *MJML templates* for generating *HTML emails*. 
These templates are used for sending various types of emails, such as *account creation*, 
*password recovery*, and *notifications*.

## 🎲 Design Decision

This section provides simple explanations to why I went with certain maybe un-convention design 
decision for this kind of project.

### ❓ Why did I implement DDD patterns?

*Domain-Driven Design (DDD)* patterns were implemented to manage the complexity 
of the domain logic and ensure that the code remains maintainable and scalable. 

The key *DDD patterns* used include:

- **Unit of Work (UoW)**: The *UnitOfWork pattern*, as seen in `unit_of_work.py`, helps 
manage transactions and coordinate the writing out of changes. It ensures that 
all changes within a business transaction are committed or rolled back together, 
maintaining data integrity.
- **Domain Models**: *Domain models*, such as `models.CWE` and `models.CAPEC`, encapsulate 
the core business logic and rules. These models represent the key concepts and 
behaviors of the domain, ensuring that the business logic is centralized and consistent.
- **Repository**: The *repository pattern* abstracts the data access layer, providing 
a clean API for the domain layer to interact with the data source. This can be seen 
in the various repository classes used in the *UnitOfWork protocol*, such as `CWERepository` 
and `CAPECRepository`.

Implementing these *DDD patterns* helps in achieving a clear separation of concerns, 
making the codebase easier to understand, test, and maintain.

### ❓ Why did I implement EDA patterns?

*Event-Driven Architecture (EDA)* patterns were implemented to decouple components 
and improve the scalability and maintainability of the system. 

The key *EDA patterns* used include:

- **Message Bus**: The *message bus* facilitates communication between different parts 
of the system by passing messages (events and commands) between them. This helps 
in achieving loose coupling and allows components to evolve independently.
- **Events and Commands**: *Events* represent something that has happened in the system, 
while *commands* represent an action that needs to be taken. Using events and commands 
helps in clearly defining the responsibilities and interactions between 
different components.
- **Handlers**: *Handlers* are responsible for processing *events* and *commands*. 
They encapsulate the *business logic* that needs to be executed in response 
to an *event* or *command*, promoting *separation of concerns* and making the system 
easier to test and maintain.

Implementing these *EDA patterns* helps in building a more flexible and responsive 
system that can easily adapt to changing requirements and handle increased load.

### ❓ Why did I choose to use `svcs` package and not rely on native FastAPI DI?

The `svcs` package was chosen over native *FastAPI dependency injection (DI)* 
to provide a more flexible and decoupled approach to service management, 
**Event-Driven Architecture (EDA)**, and testing. 

The **service locator pattern** used in `svcs` allows for better management of services 
and dependencies, making it easier to handle complex workflows and interactions 
between different components. Additionally, it supports *EDA* by facilitating 
the registration and resolution of event handlers and other services, 
promoting loose coupling and scalability. 

For testing, the *service locator pattern* simplifies the process of mocking 
and injecting dependencies, leading to more maintainable and testable code.

### ❓ Why are views not using repositories or any other already implemented classes?

Views are not using *repositories* or other already implemented classes because their responsibilities differ from those of *handlers*. While *handlers* often require operations to be performed under certain constraints, views primarily handle **select operations**. Mixing these responsibilities can lead to unnecessary complexity and potential issues when changes in one area affect another. By keeping views closer to **pure SQL**, we maintain a clear separation of concerns and simplify the codebase.

## 🚀 Next Steps

1) Use **async / await** for communicating with DB.

## ⚒️ Usage

### 🛠️ Before First Run & Database

> [!TIP]
> Because fully loaded DB has only 6mb. It is packed with code named `app_<created_date>.db`. 
You can use this db by renaming it to `app.db`.

**Migrate DB** using Alembic:

```sh
make migrate
```

**Initialize DB** data:

```sh
make init_db
```

### 🖥️ Running Development Server

```sh
PYTHONPATH=. uv run uvicorn hbit_api.main:app --reload
```

### 🧪 Running Tests

```sh
PYTHONPATH=. uv run pytest hbit_api/tests
```

### 🛠️ Updating DB Schema

Make new migrations:

```sh
make make-migrations m=example_message
```

**Migrate DB** using Alembic:

```sh
make migrate
```

# 📚 Sources

This project is inspired by book **Architecture Patterns with Python**. It takes advantage of **DDD**, **EDA** 
and other patterns described in the book, but it is not a direct copy of the book's code. It is a 
project that I created to learn and practice the concepts presented in the book. It re-implements 
most patterns in different fashion and adds some new patterns that are not described in the book.
