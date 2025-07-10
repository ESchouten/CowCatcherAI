"""
CowCatcher Script
Copyright (C) 2025

Dit programma gebruikt YOLOv11 van Ultralytics (https://github.com/ultralytics/ultralytics)
en is gelicentieerd onder de voorwaarden van de GNU Affero General Public License (AGPL-3.0).

Het getrainde model cowcatcherVx.pt is een afgeleide werk gemaakt door het trainen van het Ultralytics YOLO framework op een aangepaste dataset.
Er zijn geen wijzigingen aan de originele YOLO broncode.

Dit programma is gratis software: je mag het herverdelen en/of aanpassen
onder de voorwaarden van de GNU Affero General Public License zoals gepubliceerd door
de Free Software Foundation, versie 3 van de Licentie, of
(naar jouw keuze) elke latere versie.

Dit programma wordt verspreid in de hoop dat het nuttig zal zijn,
maar ZONDER ENIGE GARANTIE; zelfs zonder de impliciete garantie van
VERKOOPBAARHEID of GESCHIKTHEID VOOR EEN BEPAALD DOEL. Zie de
GNU Affero General Public License voor meer details.

Je zou een kopie van de GNU Affero General Public License moeten hebben ontvangen
samen met dit programma. Zo niet, zie <https://www.gnu.org/licenses/>.

Deze software gebruikt Ultralytics YOLO, beschikbaar onder de AGPL-3.0 licentie.
De complete broncode repository is beschikbaar op: https://github.com/CowCatcherAI/CowCatcherAI
"""

from ultralytics import YOLO
import cv2
import os
import time
import requests
from datetime import datetime
import config  # Importeer het configuratiebestand
from collections import deque

# Configuratie voor live scherm weergave
TOON_LIVE_FEED = True  # Zet op True om live scherm te tonen, False om uit te schakelen
VERSTUUR_GEANNOTEERDE_AFBEELDINGEN = True  # Zet op True om geannoteerde afbeeldingen te versturen, False voor originele afbeeldingen

print("Script gestart. YOLO model laden...")
# Laad je getrainde YOLO model 
model = YOLO("CowcatcherV13.pt")
print("YOLO model succesvol geladen")

# RTSP URL voor de camera - nu opgehaald uit config
rtsp_url_camera1 = config.RTSP_URL_CAMERA1
print(f"Verbinding maken met camera: {rtsp_url_camera1}")

# Map voor opslaan van screenshots
opslag_map = "dekking_detecties"
if not os.path.exists(opslag_map):
    os.makedirs(opslag_map)
    print(f"Map '{opslag_map}' aangemaakt")
else:
    print(f"Map '{opslag_map}' bestaat al")

# Telegram configuratie - nu opgehaald uit config
TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = config.TELEGRAM_CHAT_ID

# Test Telegram verbinding bij opstarten
def test_telegram_verbinding():
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url)
        if response.status_code == 200:
            print("Telegram verbinding succesvol getest.")
            return True
        else:
            print(f"FOUT bij testen Telegram verbinding: {response.text}")
            return False
    except Exception as e:
        print(f"FOUT bij testen Telegram verbinding: {str(e)}")
        return False

def verstuur_telegram_foto(afbeelding_pad, bijschrift, schakel_notificatie_uit=False):
    """Verstuurt een foto met bijschrift naar Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        with open(afbeelding_pad, 'rb') as foto:
            files = {'photo': foto}
            data = {
                'chat_id': TELEGRAM_CHAT_ID, 
                'caption': bijschrift,
                'disable_notification': schakel_notificatie_uit
            }
            response = requests.post(url, files=files, data=data)
            
        if response.status_code != 200:
            print(f"FOUT bij versturen Telegram foto: {response.text}")
            return False
            
        return response.json()
    except Exception as e:
        print(f"FOUT bij versturen Telegram foto: {str(e)}")
        return False

def verstuur_telegram_bericht(bericht):
    """Verstuurt een tekstbericht naar Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {'chat_id': TELEGRAM_CHAT_ID, 'text': bericht}
        response = requests.post(url, data=data)
        
        if response.status_code != 200:
            print(f"FOUT bij versturen Telegram bericht: {response.text}")
            return False
            
        return response.json()
    except Exception as e:
        print(f"FOUT bij versturen Telegram bericht: {str(e)}")
        return False

