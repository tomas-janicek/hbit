# Common Module

This module contains common utilities and data transfer objects (DTOs) used across the project.

## Modules

### DTOs

The DTOs are used to structure and transfer data within the application. Each DTO class includes methods for converting to and from domain models, as well as methods for generating readable string representations.

This file contains various data transfer objects (DTOs) used for representing and transferring data within the application. The DTOs include:

- `AttackStepDto`
- `SkillDto`
- `CAPECDto`
- `MitigationDto`
- `DetectionMethodDto`
- `CweDto`
- `VulnerabilityDto`
- `PatchDto`
- `DeviceDto`
- `DeviceEvaluationDto`
- `PatchEvaluationDto`

### Requests

This file provides a wrapper around HTTP requests using the `httpx` library. It includes classes for making GET and POST requests with retry logic:

- `Requests`
- `HTTPXRequests`

The `HTTPXRequests` class provides methods for making HTTP GET and POST requests with retry logic. It uses the `stamina` library to handle retries on HTTP status errors.

### Utils

This file contains utility functions used across the module:

- `create_url(base: str, path: str) -> str`: Normalizes and constructs a URL from the base and path.
