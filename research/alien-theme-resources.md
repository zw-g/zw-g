# 👽🌼 Alien/Space Theme Resources — Cottagecore-Alien Edition

> **Art Direction:** Cute, hand-drawn doodle style. Indie webcomic / Tumblr-style.
> Thick black outlines, flat mint green, daisies, scattered dots.
> Think "cute sticker art" — wholesome, Gen-Z, cottagecore-alien.
> **NOT** dark/cyberpunk/neon/hacker.

---

## 1. Color Palette (from alien GIF analysis)

| Role | Color | Hex | Preview |
|------|-------|-----|---------|
| **Primary Mint Green** | Alien skin (main) | `#90EE90` | 🟢 light/mint green |
| **Green Shadow** | Alien skin (shade) | `#7BD47B` | slightly deeper mint |
| **Daisy Yellow** | Flower centers | `#FFD700` | 🌻 golden yellow |
| **Soft Yellow** | Warmer accent | `#F5C542` | warm golden |
| **Black** | Outlines, eyes, dots | `#000000` | ⬛ |
| **White** | Background, petals | `#FFFFFF` | ⬜ |
| **Cream** | Warm background alt | `#FFF8F0` | warm off-white |
| **Beige/Wheat** | Shirt color | `#F5DEB3` | soft warm neutral |
| **Dark Navy Cap** | Hat accent | `#2D2D48` | dark navy-purple |

### Gradient Combos for capsule-render

| Name | Start → End | URL param |
|------|-------------|-----------|
| **Mint Fade** | White → Mint | `color=0:FFFFFF,100:90EE90` |
| **Daisy Field** | Mint → Soft Yellow | `color=0:90EE90,100:FFD700` |
| **Cream Mint** | Cream → Mint | `color=0:FFF8F0,100:90EE90` |
| **Mint to White** | Mint → White | `color=0:90EE90,100:FFFFFF` |
| **Pastel Meadow** | Soft Yellow → Mint → White | `color=0:F5C542,50:90EE90,100:FFFFFF` |

---

## 2. Capsule-Render — Header & Footer

### API Reference
```
https://capsule-render.vercel.app/api?type=TYPE&color=COLOR&height=HEIGHT&section=SECTION&text=TEXT&fontColor=HEX&fontSize=SIZE&animation=ANIM
```

### Available Types (best for cute theme)
| Type | Vibe | Recommended? |
|------|------|-------------|
| `waving` | Gentle wave, clean | ⭐⭐⭐ Best match — soft, organic |
| `wave` | Similar wave | ⭐⭐ Good |
| `rounded` | Pill/rounded rect | ⭐⭐ Sticker-like |
| `soft` | Soft rectangle | ⭐⭐ Clean |
| `egg` | Egg shape | ⭐ Quirky, could be fun |
| `cylinder` | 3D cylinder | ❌ Too tech |
| `venom` | Blob/organic | ❌ Too aggressive |
| `shark` | Sharp teeth | ❌ Wrong vibe |

### Animation Options
| Animation | Effect | Fit? |
|-----------|--------|------|
| `twinkling` | Gentle opacity pulse (4s cycle) | ⭐⭐⭐ Perfect — subtle, cute |
| `fadeIn` | Fade in once (1.2s) | ⭐⭐ Clean entrance |
| `scaleIn` | Scale up once (0.8s) | ⭐ OK |
| `blink` | Quick blink (0.6s) | ❌ Too harsh |
| `blinking` | Slow blink (1.6s) | ❌ |

### ⭐ Recommended Header (Mint Fade + Waving)

```html
<!-- HEADER — Cream-to-Mint waving -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:FFFFFF,100:90EE90&height=120&section=header&text=&fontSize=0" width="100%" />
</p>
```

**Live URL:**
```
https://capsule-render.vercel.app/api?type=waving&color=0:FFFFFF,100:90EE90&height=120&section=header&text=&fontSize=0
```

### ⭐ Recommended Footer (Matching)

```html
<!-- FOOTER — Mint-to-Cream waving -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:90EE90,100:FFFFFF&height=80&section=footer&text=&fontSize=0" width="100%" />
</p>
```

### Alternative: Rounded with Text + Twinkling

```html
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=rounded&color=0:FFF8F0,100:90EE90&height=150&text=Hi%20there%20%F0%9F%91%BD&fontColor=2D2D48&fontSize=36&animation=twinkling" width="100%" />
</p>
```

