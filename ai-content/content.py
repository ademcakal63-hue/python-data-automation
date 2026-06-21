"""
AI Content generator: product/topic -> SEO content pack
(meta title, meta description, product description, feature bullets).
For e-commerce/SEO agencies producing content at scale.
Claude if ANTHROPIC_API_KEY is set, else a structured template fallback.
"""
import os
import sys
import json


def generate_template(p: dict) -> dict:
    name = p.get("name", "Product")
    features = p.get("features") or []
    kw = p.get("keyword") or name.lower()
    audience = p.get("audience", "everyday use")
    feat_sentence = ", ".join(features[:3]) if features else "premium quality and reliable performance"
    desc = (
        f"Meet the {name} - made for {audience}. "
        f"With {feat_sentence}, it delivers real value without compromise. "
        f"Easy to use, built to last, and ready whenever you are - the {name} earns its place."
    )
    return {
        "meta_title": f"{name} | Buy {kw.title()} Online"[:60],
        "meta_description": (f"Shop the {name}. {feat_sentence.capitalize()}. Fast shipping and easy returns.")[:155],
        "description": desc,
        "bullets": features or ["High-quality build", "Great everyday value", "Reliable performance"],
    }


def generate_llm(p: dict) -> dict:
    import anthropic
    client = anthropic.Anthropic()
    prompt = (
        "You are an e-commerce SEO copywriter. For the product below, return ONLY JSON with keys: "
        '"meta_title" (<=60 chars), "meta_description" (<=155 chars), '
        '"description" (2-3 sentences), "bullets" (3-5 short feature bullets). '
        "Natural, benefit-led, not keyword-stuffed.\nPRODUCT:\n" + json.dumps(p)
    )
    r = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    txt = r.content[0].text.strip()
    if txt.startswith("```"):
        txt = txt.split("```")[1].lstrip("json").strip()
    return json.loads(txt)


def generate(product: dict) -> dict:
    return generate_llm(product) if os.getenv("ANTHROPIC_API_KEY") else generate_template(product)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        product = json.load(open(sys.argv[1], encoding="utf-8"))
    else:
        product = {
            "name": "AeroBuds Pro",
            "keyword": "wireless earbuds",
            "audience": "commuters and gym-goers",
            "features": ["40h battery life", "active noise cancelling", "IPX5 sweat resistance"],
        }
    print(json.dumps(generate(product), indent=2, ensure_ascii=False))
