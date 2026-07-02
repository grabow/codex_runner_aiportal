# Codex Runner fuer das HS Offenburg AI Portal

Dieses Repository richtet Codex CLI fuer das AI Portal der Hochschule
Offenburg ein.

Das Skript fragt nach:

- deinem persoenlichen AI-Portal-API-Key
- dem Modellnamen; als Standard ist `EA1_Labor_GPT-5.5` voreingestellt

Danach schreibt es die passende Codex-Konfiguration und startet Codex mit dem
Profil `aiportal`.

## Zugangsdaten erzeugen

**Wichtig: Eine VPN-Verbindung zur Hochschule ist zwingend notwendig.**

Erzeuge zuerst deinen persoenlichen API-Key im Student-Portal:

```text
https://ai-portal.hs-offenburg.de/student
```

Melde dich dort mit deiner Hochschul-E-Mail-Adresse an, bestaetige den per
E-Mail gesendeten Code und kopiere anschliessend den erzeugten API-Key.

Der Key ist persoenlich. Gib ihn nicht weiter und lade ihn nicht in GitHub
hoch. Das Setup-Skript speichert ihn in `~/.codex/config.toml` und setzt fuer
die erzeugten Konfigurationsdateien restriktive Dateirechte.

## Verwendete Einstellungen

API-Endpunkt:

```text
https://ai-portal.hs-offenburg.de/litellm/v1
```

Standardmodell:

```text
EA1_Labor_GPT-5.5
```

Codex-Profil:

```text
aiportal
```

## Voraussetzungen

Du brauchst:

- Python
- Node.js mit `npm`
- `uv`
- Codex CLI
- einen persoenlichen API-Key aus dem Student-Portal

## Codex CLI installieren

Installiere Codex CLI mit `npm`:

```bash
npm install -g @openai/codex
```

Pruefe danach:

```bash
codex --version
```

Wenn der Befehl nicht gefunden wird, starte das Terminal neu.

## uv installieren

Falls `uv` noch nicht installiert ist:

macOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Pruefe danach:

```bash
uv --version
```

## Repository herunterladen

Mit Git:

```bash
git clone https://github.com/grabow/codex_runner_aiportal.git
cd codex_runner_aiportal
```

Alternativ kannst du das Repository ueber GitHub als ZIP herunterladen und
entpacken.

## Setup starten

Im Ordner dieses Repositories:

```bash
uv run python setup_codex_aiportal.py
```

Das Skript fragt nach:

1. AI-Portal-API-Key
2. Modellname

Beim Modellnamen wird `EA1_Labor_GPT-5.5` vorgeschlagen. Mit Enter
uebernimmst du den Standard. Falls du einen anderen Modellnamen erhalten hast,
kannst du ihn stattdessen eingeben.

## Was das Skript macht

Das Skript erstellt oder aktualisiert:

```text
~/.codex/config.toml
~/.codex/aiportal.config.toml
```

Vorhandene Dateien werden vor einer Aenderung als Backup gesichert.

Codex wird danach mit diesem Profil gestartet:

```bash
codex -p aiportal
```

Stelle Codex zum Test eine kurze Frage. Wenn spaeter ein neues Terminal
geoeffnet wird, startest du das Profil erneut mit `codex -p aiportal`.

## Spaeter Codex starten

Nach dem ersten Setup reicht:

```bash
codex -p aiportal
```

## Nur konfigurieren

Wenn du nur die Konfiguration schreiben und Codex noch nicht starten willst:

```bash
uv run python setup_codex_aiportal.py --no-launch
```

## Eingabe im Terminal

Falls das kleine Eingabefenster nicht funktioniert:

```bash
uv run python setup_codex_aiportal.py --no-gui
```

## Modell direkt angeben

```bash
uv run python setup_codex_aiportal.py --model "EA1_Labor_GPT-5.5"
```

## Hinweise bei Fehlern

Codex kann beim Start melden, dass fuer `EA1_Labor_GPT-5.5` keine lokalen
Modell-Metadaten gefunden wurden. Das Modell ist ein Alias des AI Portals; die
Anfrage wird trotzdem an den konfigurierten Portal-Endpunkt gesendet.

Bei `401 Unauthorized` ist der API-Key ungueltig oder wurde nicht korrekt
eingefuegt. Erzeuge dann im Student-Portal einen neuen Key und starte das
Setup-Skript erneut.
