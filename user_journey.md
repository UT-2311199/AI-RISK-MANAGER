# User Journey & Application Flow
## AI Risk Manager — End-to-End User Experience (UX) Guide

This document defines the complete end-to-end user journey, page navigation flow, step-by-step screen transitions, and interactive user experiences across the **AI Risk Manager** platform.

---

## 1. Application Flow Diagram

```mermaid
graph TD
    Start([User Visits App]) --> AuthCheck{Is User Logged In?}
    
    %% Unauthenticated Flow
    AuthCheck -->|No| RegisterPage["1. Registration Page (/register)"]
    RegisterPage -->|Submits Credentials| LoginPage["2. Login Page (/login)"]
    AuthCheck -->|No| LoginPage
    LoginPage -->|Authenticates & Stores JWT| DashboardPage
    
    %% Authenticated Flow
    AuthCheck -->|Yes| DashboardPage["3. Dashboard Page (/dashboard)"]
    
    DashboardPage -->|Click 'Create New Project'| NewProjectPage["4. New Project Form (/projects/new)"]
    NewProjectPage -->|Fills Form & Clicks 'Create'| ProjectDetailPage["5. Project Detail Page (/projects/:id)"]
    
    DashboardPage -->|Click Existing Project Card| ProjectDetailPage
    
    %% Inside Project Detail Workspace
    subgraph Project Workspace (/projects/:id)
        ProjectDetailPage -->|Click 'Run AI Risk Analysis'| AIRiskEngine["Gemini AI Processing (Spinner UX)"]
        AIRiskEngine -->|Populates Risk Cards| RiskGrid["Risk Cards Grid (Sorted by Score)"]
        
        RiskGrid -->|Click Status Pill| StatusChange["Status Transition (Open -> Resolved)"]
        
        RiskGrid -->|Click 'Threat Radar' Widget| ThreatRadar["Threat Radar Visualization"]
        RiskGrid -->|Click 'Run Simulator'| SimulatorModal["Risk Simulator Sandbox Modal"]
        RiskGrid -->|Click 'Executive Report'| ExecutiveReportModal["Executive Summary Report Modal"]
        RiskGrid -->|Toggle 'Cyber Deck Mode'| CyberDeckView["Immersive CyberDeck Mode UX"]
    end
    
    DashboardPage -->|Click 'Logout'| LoginPage
```

---

## 2. Step-by-Step User Journey & Page Experiences

### Step 1: Entry & Authentication (`/register` and `/login`)

```
+-----------------------------------------------------------------------+
|                            AI RISK MANAGER                            |
|                                                                       |
|   +---------------------------------------------------------------+   |
|   |                        Account Login                          |   |
|   |                                                               |   |
|   |   Email Address:      [ user@company.com                  ]   |   |
|   |   Password:           [ ***************                   ]   |   |
|   |                                                               |   |
|   |   [      LOGIN TO WORKSPACE      ]                            |   |
|   |                                                               |   |
|   |   Don't have an account? [ Register here ]                    |   |
|   +---------------------------------------------------------------+   |
+-----------------------------------------------------------------------+
```

#### User Actions:
1. The user navigates to the application URL (`http://localhost:5173`).
2. Route guards evaluate authentication state. Unauthenticated users are redirected to `/login`.
3. If new, the user clicks **Register here** to navigate to `/register`, inputs their name, email, and password, and submits.
4. On `/login`, the user enters credentials. 

#### User Experience (UX) Highlights:
* **Glassmorphism Design**: Sleek dark background with translucent card containers and subtle neon accent borders.
* **Instant Validation**: Form fields provide feedback for missing or malformed email patterns before sending network requests.
* **Seamless Auth Transition**: Upon successful login, the JWT access token is stored in `localStorage`, and the user is redirected to `/dashboard`.

---

### Step 2: Main Dashboard & Project Hub (`/dashboard`)

```
+-----------------------------------------------------------------------+
| AI RISK MANAGER  [ Dashboard ]                          User: Alex (Logout) |
+-----------------------------------------------------------------------+
|                                                                       |
|  Welcome back, Alex!                                                  |
|  Track and manage AI risk assessments across your active software.    |
|                                                                       |
|  [ + CREATE NEW PROJECT ]                                             |
|                                                                       |
|  +--------------------------+  +--------------------------+           |
|  | Payment Gateway v2       |  | Patient Health Portal    |           |
|  | Risk Score: 7.8 (High)   |  | Risk Score: 8.5 (Critical|           |
|  | 5 Risks Identified       |  | 6 Risks Identified       |           |
|  | Tech: React, FastAPI     |  | Tech: Python, PostgreSQL |           |
|  | [ View Project -> ]      |  | [ View Project -> ]      |           |
|  +--------------------------+  +--------------------------+           |
+-----------------------------------------------------------------------+
```

#### User Actions:
1. The dashboard loads all projects owned by the user via `GET /projects`.
2. The user sees summary cards displaying key information: Project Name, Overall Risk Score badge, total risk count, tech stack tags, and creation date.
3. The user can click on any existing project card to view its workspace or click `+ Create New Project`.

#### UX Highlights:
* **Color-Coded Risk Badges**: Risk scores are dynamically styled with intuitive badges:
  - **Critical ($\ge 8.5$)**: Neon Red / Crimson gradient glow.
  - **High ($6.7 - 8.4$)**: Amber / Orange glow.
  - **Medium ($3.4 - 6.6$)**: Gold / Yellow accent.
  - **Low ($< 3.4$)**: Emerald Green accent.
