# 🎮 GamerBot - RPG & MMO News Aggregator

An efficient, asynchronous Discord Bot designed to fetch and deliver the latest news about **RPG** and **MMORPG** games directly from the Steam API.

> **Project Status:** 🚀 **Active Development**
>
> *Origin Story:* This project started as a technical proficiency test for the **Kodland Python Pro** course. However, seeing its potential, I decided to maintain and expand it into a fully-featured product with AI capabilities.

## ✨ Key Features

- **Asynchronous Monitoring:** Built with `discord.ext.tasks` and `aiohttp` to fetch data without blocking the event loop.
- **Smart Deduplication:** Implements an in-memory caching logic (`Set` based) to prevent spamming the same news twice.
- **Multi-Genre Support:** Configurable dictionary structure to easily manage game lists (RPG, MMORPG, etc.).
- **Docker First:** Fully containerized development environment ensuring consistency across machines.

## 🛠️ Tech Stack

- **Language:** Python 3.10
- **Core Library:** `discord.py`
- **Networking:** `aiohttp` (Async HTTP Requests)
- **Infrastructure:** Docker & Docker Compose

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose installed.
- A Discord Bot Token (with Message Content Intent enabled).

### Installation Guide


1. **Clone the repository:**
```bash
git clone https://github.com/LucasPetersCG/gamerbot.git
cd gamerbot
```
2. **Environment Setup:**
Create a .env file in the root directory (you can copy .env.example) and add your credentials:
```bash

DISCORD_TOKEN=your_token_here
NEWS_CHANNEL_ID=your_channel_id_here

```
3. **Launch with Docker:**
```bash

docker-compose up -d --build

```
4. **Initialize the Bot:**
```bash

docker-compose exec bot bash

python main.py

```
5. **Check Logs:**
```bash

docker-compose logs -f

```
**🔮 Future Roadmap**

- [] AI Integration: Translate news summaries to Portuguese (PT-BR) using LLMs (Groq API).

- [] RSS Feeds: Support for external news sources (IGN, Kotaku, Unity Blog).

- [] User Commands: Allow users to subscribe/unsubscribe from specific genres via commands.

- [] Disclaimer: This is an educational project currently under expansion.