### Alternative: Soft type (sticker-like)

```html
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=soft&color=90EE90&height=100&text=zw-g&fontColor=2D2D48&fontSize=40&animation=twinkling" width="60%" />
</p>
```

---

## 3. Animated Header — Stars Twinkling + Text Slide

Papa wants: "stars twinkling and text sliding from left to right"

### Option A: ⭐ Custom SVG (Best — full control, GitHub renders it)

GitHub renders `<img src="file.svg">` with CSS animations. No JavaScript allowed.
Commit this SVG to the repo as `assets/header-anim.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="140" viewBox="0 0 800 140">
  <style>
    /* Cream background */
    .bg { fill: #FFF8F0; }

    /* Twinkling stars (small daisies/dots) */
    .star {
      fill: #FFD700;
      animation: twinkle 3s ease-in-out infinite;
    }
    .star:nth-child(2) { animation-delay: 0.4s; }
    .star:nth-child(3) { animation-delay: 0.9s; }
    .star:nth-child(4) { animation-delay: 1.3s; }
    .star:nth-child(5) { animation-delay: 1.8s; }
    .star:nth-child(6) { animation-delay: 0.6s; }
    .star:nth-child(7) { animation-delay: 2.1s; }
    .star:nth-child(8) { animation-delay: 0.2s; }
    .star:nth-child(9) { animation-delay: 1.5s; }
    .star:nth-child(10) { animation-delay: 2.5s; }

    .dot {
      fill: #000000;
      opacity: 0.15;
      animation: twinkle 4s ease-in-out infinite;
    }
    .dot:nth-child(2) { animation-delay: 0.7s; }
    .dot:nth-child(3) { animation-delay: 1.4s; }
    .dot:nth-child(4) { animation-delay: 2.1s; }
    .dot:nth-child(5) { animation-delay: 0.3s; }

    @keyframes twinkle {
      0%, 100% { opacity: 0.2; transform: scale(0.8); }
      50% { opacity: 1; transform: scale(1.2); }
    }

    /* Text sliding from left to right */
    .slide-text {
      font-family: 'Comic Sans MS', 'Chalkboard SE', 'Comic Neue', cursive, sans-serif;
      font-size: 28px;
      font-weight: bold;
      fill: #2D2D48;
      animation: slideIn 2s ease-out forwards;
    }

    .slide-sub {
      font-family: 'Comic Sans MS', 'Chalkboard SE', 'Comic Neue', cursive, sans-serif;
      font-size: 16px;
      fill: #7BD47B;
      animation: slideIn 2s ease-out 0.5s forwards;
      opacity: 0;
    }

    @keyframes slideIn {
      0% { transform: translateX(-100px); opacity: 0; }
      100% { transform: translateX(0); opacity: 1; }
    }

    /* Small daisy decorations */
    .daisy-petal { fill: white; stroke: #000; stroke-width: 1; }
    .daisy-center { fill: #FFD700; }
  </style>

  <!-- Background -->
  <rect class="bg" width="800" height="140" rx="12"/>

  <!-- Scattered decorative dots (like the GIF) -->
  <g class="dot"><circle cx="50" cy="20" r="2"/></g>
  <g class="dot"><circle cx="150" cy="35" r="1.5"/></g>
  <g class="dot"><circle cx="300" cy="15" r="2"/></g>
  <g class="dot"><circle cx="680" cy="25" r="1.5"/></g>
  <g class="dot"><circle cx="750" cy="40" r="2"/></g>

  <!-- Twinkling stars (golden dots like daisy centers) -->
  <g class="star"><circle cx="80" cy="30" r="3"/></g>
  <g class="star"><circle cx="200" cy="18" r="2.5"/></g>
  <g class="star"><circle cx="350" cy="25" r="3"/></g>
  <g class="star"><circle cx="500" cy="15" r="2"/></g>
  <g class="star"><circle cx="620" cy="32" r="3"/></g>
  <g class="star"><circle cx="720" cy="20" r="2.5"/></g>
  <g class="star"><circle cx="130" cy="110" r="2"/></g>
  <g class="star"><circle cx="400" cy="120" r="3"/></g>
  <g class="star"><circle cx="580" cy="115" r="2.5"/></g>
  <g class="star"><circle cx="700" cy="125" r="2"/></g>

  <!-- Small daisy top-right -->
  <g transform="translate(740, 18)">
    <circle class="daisy-petal" cx="0" cy="-6" r="4"/>
    <circle class="daisy-petal" cx="5.5" cy="-2" r="4"/>
    <circle class="daisy-petal" cx="3.5" cy="4.5" r="4"/>
    <circle class="daisy-petal" cx="-3.5" cy="4.5" r="4"/>
    <circle class="daisy-petal" cx="-5.5" cy="-2" r="4"/>
    <circle class="daisy-center" cx="0" cy="0" r="3.5"/>
  </g>

  <!-- Small daisy bottom-left -->
  <g transform="translate(60, 120)">
    <circle class="daisy-petal" cx="0" cy="-5" r="3.5"/>
    <circle class="daisy-petal" cx="4.8" cy="-1.5" r="3.5"/>
    <circle class="daisy-petal" cx="3" cy="4" r="3.5"/>
    <circle class="daisy-petal" cx="-3" cy="4" r="3.5"/>
    <circle class="daisy-petal" cx="-4.8" cy="-1.5" r="3.5"/>
    <circle class="daisy-center" cx="0" cy="0" r="3"/>
  </g>

  <!-- Main text — slides in from left -->
  <text class="slide-text" x="120" y="65">👽 Hi there, welcome to my GitHub!</text>
  <text class="slide-sub" x="120" y="95">Software Engineer @ Meta • Exploring ML &amp; LLM Agents 🌱</text>
</svg>
```

