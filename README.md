# Boondockecho Virtual Radio

Browser push-to-talk radio with a ham-transceiver look: LCD channel display, S/VU meter (TX & RX), TX/RX LEDs, glowing PTT (green idle / red TX / amber BUSY), callsign chips, and a session replay log.

Live: https://vibhvesh.github.io/ptt-radio/ — single fixed channel `virtual`. Log on with your Name or Call Sign (ham callsigns like vu2abc are shown uppercased); last callsign is remembered.

- Transport: MQTT over WebSockets (shiftr.io public broker primary, fallbacks), topic prefix `ptt-radio-66ab9178/<channel>/`
- Presence heartbeats + last-will, floor control (one talker at a time), 16-bit PCM @ 12 kHz
- Session log: each transmission (yours and others') kept in memory as a WAV blob (last 50 / ~20 min), cleared when the tab closes
- Tests: `npm i && node test.js`
