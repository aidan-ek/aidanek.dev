# aidanek.dev

An interactive personal portfolio accessible over SSH, paired with a simple static website.

## Overview

This project consists of two parts:

1. **Public SSH-based interface**  
   A custom SSH server that provides a terminal-based UI for browsing my projects, skills, and links.  
   Accessible via:

        ssh aidanek.dev

2. **Static website**  
A lightweight HTML/CSS/JS site served with nginx, hosting basic information and my resume PDF at: 

    https://aidanek.dev/

    *The SSH service is intentionally sandboxed and does not provide shell access.*

## Tech Stack

- Python
- AsyncSSH
- Textual
- Linux
- systemd
- nginx

## Features

- Custom SSH server with terminal UI
- Session limits, rate limiting, and structured logging
- Secure host key management
- Key-only OpenSSH administration on a separate port
- Fail2Ban protection for admin SSH
- Simple static website served via nginx

## Repository Structure

- `sshsite/` – Python SSH application
- `web/` – Static website files
- `deploy/` – Deployment-related configs (nginx, systemd)
- `content/` – Terminal-friendly content (e.g. resume summary)

## Motivation

This project was built to explore:
- secure service deployment
- Linux permissions and service isolation
- TUI interfaces


## License

MIT
