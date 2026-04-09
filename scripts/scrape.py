#!/usr/bin/env python3
"""Scraper závodů z loslex.cz/contest — generuje contests.json"""

import re
import json
import urllib.request
from datetime import datetime

URL = "https://www.loslex.cz/contest"
OUTPUT = "contests.json"

MONTHS = {
    "ledna": 1, "února": 2, "března": 3, "dubna": 4, "května": 5, "června": 6,
    "července": 7, "srpna": 8, "září": 9, "října": 10, "listopadu": 11, "prosince": 12,
}

def fetch_page():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (compatible; LOS-tracker/1.0)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")

def parse_contests(html):
    # Odstraň HTML tagy pro snadnější parsing
    clean = re.sub(r"<[^>]+>", "\n", html)
    clean = re.sub(r"&amp;", "&", clean)
    clean = re.sub(r"&nbsp;", " ", clean)
    clean = re.sub(r"&#\d+;", "", clean)
    lines = [l.strip() for l in clean.splitlines() if l.strip()]

    contests = []
    i = 0
    while i < len(lines):
        # Hledáme řádek s datem ve formátu "D. měsíc YYYY"
        date_m = re.match(r"^(\d{1,2})\.\s+(\w+)\s+(\d{4})$", lines[i])
        if date_m:
            day, month_str, year = date_m.groups()
            month_num = MONTHS.get(month_str.lower())
            if month_num:
                date_str = f"{day}. {month_str} {year}"
                try:
                    date_obj = datetime(int(year), month_num, int(day))
                except ValueError:
                    i += 1
                    continue

                # Hledáme název závodu a URL v okolních řádcích
                title = None
                url = None
                location = None
                region = None
                contest_type = None
                weapon = None
                capacity = None
                reg_status = None

                # Prohledáme dalších ~20 řádků za datem
                for j in range(i + 1, min(i + 25, len(lines))):
                    line = lines[j]

                    # URL závodu
                    url_m = re.search(r"(https://www\.loslex\.cz/contest/(\d+))", line)
                    if url_m and not url:
                        url = url_m.group(1)
                        contest_id = url_m.group(2)

                    # Název závodu — řádek s textem po URL
                    if url and not title and len(line) > 5 and not line.startswith("http") and not re.match(r"^\d", line):
                        if not any(kw in line for kw in ["Registrace:", "Krátká", "Puška", "Brokovnice", "kraj", "Pohárový", "LOSík", "Tréning", "Klubový", "Hodnocené", "Mistrovství", "Událost"]):
                            title = line

                    # Kraj
                    if "kraj" in line.lower() or "Praha" in line:
                        if not region:
                            region = line

                    # Typ závodu
                    for t in ["Pohárový závod", "LOSík", "Klubový závod", "Mistrovství", "Tréning", "Hodnocené střelby", "Událost beze střelby"]:
                        if t in line and not contest_type:
                            contest_type = t

                    # Zbraň
                    for w in ["Krátká zbraň", "Puška", "Brokovnice"]:
                        if w in line and not weapon:
                            weapon = w

                    # Kapacita (formát "X / Y" nebo jen číslo)
                    cap_m = re.match(r"^(\d+\s*/\s*\d+|\d+)$", line)
                    if cap_m and not capacity:
                        capacity = cap_m.group(1).replace(" ", "")

                    # Stav registrace
                    if "Registrace:" in line or line in ["Aktivní", "Ukončena", "Neotevřena"]:
                        if not reg_status:
                            if "Aktivní" in line:
                                reg_status = "Aktivní"
                            elif "Ukončena" in line:
                                reg_status = "Ukončena"
                            else:
                                # Datum otevření registrace
                                reg_date_m = re.search(r"(\d{1,2}\.\s+\w+\s+\d{4}\s+\d{2}:\d{2})", line)
                                if reg_date_m:
                                    reg_status = reg_date_m.group(1).strip()

                    # Lokace — řádek před krajem, který není typ/zbraň
                    if region and not location:
                        idx = lines.index(region) if region in lines else -1
                        if idx > 0:
                            candidate = lines[idx - 1]
                            if len(candidate) > 2 and not any(kw in candidate for kw in ["kraj", "závod", "LOSík", "Krátká", "Puška"]):
                                location = candidate

                    # Konec záznamu — nové datum
                    if j > i + 3 and re.match(r"^(\d{1,2})\.\s+(\w+)\s+(\d{4})$", line):
                        break

                # Fallback na URL-based název
                if not title and url:
                    # Pokusíme se najít název jinak
                    block = " ".join(lines[i:min(i+20, len(lines))])
                    title_m = re.search(r"contest/\d+\s+(.+?)(?:\s+(?:Guncenter|LEX|SK|KVZ|Antares|DonShot|CS Solutions|Střelecký|Polárka))", block)
                    if title_m:
                        title = title_m.group(1).strip()

                if url and title:
                    contests.append({
                        "id": contest_id,
                        "title": title,
                        "date": date_str,
                        "date_iso": date_obj.strftime("%Y-%m-%d"),
                        "location": location or "",
                        "region": region or "",
                        "type": contest_type or "",
                        "weapon": weapon or "",
                        "capacity": capacity or "",
                        "reg": reg_status or "",
                        "url": url,
                    })
        i += 1

    # Deduplikace podle ID
    seen = set()
    unique = []
    for c in contests:
        if c["id"] not in seen:
            seen.add(c["id"])
            unique.append(c)

    return unique

def main():
    print(f"Načítám {URL} ...")
    html = fetch_page()
    contests = parse_contests(html)
    print(f"Nalezeno {len(contests)} závodů")

    output = {
        "updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(contests),
        "contests": contests,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Uloženo do {OUTPUT}")

if __name__ == "__main__":
    main()
