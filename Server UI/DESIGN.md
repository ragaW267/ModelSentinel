---
name: Obsidian Sentinel
colors:
  surface: '#0f131b'
  surface-dim: '#0f131b'
  surface-bright: '#353941'
  surface-container-lowest: '#0a0e15'
  surface-container-low: '#181c23'
  surface-container: '#1c2027'
  surface-container-high: '#262a32'
  surface-container-highest: '#31353d'
  on-surface: '#dfe2ed'
  on-surface-variant: '#bcc9cd'
  inverse-surface: '#dfe2ed'
  inverse-on-surface: '#2d3038'
  outline: '#869397'
  outline-variant: '#3d494c'
  surface-tint: '#4cd7f6'
  primary: '#4cd7f6'
  on-primary: '#003640'
  primary-container: '#06b6d4'
  on-primary-container: '#00424f'
  inverse-primary: '#00687a'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb2b7'
  on-tertiary: '#67001b'
  tertiary-container: '#ff7f8b'
  on-tertiary-container: '#7d0023'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#acedff'
  primary-fixed-dim: '#4cd7f6'
  on-primary-fixed: '#001f26'
  on-primary-fixed-variant: '#004e5c'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdadb'
  tertiary-fixed-dim: '#ffb2b7'
  on-tertiary-fixed: '#40000d'
  on-tertiary-fixed-variant: '#92002a'
  background: '#0f131b'
  on-background: '#dfe2ed'
  surface-variant: '#31353d'
typography:
  display-hero:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  title-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
    letterSpacing: -0.005em
  title-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0em
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.01em
  mono-lg:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: -0.01em
  mono-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0em
  mono-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 14px
    letterSpacing: 0.02em
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '700'
    lineHeight: 12px
    letterSpacing: 0.08em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  space-2xs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-base: 1rem
  space-lg: 1.25rem
  space-xl: 1.5rem
  space-2xl: 2rem
  space-3xl: 3rem
  gutter-compact: 0.75rem
  gutter-default: 1rem
  gutter-expanded: 1.5rem
---

## Brand & Style

The design system establishes an authoritative, mission-critical visual paradigm engineered for AI Security Operations Center (SOC) personnel, model governance leads, and machine learning infrastructure engineers. It conveys absolute operational control, machine-speed precision, and predictive resilience against model theft, membership inference, gradient inversion, and extraction attacks.

The aesthetic fuses **Modern Technical Minimalist** and **Tactical Cybernetic Data Density**:
- **Palette Discipline**: Dominated by deep obsidian and void-charcoal tonal planes, avoiding muddy greys in favor of blue-shifted midnight hues.
- **Controlled Luminescence**: Neon and chromatic accents are strictly functional, reserved for runtime inference telemetry, threat vector anomalies, and threat severity tiers. Chromatic noise is eliminated.
- **Architectural Rigor**: High structural density using hairline micro-borders, clean horizontal data tracks, and monospaced telemetry readouts balanced by refined, geometric sans typography for executive summary layers.

## Colors

The system uses a calibrated dark-mode hierarchy engineered to reduce optical fatigue during continuous security operations while directing ocular focus to high-priority inference anomalies.

### Surface Tiers
- **Void Surface (`#090D14`)**: Root application viewport, canvas backgrounds, and primary shell framing.
- **Layer 1 Substrate (`#0D131F`)**: Structural sidebars, dock panels, and background of primary data grids.
- **Layer 2 Container (`#131B2E`)**: Individual telemetry cards, terminal modules, and parameter inspectors.
- **Layer 3 Elevated (`#1A243B`)**: Modal surfaces, command palettes, flyout drawers, and active hover states.

### Border & Division Tokens
- **Border Subtle (`#1E293B`)**: Default panel dividers, data table gridlines, and inactive container frames.
- **Border Prominent (`#334155`)**: Interactive component outlines, focused cell borders, and card thresholds.
- **Border Highlight (`#06B6D440`)**: Neon cyan edge-glow for targeted AI endpoint layers.

### Risk Telemetry Scales
- **SAFE (`#10B981`)**: Normal query distribution, validated model entropy, benign behavioral baseline.
- **MONITORED (`#06B6D4`)**: Synthesized queries, dynamic watermarking active, rate-limiting tier 1.
- **SUSPICIOUS (`#F59E0B`)**: High token entropy, exploratory boundary-probing patterns, parameter extraction flags.
- **HIGH RISK (`#F97316`)**: Active gradient-inversion sequence, coordinated distributed scrapers, automated extraction script signature.
- **CRITICAL (`#F43F5E` / `#EF4444`)**: Real-time extraction confirmed, automated model weight protection engaged, endpoint circuit breaker trip.

### Text & Readability Tiers
- **Primary Text (`#F8FAFC`)**: High-contrast readouts, metric values, alert titles.
- **Secondary Text (`#94A3B8`)**: Field descriptors, table headers, metadata keys.
- **Muted Text (`#64748B`)**: Timestamp counters, log prefixes, inactive parameters.

## Typography

The typographic hierarchy distinguishes operational interfaces from dynamic machine intelligence streams.

- **Plus Jakarta Sans (Display & Headlines)**: Delivers clear, architectural structural headers that prevent industrial SOC layouts from feeling archaic or unapproachable.
- **Inter (Body & Controls)**: Neutral, highly legible workhorse typeface configured for micro-tables, modal dialogs, and high-density state switches.
- **JetBrains Mono (Telemetry, Logs & Data Values)**: Strictly applied to API payload hashes, token loss rates, parameter perturbation deltas, model response latencies, and real-time streaming security audit logs. Tabular figures (`tnum`) must remain enabled across all monospaced tokens to ensure zero-jitter during live data streaming.

## Layout & Spacing

