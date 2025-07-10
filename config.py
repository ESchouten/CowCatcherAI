# Camera en Telegram Bot Configuratiebestand
# Vul hieronder je persoonlijke camera gegevens in
# RTSP URLs voor camera's
# Camera 1 - positie?
RTSP_URL_CAMERA1 = "rtsp://admin:JouwWachtwoord123@192.168.178.21:554/h264Preview_01_sub"
# Camera 2 - positie?
RTSP_URL_CAMERA2 = "rtsp://admin:JouwWachtwoord123@192.168.178.22:554/h264Preview_01_sub"
# Meer camera's toevoegen - kopieer en vul in rtsp://
# RTSP_URL_CAMERA3 = "rtsp://admin:JouwWachtwoord123@192.168.178.25:554/h264Preview_01_sub"
# RTSP_URL_CAMERA4 = "rtsp://admin:JouwWachtwoord123@192.168.178.26:554/h264Preview_01_sub"

# Telegram Bot Configuratie
TELEGRAM_BOT_TOKEN = "JOUW_BOT_TOKEN_HIER"  # Verkrijg van @BotFather op Telegram
TELEGRAM_CHAT_ID = ["PRIMAIRE_CHAT_ID", "SECUNDAIRE_CHAT_ID", "DERDE_CHAT_ID"]  # Voeg meerdere gebruikers toe - Verkrijg ID van @userinfobot

# Netwerk Configuratie Voorbeelden:
# Vergeet niet om RTSP streaming in te schakelen in camera software
# Lokaal netwerk: 192.168.178.x
# Poort 554 is standaard voor RTSP
# Voor dual lens camera's: verander kanaal nummer van 01→02 of 1→2 om tweede lens te benaderen
# Gebruik substream voor lagere bandbreedte/opname
# Gebruik mainstream voor hogere kwaliteit live weergave

# Veelvoorkomende RTSP endpoints voor verschillende camera merken:
# Reolink camera's: /h264Preview_01_sub (substream) of /h264Preview_01_main (mainstream)
# Dahua camera's: /cam/realmonitor?channel=1&subtype=0 (sub) of /cam/realmonitor?channel=1&subtype=1 (main)
# Hikvision camera's: /Streaming/Channels/101 (sub) of /Streaming/Channels/1 (main)
# Axis camera's: /axis-media/media.amp?videocodec=h264 of /mjpg/video.mjpg
# Foscam camera's: /videoMain of /videoSub
# TP-Link Tapo: /stream1 (main) of /stream2 (sub)
# Amcrest camera's: /cam/realmonitor?channel=1&subtype=0 (zelfde als Dahua)
# Uniview camera's: /unicast/c1/s0/live (main) of /unicast/c1/s2/live (sub)
# Annke camera's: /Streaming/Channels/101 (zelfde als Hikvision)
# Swann camera's: /h264Preview_01_sub of /cam/realmonitor?channel=1&subtype=0
# Lorex camera's: /h264Preview_01_sub (zelfde als Reolink)
# Zmodo camera's: /videostream.cgi?loginuse=admin&loginpas=WACHTWOORD
# D-Link camera's: /live1.sdp (main) of /live2.sdp (sub)
# Netgear Arlo: /live (vereist andere authenticatie)
# Eufy camera's: /flv?port=1935&app=bcs&stream=channel0_main.bcs
# Ring camera's: (propriëtair protocol, vereist Ring API)
# Wyze camera's: /live (vereist firmware modificatie voor RTSP)
