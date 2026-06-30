#!/usr/bin/env python3
"""
Parse a Douyin (抖音) product share link and extract the product ID and details.

Usage:
    python3 parse_douyin_link.py <douyin_short_url>

Example:
    python3 parse_douyin_link.py "https://v.douyin.com/Riw-sVBtUlY/"
"""

import sys
import json
import urllib.parse
import subprocess


def get_redirect_url(short_url: str) -> str:
    """Follow the v.douyin.com short link redirect to get the real product page URL."""
    result = subprocess.run(
        [
            "curl", "-sL",
            "-o", "/dev/null",
            "-w", "%{url_effective}",
            short_url,
            "-H", "User-Agent: Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "--max-time", "15",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error: curl failed with exit code {result.returncode}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def parse_product_info(url: str) -> dict:
    """Extract product ID and optional goods_detail from the redirect URL."""
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)

    product_id = params.get("id", [""])[0]
    if not product_id:
        print("Error: Could not find product ID in URL", file=sys.stderr)
        sys.exit(1)

    info = {"product_id": product_id}

    goods_detail_raw = params.get("goods_detail", [""])[0]
    if goods_detail_raw:
        try:
            goods = json.loads(urllib.parse.unquote(goods_detail_raw))
            info["title"] = goods.get("title", "")
            min_price = goods.get("min_price", 0)
            info["price_yuan"] = min_price / 100
            info["sales"] = goods.get("sales", 0)
            img = goods.get("img", {})
            if img and img.get("url_list"):
                info["image_url"] = img["url_list"][0]
        except (json.JSONDecodeError, KeyError):
            pass

    return info


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_douyin_link.py <douyin_short_url>", file=sys.stderr)
        sys.exit(1)

    short_url = sys.argv[1]
    if not short_url.startswith("https://v.douyin.com/"):
        print("Error: URL must start with https://v.douyin.com/", file=sys.stderr)
        sys.exit(1)

    real_url = get_redirect_url(short_url)
    info = parse_product_info(real_url)

    print(f"商品ID: {info['product_id']}")
    if info.get("title"):
        print(f"商品名称: {info['title']}")
    if info.get("price_yuan"):
        print(f"价格: ¥{info['price_yuan']:,.2f}")
    if info.get("sales") is not None:
        print(f"已售: {info['sales']} 件")
    if info.get("image_url"):
        print(f"商品图片: {info['image_url']}")


if __name__ == "__main__":
    main()
