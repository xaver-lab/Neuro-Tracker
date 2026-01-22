# Neuro-Tracker 🩺

Eine Python Desktop-Anwendung zur Erfassung und Analyse von Neurodermitis-Verläufen mit Fokus auf Nahrungsmittel-Zusammenhänge.

## 📋 Übersicht

Neuro-Tracker hilft dir dabei, deinen Neurodermitis-Verlauf systematisch zu dokumentieren und mögliche Zusammenhänge mit der Ernährung zu identifizieren. Die Anwendung bietet eine intuitive Kalenderansicht, einfache Dateneingabe und aussagekräftige Statistiken.

## ✨ Hauptfunktionen

### Datenerfassung
- **Täglicher Schweregrad**: Bewertung von 1-5 für den allgemeinen Hautzustand
- **Notizfeld Schweregrad**: Optionale Notizen direkt unter der Schweregrad-Auswahl
- **Lebensmittel-Tracking**: Fixe Auswahl aus vordefinierten Lebensmitteln (Checkboxen)
- **Notizfeld Nahrung**: Optionale Notizen direkt unter der Lebensmittel-Auswahl
- **Schnelle Bearbeitung**: Jeder Tag kann durch Anklicken bearbeitet werden
- **Detail-Ansicht**: Doppelklick auf einen Tag zeigt alle Details in einem erweiterten Fenster

### Benutzeroberfläche
- **Wochenansicht**: Übersichtliche Darstellung von 2 Wochen (aktuelle + letzte Woche)
- **Navigation**: Einfaches Blättern durch vergangene Wochen
- **Eingabe-Panel**: Permanente linke Spalte für schnelle Einträge
  - Standardmäßig vorausgewählt: Aktueller Tag
  - Andere Tage auswählbar
  - Speichern-Button für jeden Eintrag

### Analyse & Export
- **Statistiken**: Graphische Darstellung von Durchschnittswerten und Trends
- **Muster-Erkennung**: Automatische Erkennung von Zusammenhängen zwischen Ernährung und Symptomen
- **Export-Funktion**: Daten als CSV/PDF für Arztbesuche exportieren

### Muster-Erkennung (NEU)
Die Muster-Erkennung analysiert automatisch, ob bestimmte Lebensmittel mit einer Verschlechterung des Hautzustands in den folgenden Tagen zusammenhängen:

- **Zeitfenster einstellbar**: 1-5 Tage nach Verzehr (Standard: 2 Tage)
- **Schwellenwert konfigurierbar**: Ab welcher Schwere gilt ein Tag als "schlecht" (Standard: 4)
- **Wahrscheinlichkeitsberechnung**:
  - Die App zählt, wie oft nach dem Verzehr eines Lebensmittels ein schlechter Tag folgte
  - Beispiel: Milch wurde 10x gegessen, 6x folgte innerhalb von 2 Tagen ein schlechter Tag = 60% Wahrscheinlichkeit
- **Farbcodierung**:
  - Rot (>50%): Hohe Wahrscheinlichkeit - möglicher Trigger
  - Orange (25-50%): Mittlere Wahrscheinlichkeit - beobachten
  - Grün (<25%): Geringe Wahrscheinlichkeit - vermutlich verträglich

### Synchronisation
- **Google Drive Integration**: Automatische Synchronisation zwischen mehreren PCs
- **Offline-Fähig**: Arbeiten auch ohne Internetverbindung möglich
- **Automatisches Backup**: Regelmäßige Sicherung deiner Daten

## 🏗️ Projektstruktur

```
NeuroTracker/
├── README.md                    # Diese Datei
├── requirements.txt             # Python-Dependencies
├── main.py                      # Einstiegspunkt der Anwendung
├── config.py                    # Konfiguration (Pfade, Einstellungen)
├── build.md                     # Build-Anleitung und Dokumentation
├── credentials.json             # Google API Credentials (nicht committen!)
├── .gitignore                   # Git Ignore-Regeln
│
├── data/                        # Lokale Datenspeicherung
│   ├── entries.json             # Tägliche Einträge
│   ├── food_suggestions.json    # Lebensmittel-Vorschläge
│   ├── sync_status.json         # Status der Google Drive Synchronisation
│   └── token.json               # OAuth Token für Google Drive
│
├── ui/                          # User Interface Komponenten
│   ├── __init__.py
│   ├── main_window.py           # Hauptfenster & Layout
│   ├── calendar_widget.py       # Wochen-Kalender-Ansicht
│   ├── entry_panel.py           # Eingabe-Panel (linke Spalte)
│   ├── day_card.py              # Einzelner Tag im Kalender
│   ├── statistics_dialog.py     # Statistik-Fenster
│   └── styles.py                # QSS Styling (Design)
│
├── models/                      # Datenmodelle & Logik
│   ├── __init__.py
│   ├── day_entry.py             # Datenmodell für einen Tag
│   ├── data_manager.py          # Speichern/Laden von Daten
│   └── food_manager.py          # Verwaltung von Lebensmitteln
│
├── utils/                       # Hilfsfunktionen
│   ├── __init__.py
│   ├── google_drive.py          # Google Drive Synchronisation
│   ├── statistics.py            # Statistik-Berechnungen
│   ├── export.py                # Export zu CSV/PDF
│   └── validators.py            # Eingabe-Validierung
```