* **Zero-State Experience**: If no projects exist, a user-friendly illustration invites the user to create their first project.

---

### Step 3: Project Setup & AI Context Input (`/projects/new`)

```
+-----------------------------------------------------------------------+
| <- Back to Dashboard                  Create New Risk Assessment      |
+-----------------------------------------------------------------------+
|                                                                       |
|  Project Name:       [ E-Commerce Payment Service                 ]   |
|  Business Objective: [ Process online credit card transactions     ]   |
|  Technologies Tag:   [ React, FastAPI, PostgreSQL, Stripe API     ]   |
|                                                                       |
|  Architecture & Security Context:                                     |
|  [ Stores user credit card tokens and PII in memory cache...      ]   |
|                                                                       |
|  [ CREATE & OPEN PROJECT ]                                            |
+-----------------------------------------------------------------------+
```

#### User Actions:
1. The user enters the project name, description, primary business objectives, and comma-separated tech stack tags.
2. The user inputs **Architecture & Security Context** (e.g., "Processes HIPAA patient records", "Stores credit card tokens").
3. The user clicks **Create & Open Project**.

#### UX Highlights:
* **Contextual Guidance**: Tooltips guide non-technical managers on how to provide rich context for more targeted AI analysis.
* **Auto Tag Creation**: Commas automatically convert technology strings into visual badge tags.

---

### Step 4: AI Analysis & Interactive Project Workspace (`/projects/:id`)

```
+-----------------------------------------------------------------------+
| E-Commerce Payment Service    Score: [ 7.8 / 10 (HIGH) ]              |
| [ RUN AI RISK ANALYSIS ]   [ Threat Radar ]  [ Simulator ]  [ Report ]|
+-----------------------------------------------------------------------+
|                                                                       |
|  RISK #1: Unencrypted Storage of PII Data in Application Cache       |
|  Category: Privacy | Severity: HIGH | Probability: HIGH | Impact: HIGH|
|  Status: [ OPEN v ]                                                   |
|                                                                       |
|  Explanation:                                                         |
|  Caching customer credit card tokens in unencrypted memory exposes... |
|                                                                       |
|  Actionable Mitigations:                                              |
|  [ ] Enable AES-256 memory encryption for cache layers                |
|  [ ] Enforce short TTLs on cached authorization tokens                |
|  [ ] Implement continuous memory scanning                             |
|                                                                       |
+-----------------------------------------------------------------------+
```

#### User Actions:
1. Upon opening a new or existing project, the user clicks **Run AI Risk Analysis**.
2. A pulsing loading animation indicates Gemini AI is analyzing the architecture across 8 risk categories.
3. Within seconds, identified risk cards stream into the view, sorted automatically by **Risk Score (Highest First)**.

#### UX Highlights:
* **Loading State**: Animated radar pulse / skeleton loader keeps the user engaged during the 5–10s AI processing window.
* **Structured Risk Breakdown**: Each card presents Title, Category Pill (Security, Privacy, Technical, etc.), Severity Pill, Explanation, and Checkbox Mitigations.

---

### Step 5: Risk Lifecycle Tracking & Mitigation Management

```
+-----------------------------------------------------------------------+
|  Status Transition Flow:                                              |
|                                                                       |
|  [ Open ]  --->  [ Under Review ]  --->  [ Mitigation in Progress ]   |
|                                                     |                 |
|                                                     v                 |
|                                             [ RESOLVED ]              |
+-----------------------------------------------------------------------+
```

#### User Actions:
1. As the team works on fixes, the user clicks the status dropdown on a risk card.
2. The user changes status from `Open` $\rightarrow$ `Under Review` $\rightarrow$ `Mitigation in Progress` $\rightarrow$ `Resolved`.
3. The backend updates the risk via `PATCH /risks/{id}/status`.

#### UX Highlights:
* **Optimistic UI Updates**: The card's status pill instantly changes color (Green for `Resolved`, Blue for `Mitigation in Progress`), providing zero latency UX.
* **Interactive Checkboxes**: Developers can check off mitigation steps as completed.

---

### Step 6: Advanced Analytics, Simulation & Reporting Modals

#### 6.1 Threat Radar Widget
* **User Experience**: Displays a breakdown of risk distribution across categories (Security vs Privacy vs Technical), highlighting risk concentration areas.

#### 6.2 Risk Simulator Sandbox Modal (`RiskSimulatorModal.jsx`)
* **User Experience**: An interactive modal allowing users to simulate scenario changes (e.g., "What if we remove Stripe and build custom PCI payments?"). Calculates predicted overall score shifts.

#### 6.3 Executive Summary Report Modal (`ExecutiveReportModal.jsx`)
* **User Experience**: One-click summary view tailored for CISOs, leadership, and external compliance auditors. Provides a clean, print/export ready overview of critical risks.

#### 6.4 Cyber Deck Mode (`CyberDeckMode.jsx`)
* **User Experience**: Toggleable high-tech visual overlay mode for SOC / war room displays with futuristic dark cyber themes.

---

## 3. UX Design Principles Summary

| Principle | Implementation in AI Risk Manager |
| :--- | :--- |
| **Instant Feedback** | All button presses display loading spinners or optimistic state updates immediately. |
| **Visual Hierarchy** | Critical & High severity risks stay pinned to the top of the workspace. |
| **Color Semantics** | Consistent color palette across scores, statuses, and categories (Red = Critical, Amber = High, Blue = In Progress, Green = Resolved). |
| **Frictionless Auth** | Auto token injection and transparent token expiration handling via Axios interceptors. |
