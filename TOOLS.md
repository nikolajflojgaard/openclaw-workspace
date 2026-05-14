# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### Memory helpers

- Build/update the local memory index with: `python3 scripts/memory_index.py`
- Search the local memory index with: `python3 scripts/memory_search.py "your query"`
- The indexed retrieval layer is a lightweight local helper; curated truth still lives in `MEMORY.md`.

### Local secrets helpers

- Home Assistant MCP token is stored in macOS Keychain under service: `homeassistant-mcp-token`
- Use `scripts/mcporter-ha.sh` to load the token into `HOMEASSISTANT_MCP_TOKEN` and run `mcporter` without keeping the token in workspace files

