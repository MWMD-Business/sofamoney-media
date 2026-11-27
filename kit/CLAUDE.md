# Sofa Money Video Kit: instructions for Claude Code

This folder makes short vertical videos (Instagram Reels / TikToks, 1080x1920, 30 fps) for **Sofa Money**
(@sofamoney.app), an app that scans the stuff in your home and shows what it could be worth.
Every video is real 3D: a three.js scene in `scenes/<name>/index.html`, rendered frame by frame in headless
Chromium, with music, sound effects and a narrator voice all made in Python. No stock footage and no samples.

The owner is **Mohammed** (founder, based in Navan, Ireland). He is not a programmer.
- Talk to him in **simple, plain words**, with respect and a light joke now and then. No jargon.
- **He loves pop-up questions.** Before building anything, ask him with the AskUserQuestion tool:
  the idea (offer 3-4 concrete options), the hook, the look, the sound, voice or text only, the length.
  Give real options with short descriptions and put your recommendation first.
- **Ask plenty of pop-up questions, and keep every message short** (no extra words). Mohammed asked for this (26 Nov).
- Show him progress early (a few test frames) so he can steer before the long render.
- He posts the videos himself. Never try to post anything.

---

## 1. First-time setup (Windows PC)

Do this once. Check what's already installed first and skip those steps.
Commands work in Git Bash or PowerShell. Run them from this kit folder.

