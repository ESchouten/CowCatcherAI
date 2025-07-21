# CowCatcher AI 🐄📱

Een automatisch "tochtdetectiesysteem" dat 24/7 koeien monitort en direct meldingen stuurt via Telegram (berichten app) wanneer tochtig gedrag wordt gedetecteerd. 

## 📋 Overzicht

CowCatcher AI is een open-source systeem dat kunstmatige intelligentie gebruikt om automatisch te herkennen wanneer een koe tochtig gedrag vertoont (springen op andere koeien). Het systeem analyseert live camerabeelden en stuurt direct foto's met meldingen naar je telefoon via Telegram.

![readme file afbeelding](https://github.com/user-attachments/assets/3139e8d8-efc5-46ad-90b9-eda2f80b9856)


📷 stal camera beelden ──→ 🤖 AI Computer Visie ──→ ⚡ detectie *springen* ──→ 💽 opslaan afbeelding ──→ 📲 Telegram notificatie met afbeelding

### Belangrijke Kenmerken
- **24/7 monitoring** van live camerabeelden
- **Automatische detectie** van tochtig gedrag met AI
- **Direct meldingen** via Telegram met foto's
- **Lokaal en veilig** – jouw data blijft op jouw bedrijf.
- **Open source** - volledig aanpasbaar en transparant
- **compleet gratis software** eenmalige setup en levenslang gebruik
- **betaalbaar en schaalbaar** voor 1 pinkenhok of complete stal
  
## 🛠️ Benodigdheden

### Hardware
- **Computer** met NVIDIA videokaart (€400-800 voor 1-2 camera's) 
- **IP-camera** met RTSP-ondersteuning (€80-170)
- **PoE-switch** voor camera's (€80 voor 4 poorten)
- **LAN-kabels** (€1 per meter)
- **Internetverbinding**
- **Schaalbaar** hoe meer camera's hoe sterkere computer

### Software
- Anaconda Python
- Sublime Text of Visualstudio code (optioneel)
- WinRAR/7-Zip voor het uitpakken van bestanden

## 📥 Installatie

### Stap 1: Software Downloaden
1. Download en installeer [Anaconda](https://www.anaconda.com/products/distribution)
2. Download en installeer [Sublime Text](https://www.sublimetext.com/) (optioneel)
3. Download en installeer [WinRAR](https://www.win-rar.com/) of 7-Zip
4. Download de latest release van [CowcatcherAI](https://github.com/CowCatcherAI/CowCatcherAI/releases)
5. Voor de Nederlandse versie downloadt u de bestanden tochtdetectie.py en config.py uit de Nederlandse branch.
   
### Stap 2: Project Voorbereiden
1. Extract het zip-bestand naar een map naar keuze (bijv. `C:/tochtdetectie`)
2. Onthoud het pad naar deze map, hier moet je constant naar verwijzen

### Stap 3: Python Omgeving Opzetten

Open **Anaconda Prompt** en voer de volgende commando's uit:

```bash
# Navigeer naar je project schijf (vervang F: door jouw schijf)
F:

# Ga naar je project map
cd tochtdetectie

# Maak een nieuwe conda omgeving aan
conda create -n tochtdetectie python=3.11

# Bevestig met 'y' wanneer gevraagd
y

# Activeer de omgeving
conda activate tochtdetectie
```

### Stap 4: Vereiste Pakketten Installeren

```bash
# Installeer Ultralytics YOLO
pip install ultralytics

# Installeer PyTorch met CUDA ondersteuning
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

### Stap 5: GPU Ondersteuning Controleren

```bash
# Start Python
python

# Test CUDA beschikbaarheid
import torch
torch.cuda.is_available()

# Zou 'True' moeten returnen voor GPU ondersteuning
# Verlaat Python
exit()
```

## 🤖 Telegram Bot Instellen

### Stap 1: Bot Aanmaken
1. Open Telegram en zoek naar `@BotFather`
2. Start een chat en stuur `/newbot`
3. Geef je bot een naam: "bijv:" `Tocht detectie`
4. Geef je bot een gebruikersnaam: `TochtdetectieBot`
5. **Bewaar de API-token** die je ontvangt, NOOIT deze token delen

### Stap 2: Je Gebruikers-ID Verkrijgen
1. Zoek naar `@userinfobot` in Telegram
2. Start een chat en stuur `/start`
3. **Noteer je persoonlijke Telegram-ID**

### Stap 3: Configuratie Instellen
Pas het `config.py` bestand aan in je project map:

```python
# Telegram configuratie
TELEGRAM_BOT_TOKEN = "JOUW_BOT_TOKEN_HIER"
TELEGRAM_CHAT_ID = "JOUW_TELEGRAM_ID_HIER"

# Camera configuratie
RTSP_URL_CAMERA1 = "rtsp://gebruiker:wachtwoord@IP_ADRES:554/stream"
```

## 🚀 Het Systeem Starten
Pas de .bat file aan, of gebruik de volgende stappen 

```bash
# Navigeer naar je project map
F:
cd tochtdetectie

# Start het detectieprogramma
python tochtdetectiebot.py
```

Bij succesvol opstarten ontvang je een bevestigingsbericht in Telegram.

## ⚙️ Configuratie Opties

Het systeem heeft verschillende aanpasbare drempelwaarden:

- **SAVE_THRESHOLD** (0.7): Drempel voor het opslaan van beelden
- **NOTIFY_THRESHOLD** (0.85): Drempel voor het versturen van meldingen
- **PEAK_DETECTION_THRESHOLD** (0.90): Drempel voor piekdetectie
- **COOLDOWN_PERIOD** (40 seconden): Tijd tussen meldingen
- **MAX_SCREENSHOTS** (2): Aantal foto's per melding
- **SOUND_EVERY_N_NOTIFICATIONS** Melding MET geluid om de 5 berichten
- 
## 📁 Projectstructuur

```
tochtdetectie/
├── README.md
├── LICENSE
├── CowcatcherV13.pt          # AI model bestand
├── tochtdetectiebot.py       # Hoofdprogramma
├── config.py                 # Configuratie bestand
└── mounting_detections/      # Map voor opgeslagen detecties
```

## 📄 Licentie

Dit project gebruikt de GNU Affero General Public License v3.0 (AGPL-3.0). Het is gebaseerd op Ultralytics YOLO en is volledig open source.

## 🙏 Met dank aan

Dit project is mogelijk gemaakt door de geweldige [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) bibliotheek. Hun state-of-the-art computer vision technologie vormt de basis voor onze AI-detectie van tochtig gedrag bij koeien.

**Bedankt Ultralytics team!** 🚀 Voor het beschikbaar maken van cutting-edge AI technologie die nu ook Nederlandse boeren helpt.

## 🤝 Bijdragen

Dit is een open source project. Je mag het aanpassen en verbeteren naar eigen inzicht. Bijdragen zijn welkom via pull requests.

## 📞 Ondersteuning

Voor vragen of ondersteuning, neem contact op via de project repository of community kanalen.

---
⚠️ Disclaimer

Gebruik op eigen risico.
Deze software is bedoeld als hulpmiddel en vormt geen vervanging voor professionele kennis en ervaring. De AI kan foutieve meldingen geven; de gebruiker blijft zelf verantwoordelijk voor de uiteindelijke beoordeling en beslissing. Fysieke controle en identificatie van het dier blijven onmisbaar.

Hoewel deze oplossing gebruiksvriendelijk en efficiënt is vormgegeven, is de onderliggende technologie niet nieuw. De gebruikte computervisie is gebaseerd op YOLO, een beproefde techniek die al jarenlang wordt toegepast voor object- en bewegingsdetectie. Ook de Telegram-notificaties maken gebruik van een bestaande API. Ondanks dat het vernieuwend kan lijken, betreft het een slimme combinatie van bestaande technologieën.
