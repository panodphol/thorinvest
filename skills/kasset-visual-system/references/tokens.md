# Tokens for PPTX / DOCX (same values as tokens.css)

| Role | Corporate Teal | Mini-Art Dark-Gold |
|---|---|---|
| Background | `#FFFFFF` | `#0A0A0A` |
| Surface / light fill | `#C5ECE6` | `#0D1F16` |
| Primary text | `#013332` | `#F5F5F0` |
| Secondary text | `#004C5E` | `#B8B8B0` |
| Accent (one highlight) | `#44C2AE` | `#C9A84C` |
| Hero number | `#013332` bold | `#E8C96A` |
| Data series 2 | `#97C6EB` | `#2D5A3D` |
| Muted series | `#ADB9CA` | `#1A3A2A` |
| RAG G / A / R | `#44C2AE` / `#FFFF00` / `#B23A48` | `#2D5A3D` / `#C9A84C` / `#B23A48` |
| Font | Arial | Arial |

## Conflicts these tokens resolve
- "No warm tones" (KAsset CI) vs "gold mandatory" (Mini-Art): each rule applies only in its own mode.
- `#00FFB9` and `#B23A48` existed only in the v3.1 design-system file; both are now listed with restricted roles.
- The `build-a-fund-live` talk palette (`#e3a94b` / `#8fd9b6`) is outside both modes. Choose: fold it in as a third mode or move the talk to Mini-Art.
