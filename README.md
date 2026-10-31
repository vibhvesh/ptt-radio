# 📻 PTT Radio

Static push-to-talk walkie-talkie in one `index.html`, hosted on GitHub Pages. No backend: browsers talk through a free public MQTT-over-WebSocket broker (shiftr.io public, with EMQX/HiveMQ/Mosquitto as fallbacks) using mqtt.js from a CDN.

- Open the page to see who's online in the channel right now (even before joining). Use `?ch=name` to preselect a channel.
- Type a name or phone number and join. Hold the big button, or Spacebar, to talk. Only one person talks at a time.
- Presence: retained heartbeat every 5s, expires after 15s, last-will clears it on disconnect.
- Floor: claim message; races go to the earliest timestamp, then the lower name+id; auto-release after 2.5s of silence from the talker.
- Audio: 12 kHz 16-bit mono PCM chunks as binary MQTT payloads.

⚠️ Public broker: no privacy (anyone who knows the topic can listen), no uptime guarantee, rate limits possible.
