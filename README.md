# 🛡️ DDoS Sentinel: Entropy-Based Detection & Analytics System

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **A high-performance, real-time security platform designed to detect and mitigate Volumetric DDoS attacks using Shannon Entropy analysis.**

---

## 1. ABSTRACT
Distributed Denial of Service (DDoS) attacks represent one of the most persistent and damaging threats to modern web infrastructure. Traditional detection methods, which rely on static thresholds or known signatures, often fail to distinguish between legitimate "flash crowds" and coordinated malicious floods. 

This project introduces a sophisticated **Entropy-Based DDoS Detection System** integrated into a live e-commerce simulation environment. By applying **Shannon Entropy** to the statistical distribution of source IP addresses and request intervals, the system identifies anomalies in traffic randomness. A sharp drop in entropy indicates a concentrated attack, even if individual requests stay below traditional rate limits. The platform features a premium storefront (Exposys Mart), an attacker simulation console (PHANTOM), and an enterprise-grade Security Analytics Dashboard, providing an end-to-end demonstration of proactive network defense.

---

## 2. TABLE OF CONTENTS
- [1. Abstract](#1-abstract)
- [2. Introduction](#3-introduction)
- [3. Existing Method](#4-existing-method)
- [4. Proposed Method with Architecture](#5-proposed-method-with-architecture)
- [5. Methodology](#6-methodology)
- [6. Implementation](#7-implementation)
- [7. Key Security Features](#8-key-security-features)
- [8. Folder Structure](#9-folder-structure)
- [9. Conclusion](#10-conclusion)

---

## 3. INTRODUCTION
In the contemporary digital landscape, web availability is paramount. For platforms like **Exposys Mart**, even seconds of downtime during a DDoS attack can lead to catastrophic financial losses. This project bridges the gap between theoretical information theory and practical cybersecurity by implementing a "Self-Defending" web ecosystem.

The system is built on the premise that legitimate user traffic is naturally "random" (high entropy), while DDoS traffic is inherently "organized" and "repetitive" (low entropy). By monitoring this live, the system can trigger mitigation strategies before the server's resources are exhausted.

---

## 4. EXISTING METHOD
Current industry standards for DDoS prevention typically rely on:
1.  **Signature-Based Detection:** Comparing traffic against a database of known attack patterns.
    - *Failure Point:* Cannot detect Zero-Day attacks or polymorphic botnets.
2.  **Rate Limiting / Thresholding:** Blocking IPs that exceed a fixed number of requests.
    - *Failure Point:* High false-positive rates during marketing events (Flash Sales) and vulnerability to "Low-and-Slow" attacks.
3.  **Blacklisting:** Static lists of known malicious IPs.
    - *Failure Point:* Ineffective against modern botnets that use spoofed IPs and rapidly changing nodes.

---

## 5. PROPOSED METHOD WITH ARCHITECTURE
Our proposed solution utilizes **Behavioral Analytics** driven by **Information Theory**. We analyze the *uncertainty* of the entire traffic stream rather than looking at individual requests in isolation.

### System Architecture
The platform is designed with a decoupled, asynchronous architecture for maximum performance:
- **FastAPI Engine:** An asynchronous Python backend that manages traffic ingestion and API responses with micro-second latency.
- **MySQL Data Store:** A robust relational database for persistent storage of product catalogs, user accounts, and granular security logs.
- **Entropy Engine:** A specialized analytical service that calculates probability distributions across sliding time windows.
- **Visual Analytics:** A real-time dashboard using Chart.js to visualize entropy trends and attack confidence levels.

---

## 6. METHODOLOGY
The core of the system is the **Shannon Entropy Algorithm**. 

### The Process:
1.  **Windowing:** The system captures traffic data in 5-second sliding windows.
2.  **Probability Mapping:** For every unique IP address $i$ in the window, it calculates the probability $P(i) = n_i / N$, where $n_i$ is the number of requests from that IP and $N$ is the total requests.
3.  **Entropy Calculation:** The system computes the entropy $H$:
    $$H = -\sum P(i) \log_2 P(i)$$
4.  **Anomaly Detection:** Under normal conditions, many unique IPs visit different pages, resulting in a high $H$ value. During an attack, a few IPs dominate the traffic, causing $H$ to plummet.
5.  **Mitigation:** When $H < \text{Threshold}$, the system flags the traffic as "Critical" and identifies the dominant IPs. Administrators can then use the **One-Click Block** feature to permanently blacklist these IPs.
6.  **Persistent Enforcement:** Blocked IPs are stored in a dedicated `blocked_ips` database table, and a specialized security middleware rejects all subsequent requests from these sources with a `403 Forbidden` status.

---

## 7. IMPLEMENTATION
The project is implemented as a full-stack solution:
- **Backend:** Python, FastAPI, SQLAlchemy, JWT Security.
- **Frontend:** Vanilla JS (ES6+), HTML5, CSS3 with GlassMorphism aesthetics.
- **Security Middleware:** Custom IP-interception layer for real-time traffic filtering.
- **Simulation:** A dedicated multi-threaded traffic generator to simulate realistic attack vectors (HTTP Flood, Bot Swarms).
- **Database:** Optimized MySQL schemas with dedicated persistence for blacklisted addresses.

---

## 8. KEY SECURITY FEATURES
- **Real-time Entropy Tracking:** Continuous monitoring of traffic randomness using Shannon Entropy.
- **Dynamic Thresholding:** Automated baseline calculation to adapt to varying traffic loads.
- **One-Click Mitigation:** Instant IP blacklisting directly from the analytics dashboard.
- **Persistent Blacklist:** MySQL-backed storage of blocked IPs for long-term protection.
- **Security Middleware:** High-performance request filtering to reject malicious traffic before it hits application logic.
- **Forensic Logging:** Detailed logs of every request, including IP, endpoint, and traffic type (Normal/Attack).

---

## 9. FOLDER STRUCTURE
```text
.
├── backend/                # FastAPI Backend Source
│   ├── app/
│   │   ├── api/            # API Routes (Admin, Store, Hacker)
│   │   ├── core/           # Security, Config & Database
│   │   ├── models/         # DB Models & Pydantic Schemas
│   │   └── services/       # Entropy & Detection Logic
│   └── main.py             # Application Entry Point
├── frontend/               # Frontend Portals
│   ├── admin/              # Security Analytics Dashboard
│   ├── store/              # Exposys Mart Storefront
│   └── hacker/             # DDoS Simulation Tool
├── DOCUMENTATION.md        # Extended Technical Guide
└── README.md               # Project Overview
```

---

## 10. CONCLUSION
The **DDoS Sentinel** project successfully demonstrates that Information Theory, specifically Shannon Entropy, is a highly effective tool for modern network defense. By focusing on the statistical signature of traffic rather than static rules, we have built a system that is resilient, accurate, and capable of protecting web infrastructure against both known and unknown DDoS threats. 

The integration of **Persistent IP Blacklisting** ensures that the system doesn't just detect attacks but actively mitigates them, providing a robust, production-ready security layer for enterprise applications.

---

### 🚀 Getting Started
1. Clone the repo: `git clone https://github.com/ashokkumarboya93/...`
2. Install dependencies: `pip install -r backend/requirements.txt`
3. Set up your `.env` with MySQL credentials.
4. Run the backend: `python backend/main.py`
5. Open `http://localhost:8000/store/` to start shopping!