**Usage in README:**
```html
<p align="center">
  <img src="./assets/header-anim.svg" width="100%" alt="Welcome header" />
</p>
```

> **Note:** GitHub caches SVGs aggressively. Bust cache by appending `?v=2` etc.

### Option B: readme-typing-svg (simpler, hosted)

Typing effect with mint/alien colors:

```html
<h4 align="center">
  <a href="https://github.com/zw-g">
    <img src="https://readme-typing-svg.demolab.com/?lines=Hi+there+%F0%9F%91%BD+welcome+to+my+Github!;Software+Engineer+%40+Meta;Exploring+ML+%26+LLM+Agents+%F0%9F%8C%B1;Building+AI-powered+automation+%F0%9F%A4%96&font=Comic+Neue&center=true&width=520&height=45&color=2D2D48&vCenter=true&pause=2000&size=18&duration=2500" />
  </a>
</h4>
```

**Key params for the cute theme:**
| Param | Value | Why |
|-------|-------|-----|
| `font` | `Comic+Neue` | Hand-drawn feel (Google Font, comic style) |
| `color` | `2D2D48` | Dark navy (matches cap), soft contrast |
| `background` | `00000000` | Transparent |
| `size` | `18` | Not too big, casual |
| `pause` | `2000` | Relaxed, not frantic |
| `duration` | `2500` | Easy reading pace |

Alternative fonts: `Patrick+Hand`, `Indie+Flower`, `Shadows+Into+Light`, `Caveat`

**Live URLs to test:**
```
https://readme-typing-svg.demolab.com/?lines=Hi+there+%F0%9F%91%BD;Welcome+to+my+Github!&font=Comic+Neue&center=true&width=400&height=40&color=2D2D48&size=20
```
```
https://readme-typing-svg.demolab.com/?lines=Hi+there+%F0%9F%91%BD;Welcome+to+my+Github!&font=Patrick+Hand&center=true&width=400&height=40&color=7BD47B&size=22
```

### Option C: capsule-render twinkling (simplest)

Capsule-render's `twinkling` animation = gentle opacity pulse on text. Not true stars, but subtle and cute:

```html
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=transparent&fontColor=2D2D48&text=👽%20zw-g&height=100&fontSize=48&animation=twinkling&desc=cottagecore%20alien%20%7C%20software%20engineer&descSize=16&descAlignY=75&descAlign=50" width="100%" />
</p>
```

### ⭐ Recommended Combo: capsule-render header wave + typing SVG + custom SVG daisies

Use waving header for the gentle color wash, then typing SVG for the text:

