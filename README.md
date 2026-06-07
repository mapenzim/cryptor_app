
# Cryptor App 🛡️

[![PyPI version](https://img.shields.io/pypi/v/cryptor-app.svg)](https://pypi.org/project/cryptor-app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A zero-trust, local-first cryptographic notebook workspace designed to encrypt, store, and manage highly sensitive credentials, access keys, and multi-factor backup tokens. 

Built on a native Python Tkinter desktop stack, this architecture integrates real-time session tracking defenses, dynamic system UI scaling, and an optimized, completely offline asynchronous local AI Copilot engine.

---

## 🚀 Key Features

* **Production PyPI Distribution:** Fully packaged and distributed as a native system command-line utility. 
* **Local Asynchronous AI Copilot:** Seamless interface integration with local Ollama (`llama3:8b`) models via non-blocking asynchronous socket pipes. Generates mathematically complex passwords or cryptographic templates without freezing the view layer canvas thread.
* **Dynamic Canvas Loading Overlay:** Automatically masks the active workspace with an accelerated native vector circular spinner tracking loop while background inference threads compile data streams.
* **Auto-Maturity Session Defenses:** A background daemon tracking countdown lifecycles. At `t-minus 3 minutes`, a centered dark warning modal prompts users to extend or safely terminate credentials. If abandoned, an automated absolute destruction routine wipes memory addresses at 0 seconds.
* **Chronological Explorer Sidebar:** Metadata-driven treeview displays records ordered dynamically, bubbling the latest modified payloads directly to the top. Secretly routes cryptographic mapping IDs behind the scenes, keeping the interface completely clear of ugly raw hexadecimal strings.

---

## 🛠️ Architecture & Core Data Flow

The codebase separates interface layouts, async threading abstractions, and local file encryption engines into standalone decoupled modules:

```text
cryptor_app/
├── pyproject.toml              # Modern build configuration (SPDX license & script bindings)
├── README.md                   # System documentation
└── src/
    └── cryptor_app/
        ├── __init__.py         # Package initialization marker
        ├── __main__.py         # Global CLI terminal launcher bridge
        ├── main.py             # Primary application loop & daemon supervisor
        ├── cryp.ico            # Main interface visual asset icon
        ├── app_files/          
        │   └── run_cookie.py   # Non-blocking session timeout security guard routines
        ├── config_files/       
        │   ├── ai_texter.py    # Async AI interface, blinking handles, and loading canvas
        │   ├── monitor_cookie.py # Centered material dark theme session renewal alert frame
        │   └── styles.py       # Central layout style sheet configuration (Teal/Dark theme)
        ├── extras/             
        │   ├── models.py       # SQLite transactional queries and encryption insertions
        │   ├── encryt.py       # AES-GCM 256-bit envelope encryption core logic
        │   └── init_run.py     # Pre-flight migration guard checking and table schemas
        └── tabs/               
            └── base_frame_tab.py # Workspace view layout structural alignment engine

```

### The Non-Blocking Async AI Pipeline

To keep the desktop UI running smoothly at 60 FPS while querying a local LLM, the application avoids processing work directly on the main thread loop:

```text
[Main Tkinter UI Thread] ---> Spawns ---> [Worker Thread Group]
         |                                           |
  (Stays Responsive:                         Initializes fresh
   Animates Vector Spinner                    asyncio Event Loop
   at 45ms loop refresh)                             |
         ^                                           v
         |-- Invokes via .after() <--- [Awaits AsyncClient.chat()]

```

---

## 🗄️ Database Schema & Migrations

The storage engine runs on an embedded SQLite model configured with native declarations parsing. To support structural metadata descriptions without data loss across legacy environments, an integrated migration guard automatically patches older tables in place on execution bounds:

```sql
CREATE TABLE IF NOT EXISTS lockedfiles(
  file_id PRIMARY KEY UNIQUE,
  owner_name TEXT,
  data_file TEXT,
  cipher_aes TEXT,
  tag TEXT,
  session_key TEXT,
  ts TIMESTAMP,
  last_updated TIMESTAMP,
  file_title TEXT DEFAULT 'Untitled',
  file_for TEXT DEFAULT 'General'
);

```

---

## ⚙️ Installation & Deployment Setup

### 1. Fulfill Local Requirements

Ensure you have the Ollama background engine up and running offline on your local machine configuration:

```bash
# Verify ollama execution and pull down your target model weight
ollama run llama3:8b

```

### 2. Install via PyPI

Open your command terminal and pull down the compiled application wheel directly from the official Python Package Index:

```bash
pip install cryptor-app

```

### 3. Launch the Application

Once installed, run the global console shortcut command anywhere on your machine:

```bash
cryptor-app

```

*(If your system environment PATH variables have not updated to register the shortcut instantly, you can execute the module directly by running `python -m cryptor_app`).*

---

## 🔒 Security Commitments

* **True Zero-Knowledge Execution:** All operations, encryption cycles, and text generation queries run completely localized on your client hardware machine. No internet sockets are ever opened to third-party APIs.
* **Zero Residual Cryptographic Traces:** Background timers clear out background threading loop processes completely upon safe exit routes to guarantee zero memory address leaks or orphaned data handles remain accessible to the host OS runtime space.

```
