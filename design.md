# Design Specification (design.md)
## AI Risk Manager — Comprehensive UI/UX Design Specs & CSS Architecture

This document provides the exhaustive design specification for the **AI Risk Manager** web application, detailing the design tokens, visual aesthetics, color semantics, typography, glassmorphism card physics, grid layout rules, keyframe animations, and a line-by-line explanation of [`frontend/src/index.css`](file:///d:/Projects/AI-RISK-MANAGER/frontend/src/index.css).

---

## 1. Design Aesthetics & Visual Identity

### 1.1 Core Aesthetic: Modern Dark Glassmorphism
The AI Risk Manager interface uses a **dark, high-contrast cyber-glass aesthetic** engineered to look like a high-end enterprise security command center. Key characteristics include:
* **Deep Dark Canvas**: Rich background shades (`#060913` and `#0b0f1e`) that reduce eye fatigue.
* **Translucent Glass Cards**: Card containers utilize `backdrop-filter: blur(20px)` and subtle alpha transparency (`rgba(255, 255, 255, 0.035)`) to create depth.
* **Vibrant Accent Gradients**: HSL-tailored indigo, violet, and cyan gradients (`linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4)`).
* **Dynamic Neon Glows**: Subtle `box-shadow` glows that ignite on hover or focus states.

---

## 2. Design Tokens (`:root` CSS Variables)

All design values are strictly centralized in `index.css` using native CSS Custom Properties.

```css
:root {
  /* Background Canvas */
  --bg-primary: #060913;         /* Deep void black canvas */
  --bg-secondary: #0b0f1e;       /* Elevated dark navy panel */
  --bg-card: rgba(255, 255, 255, 0.035);   /* Translucent glass card */
  --bg-card-hover: rgba(255, 255, 255, 0.07); /* Hover elevation state */
  --bg-glass: rgba(11, 15, 30, 0.85);        /* Modal and navigation glass */
  --bg-input: rgba(255, 255, 255, 0.05);    /* Form input background */

  /* Accent Gradients */
  --accent-primary: #6366f1;     /* Electric Indigo */
  --accent-secondary: #8b5cf6;   /* Deep Violet */
  --accent-cyan: #06b6d4;        /* Bright Cyan */
  --accent-emerald: #10b981;     /* Success Green */
  --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
  --accent-glow: 0 0 25px rgba(99, 102, 241, 0.4);

  /* Typography Colors */
  --text-primary: #f8fafc;       /* Crisp high-contrast white */
  --text-secondary: #94a3b8;     /* Slate grey for descriptions */
  --text-muted: #64748b;         /* Subdued grey for metadata */
  --text-accent: #818cf8;        /* Soft indigo highlight */

  /* Risk Severity Semantics */
  --severity-critical: #ef4444;     /* Red glow */
  --severity-critical-bg: rgba(239, 68, 68, 0.14);
  --severity-high: #f97316;         /* Orange glow */
  --severity-high-bg: rgba(249, 115, 22, 0.14);
  --severity-medium: #eab308;       /* Yellow/Gold glow */
  --severity-medium-bg: rgba(234, 179, 8, 0.14);
  --severity-low: #10b981;          /* Emerald Green glow */
  --severity-low-bg: rgba(16, 185, 129, 0.14);

  /* Status Colors */
  --status-open: #ef4444;           /* Open = Red */
  --status-review: #f97316;         /* Under Review = Orange */
  --status-progress: #6366f1;       /* In Progress = Indigo */
  --status-resolved: #10b981;       /* Resolved = Green */
  --status-accepted: #06b6d4;       /* Accepted = Cyan */

  /* Border Radii */
  --radius-sm: 6px;   --radius-md: 10px;   --radius-lg: 16px;   --radius-xl: 24px;   --radius-full: 9999px;

  /* Font Families */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}
```

---

## 3. Layout Engine & Responsive Grid System

### 3.1 Fixed Sidebar & Non-Squishing Main Workspace
To prevent content squishing on laptops and wide desktop screens, the layout enforces strict fixed layout boundaries:

* **Sidebar (`.sidebar`)**:
  - `width: 250px`: Fixed structural width.
  - `position: fixed; top: 64px; left: 0; bottom: 0`: Locks sidebar below header.
  - `backdrop-filter: blur(20px)`: Translucent glass background.
* **Main Workspace (`.main-content`)**:
  - `margin-left: 250px`: Exact offset accounting for fixed sidebar.
  - `width: calc(100% - 250px)`: Fills remaining viewport width.
  - `min-width: 0`: Prevents flexbox item collapse.

### 3.2 Dynamic Responsive Grid Specs
```css
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-lg);
}
```
* `minmax(320px, 1fr)` ensures project cards wrap smoothly across resolutions from 1080p monitors down to tablets without horizontal scrollbars.

---

## 4. Key Components & Visual Engineering

### 4.1 Glassmorphism Cards (`.glass-card` / `.project-card`)
```css
.glass-card {
  background: var(--bg-card);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: all var(--transition-med);
}

.glass-card:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-accent);
  transform: translateY(-4px);
  box-shadow: var(--shadow-glow);
}
```
* **Physics**: Lifting motion (`translateY(-4px)`) combined with an illuminating indigo border (`--border-accent`) on hover.

### 4.2 Severity Badges & Pills (`.severity-badge`)
```css
.severity-critical {
  color: var(--severity-critical);
  background: var(--severity-critical-bg);
  border: 1px solid rgba(239, 68, 68, 0.3);
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.2);
}
```
* **Accessibility**: Every severity badge uses high-contrast text against a translucent tinted background with a matching $12\text{px}$ box-shadow glow.

### 4.3 Action Buttons (`.btn-primary`)
```css
.btn-primary {
  background: var(--accent-gradient);
  color: #ffffff;
  border: none;
  font-weight: 600;
  border-radius: var(--radius-md);
  padding: 10px 20px;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.55);
}
```

---

## 5. Line-by-Line CSS Specification Breakdown ([index.css](file:///d:/Projects/AI-RISK-MANAGER/frontend/src/index.css))

Below is the complete line range map explaining what every section of `index.css` accomplishes:

| Line Range | CSS Selector / Feature | Technical Purpose & UX Role |
| :--- | :--- | :--- |
| **Lines 1 – 4** | File Header Comment | Identifies `index.css` as the central global design system. |
| **Lines 5 – 78** | `:root` Design Tokens | Declares all CSS custom properties for color palettes, gradient maps, risk severities, status indicators, spacing variables, radii, and font stacks. |
| **Lines 80 – 105** | `body.cyber-deck-mode` Overrides | Secret command-center theme. Rebinds CSS variables to electric cyan (`#00f3ff`) and matrix green (`#00ff66`) with a $30\text{px} \times 30\text{px}$ grid background pattern. |
| **Lines 107 – 130** | Universal Reset (`*`, `body`) | Sets `box-sizing: border-box`, removes browser margins/padding, enables smooth scrolling, and sets dark background color (`--bg-primary`). |
| **Lines 131 – 143** | `body::before` Background Orbs | Renders fixed, non-blocking radial background gradients at coordinates `(15%, 15%)`, `(85%, 85%)`, and `(50%, 50%)` to create subtle ambient background glow. |
| **Lines 151 – 159** | Typography Hierarchy (`h1`-`h4`, `p`, `a`) | Configures font sizes ($2.1\text{rem}$ down to $1.0\text{rem}$), line heights ($1.2$ to $1.6$), and link hover transitions. |
| **Lines 160 – 195** | `.page-layout`, `.sidebar`, `.main-content` | Structural layout rules. Locks sidebar at $250\text{px}$ width and sets main content width to `calc(100% - 250px)` to prevent viewport squishing. |
| **Lines 196 – 240** | `.navbar` & Top Header Navigation | Fixed header navbar ($64\text{px}$ height) with glassmorphism backdrop blur ($20\text{px}$), flex alignment, brand logo styling, and user menu triggers. |
| **Lines 241 – 290** | `.glass-card` & `.project-card` | Glassmorphism physics engine. Translucent card backgrounds, hover elevation, subtle borders, and neon box-shadow glows. |
| **Lines 291 – 350** | Severity & Status Pills | Color styles for `Critical`, `High`, `Medium`, and `Low` risk badges, plus status pills (`Open`, `Under Review`, `Mitigation in Progress`, `Resolved`, `Accepted`). |
| **Lines 351 – 420** | Button Components (`.btn-*`) | Styling for primary gradient buttons, secondary outlined buttons, danger delete buttons, icon buttons, disabled loading states, and active pressed effects. |
| **Lines 421 – 480** | Form Controls (`.form-group`, `.input`, `.select`) | Custom dark mode form fields. Translucent inputs with indigo border highlights on `:focus` and glowing focus rings. |
| **Lines 481 – 540** | Risk Cards & Mitigation Checklists | Card layout inside project detail workspace. Includes risk title styling, category tag styling, AI explanation text, and interactive mitigation checkbox lists. |
| **Lines 541 – 620** | Modal Overlay & Dialog Windows | Backdrop overlay styling (`rgba(0,0,0,0.75)` with `backdrop-filter: blur(8px)`) and centered modal content boxes for Simulator, Report, and Delete confirmations. |
| **Lines 621 – 710** | Widgets: Threat Radar & Score Gauge | Circular threat radar chart layout, category distribution progress bars, and score gauge color transitions. |
| **Lines 711 – 790** | Executive Report & Print Styling | High-contrast clean report printable view styles (`@media print`) for converting dark mode workspace into audit-ready white document format. |
| **Lines 791 – 860** | Voice Assistant & Audio Controls | Floating mic action button (`.voice-assistant-fab`) with pulsing audio wave animation indicator during voice recording. |
| **Lines 861 – 930** | Custom Scrollbars & Utilities | Webkit custom dark scrollbars (`::-webkit-scrollbar` with $8\text{px}$ width, subtle track, and rounded indigo thumb) and utility classes (`.text-gradient`, `.flex-between`). |
| **Lines 931 – 1021** | Responsive Media Queries | Breakpoints at `@media (max-width: 1024px)`, `768px`, and `480px` adjusting layout from multi-column grid to single-column layout on mobile devices. |