```html
<!-- Mint wave header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:FFFFFF,100:90EE90&height=120&section=header&text=&fontSize=0" width="100%" />
</p>

<!-- Typing text with handwritten font -->
<h4 align="center">
  <a href="https://github.com/zw-g">
    <img src="https://readme-typing-svg.demolab.com/?lines=Hi+there+%F0%9F%91%BD+welcome+to+my+Github!;Software+Engineer+%40+Meta+%E2%80%A2+Core+Feed+Ranking;Exploring+ML+%26+LLM+Agents+%F0%9F%8C%B1;Building+AI-powered+automation+%F0%9F%A4%96&font=Comic+Neue&center=true&width=520&height=45&color=2D2D48&vCenter=true&pause=2000&size=18&duration=2500" />
  </a>
</h4>
```

---

## 4. Icon Sources — Reliability Testing Results

### Summary Table

| Source | LinkedIn | GitHub | Gmail | Anthropic | Reliability | Notes |
|--------|----------|--------|-------|-----------|-------------|-------|
| `cdn.simpleicons.org/SLUG` | ❌ 404 | ✅ | ✅ | ✅ | ⚠️ Inconsistent | Some slugs missing |
| `cdn.simpleicons.org/SLUG/COLOR` | ❌ 404 | ✅ | — | ✅ | ⚠️ Same issue | Color param works when slug exists |
| `cdn.jsdelivr.net/npm/simple-icons@latest/icons/SLUG.svg` | ✅ | ✅ | ✅ | ✅ | ✅ Reliable | **Best for raw SVGs** |
| `cdn.jsdelivr.net/gh/devicons/devicon/icons/SLUG/SLUG-original.svg` | ✅ | ✅ | — | ❌ | ✅ Reliable | Traditional dev icons only |
| `raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/SLUG.svg` | ❌ 404 | — | — | — | ❌ Broken | Path changed, don't use |
| `skillicons.dev/icons?i=SLUG` | ✅ | ✅ | ✅ | ❌ | ✅ Reliable | Pretty dark-bg tiles, no AI brands |
| `img.shields.io/badge/...` | ✅ | ✅ | ✅ | ✅ | ✅ Reliable | **Most customizable** |

### ⭐ Recommended: shields.io badges (themed for cottagecore)

shields.io lets you set ANY background color and logo color. Perfect for the mint theme:

```html
<!-- LinkedIn — mint themed -->
<a href="https://www.linkedin.com/in/zhaoweigu/">
  <img alt="LinkedIn" src="https://img.shields.io/badge/LinkedIn-90EE90?style=for-the-badge&logo=linkedin&logoColor=2D2D48" />
</a>

<!-- GitHub — mint themed -->
<a href="https://github.com/zw-g">
  <img alt="GitHub" src="https://img.shields.io/badge/GitHub-90EE90?style=for-the-badge&logo=github&logoColor=2D2D48" />
</a>

<!-- Gmail — mint themed -->
<a href="mailto:zhaoweifz@gmail.com">
  <img alt="Gmail" src="https://img.shields.io/badge/Gmail-90EE90?style=for-the-badge&logo=gmail&logoColor=2D2D48" />
</a>
```

### Alternative: Minimal icon-only approach (matches doodle vibe better)

For a cleaner, more hand-drawn feel, small icons without badge chrome:

```html
<p align="center">
  <a href="https://www.linkedin.com/in/zhaoweigu/">
    <img alt="LinkedIn" title="LinkedIn" height="28" width="28" src="https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/linkedin.svg" style="filter: invert(0);" />
  </a>
  &nbsp;&nbsp;
  <a href="https://github.com/zw-g">
    <img alt="GitHub" title="GitHub" height="28" width="28" src="https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/github.svg" />
  </a>
  &nbsp;&nbsp;
  <a href="mailto:zhaoweifz@gmail.com">
    <img alt="Gmail" title="Gmail" height="28" width="28" src="https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/gmail.svg" />
  </a>
</p>
```

> **⚠️ Note:** jsdelivr SVGs are black fill by default. On GitHub's white background they show fine. No color customization without hosting your own copy or using shields.io.

### Alternative: skillicons.dev (pretty but fixed style)

```html
<p align="center">
  <a href="https://www.linkedin.com/in/zhaoweigu/">
    <img src="https://skillicons.dev/icons?i=linkedin&theme=light" height="36" alt="LinkedIn" />
  </a>
  &nbsp;
  <a href="https://github.com/zw-g">
    <img src="https://skillicons.dev/icons?i=github&theme=light" height="36" alt="GitHub" />
  </a>
  &nbsp;
  <a href="mailto:zhaoweifz@gmail.com">
    <img src="https://skillicons.dev/icons?i=gmail&theme=light" height="36" alt="Gmail" />
  </a>
</p>
```

