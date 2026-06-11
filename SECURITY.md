# Security Policy

## Supported Versions

The following versions of AI Code Review Agent are currently supported with security updates.

| Version            | Supported |
| ------------------ | --------- |
| Latest Release     | ✅         |
| Development Branch | ✅         |
| Older Versions     | ❌         |

---

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

### How to Report

Open a private GitHub issue or contact the maintainer with the following information:

* Description of the vulnerability
* Steps to reproduce
* Potential impact
* Suggested mitigation (if available)

### Response Timeline

* Initial acknowledgement: Within 72 hours
* Investigation: Within 7 days
* Resolution timeline: Depends on severity and complexity

---

## Responsible Disclosure

Please do not publicly disclose security vulnerabilities until they have been reviewed and addressed.

Responsible disclosure helps protect users and allows fixes to be developed before details become public.

---

## Security Best Practices

When using this project:

* Never commit API keys, access tokens, or secrets.
* Store credentials in environment variables or a `.env` file.
* Keep dependencies updated.
* Review AI-generated recommendations before applying them.
* Restrict GitHub token permissions to the minimum required scope.

---

## Scope

This project interacts with:

* GitHub repositories
* GitHub API tokens
* Local LLM services through Ollama
* User-provided source code

Users are responsible for ensuring sensitive information is not exposed during repository analysis.

---

## Disclaimer

AI Code Review Agent is provided for educational, research, and development purposes. While the system attempts to identify security vulnerabilities and code-quality issues, it does not guarantee the detection of all bugs, vulnerabilities, or malicious code.

Always perform manual verification before applying recommendations to production systems.

---

## Maintainer

**Rishiraj Chaurasiya**
B.Tech — Artificial Intelligence & Machine Learning

GitHub: https://github.com/chaurasiyarishiraj84-alt