The layout model utilizes a fluid 12-column engineering grid tailored for multi-screen SOC operations desks, scalable to ultra-wide panoramic monitors while offering responsive collapsing for triage on tablet and mobile viewports.

### Grid & Density Rules
- **Desktop (1440px and above)**: Full 12-column grid. Continuous live feeds occupy dedicated multi-split side drawers (fixed 320px to 380px width) while telemetry visualizers and graph nodes span the remaining fluid space.
- **Tablet / Small Laptop (1024px to 1439px)**: 8-column layout. Global topology views transition from side-by-side to stacked panels with tabbed log docks.
- **Mobile (Below 1023px)**: Single column with persistent bottom-pinned critical status bar. Detail metrics collapse into swipeable cards.

### Spacing Rhythm
The spatial cadence is built upon a 4px baseline module. Telemetry dashboards rely heavily on dense structural packing (`space-xs` to `space-base`) to maintain maximum situational awareness without requiring excessive scrolling. Section grouping uses `space-xl` and `space-2xl` strictly around major domain boundaries (e.g., separating Model Defense Gateways from Vector Quarantine Storage).

## Elevation & Depth

This design system avoids traditional drop shadows in favor of **Tonal Luminance Stacking** combined with **Low-Opacity Optical Edge Glows**.

### Surface Hierarchy
Depth is created by lightening background fills as surfaces elevate closer to the operator:
- **Base Level (Canvas)**: `#090D14` with a 1px micro-border (`#1E293B`).
- **Mid-Tier (Cards & Inspectors)**: `#0D131F` with inner border stroke `#1E293B` and optional subtle top-edge highlight (`rgba(255, 255, 255, 0.05)`).
- **Floating Shells (Command K-Bar, Modals, Overlays)**: `#1A243B` bordered by `#334155`.

### Tactical Glow Architecture
Shadows are replaced with localized cybernetic glow tokens applied exclusively to denote risk states or system activity:
- **Threat Aura (Critical)**: `0 0 16px -2px rgba(244, 63, 94, 0.35), 0 0 0 1px rgba(244, 63, 94, 0.5)`
- **Monitored Aura (Cyan)**: `0 0 12px -2px rgba(6, 182, 212, 0.3), 0 0 0 1px rgba(6, 182, 212, 0.4)`
- **Standard Overlay Shadow**: `0 12px 32px -4px rgba(0, 0, 0, 0.75), 0 0 0 1px #334155`

## Shapes

The interface embraces a precise, low-radius geometric contouring strategy (`roundedness: 1`). Large radii and pill-shaped components are strictly excluded from functional components, as rounded geometry contradicts high-density technical layouts and reduces tabular screen real estate.

- **Base Radius (`0.25rem` / `4px`)**: Buttons, badge tags, form input controls, dropdown items, table rows.
- **Container Radius (`0.5rem` / `8px`)**: Data cards, chart enclosures, terminal viewers, telemetry widgets.
- **Overlay Radius (`0.75rem` / `12px`)**: System alert flyouts, model configuration dialogs, authentication wrappers.
- **Strict Square (`0px`)**: Live terminal feed containers, raw code diff viewers, and model vector heatmaps.

## Components

### Buttons & Operational Triggers
- **Primary Functional (Cyan Action)**: Fills with `#06B6D4`, text `#090D14` (Inter bold), 4px border radius. On hover, escalates to `#22D3EE` with a cyan outer glow (`0 0 12px rgba(6, 182, 212, 0.4)`).
- **Secondary Defensive (Surface Outline)**: Background `#131B2E`, 1px border `#334155`, text `#F8FAFC`. On hover, background shifts to `#1A243B` with border `#06B6D4`.
- **Emergency Mitigation (Circuit Breakers)**: Background `#F43F5E` with text `#FFFFFF`. Used for "Sever Model Endpoint" or "Inject Perturbation Mask". Features a persistent 1.5s subtle pulse glow.

### Chips & Telemetry Status Badges
- Composed of `label-caps` typography, 4px border radius, padding `2px 8px`.
- **Structure**: Always pair a 6px status LED indicator dot on the leading edge with the capitalized status token (e.g., `[●] CRITICAL_EXTRACTION`).
- **Colorway**: 15% opacity background tint matched to 100% solid text and 40% border stroke (e.g., High Risk = bg `rgba(249, 115, 22, 0.15)`, text `#F97316`, border `rgba(249, 115, 22, 0.4)`).

### Input Fields & Filter Consoles
- **Field Canvas**: `#0D131F` background, 1px solid border `#1E293B`, placeholder text in `#64748B`.
- **Focus Mechanics**: Border shifts instantly to `#06B6D4` with an inner hairline glow. No browser-default outlines.
- **Prefix Labels**: Integrated monospaced schema identifiers (e.g., `model_id:`, `ip_cidr:`) rendered in `#94A3B8`.

### Data Grids & Audit Tables
- **Header Structure**: Sticky, `#090D14` background, uppercase `label-caps` font in `#64748B`, bottom 1px separator in `#1E293B`.
- **Row Styling**: Alternating zebra backgrounds (`#0D131F` to `#101726`) with a 1px bottom border `#1E293B`.
- **Hover State**: Entire row transitions to `#1A243B` with a `#06B6D4` 2px vertical accent bar on the left cell edge.

### Specialized AI-SOC Components
- **Watermark Perturbation Meter**: High-density horizontal bar visualizer with segmented steps showing real-time noise injection level.
- **Model Boundary Probe Radar**: Miniaturized canvas chart mapping incoming request vectors against known extraction manifolds with animated cyan/crimson threat pings.
- **Terminal Log Streamer**: Dedicated `#090D14` black box with monospace font (`mono-sm`), syntax highlighting for JSON request payloads, and fixed-width timestamp anchors.