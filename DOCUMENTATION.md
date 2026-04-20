# Project Documentation: Entropy-Based DDoS Detection & Analytics System

## 1. ABSTRACT
The rapid expansion of internet-based services has made Distributed Denial of Service (DDoS) attacks one of the most significant threats to cybersecurity. Traditional signature-based detection systems often fail against modern, sophisticated, and evolving attack patterns. This project presents a robust, real-time **Entropy-Based DDoS Detection System** integrated into a high-performance e-commerce simulation environment. 

The system utilizes mathematical entropy—a measure of randomness and uncertainty—to analyze incoming network traffic. By monitoring the statistical distribution of source IP addresses, request frequencies, and packet characteristics, the engine can distinguish between legitimate spikes in user traffic and coordinated malicious floods. The architecture includes a sophisticated backend built with FastAPI, a real-time monitoring dashboard, and a live e-commerce storefront that serves as the testing ground. Experimental results demonstrate that the entropy-based approach provides high detection accuracy with minimal false positives, offering an effective shield for enterprise-level web applications.

---

## 2. TABLE OF CONTENTS
1. [Abstract](#1-abstract)
2. [Introduction](#3-introduction)
3. [Existing Method](#4-existing-method)
4. [Proposed Method with Architecture](#5-proposed-method-with-architecture)
5. [Methodology](#6-methodology)
6. [Implementation](#7-implementation)
7. [Conclusion](#8-conclusion)

---

## 3. INTRODUCTION
In today's digital economy, availability is as critical as security. For platforms like online stores, even a few minutes of downtime can result in significant financial loss and brand damage. DDoS attacks aim to exhaust the target's resources—such as bandwidth, CPU, or memory—by overwhelming it with a massive volume of illegitimate requests.

This project focuses on building a "Self-Defending" ecosystem. We have created a complete three-tier application:
- **The Victim:** A premium e-commerce storefront called "Exposys Mart."
- **The Protector:** A real-time Security Analytics Dashboard that calculates entropy and blocks malicious actors.
- **The Attacker:** A dedicated DDoS simulation tool ("PHANTOM") to test the system's limits.

The core innovation lies in using **Shannon Entropy** to detect anomalies in traffic behavior. Unlike traditional systems that look for "bad" code, our system looks for "unnatural" statistical patterns, making it highly effective against Zero-Day attacks and botnets.

---

## 4. EXISTING METHOD
Most current DDoS prevention systems rely on one of two methods:
1.  **Signature-Based Detection:** This looks for specific patterns or "signatures" of known attacks.
    - *Limitation:* It is completely ineffective against new, unknown (Zero-Day) attack types.
2.  **Threshold-Based Detection:** This blocks an IP if it exceeds a certain number of requests per second (e.g., more than 100 req/sec).
    - *Limitation:* It often blocks legitimate users during high-traffic events like "Flash Sales" or "Black Friday," leading to high false-positive rates. It also fails against low-and-slow DDoS attacks that stay just below the threshold but still exhaust resources.

---

## 5. PROPOSED METHOD WITH ARCHITECTURE
The proposed system moves away from simple counts and instead analyzes the **uncertainty** of the traffic.

### System Architecture:
The system is built on a modern, decoupled architecture:
- **Frontend (Presentation Layer):** Three distinct web interfaces built with HTML5, Vanilla CSS3, and JavaScript. 
- **Backend (API & Logic Layer):** A high-performance FastAPI server that handles traffic ingestion, database operations, and detection logic.
- **Data Layer:** A MySQL database that stores product information, user accounts, and detailed security logs for historical analysis.
- **Detection Engine:** A specialized service that performs real-time window-based entropy calculations on every incoming request.

### Core Architecture Components:
- **Metrics Aggregator:** Collects live data on every request (IP, Port, Path, Timestamp).
- **Entropy Calculator:** Computes the probability distribution of incoming traffic over a sliding time window (e.g., every 5 seconds).
- **Automated Response System:** Triggers alerts and updates the firewall (simulated) when entropy drops below the safety threshold.

---

## 6. METHODOLOGY
The system operates based on the principle that **DDoS attacks reduce the randomness (entropy) of traffic.**

### The Detection Logic:
1.  **Data Collection:** Every request to the store is logged with its Source IP and Path.
2.  **Probability Calculation:** The system calculates the frequency of each unique IP within a specific time frame.
3.  **Shannon Entropy Formula:** We apply the formula:  
    `H(X) = -Σ P(xi) log2 P(xi)`  
    Where `P(xi)` is the probability of a specific IP appearing.
4.  **Anomaly Identification:**
    - **Normal Traffic:** Many different users visit different pages. This results in high randomness and **high entropy**.
    - **DDoS Attack:** A few IPs (or a botnet) flood the system with many identical requests. This creates high concentration and **low entropy**.
5.  **Thresholding:** If the calculated entropy value falls below a pre-defined threshold (e.g., 2.5 bits), the system flags the session as a potential attack.

---

## 7. IMPLEMENTATION
The implementation was executed in several phases:

### Phase 1: E-Commerce Simulation
A professional e-commerce site was developed with features including:
- A dynamic product catalog of 40+ items with high-resolution images.
- A functional shopping cart and checkout system.
- User authentication and persistent sessions.

### Phase 2: Backend Development
The FastAPI backend was optimized for low latency:
- **SQLAlchemy ORM** was used for secure and efficient MySQL database interaction.
- **Asynchronous endpoints** allow the system to handle thousands of requests without blocking.
- **JWT (JSON Web Tokens)** ensure that only authorized admins can access the Security Dashboard.

### Phase 3: The Analytics Dashboard
A real-time dashboard was built using **Chart.js**:
- Visualizes "Total Requests vs. Entropy Level."
- Displays a "Live Security Status" badge (Healthy, Warning, or Critical).
- Provides CSV and PDF export functionality for compliance and incident reporting.

### Phase 4: Integration & Testing
The simulation tool "PHANTOM" was used to launch HTTP Flood and Slowloris attacks. The system successfully detected these attacks within seconds, proving the efficacy of the entropy-based algorithm.

---

## 8. CONCLUSION
The **Entropy-Based DDoS Detection System** developed in this project represents a significant step forward in proactive network security. By shifting the focus from individual request counts to the statistical behavior of the entire traffic stream, we have created a system that is both sensitive to sophisticated attacks and resilient against legitimate traffic spikes.

Key achievements of this project include:
- Successful integration of a complex mathematical detection engine into a real-world web application.
- Creation of a premium, user-friendly interface for security monitoring.
- High accuracy in distinguishing between "Flash Crowd" traffic and "DDoS" traffic.

Future enhancements could include implementing Machine Learning models to dynamically adjust entropy thresholds and integrating automatic IP blacklisting via cloud-based firewalls.
