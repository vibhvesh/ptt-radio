# PTT Radio protected baseline

Repository: vibhvesh/ptt-radio

Baseline inspected before catalogue work. Existing radio implementation is `radio.html` (the root `index.html` redirects to the maintained Boondock Echo Live page).

Protected behaviour:
- MQTT over WebSockets with existing broker fallback list
- Topic prefix `ptt-radio-66ab9178/<channel>/`
- Existing `virtual` channel default and channel query support in the maintained radio page
- Presence heartbeats and last-will
- Single-talker floor control
- 12 kHz, 16-bit PCM audio
- Existing session recording/replay and SSTV features

Rule: all new radio-directory/catalogue work belongs under `catalogue/` and `scripts/` plus its dedicated GitHub Actions workflow. Do not edit `radio.html`, root `index.html`, PTT protocol code, or existing audio controls as part of catalogue work.

The catalogue is discovery metadata only. It does not guarantee stream availability or grant rebroadcast rights.
