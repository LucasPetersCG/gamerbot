# 🎮 GamerBot - AI-Powered RPG & MMO News Aggregator

An intelligent, asynchronous Discord Bot designed to fetch, translate, and summarize the latest news about **RPG**, **MMORPG**, **Tibia**, and **Tabletop Games** directly to your server.

> **Project Status:** 🚀 **Active & Feature-Rich**
>
> *Origin Story:* This project started as a technical proficiency test for the **Kodland Python Pro** course. It has since evolved into a fully-featured product with AI capabilities (Groq/Llama 3), persistent configuration, and multi-source support.

## ✨ Key Features

- **🧠 AI-Powered Summaries:** Uses **Groq API (Llama 3)** to translate and summarize news from English to Portuguese (PT-BR) with a "gamer" persona.
- **📡 Multi-Source Aggregation:**
  - **Steam:** Fetches updates for major RPGs (Baldur's Gate 3, Cyberpunk, Witcher, etc.).
  - **TibiaData API:** Tracks news and tickers directly from Tibia.com.
  - **RSS Feeds:** Monitors tabletop RPG news (D&D, Pathfinder) via Tribality/ENWorld.
- **⚙️ Dynamic Subscription System:** Admins can configure specific channels to receive specific types of news (e.g., `#tibia-news` only gets Tibia updates).
- **💾 JSON Persistence:** Saves channel configurations and history of seen news to prevent data loss on restarts.
- **🐳 Dockerized:** Fully containerized environment ensuring consistency and easy deployment.

## 🛠️ Tech Stack

- **Language:** Python 3.10
- **Core Library:** `discord.py` (Commands & Tasks)
- **AI & LLM:** `groq` (Async Client for Llama 3)
- **Data Fetching:** `aiohttp` (Async Web), `feedparser` (RSS)
- **Architecture:** Modular Service-Based (`services/` folder pattern)
- **Infrastructure:** Docker & Docker Compose

## 🤖 Bot Commands

Commands are restricted to **Administrators** to prevent configuration spam.

### 🔌 Setup & Configuration (Subscribe)
| Command | Description |
| :--- | :--- |
| `!setup_all_news` | Configures the current channel to receive **ALL** news types. |
| `!setup_steam_news` | Configures the current channel to receive only **Steam** news. |
| `!setup_tibia_news` | Configures the current channel to receive only **Tibia** news. |
| `!setup_rpg_news` | Configures the current channel to receive only **RPG/D&D** news. |

### ❌ Removal (Unsubscribe)
| Command | Description |
| :--- | :--- |
| `!remove_all` | Removes **all** subscriptions from the current channel. |
| `!remove_steam` | Stops receiving **Steam** news in the current channel. |
| `!remove_tibia` | Stops receiving **Tibia** news in the current channel. |
| `!remove_rpg` | Stops receiving **RPG** news in the current channel. |

### 🔎 Manual Checks & Debug
| Command | Description |
| :--- | :--- |
| `!force_check` | Forces a global search cycle immediately (respects history/duplicates). |
| `!last_tibia <days>` | Fetches Tibia news from the last X days and posts them **immediately** (ignoring history). |
| `!last_steam` | Fetches and posts the latest news for configured Steam games (ignoring history). |
| `!last_rpg` | Fetches and posts the latest RSS entry from the RPG feed (ignoring history). |
| `!export_chats` | **(Admin)** Exports the logged message history as a `.zip` and sends it in the current channel. |

## ☁️ Deployment & DevOps

The project runs 24/7 in a production environment with an automated pipeline.

- **Infrastructure:** Hosted on **Oracle Cloud Infrastructure (OCI)** using an Ampere (ARM) instance.
- **Containerization:** The application runs inside a Docker container managed by `docker-compose`, ensuring isolation and easy restart policies (`restart: always`).
- **CI/CD Pipeline:** Integrated with **GitHub Actions**.
  1.  Developer pushes code to `main` branch.
  2.  GitHub Action triggers an SSH connection to the Oracle Cloud instance.
  3.  The pipeline executes `git pull`, rebuilds the Docker image, and restarts the service automatically.

## 🚀 Getting Started (Local Development)

### Prerequisites
- Docker & Docker Compose installed.
- A **Discord Bot Token** (with Message Content Intent enabled).
- A **Groq API Key** (for AI summarization).

### Installation Guide

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LucasPetersCG/gamerbot.git
   cd gamerbot
  ```
2. **Environment Setup:** Create a .env file in the root directory and add your credentials:
  ```bash
  DISCORD_TOKEN=your_token_here
  GROQ_API_KEY=your_groq_api_key_here
  ```
3. **Launch with Docker:**
  ```bash
  docker-compose up -d --build
  ```
4. **Verify Installation:** Check the logs to ensure the bot connected successfully.
  ```bash
  docker-compose logs -f
  ```
📂 **Project Structure**

/gamerbot
  ├── main.py                # Bot Entry Point & Command Handler
  ├── requirements.txt       # Python Dependencies
  ├── docker-compose.yml     # Container Orchestration
  ├── .env                   # Secrets (Not committed)
  ├── data/                  # Persisted Data (JSONs)
  │    ├── channel_subscriptions.json
  │    └── seen_news.json
  └── services/              # Logic Modules
       ├── ai_service.py     # Groq/Llama 3 Handler
       ├── steam_service.py  # Steam API Fetcher
       ├── tibia_service.py  # TibiaData API Fetcher
       └── rss_service.py    # Feedparser Logic

## 🔮 Future Roadmap

- [x] AI Integration: Translate news summaries to Portuguese (PT-BR) using LLMs.

- [x] RSS Feeds: Support for external news sources.

- [x] User Commands: Allow users to subscribe/unsubscribe from specific genres.

- [x] Persistence: Save configuration to JSON files.

- [x] CI/CD: Automated deployment to Oracle Cloud.

- [ ] Database: Migrate from JSON to SQLite/PostgreSQL for better scalability.

- [ ] Web Dashboard: Simple front-end to view logs and manage subscriptions.

*Disclaimer:* This is an educational project currently under expansion.