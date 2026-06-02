<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0D1117,1a1a2e,16213e&height=200&section=header&text=MD.%20Kawsar%20Ahmed&fontSize=60&fontColor=ffffff&animation=fadeIn&fontAlignY=45&desc=Software%20Engineer%20%7C%20Data%20Science%20Major%20%7C%20National%20Hackathon%20Champion&descAlignY=65&descColor=8b949e" />

[![Profile Views](https://komarev.com/ghpvc/?username=curl-kawsar&style=flat-square&color=0d1117&labelColor=161b22&label=profile+views)](https://github.com/curl-kawsar)
[![GitHub Followers](https://img.shields.io/github/followers/curl-kawsar?style=flat-square&color=0d1117&labelColor=161b22&label=followers)](https://github.com/curl-kawsar)

</div>

---

## About

Language-agnostic engineer with a trajectory from frontend development through full-stack systems into DevOps and data science. I primarily work with JavaScript and TypeScript, maintain deep proficiency in Python, and am actively expanding into distributed systems and cloud infrastructure. A competitive builder with multiple national hackathon championships and a proven track record of delivering production-grade software under pressure.

- Based in Cumilla, Bangladesh
- B.Sc. CSE (Data Science Major) at BAIUST, graduating 2026
- Thesis on Voice-based Emotion Recognition
- General Secretary, BAIUST Computer Club
- Open to full-time and internship opportunities in software engineering

---

## Skills

**Programming**
`JavaScript` `TypeScript` `Python` `C/C++` `SQL`

**Backend**
`Node.js` `Express.js` `Hono` `Next.js` `Django` `FastAPI`

**Database and Caching**
`MongoDB` `MySQL` `PostgreSQL` `Redis`

**DevOps and Infrastructure**
`Docker` `GitHub Actions` `AWS` `VPS` `PM2` `Caddy`

**Observability**
`OpenTelemetry` `Prometheus` `Grafana` `Loki`

**Messaging and Queues**
`RabbitMQ` `BullMQ`

**Frontend**
`HTML` `CSS` `React` `Next.js` `Axios` `TanStack`

**Tools and Others**
`Git` `Linux` `Prompt Engineering` `Product Management` `Trello` `Notion` `Vercel` `Render` `Clerk`

---

## Tech Stack

<div align="center">
  <img src="https://skillicons.dev/icons?i=js,ts,python,cpp,nodejs,react,nextjs,express,django,fastapi,mongodb,postgresql,mysql,redis,docker,aws,git,linux,github,vscode&theme=dark&perline=10" />
</div>

---

## Honours and Rewards

| Rank | Competition | Year | Location |
|------|-------------|------|----------|
| **Champion** | UAP Innovatex 2025 - National Hackathon | 2025 | Dhaka, BD |
| **Champion** | NSU Tech Fest 2025 - National Hackathon | 2025 | Dhaka, BD |
| **Champion** | DevFest AI Hackathon by Google Developer Group | 2023 | Cumilla, BD |
| **1st Runner Up** | MIST Inventious 4.1 - National Hackathon | 2025 | Dhaka, BD |
| **1st Runner Up** | CUET CSE FEST Micro-ops National Hackathon | 2026 | Chittagong, BD |
| **1st Runner Up** | Televerse 1.0 API Avengers - National Hackathon | 2025 | Chittagong, BD |
| **Top 10 Finalists** | OpenAPI National Hackathon - IUT Tech Fest | 2024 | Gazipur, BD |
| **Top 9 Finalists** | SUST CSE Carnival 2024 - National Hackathon | 2024 | Sylhet, BD |
| **Participant** | NASA Space Apps Challenge 2025 | 2025 | Cumilla, BD |
| **Problem Setter (2x)** | BAIUST CSE FEST 2025 (Spring, Fall) | 2025 | Cumilla, BD |

---

## Projects

### Multi-tenant SaaS Platform

`Turborepo` `Bun` `Hono` `Next.js` `Docker` `Caddy` `Let's Encrypt` `WhatsApp API` `IVR`

Architected a Turborepo + Bun monorepo with 6 applications; designed a two-system platform separating a SaaS Control Plane (tenant lifecycle, auth, billing) from an Ecommerce Runtime (multi-tenant storefront).

- Built automated store provisioning pipeline with env config generation, Caddy reverse-proxy management, SSL via ACME/Let's Encrypt, and health checks with real-time status tracking through deployment states
- Implemented shared-container Next.js storefront serving all merchants via hostname-based tenant resolution with product catalog, checkout, customer auth, order tracking, and theme customization
- Integrated idempotent payment gateway, WhatsApp marketing via Baileys with per-store session isolation, and voice marketing via IVR
- Built modular REST API (Hono + Bun, DDD) with 35 feature modules; authored 3 production Dockerfiles and Docker Compose orchestrating 7 services with health checks and persistence
- Managed production deployment via PM2 and GitHub Actions CI/CD

---

### Offline-First Restaurant POS System

`IndexedDB` `Dexie.js` `PostgreSQL` `BullMQ` `Redis` `Web Bluetooth` `Zustand` `Recharts`

Production-grade offline-first Point-of-Sale application enabling uninterrupted cashier operations during network outages with zero data loss.

- Engineered a dual-database sync pipeline using Dexie.js client-side write-ahead log and PostgreSQL canonical store, with BullMQ + Redis background worker ensuring exactly-once order processing via idempotency-key deduplication (24h TTL + DB constraints)
- Integrated Web Bluetooth API for direct ESC/POS thermal receipt printer communication with automatic GATT discovery and Unicode-to-raster conversion using Canvas 2D API with Floyd-Steinberg dithering for Bengali, Arabic, and CJK scripts
- Implemented PIN-based RBAC authentication across 4 roles with Redis-backed server sessions and 12-hour offline cache; designed Zustand cart engine with per-line/order discounts, variants, modifiers, and category-level taxes
- Built admin dashboard with menu/staff CRUD, table management, analytics via Recharts, dynamic CSS theming, and keyboard-driven command palette; deployed via Docker Compose + PM2 with separate web/worker processes

---

## Education

**Bangladesh Army International University of Science and Technology (BAIUST)**
B.Sc. in Computer Science and Engineering, Data Science Major
CGPA: 3.02 | 2022 - 2026 | Cumilla, Bangladesh

- Thesis: Voice-based Emotion Recognition
- Received the BAIUST National and International Distinguished Student Award three times

---

## Leadership

**BAIUST Computer Club (BCC) - General Secretary**

- Launched the Software Intern Program, coaching 102 students to ship 6 software modules for the campus
- Hosting twice-weekly "Engineering Adda" tech round-tables averaging 40 attendees, boosting club retention
- Organized a 24-hour hackathon for 51 teams and 196 participants end-to-end, achieving a 90% participant NPS
- Developed the internal management system and mail server for the club

**BAIUST CSE FEST 2025 - Organizer, Mentor, Problem Setter**

- Organized a 24-hour hackathon, IUPC, e-football, typing contest, and ICT quiz for 600+ participants
- Worked closely with faculty to plan and execute the event end-to-end
- Problem setter for the hackathon segment; mentored participants throughout

**Stars Intern Program, BAIUST - Team Lead**

Key deliverables:
- Bus Tracker: real-time tracking for 12 buses with live map and ETA for students and admins
- Treasurer Branch Reconciliation: automated matching of bank statements and student payments with instant mismatch alerts and ready-to-sign reports
- Alumni Portal: secure platform for graduate profiles, updates, and networking
- MCP Server: central information agent aggregating live academic, finance, and transport data for quicker institutional decision-making

---

## GitHub Analytics

<div align="center">
  <img width="49%" src="https://github-readme-stats.vercel.app/api?username=curl-kawsar&show_icons=true&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=ffffff&icon_color=58a6ff&text_color=8b949e&border_radius=8" />
  <img width="49%" src="https://streak-stats.demolab.com?user=curl-kawsar&theme=github-dark-blue&hide_border=true&background=0d1117&stroke=ffffff&ring=58a6ff&fire=ff7b72&currStreakNum=ffffff&sideNums=ffffff&currStreakLabel=58a6ff&sideLabels=8b949e&dates=8b949e&border_radius=8" />
</div>

<div align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=curl-kawsar&theme=github-compact&bg_color=0d1117&color=58a6ff&line=58a6ff&point=ffffff&area=true&hide_border=true" width="100%" />
</div>

---

## Connect

<div align="center">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0d1117?style=for-the-badge&logo=linkedin&logoColor=58a6ff)](https://linkedin.com/in/curl-kawsar)
[![GitHub](https://img.shields.io/badge/GitHub-0d1117?style=for-the-badge&logo=github&logoColor=ffffff)](https://github.com/curl-kawsar)
[![Codeforces](https://img.shields.io/badge/Codeforces-0d1117?style=for-the-badge&logo=codeforces&logoColor=58a6ff)](https://codeforces.com/profile/curl-kawsar)
[![HackerRank](https://img.shields.io/badge/HackerRank-0d1117?style=for-the-badge&logo=hackerrank&logoColor=2ec866)](https://www.hackerrank.com/@knownaskawsar)
[![Facebook](https://img.shields.io/badge/Facebook-0d1117?style=for-the-badge&logo=facebook&logoColor=1877f2)](https://fb.com/python.kawsar)
[![Instagram](https://img.shields.io/badge/Instagram-0d1117?style=for-the-badge&logo=instagram&logoColor=e1306c)](https://instagram.com/justin.kawchar)

**knownaskawsar@gmail.com** | **01847556023**

</div>

---

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0D1117,1a1a2e,16213e&height=120&section=footer&text=Let's%20build%20something%20impactful%20together&fontSize=20&fontColor=8b949e&animation=twinkling&fontAlignY=65" width="100%" />
</div>