1. **Programs** (each takes a minute; Windows may ask Mohammed to click Yes):
   ```
   winget install -e --id OpenJS.NodeJS.LTS
   winget install -e --id Python.Python.3.12
   winget install -e --id Gyan.FFmpeg
   ```
   Python must be **3.10-3.12** (the voice package can't install on 3.13).
   After installing, `node`, `ffmpeg` or `py` may not be found until the terminal is reopened.
   If so, ask Mohammed to close and reopen Claude Code in this folder, then carry on.
2. **Node packages + browser** (three.js, fonts, Playwright's Chromium):
   ```
   npm install
   npx playwright install chromium
   ```
3. **Python packages** (voice, speech check, sound). Several minutes, about 1 GB, because it includes PyTorch:
   ```
   py -3.12 -m venv .venv
   .venv/Scripts/python -m pip install --upgrade pip
   .venv/Scripts/python -m pip install -r requirements.txt
   ```
4. **Check everything:**
   ```
   .venv/Scripts/python tools/check_setup.py
   ```
   It should end with `ALL GOOD` and make `out/_setup_test_2.00.jpg`, a cosy living room. Look at that picture.
5. The first voice run downloads the Kokoro voice model, about 330 MB. The first speech check downloads the
   Whisper `small.en` model, a few hundred MB. After that, both work offline.

On Mac/Linux, use `.venv/bin/python` wherever this file says `.venv/Scripts/python`.

---

## 2. How a video is made

```
scenes/<name>/index.html   three.js scene + HTML text overlays. Exposes window.renderAt(t) and window.ready
        |  node tools/render.js            -> test pictures, then the silent video (out/<name>_video.mp4)
scenes/<name>/lines.json   narrator lines
        |  tools/tts.py                    -> scenes/<name>/vo/*.wav
scenes/<name>/audio.py     music + effects + sound pack + voice, timed to the picture
        |                                  -> out/<name>_audio_raw.wav
tools/finish.py            levels the sound to -14 LUFS and joins it to the video -> out/<Name>-FINAL.mp4
tools/check_voice.py       speech recognition: every narrator line must be heard
tools/frames.py            contact sheet of the finished video, to look at with the Read tool
```

### Commands (example: the Hidden Room reel)
```
node tools/render.js scenes/hidden-room shots 0.5,3,6,9,12 out/hr                    # test pictures
node tools/render.js scenes/hidden-room video 0 14.3 out/hidden-room_video.mp4        # full silent render
.venv/Scripts/python tools/tts.py scenes/hidden-room/lines.json scenes/hidden-room/vo # voice lines
.venv/Scripts/python scenes/hidden-room/audio.py                                      # the soundtrack
.venv/Scripts/python tools/finish.py out/hidden-room_video.mp4 out/hidden-room_audio_raw.wav out/Hidden-Room-FINAL.mp4
.venv/Scripts/python tools/check_voice.py out/Hidden-Room-FINAL_audio.wav "There's twelve hundred and forty euro hidden in this room." "Look again." "It's not hidden. It's your stuff." "Sofa Money finds it. Link in bio."
.venv/Scripts/python tools/frames.py out/Hidden-Room-FINAL.mp4 0.5,3,5,7,9,11,13 out/check.jpg
ffmpeg -y -ss 0.5 -i out/Hidden-Room-FINAL.mp4 -frames:v 1 -q:v 2 out/Hidden-Room-cover.jpg   # cover
```
A scene with options takes them after `?`, e.g. `node tools/render.js "scenes/how-it-works?p=sm" video 0 18.6 out/hiw_video.mp4`.

**Rendering is slow** (software WebGL, roughly 1-3 s per frame, so a 15 s video takes about 8-25 minutes).
Always check test pictures of the busiest moments first and aim for **one** full render.
If only one part is wrong, re-render just that time range and join the pieces with ffmpeg's concat filter
(re-encode at the same settings). Tell Mohammed how long it will take before a full render.

### The scene contract (what every index.html must do)
- 1080x1920 page, three.js 0.160 from `/node_modules/three/build/three.module.js` (importmap), fonts by
  `@font-face` from `/node_modules/@fontsource/...` (Inter, Space Grotesk, Anton, Chakra Petch, JetBrains Mono).
  Paths starting with `/` are served from the kit folder; other paths are relative to the scene folder.
- `window.renderAt(t)` draws the exact frame for time `t` (seconds) **from t alone**: no clocks, no
  `requestAnimationFrame` timing, no unseeded `Math.random()` (use a seeded generator). Same t = same picture.
- `window.ready = true` only after fonts, textures and models have loaded
  (`await document.fonts.load(...)` for every font used, then redraw any canvas textures).
- Post-processing used in the templates: EffectComposer -> RenderPass -> NaN-clamp pass -> UnrealBloom ->
  OutputPass -> a grade pass (vignette, grain, blur/desaturate for freeze frames).
- Text lives in HTML overlays above the canvas (sharp and easy to animate), driven by `renderAt(t)` too.
- Letterbox bars 130-140 px at top and bottom. Keep important text inside **x 60-1020, y 200-1500**,
  because Instagram's buttons and caption cover the bottom and right side.

### Templates in `scenes/` (copy the closest one to a new folder, never edit the originals)
| Folder | What it is | Length |
|---|---|---|
| `hidden-room/` | **Reel 46**, "There's €1,240 hidden in this room". Cosy realistic 3D living room at night, hook text in frame 0, sofa-cushion fake-out (€2.40 + TV remote), record scratch "NOT IT.", gold Sofa Money room scan with 6 price tags popping on the beat, punch line, end card, loops back to the start. **The best starting point.** | 14.3 s |
| `burglar/` | **"The Burglar"**: dark POV story at 02:14, torch light, attic, lightning scare, grandad's watch in a chest, the burglar scans it with Sofa Money. Text + sound only until the 2 narrator lines at the end. | 25.5 s |
| `how-it-works/` | **3D exploded-view breakdown** with narrator. `?p=sm` is Sofa Money (`sk`/`ml` are Safe Key / MWD LINE; their voice lines are in `lines_sk.json` / `lines_ml.json`, so make them with tts.py if ever needed). | 18.6 s (sm) |
| `_draft-clock/` | Unfinished draft (no sound): grandad's mantel clock knocked off a shelf in slow-mo lands on the sofa, freeze, red circle, phone scan overlay. Mohammed scrapped the idea as too weak, but the slow-mo fall and the phone-scan overlay code are useful. | 14 s |

---

## 3. Sofa Money Reel rules (from Mohammed, keep all of them)

**The formula** (from the Wants and Needs brand, which grew to about 685k followers with it; copy the
*idea*, never their videos):
1. **Scroll bait, 0-3 s:** a big, surprising moment in **frame 0** that has nothing to do with money at first.
   Big on-screen line in frame 0, sound from the first frame.
2. **Entertain:** the story beat, punch line or twist.
3. **The Sofa Money twist near the end:** the thing turns out to be worth money -> the Sofa Money scan
   (marked **Demo**, amount marked **Example**) -> "Link in bio" / @sofamoney.app.
- The current direction is **short animated stories**, 10-25 s (Reel 38's fake-out energy, told as a mini story
  like The Burglar or the Hidden Room). Cinematic: letterbox, flash cuts, a sound on every cut, a bright drop
  into the app, and a loop ending where it fits.

**Look:** realistic 3D, **never flat or cartoon**. "Higher quality" to Mohammed means a realistic 3D look and
bigger sound. Original art only: no logos, no brands, no real car/console/watch designs, no real people.
People are faceless silhouettes or a gloved hand.

**Voice:** Kokoro `am_fenrir` is the Sofa Money narrator, and `af_heart` is Mom. Write numbers in **words** in
lines.json ("twelve hundred and forty euro"), but show **digits** on screen (€1,240). Lines are short and punchy.
Never use the whispery `am_echo` (that's Project 307's voice).

**Music and sounds:** every Sofa Money reel has music: a tense bed under the hook, dead silence after the
punch line, then the drop into the app. All sound is **synthesised** (`tools/sfx.py` and code in audio.py),
with no samples or copied recordings, even for meme-style sounds. **Use his sound pack** where it fits
(`sounds/`, see section 6). He especially loves the **night vision** sound and the **walkie chirp** (Nextel style).
Keep music low under the narrator (duck it), and make sound effects end before a spoken line starts.

**Words:** say "mom", not "mam". No nickname ("Hamoudyi"). No 3:07 / 307 references on Sofa Money videos.

**Labels:** every amount says Example and app screens say Demo (e.g. "Example amounts · Demo app"). Any real
fact needs a reliable source, shown on screen and in the caption. Stories that only use Example amounts need
no source. When Mohammed posts, the **AI label is always on**.
**Never write "Made with AI" (or any AI text) in anything you make**: not in videos, end cards, Stories, covers or
captions. Mohammed asked for this (26 Nov). The only AI marking is Instagram's own AI label switch when he posts.

**Comments:** no comment-bait and no share-bait ("comment YES if..."). A real question in the pinned comment is fine.

**What works on the account (real numbers):**
- **Reel 38, the supercar fake-out** (POV: you reversed into a €3,000,000 supercar... it's a toy... from 1971...
  Sofa Money scan): the best by far, 2,629 views, 9.7 s average watch on a 13 s reel. **A huge fake-out hook in frame 0 is the thing to repeat.**
- Irish money rules most people don't know, with a deadline or a catch (Reel 35, gift cards: 1,360 views).
- Reel 19, the Cork vase: 1,432 views.
- **Flopped:** the "Eagle One" mission series (dialogue-heavy, 160 views; Mohammed disliked it and dropped
  Reels 41-45), slow text-heavy lists and ad-style posts. Shares and new followers are still the weak spot.

**Unused ideas** (from the idea bank; always invent the story fresh):
the teleport box (old thing goes in, money comes out on the phone) · cooking a "recipe for €200" from drawer
junk · tier list where the worst-ranked attic item is worth the most · moving-day near-miss · house clearance /
inheritance · found it in a skip · pawnshop near-miss · flea-market find · "WAIT! Don't bin it" (slow-mo box
into the bin, freeze, rewind, scan) · unwanted Christmas presents (late December; any stat must be sourced).

---

## 4. Making a new reel, step by step

1. **Ask Mohammed** (pop-ups): pick from 3-4 fresh story ideas, then the hook, look/mood, sound, voice, length.
2. **Write a beat sheet** with timings (e.g. 0-3.2 s hook, 3.2 s freeze + record scratch, ...). Keep it 10-25 s.
3. `scenes/<new-name>/`: copy the closest template and rebuild it for the new story. Keep the timing
   constants in one place at the top of index.html and use the same numbers in audio.py.
4. **Test pictures** of the busiest moments (`shots`), look at every one with the Read tool, fix, repeat.
   Send Mohammed a few good frames before the long render.
5. `lines.json` -> `tools/tts.py` -> check each line's length fits its slot.
6. `audio.py` -> `out/<name>_audio_raw.wav` (48 kHz stereo). Copy the structure of `scenes/hidden-room/audio.py`.
7. **One full render** -> `tools/finish.py` -> `out/<Name>-FINAL.mp4`.
8. **Checks** (all must pass, see the next section), then the cover and caption.
9. Tell Mohammed where the files are, in simple words: the video, the cover and the caption file to copy from.
   Remind him to turn on the AI label (Advanced settings) when he posts.

## 5. Checks before a video counts as done
- `tools/frames.py` sheet of 6-10 moments, looked at: nothing cut off, nothing under the letterbox bars or
  Instagram's buttons, no blown-out white glare, no z-fighting flicker, text in the right fonts (not serif).
- `tools/check_voice.py` on `out/<Name>-FINAL_audio.wav` with every narrator line: **all lines heard**.
  If one misses, reword the line (don't loosen the checker). It sometimes hears "Sofa Money" as
  "so for money", which is fine.
- Loudness **-14 LUFS**, true peak **-1 dB or lower** (finish.py prints it).
- Cover: a strong frame, text inside the **3:4 grid crop** (the middle 1080x1440, y 240-1680).
- Caption file in `captions/` like `captions/Caption-Reel-46-Hidden-Room.txt`: hook line, 2-4 short lines of
  story, a real question, "Scan your room with Sofa Money 👉 link in bio",
  "Demo app · Example amounts" (no AI text), 5-7 hashtags
  (#sofamoney #ireland ...), a pinned-comment question, and posting notes (AI label ON, cover file).

## 6. What's where
- `sounds/`: the **Sofa Money sound pack** (all synthesised, safe to use). `nightvision.wav` (night-vision
  switch-on; scan mode), `chirp.wav` (walkie chirp, Nextel style), `cash.wav` (cash register), `scanbeep.wav`,
  `whoosh.wav`, `pop.wav` (price tags popping), `levelup.wav`. The full pack had 21 sounds; the others
  (double chirp, radio squelch, target lock, HUD boot, sonar ping, pager, flash charge, dial-up, 8-bit boot,
  access granted/denied, laser, meme boom, record scratch, glitch, tape stop, parking beeps, crunch) were lost,
  so synthesise them in code when needed. Reel 46 made its record scratch by scratching its own music.
- `tools/sfx.py`: synthesised sound library (boom, braam, riser, heartbeat, strings, warm pad, rain, thunder,
  creak, steps, thud, click, blip, chime, shimmer, cash, scan hum, breath...) plus `Mix` with voice ducking.
- `brand/`: app icon and `brand.md` (colours, fonts, handles, wording).
- `captions/`: finished captions to copy the style from.
- `docs/reel-history.md`: every reel so far, what it was, how it did, and what Mohammed said about style.
  All finished reels are also on GitHub: github.com/MWMD-Business/sofamoney-media (branch `media`).
- `reference-videos/`: Mohammed can drop example videos here. Look at one with
  `tools/frames.py reference-videos/x.mp4 0.5,2,4,6,8,10 out/ref.jpg` and the Read tool.
- `out/`: everything you render (can be emptied any time).

## 7. Lessons learned (save yourself the pain)
- Canvas textures drawn before fonts finish loading come out in a serif font: redraw them after `document.fonts.load`.
- A point light right next to an object, or a strong spotlight on a cream surface, blows it out to white.
  Keep bloom threshold around 0.9 and check close-ups.
- Coplanar surfaces flicker (z-fighting): offset them by a few millimetres.
- SwiftShader is CPU only: keep shadow maps at 1024-2048, avoid millions of triangles, bloom at half size.
- Narrator lines can be misheard: "Safe Key. Tap..." was heard as "Safe keys". Fix with rewording
  ("It's called Safe Key."). End-card music once masked a word, so keep music low under the narrator.
- In Python sound code, make lengths with `int(round(d * SR))` to avoid off-by-one array errors.
- render.js writes to a temporary `.tmp.mp4` name and renames at the end, so a half render never looks finished.
- Python on Windows: open text files with `encoding='utf-8'` (lines contain €).