## 🚀 Installation

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Schritt-für-Schritt Anleitung

1. **Repository klonen**
   ```bash
   git clone https://github.com/your-username/Neuro-Tracker.git
   cd Neuro-Tracker
   ```

2. **Virtual Environment erstellen** (empfohlen)
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Dependencies installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Google Drive Synchronisation einrichten** (optional)
   - Google Cloud Projekt erstellen
   - Drive API aktivieren
   - Credentials herunterladen und als `credentials.json` im Projektordner speichern

5. **Anwendung starten**
   ```bash
   python main.py
   ```

## 🔧 Technologie-Stack

- **GUI Framework**: PyQt5 (moderne, plattformübergreifende Desktop-UI)
- **Datenformat**: JSON (einfach, lesbar, portabel)
- **Charts**: matplotlib / pyqtgraph (für Statistiken)
- **Google Drive**: google-api-python-client (Synchronisation)
- **Export**: reportlab (PDF) / pandas (CSV)

## 📊 Datenmodell

### Tag-Eintrag (DayEntry)
```python
{
    "date": "2026-01-22",
    "severity": 3,                    # Schweregrad 1-5
    "foods": ["Tomaten", "Milch"],    # Liste von Lebensmitteln
    "notes": "Viel Stress heute",     # Optional
    "created_at": "2026-01-22T10:30:00",
    "updated_at": "2026-01-22T10:30:00"
}
```

## 🎯 Geplante Features (Roadmap)

- [x] **v1.0 - Grundfunktionen**
  - [x] Projektstruktur
  - [x] Kalenderansicht mit 2 Wochen
  - [x] Eingabe-Panel für neue Einträge
  - [x] Daten lokal speichern (JSON)
  - [x] Bearbeiten bestehender Einträge

- [x] **v1.1 - Synchronisation**
  - [x] Google Drive Integration
  - [x] Automatisches Backup
  - [ ] Konflikt-Auflösung bei mehreren PCs

- [x] **v1.2 - Analyse**
  - [x] Basis-Statistiken (Durchschnittswerte, Trends)
  - [x] Korrelation Essen ↔ Schweregrad
  - [x] Muster-Erkennung mit Zeitfenster
  - [x] Wahrscheinlichkeitsberechnung für Trigger

- [ ] **v1.3 - Erweiterte Features**
  - [ ] Export zu CSV/PDF
  - [ ] Interaktive Charts
  - [ ] Dunkler Modus (Dark Mode)
  - [ ] Mehrsprachigkeit (DE/EN)

- [ ] **v2.0 - Advanced**
  - [ ] Lebensmittel-Kategorien
  - [ ] Mehrere Körperstellen tracken

## 🤝 Mitwirken

Contributions sind willkommen! Wenn du Ideen oder Verbesserungsvorschläge hast:

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz veröffentlicht - siehe [LICENSE](LICENSE) für Details.

## 💡 Verwendung

### Ersten Eintrag erstellen
1. Starte die Anwendung
2. Das Eingabe-Panel links zeigt automatisch den heutigen Tag
3. Wähle den Schweregrad (1-5) und füge optional Notizen hinzu
4. Wähle die gegessenen Lebensmittel aus den Checkboxen
5. Optional: Notizen zur Nahrung hinzufügen
6. Klicke auf "Speichern"

### Vergangene Tage bearbeiten
1. Klicke auf einen Tag im Kalender
2. Der Tag wird ins Eingabe-Panel geladen
3. Nimm deine Änderungen vor
4. Klicke auf "Speichern"

### Tagesdetails ansehen
1. Doppelklicke auf einen Tag im Kalender
2. Ein Detail-Fenster zeigt alle Informationen des Tages

### Muster-Erkennung nutzen
1. Klicke auf den "Statistiken"-Button in der Toolbar
2. Wechsle zum Tab "Muster-Erkennung"
3. Stelle das Zeitfenster ein (wie viele Tage nach Verzehr soll geprüft werden)
4. Stelle den Schwellenwert ein (ab welcher Schwere gilt ein Tag als schlecht)
5. Die Tabelle zeigt alle erkannten Muster mit Wahrscheinlichkeiten

## 🐛 Bekannte Probleme & FAQ

**Q: Wie oft wird mit Google Drive synchronisiert?**
A: Automatisch bei jedem Speichern + alle 5 Minuten im Hintergrund.

**Q: Kann ich die App ohne Google Drive nutzen?**
A: Ja! Die App funktioniert vollständig offline mit lokaler Speicherung.

**Q: Sind meine Daten sicher?**
A: Alle Daten werden nur lokal und in deinem persönlichen Google Drive gespeichert. Keine Cloud-Server.

## 📧 Kontakt

Bei Fragen oder Problemen erstelle bitte ein [Issue](https://github.com/your-username/Neuro-Tracker/issues).

---

**Hinweis**: Diese Software dient nur zur persönlichen Dokumentation und ersetzt keine ärztliche Beratung.