> Use `theme=light` for white icon backgrounds (matches cottagecore vibe).

---

## 5. AI/Modern Tech Stack Icons

### Availability Matrix

| Brand | Simple Icons CDN | jsdelivr npm | shields.io | skillicons.dev | Logo slug |
|-------|-----------------|-------------|-----------|---------------|-----------|
| **Anthropic** | ✅ `anthropic` | ✅ `anthropic.svg` | ✅ `logo=anthropic` | ❌ | `anthropic` |
| **OpenAI** | ❌ | ✅ `openai.svg` | ✅ `logo=openai` | ❌ | `openai` |
| **Google Gemini** | ✅ `googlegemini` | ✅ `googlegemini.svg` | ✅ `logo=googlegemini` | ❌ | `googlegemini` |
| **Claude** | — (use Anthropic) | — | ✅ (custom text) | ❌ | `anthropic` |
| **ChatGPT** | — (use OpenAI) | — | ✅ (custom text) | ❌ | `openai` |
| **Claude Code** | — (use Anthropic) | — | ✅ (custom text) | ❌ | `anthropic` |

### ⭐ Ready-to-Use AI Badges (Cottagecore Mint Theme)

```html
<!-- Anthropic / Claude -->
<img alt="Claude" src="https://img.shields.io/badge/Claude-FFF8F0?style=for-the-badge&logo=anthropic&logoColor=2D2D48" />

<!-- OpenAI / ChatGPT -->
<img alt="ChatGPT" src="https://img.shields.io/badge/ChatGPT-FFF8F0?style=for-the-badge&logo=openai&logoColor=2D2D48" />

<!-- Google Gemini -->
<img alt="Gemini" src="https://img.shields.io/badge/Gemini-FFF8F0?style=for-the-badge&logo=googlegemini&logoColor=2D2D48" />

<!-- Claude Code (uses Anthropic logo) -->
<img alt="Claude Code" src="https://img.shields.io/badge/Claude_Code-FFF8F0?style=for-the-badge&logo=anthropic&logoColor=2D2D48" />
```

### Mint-Green Background Variant

```html
<img alt="Claude" src="https://img.shields.io/badge/Claude-90EE90?style=for-the-badge&logo=anthropic&logoColor=000000" />
<img alt="ChatGPT" src="https://img.shields.io/badge/ChatGPT-90EE90?style=for-the-badge&logo=openai&logoColor=000000" />
<img alt="Gemini" src="https://img.shields.io/badge/Gemini-90EE90?style=for-the-badge&logo=googlegemini&logoColor=000000" />
```

### shields.io Badge Anatomy
```
https://img.shields.io/badge/LABEL-BG_COLOR?style=STYLE&logo=LOGO_SLUG&logoColor=LOGO_COLOR
```
- `style`: `flat`, `flat-square`, `plastic`, `for-the-badge`, `social`
- `for-the-badge` = big + bold (most visible)
- `flat` = compact, cleaner
- Colors: hex without `#`

---

## 6. Tech Stack Icons (skillicons.dev)

skillicons.dev is ideal for tech stack display. Key icons available:

```
python, java, javascript, typescript, react, vue, angular, nodejs,
docker, kubernetes, aws, gcp, azure, git, github, linux, bash,
tensorflow, pytorch, flask, fastapi, django, express,
postgres, mysql, mongodb, redis, graphql, firebase,
html, css, tailwind, sass, webpack, vite,
figma, vscode, idea, vim, neovim
```

### ⭐ Tech Stack Display (light theme for cottagecore)

```html
<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,java,react,typescript,nodejs,docker,aws,tensorflow&theme=light" alt="Tech Stack" />
  </a>
</p>
```

### Multi-row with perline

```html
<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,java,react,typescript,nodejs,docker,aws,tensorflow,pytorch,postgres,redis,graphql&theme=light&perline=6" alt="Tech Stack" />
  </a>
</p>
```

### What skillicons.dev does NOT have
- ❌ Anthropic / Claude
- ❌ OpenAI / ChatGPT
- ❌ Google Gemini
- ❌ Meta (the company)
→ Use shields.io badges for these (see Section 5)

---

## 7. GitHub Readme Activity Graph — Cottagecore Theme

### Custom Parameters Reference

