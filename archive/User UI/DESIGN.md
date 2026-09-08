---
name: Adversarial Console Theme
colors:
  surface: '#10141a'
  surface-dim: '#10141a'
  surface-bright: '#353940'
  surface-container-lowest: '#0a0e14'
  surface-container-low: '#181c22'
  surface-container: '#1c2026'
  surface-container-high: '#262a31'
  surface-container-highest: '#31353c'
  on-surface: '#dfe2eb'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dfe2eb'
  inverse-on-surface: '#2d3137'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#ffb3ad'
  on-secondary: '#68000a'
  secondary-container: '#a40217'
  on-secondary-container: '#ffaea8'
  tertiary: '#4cd7f6'
  on-tertiary: '#003640'
  tertiary-container: '#00b2d0'
  on-tertiary-container: '#003f4b'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#ffdad7'
  secondary-fixed-dim: '#ffb3ad'
  on-secondary-fixed: '#410004'
  on-secondary-fixed-variant: '#930013'
  tertiary-fixed: '#acedff'
  tertiary-fixed-dim: '#4cd7f6'
  on-tertiary-fixed: '#001f26'
  on-tertiary-fixed-variant: '#004e5c'
  background: '#10141a'
  on-background: '#dfe2eb'
  surface-variant: '#31353c'
typography:
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 16px
    fontWeight: '500'
    lineHeight: 24px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.01em
  code-lg:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 22px
    letterSpacing: -0.01em
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.08em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  space-2xs: 2px
  space-xs: 4px
  space-sm: 8px
  space-md: 12px
  space-lg: 16px
  space-xl: 20px
  space-2xl: 24px
  space-3xl: 32px
  pane-header-height: 36px
  panel-gutter: 12px
  console-min-width: 1280px
---

## Brand & Style

This design system establishes a high-density, mission-critical workspace for ML security engineers, red-team researchers, and autonomous defense operators. The visual narrative balances clinical precision with intense operational focus: an environment that prioritizes signal over noise, telemetry over decoration, and immediate situational clarity during active adversarial simulations.

The aesthetic fuses **Modern Technical Minimalism** with **Tactical Terminal Controls**:
- **Palette & Atmosphere:** Dark, light-absorbing charcoal and abyssal slate layers, calibrated for prolonged zero-eye-strain sessions in darkened operations centers.
- **Visual Weight:** Ultra-fine architectural borders, razor-sharp grid structures, and tactical glowing indicators that clearly communicate defensive health, payload anomalies, and breach thresholds.
- **Feedback & States:** Telemetry streams, dynamic vector matrices, and live trajectory nodes operate with low-latency responsiveness. The design rejects arbitrary flourishes in favor of crisp status markers, mono-spaced data columns, and focused data density.

## Colors

The color system is organized around strict defensive semantics and hierarchical optical depth:

- **Base Surfaces:**
  - `surface-canvas`: `#090D14` (Deep void, application backplane)
  - `surface-base`: `#0D1117` (Default panel surface)
  - `surface-raised`: `#161B22` (Interactive cards, inspectors, tab bars)
  - `surface-overlay`: `#1F242C` (Dropdowns, modals, floating popovers)
- **Borders & Separators:**
  - `border-subtle`: `#21262D` (Structural grid dividers, table row outlines)
  - `border-muted`: `#30363D` (Card outlines, interactive bounds)
  - `border-active`: `#484F58` (Focus indicators, active inspector states)
- **Status & Threat Telemetry:**
  - `signal-safe` (`Primary`): `#10B981` (Normal inference, nominal latency, passed test suites)
  - `signal-safe-subtle`: `#064E3B` (Safe token background badges)
  - `signal-alert` (`Secondary`): `#EF4444` (Adversarial jailbreaks, gradient inversions, prompt extraction)
  - `signal-alert-glow`: `rgba(239, 68, 68, 0.2)` (Attack trajectory warning hulls)
  - `signal-warn`: `#F59E0B` (Drift detected, anomalous entropy, rate-limiting)
  - `signal-cyan` (`Tertiary`): `#06B6D4` (Vector modifications, feature embeddings, active telemetry probes)
  - `signal-purple`: `#A855F7` (Model weight introspection, synthetic payload generators)
- **Data & Text Hierarchy:**
  - `text-high-contrast`: `#F0F6FC` (Active values, numerical weights, headers)
  - `text-medium-contrast`: `#C9D1D9` (Labels, standard console readouts)
  - `text-muted`: `#8B949E` (Metadata, unselected tabs, inactive vectors)
  - `text-faint`: `#484F58` (Timestamps, terminal line numbers)

## Typography

The typographic hierarchy enforces immediate distinction between human-readable interfaces and machine-generated telemetry:

- **Structural UI (`Space Grotesk`):** Applied to console panel titles, operational modes, modal headers, and system status indicators. Provides geometric stability and technical authority without sacrificing scan-ability.
- **Contextual Workflows (`Inter`):** Reserved for contextual descriptions, field hints, documentation tooltips, and human analyst annotations. Its high x-height maintains high legibility across dense dashboard spaces.
- **Machine Readouts & Payloads (`JetBrains Mono`):** Applied to numerical vector arrays, tensor shapes, raw JSON payloads, terminal streams, and tabular statistics. Tabular figures (`tnum`) and slashed zeros must be enabled globally across all monospace declarations to prevent visual jitter during streaming real-time telemetry.

## Layout & Spacing

