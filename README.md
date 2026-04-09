# Sledovač závodů LOS

Webová aplikace pro sledování závodů a registrací z [loslex.cz](https://www.loslex.cz/contest).

## Funkce

- 📋 Přehled všech závodů s filtry (kraj, typ, stav registrace)
- ⭐ Sledované závody s upomínkami
- 📅 Export do Google / Apple kalendáře (.ics)
- 🔄 Automatická aktualizace dat každý den přes GitHub Actions

---

## Nastavení (jednorázové, ~10 minut)

### 1. Vytvoř GitHub účet
Jdi na [github.com](https://github.com) a zaregistruj se zdarma.

### 2. Vytvoř nový repozitář
- Klikni **New repository**
- Název: `loslex` (nebo cokoliv chceš)
- Viditelnost: **Public** (nutné pro GitHub Pages zdarma)
- Klikni **Create repository**

### 3. Nahraj soubory
Přes webové rozhraní GitHubu (záložka **Add file → Upload files**) nahraj:
```
index.html
manifest.json
contests.json          ← vygeneruj poprvé spuštěním scrape.py
scripts/scrape.py
.github/workflows/update.yml
```

Nebo pomocí gitu:
```bash
git init
git add .
git commit -m "První commit"
git remote add origin https://github.com/TVOJE-JMENO/loslex.git
git push -u origin main
```

### 4. Zapni GitHub Pages
- Jdi do repozitáře → **Settings → Pages**
- Source: **Deploy from a branch**
- Branch: `gh-pages` (vytvoří se automaticky po prvním spuštění workflow)
- Klikni **Save**

### 5. Spusť workflow poprvé ručně
- Jdi do záložky **Actions** v repozitáři
- Vyber workflow **Aktualizace závodů LOS**
- Klikni **Run workflow**

### 6. Otevři aplikaci
Po ~2 minutách bude dostupná na:
```
https://TVOJE-JMENO.github.io/loslex/
```

---

## Automatická aktualizace

GitHub Actions spustí scraper každý den v **7:00 ráno** (SEČ) a aktualizuje `contests.json`. Nové závody se objeví automaticky.

---

## E-mailové notifikace (volitelné)

### Varianta A — Google Kalendář (nejjednodušší)
1. V aplikaci klikni **Export .ics kalendáře**
2. Otevři [calendar.google.com](https://calendar.google.com)
3. **+** → **Z URL / Ze souboru** → nahraj .ics
4. Google Kalendář ti sám pošle e-mail před každým závodem

### Varianta B — automatický e-mail přes GitHub Actions + Gmail
Přidej do `.github/workflows/update.yml` krok po scraperu:

```yaml
- name: Pošli upomínky e-mailem
  env:
    SMTP_USER: ${{ secrets.GMAIL_USER }}
    SMTP_PASS: ${{ secrets.GMAIL_APP_PASS }}
  run: python scripts/send_reminders.py
```

Skript `scripts/send_reminders.py` porovná termíny závodů ze `contests.json` s nastaveným e-mailem a pošle upomínku, pokud je závod za 7 / 3 / 1 den.

Do **Settings → Secrets and variables → Actions** přidej:
- `GMAIL_USER` = tvůj gmail
- `GMAIL_APP_PASS` = [App Password](https://myaccount.google.com/apppasswords) (ne heslo ke Gmail účtu)

---

## Soubory

| Soubor | Popis |
|--------|-------|
| `index.html` | Hlavní aplikace |
| `contests.json` | Data závodů (generuje scraper) |
| `manifest.json` | PWA manifest (instalace na mobil) |
| `scripts/scrape.py` | Scraper loslex.cz |
| `.github/workflows/update.yml` | GitHub Actions workflow |
