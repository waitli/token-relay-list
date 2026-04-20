#!/usr/bin/env python3
"""检查各中转平台是否可访问"""
import requests
import json
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}


def check_platform(p):
    """检查单个平台是否可访问"""
    url = p["url"]
    result = {"name": p["name"], "url": url, "desc": p.get("desc", ""), "type": p.get("type", ""), "accessible": False, "status_code": 0, "response_time": 0}
    try:
        start = time.time()
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        elapsed = round(time.time() - start, 2)
        result["status_code"] = resp.status_code
        result["response_time"] = elapsed
        result["accessible"] = resp.status_code < 400
        # 尝试检测是否是真实的内容页面
        if resp.status_code == 200:
            text = resp.text[:2000].lower()
            if "cloudflare" in text and "challenge" in text:
                result["accessible"] = False
                result["note"] = "Cloudflare 验证"
    except requests.exceptions.ConnectionError:
        result["note"] = "无法连接"
    except requests.exceptions.Timeout:
        result["note"] = "超时"
    except Exception as e:
        result["note"] = str(e)[:50]
    return result


def main():
    # 加载平台列表
    platforms_path = os.path.join(DATA_DIR, "all_platforms.json")
    with open(platforms_path, "r", encoding="utf-8") as f:
        platforms = json.load(f)

    print(f"共 {len(platforms)} 个平台待检查\n")

    results = []
    # 并发检查（限制并发数避免被封）
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_platform, p): p for p in platforms}
        for future in as_completed(futures):
            r = future.result()
            status = "✓" if r["accessible"] else "✗"
            note = f" ({r.get('note', '')})" if r.get("note") else ""
            time_str = f"{r['response_time']}s" if r["response_time"] else ""
            print(f"  {status} {r['name']:25s} {r['status_code']:>3} {time_str:>6}{note}")
            results.append(r)

    # 按分类排序，再按可访问性排序
    type_order = {"relay": 0, "source": 1, "github": 2}
    results.sort(key=lambda x: (type_order.get(x.get("type", ""), 9), -int(x["accessible"]), x["name"]))

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    accessible_count = sum(1 for r in results if r["accessible"])

    output = {
        "last_updated": now,
        "total": len(results),
        "accessible": accessible_count,
        "platforms": results,
    }

    out_path = os.path.join(DATA_DIR, "checked.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] {accessible_count}/{len(results)} 个平台可访问")
    print(f"  已保存到 {out_path}")


if __name__ == "__main__":
    main()