The layout is built for high information density, calibrated specifically around an ultra-efficient **1440x900 viewport** standard, scaling upwards to multi-display workstation rigs:

- **Layout Grid & Anatomy:**
  - Top Global Utility Bar: Fixed 44px height (Model selector, active target node, global threat meter, latency ping).
  - Main Body: Dynamic multi-pane CSS grid system utilizing fixed gutters of `12px` and panel margins of `16px`.
  - Left Rail (Vectors & Controls): 340px fixed width housing 9 fine-grained numerical vector inputs, perturbation parameters, and injection controls.
  - Central Stage (Attack Visualization & Telemetry): Fluid grid area displaying the live attack trajectory graph above an expandable terminal log.
  - Right Inspector (Payload Matrix & Target Inspection): 380px fixed width detailing gradient norms, raw tensor decoders, and defense responses.
- **Density Principle:**
  - Component padding utilizes strict increments of 4px and 8px to pack maximum context per square inch without visual clutter.
  - Vertical panel real estate is preserved by compact 36px panel headers featuring integrated inline controls and micro-actions.

## Elevation & Depth

Visual hierarchy is communicated through **structural tonal layering and high-contrast bounding lines**, supplemented by tactical backplane blurs rather than diffuse shadows:

- **Surface Tiers:**
  - `Level 0 (Canvas)`: `#090D14`. Background for global canvas framing and negative space.
  - `Level 1 (Panels)`: `#0D1117` with a 1px solid border of `#21262D`. Primary workspace for inspectors, vector controls, and stream monitors.
  - `Level 2 (In-Panel Containers & Cards)`: `#161B22` with a 1px solid border of `#30363D`. Used for vector input groupings, payload summaries, and log segments.
  - `Level 3 (Floating Controls & Overlays)`: `#1F242C` with `rgba(13, 17, 23, 0.85)` backdrop blur (8px) and a 1px solid border of `#484F58`.
- **Glow & Radiation Rules:**
  - Soft ambient shadows are strictly eliminated. Depth is reinforced via subtle colored radiance on key event triggers.
  - Critical alerts emit a tight, directional accent glow: `box-shadow: 0 0 12px rgba(239, 68, 68, 0.25)`.
  - Active feature vector probes emit a cool, precise cyan edge glow: `box-shadow: 0 0 8px rgba(6, 182, 212, 0.2)`.

## Shapes

The design system maintains a structured, technical aesthetic using small corner radii (`4px` base):

- **Panels, Cards, and Inputs:** Uniformly set to `rounded-sm` (4px). This creates clean alignment with grid lines and matches the dense, monospaced layout.
- **Pills & Status Indicators:** Numerical tags, attack mode indicators, and telemetry pill badges use `rounded-sm` (4px) or strict square profiles (0px) to preserve a precise terminal look. Rounded-full/pill shapes are banned to avoid an overly consumer-app feel.
- **Sliders & Step Handles:** Feature vector sliders utilize faceted 4px thumb components with 1px internal highlight borders to provide explicit visual grip.

## Components

### Buttons & Trigger Controls
- **Primary Attack Action:** Solid crimson background (`#DC2626`), high-contrast white text, 1px border (`#EF4444`). Hover state elevates brightness with an instantaneous red perimeter glow (`0 0 10px rgba(239,68,68,0.4)`).
- **Secondary / Utility Controls:** Deep zinc slate background (`#161B22`), muted text (`#C9D1D9`), 1px border (`#30363D`). Hover state shifts background to `#1F242C` with border color transition to `#484F58`.
- **Micro / Inline Actions:** Monospace font (`code-sm`), zero background, 2px internal padding, switching to emerald (`#10B981`) or cyan (`#06B6D4`) on hover.

### Feature Vector Inputs (Numerical Sliders + Steppers)
- **Track & Rail:** 4px tall track in `#21262D` with an active fill gradient representing perturbation range (Emerald-to-Crimson spectrum).
- **Thumb:** 12x12px square or slightly chamfered block (`#F0F6FC`) with active border indicator.
- **Value Stepper Input:** Directly adjacent to slider; 48px wide monospaced numerical box with 1px `#30363D` border. Displays floats formatted to 4 decimal places (`0.0000`). Up/Down micro-chevrons activate on hover.

### Data Stream & Console Logs
- **Log Container:** Monolithic black slate (`#090D14`) container with fixed height and virtual scrolling.
- **Line Structure:** Fixed 20px line height containing: timestamp (`text-faint`), log level badge (`signal-safe`, `signal-warn`, or `signal-alert`), thread hash (`text-muted`), and formatted payload token string.
- **Selection & Highlighting:** Selecting any row highlights the line with an ultra-thin left border (2px `#06B6D4`) and background tint (`rgba(6, 182, 212, 0.08)`).

### Status Badges & Glow Indicators
- **Live Status Dots:** 6px solid circular element with a concentric ping ring. Safe runs use `#10B981`; active adversarial attacks use `#EF4444`.
- **Telemetry Chips:** Surface `#161B22`, border `#30363D`, font `label-caps`. Format: `METRIC: VALUE` (e.g., `EPSILON: 0.0342` or `DRIFT: +14.2%`).

### Interactive Trajectory Graph & Canvas Panels
- **HUD Frame:** High-precision SVG bounding box with subtle corner crosshairs (`#484F58`) and axis lines in `#21262D`.
- **Node Anchors:** Adversarial step nodes rendered as diamond points. Successful defense: `#10B981` node with subtle drop line. Model bypass: `#EF4444` node with expanding threat radius.