# Test Telegram verbinding
if not test_telegram_verbinding():
    print("Telegram verbinding gefaald, script wordt afgesloten.")
    exit()

# Open de camera stream
print("Camera stream openen...")
cap = cv2.VideoCapture(rtsp_url_camera1)
if not cap.isOpened():
    print("FOUT: Kan camera stream niet openen")
    exit()
else:
    print("Camera stream succesvol geopend")
    print(f"Live weergave is {'ingeschakeld' if TOON_LIVE_FEED else 'uitgeschakeld'}")

# Constanten voor detectie
OPSLAG_DREMPELWAARDE = 0.7      # Drempelwaarde voor opslaan van afbeeldingen
MELDING_DREMPELWAARDE = 0.84    # Drempelwaarde voor versturen van meldingen
PIEK_DETECTIE_DREMPELWAARDE = 0.89  # Drempelwaarde voor piek detectie
MAX_SCREENSHOTS = 2             # Aantal screenshots om per gebeurtenis te versturen
VERZAMEL_TIJD = 50              # Maximale tijd om screenshots te verzamelen in seconden
MIN_VERZAMEL_TIJD = 4           # Minimale tijd om te verzamelen, zelfs na piek detectie
INACTIVITEIT_STOP_TIJD = 6      # Stopt met verzamelen na 6 seconden zonder detecties boven OPSLAG_DREMPELWAARDE
MIN_HOGE_VERTROUWEN_DETECTIES = 3  # NIEUW: Minimum vereiste detecties boven MELDING_DREMPELWAARDE
frame_teller = 0
verwerk_elke_n_frames = 2       # Verwerk elke 2 frames
laatste_detectie_tijd = None
cooldown_periode = 40           # Seconden tussen opeenvolgende meldingen

# NIEUW: Variabelen voor geluidsmeldingen
melding_teller = 0              # Teller voor meldingen
GELUID_ELKE_N_MELDINGEN = 5     # Geluid elke 5e melding

# Nieuw: Deque voor het bijhouden van vertrouwen score progressie
vertrouwen_geschiedenis = deque(maxlen=10)  # Houd laatste 10 vertrouwen scores bij
frame_geschiedenis = deque(maxlen=10)       # Houd bijbehorende frames bij
tijdstempel_geschiedenis = deque(maxlen=10) # Houd bijbehorende tijdstempels bij

# Variabelen voor verzamelen van de beste screenshots tijdens een gebeurtenis
verzamel_screenshots = False
verzamel_start_tijd = None
gebeurtenis_detecties = []      # Lijst van tuples (vertrouwen, frame, tijdstempel, origineel_afbeelding_pad, resultaten_obj)
piek_gedetecteerd = False       # Indicator of een piek werd gedetecteerd
laatste_detectie_tijd = None    # Laatste keer dat er een detectie was boven OPSLAG_DREMPELWAARDE
inactiviteit_periode = 0        # Bijhouden hoelang er geen activiteit is geweest

print(f"Verwerking gestart, elke {verwerk_elke_n_frames} frames worden geanalyseerd")
print(f"Afbeelding opslag drempelwaarde: {OPSLAG_DREMPELWAARDE}")
print(f"Melding verstuur drempelwaarde: {MELDING_DREMPELWAARDE}")
print(f"Piek detectie drempelwaarde: {PIEK_DETECTIE_DREMPELWAARDE}")
print(f"Maximaal {MAX_SCREENSHOTS} screenshots per gebeurtenis")
print(f"Verzamel tijd: {MIN_VERZAMEL_TIJD}-{VERZAMEL_TIJD} seconden")
print(f"Stopt automatisch na {INACTIVITEIT_STOP_TIJD} seconden van inactiviteit")
print(f"Minimum {MIN_HOGE_VERTROUWEN_DETECTIES} detecties boven {MELDING_DREMPELWAARDE} vereist voor melding")
print(f"Telegram afbeeldingen: {'Met begrenzingsboxen' if VERSTUUR_GEANNOTEERDE_AFBEELDINGEN else 'Zonder begrenzingsboxen'}")
print(f"Geluidsmelding elke {GELUID_ELKE_N_MELDINGEN} waarschuwingen")

