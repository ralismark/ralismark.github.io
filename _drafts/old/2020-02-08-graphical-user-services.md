---
layout: post
title: Managing graphical user services
tags: linux
---

- sway needs the display manager's environment to start
- systemd user services need sway's environment variable to interact with it (e.g. SWAYSOCK)
- sway also launches programs itself, so needs systemd's environment (e.g. from .config/environment.d)