| Param | Description |
|-------|-------------|
| `bg_color` | Background color (hex, no #) |
| `color` | Text color |
| `title_color` | Title color |
| `line` | Line/graph color |
| `point` | Point dot color |
| `area_color` | Fill under the line |
| `area` | Enable area fill (true/false) |
| `hide_border` | Hide border (true/false) |
| `border_color` | Border color |
| `radius` | Border radius (0-16) |

### ⭐ Cottagecore Alien Theme (custom)

```html
<p align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=zw-g&bg_color=FFF8F0&color=2D2D48&title_color=2D2D48&line=90EE90&point=7BD47B&area=true&area_color=90EE90&hide_border=true&radius=12" width="98%" />
</p>
```

**Live URL:**
```
https://github-readme-activity-graph.vercel.app/graph?username=zw-g&bg_color=FFF8F0&color=2D2D48&title_color=2D2D48&line=90EE90&point=7BD47B&area=true&area_color=90EE90&hide_border=true&radius=12
```

### Alternative: White background (cleaner)

```
https://github-readme-activity-graph.vercel.app/graph?username=zw-g&bg_color=FFFFFF&color=000000&title_color=2D2D48&line=90EE90&point=FFD700&area=true&area_color=90EE90&hide_border=true
```

### Closest Built-in Themes
| Theme | Vibe | Notes |
|-------|------|-------|
| `green` | Green on white | Close but not custom enough |
| `minimal` | Clean minimal | Good base, wrong green |
| `github-light` | Light GitHub | Too corporate |

→ **Use custom params, not a preset theme.**

---

## 8. GitHub Stats Cards — Matching Theme

### github-readme-stats (Cottagecore)

```html
<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=zw-g&show_icons=true&hide_border=true&bg_color=FFF8F0&title_color=2D2D48&icon_color=90EE90&text_color=2D2D48&count_private=true" width="49%" />
  <img src="https://streak-stats.demolab.com/?user=zw-g&hide_border=true&background=FFF8F0&ring=90EE90&fire=FFD700&currStreakLabel=2D2D48&sideLabels=2D2D48&currStreakNum=2D2D48&sideNums=2D2D48&dates=7BD47B" width="49%" />
</p>
```

### Stats card params map:
| Param | Cottagecore Value | What it affects |
|-------|------------------|-----------------|
| `bg_color` | `FFF8F0` (cream) | Card background |
| `title_color` | `2D2D48` (dark navy) | Title text |
| `text_color` | `2D2D48` | Body text |
| `icon_color` | `90EE90` (mint) | Star/fork/etc icons |
| `hide_border` | `true` | Cleaner look |

### Streak stats params map:
| Param | Cottagecore Value | What it affects |
|-------|------------------|-----------------|
| `background` | `FFF8F0` | Card background |
| `ring` | `90EE90` | Streak ring |
| `fire` | `FFD700` (daisy yellow) | Fire/streak icon |
| `currStreakLabel` | `2D2D48` | Current streak label |
| `sideLabels` | `2D2D48` | Side labels |
| `dates` | `7BD47B` | Date text (softer green) |

---

## 9. Complete Doodle Elements — Custom SVGs

### Daisy Separator (commit to repo as `assets/daisy-separator.svg`)

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="30" viewBox="0 0 400 30">
  <style>
    .petal { fill: white; stroke: #000; stroke-width: 0.8; }
    .center { fill: #FFD700; }
    .dot { fill: #000; opacity: 0.2; }
    .stem { stroke: #90EE90; stroke-width: 1.5; fill: none; }
  </style>

  <!-- Left dots -->
  <circle class="dot" cx="40" cy="15" r="1.5"/>
  <circle class="dot" cx="70" cy="10" r="1"/>
  <circle class="dot" cx="100" cy="18" r="1.5"/>

  <!-- Left stem -->
  <path class="stem" d="M 120,15 Q 150,5 180,15"/>

  <!-- Daisy 1 -->
  <g transform="translate(200, 15)">
    <circle class="petal" cx="0" cy="-7" r="5"/>
    <circle class="petal" cx="6.7" cy="-2.2" r="5"/>
    <circle class="petal" cx="4.1" cy="5.7" r="5"/>
    <circle class="petal" cx="-4.1" cy="5.7" r="5"/>
    <circle class="petal" cx="-6.7" cy="-2.2" r="5"/>
    <circle class="center" cx="0" cy="0" r="4"/>
  </g>

  <!-- Right stem -->
  <path class="stem" d="M 220,15 Q 250,25 280,15"/>

  <!-- Right dots -->
  <circle class="dot" cx="300" cy="12" r="1.5"/>
  <circle class="dot" cx="330" cy="18" r="1"/>
  <circle class="dot" cx="360" cy="13" r="1.5"/>
</svg>
```

**Use as section divider:**
```html
<p align="center"><img src="./assets/daisy-separator.svg" width="50%" /></p>
```

---

## 10. Full Integrated Snippet — Ready to Assemble

All the pieces together for reference. The actual README should mix-and-match:

```html
<!-- ═══════════════════════════════════════════════ -->
<!-- HEADER WAVE — mint gradient -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:FFFFFF,100:90EE90&height=120&section=header&text=&fontSize=0" width="100%" />
</p>

<!-- TYPING SVG — handwritten font -->
<h4 align="center">
  <a href="https://github.com/zw-g">
    <img src="https://readme-typing-svg.demolab.com/?lines=Hi+there+%F0%9F%91%BD+welcome+to+my+Github!;Software+Engineer+%40+Meta+%E2%80%A2+Core+Feed+Ranking;Exploring+ML+%26+LLM+Agents+%F0%9F%8C%B1;Building+AI-powered+automation+%F0%9F%A4%96&font=Comic+Neue&center=true&width=520&height=45&color=2D2D48&vCenter=true&pause=2000&size=18&duration=2500" />
  </a>
</h4>

<!-- ALIEN GIF -->
<p align="center">
  <img width="250" src="https://media.giphy.com/media/LXjLNXabM2b0qN4DV6/giphy.gif" alt="cute alien">
</p>

<!-- CONTACT ICONS — shields.io mint badges -->
<p align="center">
  <a href="https://www.linkedin.com/in/zhaoweigu/">
    <img alt="LinkedIn" src="https://img.shields.io/badge/LinkedIn-90EE90?style=for-the-badge&logo=linkedin&logoColor=2D2D48" />
  </a>
  &nbsp;
  <a href="https://github.com/zw-g">
    <img alt="GitHub" src="https://img.shields.io/badge/GitHub-90EE90?style=for-the-badge&logo=github&logoColor=2D2D48" />
  </a>
  &nbsp;
  <a href="mailto:zhaoweifz@gmail.com">
    <img alt="Gmail" src="https://img.shields.io/badge/Gmail-90EE90?style=for-the-badge&logo=gmail&logoColor=2D2D48" />
  </a>
</p>

<!-- ═══════════════════════════════════════════════ -->
<!-- DETAILS SECTION -->
<details>
<summary align="center"><samp> more about me 🌼 </samp></summary>

#

<!-- ABOUT ME -->
<div align="left">

  - 👽 My name sounds like **Jaw-Way**
  - 🎓 BS in **Technology Information Management** & MS in **Software Development**
  - 🔭 Currently working on **Facebook Feed Ranking** @ Meta
  - 🌱 Exploring **Machine Learning**, **LLM Agents**, and AI-powered automation
  - 🌻 Building innovative products that enrich people's everyday experiences

</div>

<br/>

<!-- STATS — cream bg, mint accents -->
<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=zw-g&show_icons=true&hide_border=true&bg_color=FFF8F0&title_color=2D2D48&icon_color=90EE90&text_color=2D2D48&count_private=true" width="49%" />
  <img src="https://streak-stats.demolab.com/?user=zw-g&hide_border=true&background=FFF8F0&ring=90EE90&fire=FFD700&currStreakLabel=2D2D48&sideLabels=2D2D48&currStreakNum=2D2D48&sideNums=2D2D48&dates=7BD47B" width="49%" />
</p>

<!-- ACTIVITY GRAPH — mint on cream -->
<p align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=zw-g&bg_color=FFF8F0&color=2D2D48&title_color=2D2D48&line=90EE90&point=7BD47B&area=true&area_color=90EE90&hide_border=true&radius=12" width="98%" />
</p>

<hr/>

<!-- CODE CYCLE -->
<div align="center">

  **Code Cycle**

  <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Face%20with%20Spiral%20Eyes.png" width="10%" alt="Broken system!"/>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Relieved%20Face.png" width="10%" alt="It's working!"/>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Astonished%20Face.png" width="10%" alt="It's working but you don't know how!"/>

</div>

</details>

<!-- ═══════════════════════════════════════════════ -->
<!-- FOOTER WAVE — matching mint gradient -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:90EE90,100:FFFFFF&height=80&section=footer&text=&fontSize=0" width="100%" />
</p>
```

---

## 11. Quick Reference — Copy-Paste URLs

### Capsule-render
```
Header: https://capsule-render.vercel.app/api?type=waving&color=0:FFFFFF,100:90EE90&height=120&section=header&text=&fontSize=0
Footer: https://capsule-render.vercel.app/api?type=waving&color=0:90EE90,100:FFFFFF&height=80&section=footer&text=&fontSize=0
```

### Typing SVG
```
https://readme-typing-svg.demolab.com/?lines=Hi+there+%F0%9F%91%BD+welcome+to+my+Github!;Software+Engineer+%40+Meta;Exploring+ML+%26+LLM+Agents+%F0%9F%8C%B1&font=Comic+Neue&center=true&width=520&height=45&color=2D2D48&vCenter=true&pause=2000&size=18&duration=2500
```

### Stats Cards
```
Stats:  https://github-readme-stats.vercel.app/api?username=zw-g&show_icons=true&hide_border=true&bg_color=FFF8F0&title_color=2D2D48&icon_color=90EE90&text_color=2D2D48&count_private=true
Streak: https://streak-stats.demolab.com/?user=zw-g&hide_border=true&background=FFF8F0&ring=90EE90&fire=FFD700&currStreakLabel=2D2D48&sideLabels=2D2D48&currStreakNum=2D2D48&sideNums=2D2D48&dates=7BD47B
Graph:  https://github-readme-activity-graph.vercel.app/graph?username=zw-g&bg_color=FFF8F0&color=2D2D48&title_color=2D2D48&line=90EE90&point=7BD47B&area=true&area_color=90EE90&hide_border=true&radius=12
```

### Contact Badges
```
LinkedIn: https://img.shields.io/badge/LinkedIn-90EE90?style=for-the-badge&logo=linkedin&logoColor=2D2D48
GitHub:   https://img.shields.io/badge/GitHub-90EE90?style=for-the-badge&logo=github&logoColor=2D2D48
Gmail:    https://img.shields.io/badge/Gmail-90EE90?style=for-the-badge&logo=gmail&logoColor=2D2D48
```

### AI Badges
```
Claude:      https://img.shields.io/badge/Claude-FFF8F0?style=for-the-badge&logo=anthropic&logoColor=2D2D48
ChatGPT:     https://img.shields.io/badge/ChatGPT-FFF8F0?style=for-the-badge&logo=openai&logoColor=2D2D48
Gemini:      https://img.shields.io/badge/Gemini-FFF8F0?style=for-the-badge&logo=googlegemini&logoColor=2D2D48
Claude Code: https://img.shields.io/badge/Claude_Code-FFF8F0?style=for-the-badge&logo=anthropic&logoColor=2D2D48
```

### Tech Stack (skillicons.dev, light theme)
```
https://skillicons.dev/icons?i=python,java,react,typescript,nodejs,docker,aws,tensorflow&theme=light
```

---

## 12. Design Decision Notes

### Why this palette works
- **Mint green (#90EE90)** = the alien's skin, warm and approachable
- **Cream (#FFF8F0)** = softer than pure white, feels hand-drawn/paper-like
- **Dark navy (#2D2D48)** = from the alien's cap, provides contrast without harsh black text
- **Golden yellow (#FFD700)** = daisy centers, adds warmth
- **Black outlines** = matches the GIF's thick doodle outlines

### What to avoid
- ❌ Pure black backgrounds (`0D1117`, `000000`)
- ❌ Neon greens (`00FF00`, `00FF41`)
- ❌ Cyberpunk purples (`7B2FBE`)
- ❌ Dark themes (tokyonight, dracula, radical)
- ❌ Matrix/hacker terminal aesthetics
- ❌ Sharp/angular designs — keep everything soft and rounded

### Emoji choices for the theme
Use cute/nature emojis, not tech ones:
- 👽 (alien — the star)
- 🌼🌻🌸 (flowers/daisies)
- 🌱 (growth/learning)
- ✨ (sparkle)
- 🍃 (nature)
- 🌿 (plant)
- ☁️ (cloud, soft)

---

*Research completed 2026-03-02 by Momo 🍑*