# Verstuur een start bericht om te bevestigen dat alles werkt
start_bericht = f"📋 Cowcatcher detectie script gestart op {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n⚠️ DISCLAIMER: Gebruik op eigen risico. Dit programma gebruikt Ultralytics YOLO en valt onder de GNU Affero General Public License v3.0 (AGPL-3.0). De complete broncode is beschikbaar op https://github.com/CowCatcherAI/CowCatcherAI."
verstuur_telegram_bericht(start_bericht)

def detecteer_dekking_piek(vertrouwen_geschiedenis, frame_geschiedenis, tijdstempel_geschiedenis):
    """
    Detecteert de piek van een dekking gebeurtenis gebaseerd op vertrouwen score progressie.
    Retourneert een tuple met (piek_index, piek_vertrouwen, voor_piek_index, na_piek_index)
    """
    if len(vertrouwen_geschiedenis) < 5:  # We hebben minstens 5 datapunten nodig
        return None, None, None, None
    
    # Vind de hoogste vertrouwen score
    max_vertr = max(vertrouwen_geschiedenis)
    max_idx = vertrouwen_geschiedenis.index(max_vertr)
    
    # Als het maximale vertrouwen onder onze piek drempel is, is dit geen duidelijk piek moment
    if max_vertr < PIEK_DETECTIE_DREMPELWAARDE:
        return None, None, None, None
    
    # Vind een frame van net voor de piek (voor context)
    voor_piek_idx = max(0, max_idx - 2)
    
    # Vind een frame van net na de piek (om de daling te zien)
    na_piek_idx = min(len(vertrouwen_geschiedenis) - 1, max_idx + 2)
    
    # Retourneer informatie over de piek en omringende frames
    return max_idx, voor_piek_idx, na_piek_idx, max_vertr

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("FOUT: Kan frame niet lezen van camera")
            # Probeer opnieuw verbinding te maken met de camera
            cap.release()
            time.sleep(5)
            cap = cv2.VideoCapture(rtsp_url_camera1)
            continue
            
        frame_teller += 1
        
        if frame_teller % 100 == 0:
            print(f"Frames verwerkt: {frame_teller}")
        
        # Verwerk alleen elke n frames
        if frame_teller % verwerk_elke_n_frames == 0:
            # Voer detectie uit
            results = model.predict(source=frame, classes=[0], conf=0.2, verbose=False)
            
            # Vind hoogste vertrouwen detectie
            hoogste_vertr_detectie = None
            hoogste_vertr = 0.0
            if len(results[0].boxes) > 0:
                # Sorteer detecties op vertrouwen (hoogste eerst)
                gesorteerde_detecties = sorted(results[0].boxes, key=lambda x: float(x.conf), reverse=True)
                if len(gesorteerde_detecties) > 0:
                    hoogste_vertr_detectie = gesorteerde_detecties[0]
                    hoogste_vertr = float(hoogste_vertr_detectie.conf)
            
            huidige_tijd = datetime.now()
            tijdstempel = huidige_tijd.strftime("%Y%m%d_%H%M%S")
            
            # Sla detectie op in geschiedenis (zelfs bij laag vertrouwen om progressie te zien)
            if hoogste_vertr_detectie is not None:
                vertrouwen_geschiedenis.append(hoogste_vertr)
                frame_geschiedenis.append(frame.copy())  # Sla een kopie van het frame op
                tijdstempel_geschiedenis.append(tijdstempel)
            else:
                # Voeg nul toe als er geen detectie is (belangrijk voor het detecteren van progressie)
                vertrouwen_geschiedenis.append(0.0)
                frame_geschiedenis.append(frame.copy())
                tijdstempel_geschiedenis.append(tijdstempel)
                
            kan_melding_versturen = (laatste_detectie_tijd is None or 
                                    (huidige_tijd - laatste_detectie_tijd).total_seconds() > cooldown_periode)
            
            # Start screenshots verzamelen als we een detectie hebben boven OPSLAG_DREMPELWAARDE
            if hoogste_vertr >= OPSLAG_DREMPELWAARDE and not verzamel_screenshots and kan_melding_versturen:
                print(f"Start screenshot verzameling voor {VERZAMEL_TIJD} seconden (zoeken naar piek moment)")
                verzamel_screenshots = True
                verzamel_start_tijd = huidige_tijd
                gebeurtenis_detecties = []
                piek_gedetecteerd = False
                
                # Voeg eerdere frames toe die al in geschiedenis staan (voor context)
                for i in range(len(vertrouwen_geschiedenis)):
                    if vertrouwen_geschiedenis[i] >= OPSLAG_DREMPELWAARDE:
                        # Krijg historisch frame
                        hist_frame = frame_geschiedenis[i]
                        hist_tijdstempel = tijdstempel_geschiedenis[i]
                        hist_vertr = vertrouwen_geschiedenis[i]
                        
                        # Sla het originele frame op
                        hist_origineel_opslag_pad = os.path.join(opslag_map, f"dekking_gedetecteerd{hist_tijdstempel}_vertr{hist_vertr:.2f}_geschiedenis.jpg")
                        cv2.imwrite(hist_origineel_opslag_pad, hist_frame)
                        
                        # We hebben geen resultaat object voor historische frames, dus maak een eenvoudige annotatie
                        hist_geannoteerd_frame = hist_frame.copy()
                        cv2.putText(hist_geannoteerd_frame, f"Vertr: {hist_vertr:.2f}", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        # Voeg toe aan gebeurtenis_detecties (zonder resultaat object, met geannoteerd frame)
                        if TOON_LIVE_FEED:
                            gebeurtenis_detecties.append((hist_vertr, hist_geannoteerd_frame, hist_tijdstempel, hist_origineel_opslag_pad, None))
                        else:
                            gebeurtenis_detecties.append((hist_vertr, None, hist_tijdstempel, hist_origineel_opslag_pad, None))
                
            # Als we aan het verzamelen zijn
            if verzamel_screenshots:
                # Als er een detectie is, voeg toe aan verzameling
                if hoogste_vertr_detectie is not None and hoogste_vertr >= OPSLAG_DREMPELWAARDE:
                    # Sla origineel frame op
                    origineel_opslag_pad = os.path.join(opslag_map, f"dekking_gedetecteerd_{tijdstempel}_vertr{hoogste_vertr:.2f}.jpg")
                    cv2.imwrite(origineel_opslag_pad, frame)
                    
                    # Maak geannoteerd frame voor live weergave, maar sla het nog niet op
                    geannoteerd_frame = results[0].plot()
                    
                    # Voeg toe aan verzameling - met geannoteerd_frame voor live weergave en results[0] voor latere annotaties
                    if TOON_LIVE_FEED:
                        gebeurtenis_detecties.append((hoogste_vertr, geannoteerd_frame.copy(), tijdstempel, origineel_opslag_pad, results[0]))
                    else:
                        gebeurtenis_detecties.append((hoogste_vertr, None, tijdstempel, origineel_opslag_pad, results[0]))
                    
                    print(f"Detectie toegevoegd aan verzameling: {hoogste_vertr:.2f}")
                    
                    # Reset inactiviteit periode wanneer we een detectie hebben boven OPSLAG_DREMPELWAARDE
                    inactiviteit_periode = 0
                    laatste_detectie_tijd = huidige_tijd
                    
                    # Controleer of we een piek hebben gedetecteerd
                    if hoogste_vertr >= PIEK_DETECTIE_DREMPELWAARDE and not piek_gedetecteerd:
                        piek_gedetecteerd = True
                        print(f"Mogelijke piek gedetecteerd met vertrouwen {hoogste_vertr:.2f}")
                else:
                    # Als er geen detectie is boven OPSLAG_DREMPELWAARDE, verhoog inactiviteit periode
                    if laatste_detectie_tijd is not None:
                        inactiviteit_periode = (huidige_tijd - laatste_detectie_tijd).total_seconds()
                        if inactiviteit_periode >= 2:  # Log elke 2 seconden
                            print(f"Inactiviteit periode: {inactiviteit_periode:.1f}s")
                
                # Controleer of we moeten stoppen met verzamelen
                verzamel_duur = (huidige_tijd - verzamel_start_tijd).total_seconds()
                
                # Stop met verzamelen als:
                # 1. We hadden een piek moment en minimale verzamel tijd is verstreken, of
                # 2. We bereikten maximale verzamel tijd, of
                # 3. We hebben een zeer duidelijke detectie (boven 0.85) - directe reactie voor duidelijke gevallen, of
                # 4. De inactiviteit periode heeft INACTIVITEIT_STOP_TIJD bereikt (geen detecties voor X seconden)
                if (piek_gedetecteerd and verzamel_duur >= MIN_VERZAMEL_TIJD) or \
                   verzamel_duur >= VERZAMEL_TIJD or \
                   (hoogste_vertr >= 0.85 and verzamel_duur >= 1) or \
                   inactiviteit_periode >= INACTIVITEIT_STOP_TIJD:
                    # Tijd om te stoppen met verzamelen en bepalen welke afbeeldingen te versturen
                    print(f"Verzameling gestopt na {verzamel_duur:.1f} seconden met {len(gebeurtenis_detecties)} detecties")
                    
                    # Vind het piek moment in de verzamelde data
                    huidige_vertouwens = [vertr for vertr, _, _, _, _ in gebeurtenis_detecties]
                    
                    # NIEUW: Controleer of er genoeg detecties zijn boven MELDING_DREMPELWAARDE
                    hoge_vertr_detecties = sum(1 for vertr in huidige_vertouwens if vertr >= MELDING_DREMPELWAARDE)
                    print(f"Aantal hoge vertrouwen detecties: {hoge_vertr_detecties}/{MIN_HOGE_VERTROUWEN_DETECTIES} vereist")
                    
                    # Voor korte gebeurtenissen: zelfs met weinig detecties, stuur nog steeds een melding
                    if len(huidige_vertouwens) > 0:
                        # Vind het hoogste vertrouwen en index
                        max_vertr = max(huidige_vertouwens)
                        max_idx = huidige_vertouwens.index(max_vertr)
                        
                        # Bepaal welke afbeeldingen we willen versturen
                        geselecteerde_indices = []
                        
                        # Voor zeer korte gebeurtenissen met weinig frames
                        if len(huidige_vertouwens) <= 2:
                            # Als we maar 1 of 2 frames hebben, stuur ze allemaal
                            geselecteerde_indices = list(range(len(huidige_vertouwens)))
                        else:
                            # Voor langere gebeurtenissen: probeer voor, piek, en na te selecteren
                            # Voeg de piek toe
                            geselecteerde_indices.append(max_idx)
                            
                            # Probeer een afbeelding voor de piek toe te voegen - als het bestaat
                            if max_idx > 0:
                                geselecteerde_indices.append(max(0, max_idx - 1))  # Direct voor de piek
                            
                            # Probeer een afbeelding na de piek toe te voegen - als het bestaat
                            if max_idx < len(gebeurtenis_detecties) - 1:
                                geselecteerde_indices.append(max_idx + 1)  # Direct na de piek
                        
                        # Sorteer en limiteer tot MAX_SCREENSHOTS
                        geselecteerde_indices = sorted(geselecteerde_indices)[:MAX_SCREENSHOTS]
                        
                        # GEWIJZIGD: Verstuur de geselecteerde afbeeldingen als we zowel voldoende vertrouwen
                        # als voldoende detecties boven de drempel hebben
                        if max_vertr >= MELDING_DREMPELWAARDE and hoge_vertr_detecties >= MIN_HOGE_VERTROUWEN_DETECTIES:
                            # NIEUW: Verhoog de melding teller
                            melding_teller += 1
                            
                            # NIEUW: Bepaal of geluid moet afspelen (elke 5e melding)
                            speel_geluid = (melding_teller % GELUID_ELKE_N_MELDINGEN == 0)
                            
                            for rang, idx in enumerate(geselecteerde_indices):
                                vertr, img, ts, origineel_pad, resultaten_obj = gebeurtenis_detecties[idx]
                                
                                # Voor zeer korte gebeurtenissen (met 1-2 frames), gebruik eenvoudigere labels
                                if len(geselecteerde_indices) <= 2:
                                    stadium = "Beste opname" if idx == max_idx else "Extra opname"
                                else:
                                    # Bepaal stadium (voor piek, piek, na piek)
                                    stadium = "Voor piek" if idx < max_idx else "Piek" if idx == max_idx else "Na piek"
                                
                                # Bepaal welk pad te gebruiken gebaseerd op configuratie
                                if VERSTUUR_GEANNOTEERDE_AFBEELDINGEN:
                                    # We moeten de geannoteerde versie opslaan voor versturen
                                    geannoteerd_opslag_pad = os.path.join(opslag_map, f"dekking_gedetecteerd_{ts}_vertr{vertr:.2f}_geannoteerd.jpg")
                                    
                                    # Als de geannoteerde afbeelding al gemaakt is (via live weergave), gebruik het
                                    if img is not None:
                                        # Sla de afbeelding op die al in het geheugen staat
                                        cv2.imwrite(geannoteerd_opslag_pad, img)
                                        verstuur_pad = geannoteerd_opslag_pad
                                    # Anders, als we een resultaat object hebben, maak een nieuwe annotatie
                                    elif resultaten_obj is not None:
                                        # Laad het originele frame
                                        orig_frame = cv2.imread(origineel_pad)
                                        if orig_frame is not None:
                                            # Maak een nieuwe annotatie met het resultaat object
                                            geannoteerd_frame = resultaten_obj.plot()
                                            # Sla de geannoteerde versie op
                                            cv2.imwrite(geannoteerd_opslag_pad, geannoteerd_frame)
                                            verstuur_pad = geannoteerd_opslag_pad
                                        else:
                                            # Fallback als het originele frame niet kan worden geladen
                                            print(f"Kon origineel frame niet laden voor {origineel_pad}, verstuur origineel")
                                            verstuur_pad = origineel_pad
                                    else:
                                        # Fallback als we geen geannoteerde versie kunnen maken
                                        print(f"Geen resultaat object beschikbaar voor {ts}, verstuur origineel")
                                        verstuur_pad = origineel_pad
                                else:
                                    # Gebruik het originele pad zonder annotaties
                                    verstuur_pad = origineel_pad
                                
                                # NIEUW: Bericht voor Telegram met geluid indicator
                                geluid_indicator = "🔊" if speel_geluid else "🔇"
                                bericht = f"{geluid_indicator} Dekking gedetecteerd ({ts}) - Vertrouwen: {vertr:.2f}\n"
                                bericht += f"Stadium: {stadium} - Rang {rang+1}/{len(geselecteerde_indices)}\n"
                                bericht += f"Gebeurtenis duur: {verzamel_duur:.1f}s\n"
                                bericht += f"Waarschuwing #{melding_teller} (Geluid: {'AAN' if speel_geluid else 'UIT'})"
                                
                                # NIEUW: Verstuur naar Telegram (geluid uit behalve voor elke 5e melding)
                                response = verstuur_telegram_foto(verstuur_pad, bericht, schakel_notificatie_uit=not speel_geluid)
                                if response:
                                    geluid_status = "MET geluid" if speel_geluid else "zonder geluid"
                                    print(f"Telegram bericht verstuurd voor {stadium}: {vertr:.2f} "
                                          f"({'met' if VERSTUUR_GEANNOTEERDE_AFBEELDINGEN and verstuur_pad != origineel_pad else 'zonder'} begrenzingsboxen) - {geluid_status}")
                                else:
                                    print(f"Telegram bericht versturen gefaald voor {stadium}")
                            
                            # Stel laatste detectie tijd in voor cooldown
                            laatste_detectie_tijd = huidige_tijd
                            print(f"Cooldown periode van {cooldown_periode} seconden gestart")
                            # NIEUW: Log geluid status
                            if speel_geluid:
                                print(f"🔊 GELUIDSMELDING #{melding_teller} verstuurd!")
                            else:
                                print(f"🔇 Stille melding #{melding_teller} verstuurd (geluid elke {GELUID_ELKE_N_MELDINGEN})")
                        else:
                            # GEWIJZIGD: Geef duidelijke reden waarom geen melding werd verstuurd
                            if max_vertr < MELDING_DREMPELWAARDE:
                                print(f"Hoogste vertrouwen ({max_vertr:.2f}) lager dan MELDING_DREMPELWAARDE ({MELDING_DREMPELWAARDE}). Geen melding verstuurd.")
                            elif hoge_vertr_detecties < MIN_HOGE_VERTROUWEN_DETECTIES:
                                print(f"Te weinig hoge vertrouwen detecties ({hoge_vertr_detecties}/{MIN_HOGE_VERTROUWEN_DETECTIES}). Geen melding verstuurd.")
                    
                    # Reset verzamel status
                    verzamel_screenshots = False
                    piek_gedetecteerd = False
                    inactiviteit_periode = 0
                    
                    # Log reden voor stoppen verzameling
                    if inactiviteit_periode >= INACTIVITEIT_STOP_TIJD:
                        print(f"Verzameling gestopt vanwege inactiviteit ({inactiviteit_periode:.1f}s zonder detecties)")
                    elif hoogste_vertr >= 0.85 and verzamel_duur >= 1:
                        print(f"Verzameling gestopt vanwege zeer hoge vertrouwen detectie ({hoogste_vertr:.2f})")
                    elif piek_gedetecteerd and verzamel_duur >= MIN_VERZAMEL_TIJD:
                        print(f"Verzameling gestopt na piek detectie en minimale verzamel tijd ({verzamel_duur:.1f}s)")
                    else:
                        print(f"Verzameling gestopt na maximale verzamel tijd ({verzamel_duur:.1f}s)")
            
            # Toon het frame met detecties alleen als TOON_LIVE_FEED is ingeschakeld
            if TOON_LIVE_FEED and len(results) > 0:  # Controleer of er resultaten zijn
                geannoteerd_frame = results[0].plot()
                cv2.imshow("Cowcatcher Detectie", geannoteerd_frame)
        
        # Toetsdruk om te stoppen (q), maar controleer alleen als het venster open is
        if TOON_LIVE_FEED and (cv2.waitKey(1) & 0xFF == ord('q')):
            print("Gebruiker drukte 'q'. Script wordt gestopt.")
            break

except KeyboardInterrupt:
    print("Script gestopt door gebruiker (Ctrl+C)")
    stop_reden = "Script handmatig gestopt door gebruiker (Ctrl+C)"
except Exception as e:
    print(f"Onverwachte fout: {str(e)}")
    stop_reden = f"Script gestopt vanwege fout: {str(e)}"
    
finally:
    # Opruimen
    cap.release()
    if TOON_LIVE_FEED:
        cv2.destroyAllWindows()
    print("Camera stream gesloten en bronnen vrijgegeven")
    print(f"Totaal verwerkte frames: {frame_teller}")
    
    # Verstuur een bericht dat het script is gestopt
    stop_tijd = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if 'stop_reden' not in locals():
        stop_reden = "Script gestopt (reden onbekend)"
    
    stop_bericht = f"⚠️ WAARSCHUWING: Cowcatcher detectie script gestopt op {stop_tijd}\n"
    stop_bericht += f"Reden: {stop_reden}\n"
    stop_bericht += f"Totaal verwerkte frames: {frame_teller}\n"
    stop_bericht += f"Totaal verstuurde meldingen: {melding_teller}"  # NIEUW: Toon totaal aantal meldingen
    
    verstuur_telegram_bericht(stop_bericht)
    print(f"Stop bericht verstuurd naar Telegram")
