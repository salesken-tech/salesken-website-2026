# Salesken.ai Website Clone

A local static mirror of [www.salesken.ai](https://www.salesken.ai) with all navigation menu pages and full site content.

## Pages included

- **Home** — `/`
- **Products** — Quality Assurance AI, AI Sales Assistant, Revenue Intelligence AI
- **Use Cases** — RevOps, Sales Team, Compliance
- **Pricing** — `/pricing`
- **Resources** — `/blog` (and all blog posts from sitemap)
- **Book a Demo** — `/book-a-demo`
- **Legal** — Privacy Policy, Terms & Conditions, Data Processing Addendum
- **Calculators** — Sales percentage, lift, forecast, mix, revenue projection, profit-to-sales ratio

## Setup

```bash
# Download all pages from salesken.ai (133 pages including blog posts)
python3 scripts/mirror.py

# Or menu pages only (faster)
python3 scripts/mirror.py --menu-only
```

## Run locally

```bash
npm run serve
```

Open [http://localhost:8080](http://localhost:8080)

## Notes

- HTML content is fetched directly from the live site and saved locally.
- CSS, images, and fonts load from the original Webflow CDN for visual fidelity.
- Analytics/tracking scripts are stripped from the local copy.
