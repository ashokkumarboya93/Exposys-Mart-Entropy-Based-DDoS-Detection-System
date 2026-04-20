# 🛡️ Exposys Mart — Entropy-Based DDoS Detection Platform

## 1. ABSTRACT
Distributed Denial of Service (DDoS) attacks remain one of the most critical threats to modern web infrastructure. Traditional threshold-based detection mechanisms often struggle to differentiate between legitimate flash crowds and coordinated botnet traffic. This project presents **Exposys Mart**, a full-stack, enterprise-grade e-commerce simulation platform integrated with a real-time, custom-built DDoS detection engine. The core of this detection system leverages **Shannon Entropy** to analyze the spatial distribution of incoming IP addresses over sliding time windows. By calculating the entropy of traffic sources, the system can detect volumetric anomalies: a sudden drop in entropy indicates a concentrated attack from a limited pool of IPs, while high entropy signifies normal, distributed user traffic. The platform consists of three distinct interfaces: a public-facing e-commerce storefront, a hacker console for simulating various attack vectors, and an administrative security dashboard for real-time traffic monitoring and analytics. Built using a robust technology stack including FastAPI, MySQL, Celery, and vanilla web technologies, this project serves as a comprehensive demonstration of advanced network security concepts applied in a realistic application environment.

## 2. Table of Contents
1. [ABSTRACT](#1-abstract)
2. [Table of Contents](#2-table-of-contents)
3. [Introduction](#3-introduction)
4. [Existing Method](#4-existing-method)
5. [Proposed method with Architecture](#5-proposed-method-with-architecture)
6. [Methodology](#6-methodology)
7. [Implementation](#7-implementation)
    - [7.1 Tech Stack](#71-tech-stack)
    - [7.2 Folder Structure & File Descriptions](#72-folder-structure--file-descriptions)
    - [7.3 Flow of Execution & Process](#73-flow-of-execution--process)
8. [Conclusion](#8-conclusion)

## 3. Introduction
In the contemporary digital landscape, web applications are continuously exposed to malicious activities, with Volumetric DDoS (Distributed Denial of Service) attacks being particularly prevalent. These attacks aim to exhaust the resources of a target system, rendering it unavailable to legitimate users. 

**Exposys Mart** is an educational and analytical project designed to simulate a complete ecosystem comprising an e-commerce platform, an attacker's toolkit, and a security monitoring system. The primary goal is to demonstrate how Shannon Entropy can be effectively utilized to detect DDoS attacks in real-time.

The system is compartmentalized into three primary portals:
1. **The Exposys Mart Store**: A fully functional, premium e-commerce storefront where legitimate simulated users can browse products, add items to their cart, and complete checkouts. This generates the baseline "normal" traffic.
2. **The PHANTOM Hacker Console**: A specialized interface designed with a cyberpunk aesthetic that allows users to launch simulated DDoS attacks against the store. It provides various attack presets (e.g., Traffic Spike, Bot Swarm, Sustained Flood) to test the detection engine's resilience.
3. **The Admin Security Dashboard**: A comprehensive command center for security analysts. It visualizes real-time traffic metrics, entropy scores, active attacks, and a live packet feed, providing immediate insights into the network's health and security posture.

## 4. Existing Method
Historically, web servers and firewalls have relied on several conventional methods to mitigate DDoS attacks:
- **Signature-Based Detection**: This method relies on maintaining a database of known attack signatures (patterns). While effective against known threats, it completely fails against zero-day attacks or morphed packet structures.
- **Rate Limiting**: Restricting the number of requests a single IP can make within a specific timeframe. Attackers easily bypass this by utilizing large, distributed botnets where each node stays below the rate limit.
- **Static Thresholding**: Triggering an alert when the total volume of traffic exceeds a predefined limit. This approach is highly prone to false positives, often blocking legitimate users during sudden spikes in popularity (e.g., flash sales, viral content).
- **IP Blacklisting**: Manually or automatically blocking IPs that exhibit suspicious behavior. This is a reactive measure and often ineffective against IP spoofing or rapidly changing botnet nodes.

**Limitations of Existing Methods**:
These traditional approaches lack the contextual awareness needed to distinguish between a coordinated attack and organic traffic surges. They analyze traffic volume or static patterns without understanding the fundamental *distribution* and *randomness* of the traffic sources.

## 5. Proposed method with Architecture
To overcome the limitations of traditional methods, this system proposes a behavioral analysis approach using **Shannon Entropy**. Instead of merely counting requests, the system analyzes the probability distribution of incoming IP addresses.

**Why Shannon Entropy?**
In information theory, Shannon Entropy measures the unpredictability or randomness of data. In the context of network traffic:
- **High Entropy (Normal State)**: Traffic originates from a wide, diverse set of IP addresses (legitimate shoppers from various locations). The probability distribution is relatively uniform, resulting in high entropy.
- **Low Entropy (Attack State)**: Traffic is suddenly dominated by a massive volume of requests from a concentrated group of IP addresses (a botnet). The probability distribution skews heavily, resulting in a sharp drop in entropy.

**System Architecture**:
The architecture is designed for high performance, decoupling the request serving from the heavy analytical processing.

1. **Client Layer**: The three frontends (Store, Hacker, Admin) communicate with the backend via RESTful APIs and WebSocket-like polling for real-time data.
2. **API Layer (FastAPI)**: Handles incoming HTTP requests. It acts as the gateway, serving products to the store, accepting attack commands from the hacker console, and serving metrics to the admin dashboard.
3. **Middleware / Interceptor**: Every incoming request to the store is intercepted, and its metadata (IP, endpoint, method, timestamp) is logged to the database as a `TrafficEvent`.
4. **Asynchronous Processing (Celery)**: Background workers continuously pull recent `TrafficEvent` data to perform the intensive entropy calculations without blocking the main API threads.
5. **Data Layer (MySQL / SQLAlchemy)**: Persistently stores user data, product catalogs, traffic logs, and historical entropy scores.

## 6. Methodology
The DDoS detection methodology operates on a continuous, sliding-window basis.

1. **Traffic Ingestion**: All requests made to the Store endpoints are logged into the `traffic_events` table.
2. **Sliding Window Extraction**: Every predefined interval (e.g., 5 seconds), the `DetectionEngine` extracts all traffic events from the last *N* seconds (the sliding window).
3. **Probability Calculation**: The system counts the number of requests originating from each unique IP address within the window. It calculates the probability $p(x_i)$ of each IP address $x_i$:
   `p(x_i) = (Requests from IP_i) / (Total Requests in Window)`
4. **Shannon Entropy Calculation**: The entropy $H(X)$ of the traffic distribution is computed using the formula:
   `H(X) = - Σ [ p(x_i) * log2(p(x_i)) ]`
5. **Baseline Comparison**: The calculated entropy $H(X)$ is compared against a dynamic or pre-established baseline entropy representing normal traffic.
6. **Threshold Triggering**: If $H(X)$ drops below a critical threshold (e.g., `Baseline * 0.7`), the system infers that the traffic is abnormally concentrated.
7. **Attack Classification**: The system updates its global state to `DDOS_ATTACK`, calculates an "Attack Confidence" score based on the severity of the entropy drop, and flags the IPs with the highest request counts as `suspicious_ips`.
8. **Mitigation (Simulated)**: In a real-world scenario, flagged IPs would be dynamically added to a firewall blocklist. In this simulation, they are highlighted in red on the admin dashboard.

## 7. Implementation
This section details the technical realization of the platform.

### 7.1 Tech Stack
**Backend Engine**:
- **Python 3.9+**: The core programming language.
- **FastAPI**: An asynchronous, high-performance web framework for building REST APIs. Chosen for its speed and native Pydantic integration.
- **MySQL**: The primary relational database management system.
- **SQLAlchemy**: The Object-Relational Mapper (ORM) used to interact with the database.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **Celery**: An asynchronous task queue/job queue based on distributed message passing, used for offloading entropy calculations and attack simulations.
- **python-jose (JWT)**: Used for secure, stateless authentication tokens.
- **passlib (bcrypt)**: For secure password hashing.
- **slowapi**: A rate-limiting library for FastAPI.

**Frontend Applications**:
- **HTML5, CSS3, Vanilla JavaScript**: The frontends are built without complex build steps or heavy frameworks (like React or Angular) to ensure raw performance and ease of deployment.
- **Chart.js**: A robust JavaScript charting library used extensively in the Admin Dashboard for visualizing real-time entropy trends, traffic distributions, and attack metrics.
- **CSS Variables & Flexbox/Grid**: Used for responsive, modern UI design (glassmorphism, dark themes).

### 7.2 Folder Structure & File Descriptions
Below is a comprehensive breakdown of the repository structure and the specific role of each file:

```text
ddos-detection-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Marks the directory as a Python package.
│   │   ├── api/
│   │   │   ├── __init__.py      # Package initializer for API routes.
│   │   │   ├── dependencies.py  # Reusable FastAPI dependencies (e.g., get_db, get_current_user).
│   │   │   └── routes/          # Directory containing all API endpoint definitions.
│   │   │       ├── admin.py     # Admin dashboard endpoints (analytics, logs, reports).
│   │   │       ├── attack.py    # Hacker console endpoints for launching attacks.
│   │   │       ├── auth.py      # Authentication endpoints (login, register) for all portals.
│   │   │       ├── metrics.py   # Endpoints providing real-time data for dashboard charts.
│   │   │       └── store.py     # E-commerce endpoints (products, categories, tracking).
│   │   ├── core/
│   │   │   ├── config.py        # Centralized application configuration (loads .env variables).
│   │   │   ├── database.py      # Database connection setup and SQLAlchemy session factory.
│   │   │   ├── security.py      # JWT token generation, verification, and password hashing logic.
│   │   │   └── events.py        # Startup/shutdown event handlers.
│   │   ├── models/
│   │   │   ├── domain.py        # SQLAlchemy ORM models (Users, TrafficEvents, Products, etc.).
│   │   │   └── schemas.py       # Pydantic models for request/response validation and serialization.
│   │   ├── repositories/
│   │   │   └── crud.py          # Database abstraction layer; encapsulates all raw SQL/ORM queries.
│   │   ├── services/
│   │   │   ├── detection.py     # The core DetectionEngine class managing the sliding window logic.
│   │   │   ├── entropy.py       # Mathematical implementation of the Shannon Entropy algorithm.
│   │   │   ├── attacker.py      # Logic for simulating attack waves, IP spoofing, and preset loads.
│   │   │   └── store_svc.py     # Business logic for the e-commerce operations.
│   │   └── utils/
│   │       └── logger.py        # Custom logging configuration for the backend.
│   ├── tasks/
│   │   └── worker.py            # Celery worker definitions for async background tasks.
│   ├── main.py                  # The main FastAPI application instance; assembles routes and mounts static files.
│   ├── seed.py                  # A utility script to populate the database with initial data (products, default users).
│   ├── celery_app.py            # Configuration and initialization of the Celery task queue.
│   ├── requirements.txt         # List of Python dependencies.
│   └── .env                     # Environment variables (DB credentials, secret keys).
├── frontend/
│   ├── store/                   # The E-commerce Application
│   │   ├── index.html           # The main landing page displaying the product catalog.
│   │   ├── auth.html            # User login and registration interface.
│   │   ├── product.html         # Detailed view for a single product.
│   │   ├── css/store.css        # Stylesheet for the store (bright, modern, premium theme).
│   │   ├── js/store-api.js      # Handles all API fetch requests to the backend store routes.
│   │   ├── js/store-app.js      # Core UI logic (DOM manipulation, event listeners).
│   │   └── js/store-cart.js     # Manages the shopping cart state using browser localStorage.
│   ├── admin/                   # The Security Dashboard
│   │   ├── login.html           # Admin authentication portal.
│   │   ├── dashboard.html       # The main analytics dashboard with charts and tables.
│   │   ├── css/admin.css        # Stylesheet for the dashboard (dark, professional SaaS theme).
│   │   ├── js/admin-api.js      # Handles fetching metrics and logs from the backend.
│   │   ├── js/admin-auth.js     # Manages admin JWT tokens and session state.
│   │   └── js/admin-dashboard.js# Initializes Chart.js, handles WebSocket/polling updates, and populates UI.
│   └── hacker/                  # The Attack Simulation Console
│   │   ├── login.html           # Cyberpunk-themed terminal login page.
│   │   ├── index.html           # The attack control panel (presets and custom attacks).
│   │   ├── css/hacker.css       # Stylesheet for the hacker console (neon green, dark background, CRT effects).
│   │   ├── js/hacker-api.js     # Communicates with the backend attack simulation endpoints.
│   │   └── js/hacker-app.js     # Manages the attack UI, animations, and preset selection logic.
└── README.md                    # This comprehensive project documentation.
```

### 7.3 Flow of Execution & Process

**Process 1: Normal User Interaction (Store Flow)**
1. A user visits `localhost:8000/store/index.html`.
2. `store-app.js` initializes and calls `store-api.js` to fetch products.
3. The browser sends a `GET /api/store/products` request to the FastAPI backend.
4. The request hits `main.py`, which routes it to `api/routes/store.py`.
5. The endpoint interacts with `repositories/crud.py` to query the MySQL database.
6. The database returns the product list, validated by Pydantic schemas, and returned as JSON.
7. **Crucially**, during this process, a middleware/interceptor logs this request (IP, time, endpoint) into the `traffic_events` table.

**Process 2: Attack Simulation (Hacker Flow)**
1. The attacker logs into the Hacker Console and selects the "Sustained Flood" preset.
2. `hacker-app.js` sends a `POST /api/attack/preset/sustained_flood` request to the backend.
3. The `attack.py` route receives the request and utilizes the `attacker.py` service.
4. The backend offloads the heavy simulation to a **Celery background task**.
5. The Celery worker generates thousands of dummy requests, simulating IP spoofing, and rapidly inserts them into the `traffic_events` table, simulating a massive volumetric surge.

**Process 3: DDoS Detection & Dashboard Monitoring (Admin Flow)**
1. In the background, a scheduled task (or a continuous loop in the `DetectionEngine`) wakes up every few seconds.
2. It queries the `traffic_events` table for all requests in the last time window.
3. It passes this data to the `EntropyCalculator` (`entropy.py`).
4. If the attacker is running the simulation (Process 2), the entropy score will plummet because thousands of requests are coming from a small pool of simulated IPs.
5. The engine updates the system state to `DDOS_ATTACK` and flags the IPs.
6. Meanwhile, the Admin Dashboard (`admin-dashboard.js`) is continuously polling `GET /api/admin/analytics`.
7. The backend returns the new, low entropy score, the high attack confidence, and the list of flagged IPs.
8. The dashboard instantly updates: the entropy chart line drops into the red zone, the "Suspicious IPs" table populates with the attackers, and the live packet feed visually highlights malicious packets in red.

## 8. Conclusion
The Exposys Mart platform successfully demonstrates the efficacy of Shannon Entropy as a sophisticated mechanism for detecting volumetric DDoS attacks. By shifting the paradigm from simple rate-limiting and threshold-based detection to behavioral probability analysis, the system proves highly capable of distinguishing between legitimate traffic surges and coordinated malicious floods. The decoupled, microservice-inspired architecture utilizing FastAPI and Celery ensures that the complex mathematical calculations required for entropy analysis do not impede the performance of the core e-commerce application. This project serves as a robust educational tool and a foundation for developing advanced, real-time intrusion detection systems in production environments. Future enhancements could involve integrating machine learning models to dynamically adjust the entropy baseline and implementing automated IP-table updates for active mitigation.
