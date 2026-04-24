#!/usr/bin/env python3
"""
GreenViet LEED Tracker — Supabase Auto Backup
Dùng với GitHub Actions: đọc key từ environment variables
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from supabase import create_client, Client

# ── Đọc config từ environment variables (GitHub Secrets) ──────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Thiếu SUPABASE_URL hoặc SUPABASE_KEY trong environment!")

# Các bảng cần backup
TABLES = ["profiles", "projects", "tasks", "activity_logs"]

# Thư mục lưu (trong repo GitHub)
BACKUP_DIR = Path("backup_data")
BACKUP_DIR.mkdir(exist_ok=True)

def fetch_table(client: Client, table: str) -> list:
    """Tải toàn bộ dữ liệu, hỗ trợ phân trang."""
    all_rows = []
    page_size = 1000
    offset = 0
    while True:
        resp = (
            client.table(table)
            .select("*")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        rows = resp.data or []
        all_rows.extend(rows)
        print(f"  {table}: {len(all_rows)} dòng...")
        if len(rows) < page_size:
            break
        offset += page_size
    return all_rows

def save_csv(data: list, filepath: Path):
    if not data:
        filepath.write_text("(empty)\n", encoding="utf-8")
        return
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def save_json(data: list, filepath: Path):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"=== Backup {date_str} ===")

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    summary = {}
    for table in TABLES:
        print(f"\n>> {table}")
        try:
            rows = fetch_table(client, table)
            # Lưu theo ngày + latest
            day_dir = BACKUP_DIR / date_str
            day_dir.mkdir(exist_ok=True)
            save_csv(rows,  day_dir / f"{table}.csv")
            save_json(rows, day_dir / f"{table}.json")
            # Ghi đè file latest để dễ xem
            save_csv(rows,  BACKUP_DIR / f"{table}_latest.csv")
            summary[table] = len(rows)
            print(f"   OK: {len(rows)} dòng")
        except Exception as e:
            print(f"   LỖI: {e}")
            summary[table] = f"ERROR: {e}"

    # Lưu summary
    summary_path = BACKUP_DIR / f"{date_str}_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "url": SUPABASE_URL,
            "tables": summary
        }, f, ensure_ascii=False, indent=2)

    print(f"\n=== XONG: {sum(v for v in summary.values() if isinstance(v,int)):,} dòng tổng ===")

if __name__ == "__main__":
    main()

