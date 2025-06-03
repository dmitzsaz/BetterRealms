# BetterRealms

> Self-hosted Minecraft Realms solution with almost fully reversed API. **Under heavy development.**

## 🚀 Quickstart (Docker)

### Clone & Setup

```bash
git clone https://github.com/yourusername/BetterRealms.git
cd BetterRealms
docker compose up -d
```

### Configuration

* Copy `.env.example` to `.env` and configure:

  * `DB_ROOT_PASSWORD`
  * `R2_ENDPOINT`, `R2_ACCESS_KEY`, `R2_SECRET_KEY`, `R2_BUCKET`
  * `REALMSORCHESTRATOR_IP` (requires [RealmsOrchestrator](https://github.com/dmitzsaz/RealmsOrchestrator))

## 📦 Key Features

* Almost fully reversed Minecraft Realms API
* Realms and World Slots Management
* Invite system
* Snapshot backups to Cloudflare R2

Check `main.py` for complete API endpoints.

## 🤝 Contributing

PRs and issues welcome!
