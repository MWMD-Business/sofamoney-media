# Sofa Money Video Kit: start here, Mohammed 👋

This folder has everything Claude Code needs to make new Sofa Money videos on your PC:
the 3D scenes from your best videos, your sound pack, the narrator voice, your brand, and all your rules
(what works, what flopped, Demo/Example labels, "mom" not "mam"...). Claude Code reads the rules by itself.

## The first time (about 30 minutes, mostly waiting)
1. **Download** `Sofa-Money-Video-Kit.zip` from the Google Drive folder.
2. **Right-click it -> Extract All... -> Extract.** Move the folder somewhere easy, like Documents.
3. **Open Claude Code in that folder.** Pick one of these:
   - **Claude desktop app:** open the **Code** tab, choose this folder.
   - **Terminal:** open the folder, click the address bar, type `cmd` and press Enter, then type `claude`
     and press Enter. (No Claude Code yet? In PowerShell run `irm https://claude.ai/install.ps1 | iex` first.)
4. **Paste this:**
   > Read CLAUDE.md and set up this PC for the video kit (first-time setup). Install whatever is missing,
   > then run the setup check and show me the test picture.

   Say yes when it asks to install things (Node.js, Python 3.12, ffmpeg). If it says something "isn't found"
   right after installing, close Claude Code, open it again in the same folder and say "carry on with the setup".

## Every time you want a new video
Open Claude Code in the folder and paste:
> Read CLAUDE.md. Make a new Sofa Money Reel. Ask me pop-up questions first about the idea, the hook,
> the look and the sound.

It will ask you questions, show you a few test pictures, then do the long render (about 10-25 minutes,
so keep the PC awake and plugged in). You get three things in the `out` folder:
the video (`...-FINAL.mp4`), the cover (`...-cover.jpg`) and the caption to copy.

**When you post:** use the cover, paste the caption, and turn on the **AI label** (Advanced settings).

## Good to know
- Want it to copy the style of a video? Put the video in the `reference-videos` folder and tell Claude Code.
- The 6 example videos are in the Drive folder **Example videos** (small preview copies). The full-quality
  versions are in our chat, and every reel ever made is also on GitHub: github.com/MWMD-Business/sofamoney-media
- Ideas that did best: big fake-out hooks (Reel 38, the supercar: 2,629 views). Ideas that flopped: long
  dialogue missions (Eagle One) and slow text lists.
- If anything breaks, just tell Claude Code what you saw. It can read the whole kit and fix it.
