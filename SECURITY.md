# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

The Redis-Shake Management Platform team takes security bugs seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

### How to Report a Security Vulnerability?

If you believe you have found a security vulnerability in Redis-Shake Management Platform, please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@your-domain.com**

Please include the following information in your report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours.
- **Initial Response**: We will send you a more detailed response within 72 hours indicating the next steps in handling your report.
- **Progress Updates**: We will keep you informed of the progress towards a fix and full announcement.
- **Credit**: We may ask if you would like to be credited for the discovery when we announce the fix.

### Security Update Process

1. **Confirmation**: We confirm the vulnerability and determine its severity
2. **Fix Development**: We develop a fix for the vulnerability
3. **Testing**: We thoroughly test the fix
4. **Release**: We release the security update
5. **Disclosure**: We publicly disclose the vulnerability details after the fix is available

## Security Best Practices

When using Redis-Shake Management Platform:

1. **Network Security**
   - Run the application behind a firewall
   - Use HTTPS in production environments
   - Restrict access to management interfaces

2. **Authentication**
   - Use strong passwords for Redis instances
   - Enable Redis AUTH when possible
   - Consider using TLS for Redis connections

3. **Configuration**
   - Review TOML configurations before deployment
   - Avoid exposing sensitive information in logs
   - Use environment variables for sensitive data

4. **Updates**
   - Keep the platform updated to the latest version
   - Monitor security advisories
   - Subscribe to release notifications

## Scope

This security policy applies to the following components:

- Redis-Shake Management Platform backend (FastAPI)
- Redis-Shake Management Platform frontend (React)
- Docker configurations
- CI/CD pipelines
- Documentation and examples

## Out of Scope

The following are generally considered out of scope:

- Vulnerabilities in third-party dependencies (please report to respective maintainers)
- Issues in Redis-Shake itself (please report to the Redis-Shake project)
- Social engineering attacks
- Physical attacks

## Contact

For any questions about this security policy, please contact us at security@your-domain.com.

## Recognition

We would like to thank the following individuals for their responsible disclosure of security vulnerabilities:

<!-- This section will be updated as we receive and address security reports -->

---

**Note**: Please replace `security@your-domain.com` with your actual security contact email address.
