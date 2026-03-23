# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities.
2. Instead, please email the maintainer or open a private security advisory on GitHub.

## Security Considerations

### API Keys

- Never commit your `.env` file or API keys to version control.
- The `.env` file is included in `.gitignore` by default.
- When using the Lightroom plugin settings UI, your OpenAI API key is stored locally in Lightroom's preferences.

### Local Server

- The analysis server binds to `127.0.0.1:8500` (localhost only).
- No authentication is required for the local server -- it is intended for single-user local use only.
- Do not expose the server to the public internet.

### Data Transmission

- Photo data is sent to OpenAI's API over HTTPS (encrypted in transit).
- No data is sent to any other external service.
