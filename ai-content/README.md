# AI Content Generator — Product → SEO Content Pack

Bulk-produces the content e-commerce/SEO clients need: **meta title, meta description, product description, and feature bullets** from a product's name + features + target keyword. Built for agencies generating content across hundreds of SKUs.

## Run

```bash
pip install -r requirements.txt          # only needed for the AI path
python content.py                        # built-in sample product
python content.py product.json           # your own product JSON
```

No API key → a clean structured template fills in. Set `ANTHROPIC_API_KEY` for natural, benefit-led copy from Claude.

## Input (`product.json`)
```json
{
  "name": "AeroBuds Pro",
  "keyword": "wireless earbuds",
  "audience": "commuters and gym-goers",
  "features": ["40h battery life", "active noise cancelling", "IPX5 sweat resistance"]
}
```

## Output
`meta_title` (≤60 chars) · `meta_description` (≤155 chars) · `description` (2-3 sentences) · `bullets` (3-5) — ready to paste into Shopify/WooCommerce or a CMS.

## Roadmap
- Batch mode: a CSV of products → a CSV of content
- Multi-language (TR/EN/DE) output
- Tone presets per brand
- Direct Shopify / WooCommerce push
