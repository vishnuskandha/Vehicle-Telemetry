# Security Policy

## Supported versions

Only the latest `main` branch receives security updates.

## Reporting a vulnerability

Please do not open a public issue for security problems. Report them privately by
opening a private security advisory on GitHub at:

https://github.com/vishnuskandha/Vehicle-Telemetry/security/advisories/new

or by contacting the maintainer directly. You will receive an acknowledgement
within 5 business days and a plan for the fix.

## Scope

This project runs locally on a Raspberry Pi and reads on-board I2C/GPIO sensors.
There are no network-facing services, authentication endpoints, or secrets in
this repository. Captured telemetry (CSV logs) stays on the device unless you
choose to copy it elsewhere.
