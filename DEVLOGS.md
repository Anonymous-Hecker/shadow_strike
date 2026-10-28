# Shadow Strike - Devlogs

## Devlog #1: Enter the Dojo! 🥋 Introducing Shadow Strike
**Date:** [Insert Date]

Hey everyone! I’m super excited to officially unveil the project I've been pouring my heart into: **Shadow Strike**, a 2D arcade fighting game built entirely in Python using Pygame! 🎮

I wanted to create a fighting game that captures that classic arcade feel but adds modern RPG-lite progression. In Shadow Strike, you don't just pick a character; you level them up, unlock a sprawling Skill Tree, and train in a Dojo to master your combos. 

The game currently features **10 distinct fighters** (from the heavy-hitting Warlord and Berserker to the lightning-fast Shadowblade and Kage). Each character has their own stats, attack ranges, and a unique critical hit trait. 

I'm incredibly proud of the Dojo training mode. I didn't want just a static dummy, so I built a physics-based punching bag that swings like a real pendulum. If you hit it with a light jab, it sways slightly. If you nail it with an Ultra Hit, it goes flying! 

I'll be posting regular updates here as the game evolves. Next time, I’ll dive into how I built the combat system and the AI. Let the battles begin! 🔥

---

## Devlog #2: The Art of Combat: Combos, Skills, and Enemy AI
**Date:** [Insert Date]

Welcome back! Today I want to talk about the meat and potatoes of any fighting game: the combat. ⚔️

My goal was to make combat feel weighty and responsive. Every fighter operates on a strict state machine (`idle`, `walk`, `attack_light`, `block`, `hurt`, etc.). This means you can't jump if you're in the middle of a heavy attack animation, and you can't block if you're stunned. 

Recently, I implemented a new universal move: the **Sweep**. By pressing 'N', your character executes a low sweep that actually disarms the opponent and stuns them for 1.5 seconds. It adds a huge layer of strategy, especially against the AI!

Speaking of progression, I just wrapped up the **Skill Tree**. By winning fights, you earn coins and XP. You can spend these in the Skill Tree (which has 4 tiers: Novice, Adept, Master, and Shadow) to unlock devastating moves like Ground Slam, Counter Strike, and Shadow Step. 

Finally, I spent a lot of time tweaking the fighter facing logic. In early builds, characters faced the direction they were walking. It looked hilarious when you tried to back away from an enemy and your character just turned their back to them! Now, the game constantly calculates relative positions so you *always* face your opponent. 

---

## Devlog #3: Battling the "Ghost" Bug: The Nightmare of Sprite Transparency
**Date:** [Insert Date]

Game dev isn't all fun and combos. Sometimes, you spend days fighting a single, infuriating bug. For me, that was the "Ghost Bug." 👻

I’m using AI-generated sprite sheets for the characters. They look amazing, but unlike traditional pixel art, they don't have perfect, uniform background colors. The backgrounds have subtle gradients, shadows, and noise. 

Initially, I used Pygame's standard `set_colorkey()` to make the background transparent. Because the background wasn't uniform, it left an ugly, chunky border around the characters. So, I tried a threshold approach (removing anything darker than a certain shade). The result? Characters with dark armor (like the Warrior and Ninja) had their chests hollowed out! They looked like ghosts.

**The Fix:**
I had to get creative. I brought in `numpy` and `scipy.ndimage` and built a **connected-component flood-fill algorithm**. 
Instead of looking at the whole sheet, the game samples the exact four corners of every single animation frame. It finds pixels that match that background color, but *only* removes them if they physically connect to the edge of the frame. Because the character acts like a wall, their dark armor is protected from the flood-fill! 

It was a huge technical hurdle, but now all 10 characters look crisp and solid on screen. 💪

---

## Devlog #4: Polish, Particles, and the Road Ahead
**Date:** [Insert Date]

Shadow Strike is really coming together. With the core combat and sprites working, I’ve shifted focus to "juice"—the little things that make the game feel alive. ✨

I’ve added three new arenas: the Temple, Storm Castle, and Night Market. To make them feel dynamic, I built a custom particle system. Now, sparks fly from torches, heavy rain falls at the castle, and a soft red glow emanates from the market lanterns. 

I also completely overhauled the UI. The Main Menu now scales properly regardless of your resolution (Full Screen `F11` is fully supported!), and the Skill Tree features procedural icons with hover tooltips that properly respect Z-ordering (no more text hiding behind other buttons!).

Thanks for following the journey! Let me know what feature you're most excited about in the comments. 🎮

---

## Devlog #5: A Main Menu That Knows Who You Are
**Date:** September 2026

Small change, big feel. 🎭

Up until now, the main menu showed a rotating carousel of *all* the characters just to show off. Cool at first, but kind of impersonal. Today I changed it so the menu only shows **your** character — the one you've actually selected and are training with.

The fighter now stands on the right side of the screen, fully animated, cycling through their idle stance and attack poses. The subtle glow behind them uses their unique **aura colour** (red for the Warlord, cyan for the Shadow, blue for the Guardian, etc.), so the whole menu changes vibe depending on who you've picked. It feels like *your* game now, not a demo reel.

I also swapped out the bright orange volcanic background for something darker and more cinematic — a moody palace courtyard backdrop. The falling ember particles are now soft grey ash instead of bright orange fireballs, which stops the background from competing with the character and the UI for attention.

These kinds of "feel" changes are easy to overlook in development, but they're what transforms a prototype into something that actually *looks* like a real game when you first boot it up.

**Next up:** The info bar (coins/level) is currently drawing over the top of the character — going to fix the z-ordering so the fighter always stands in front of the HUD elements. ⚔️

---

## Devlog #6: Layers Matter — Z-Ordering and a Living Background
**Date:** September 2026

Two small fixes, one big difference. 🖼️

**Fix 1 — The character now stands IN FRONT of the info bar.**
This was a classic z-ordering mistake. The player info strip (name, level, coins) was being drawn *after* the character sprite, so it sliced right through the fighter's legs like a floating ribbon. The fix was simply reordering the draw calls: info bar first, then fighter on top. Now the character properly stands in the scene rather than being cut in half by the UI.

**Fix 2 — The background now breathes.**
The main menu background slowly crossfades between three different arenas — the Palace, the ancient Temple, and the volcanic crater. Each transition takes about a second of smooth alpha-blending. It keeps the menu from feeling static when you're sitting on it, and each backdrop has a completely different mood (moonlit stone → flickering torches → molten rock). The whole effect runs without any performance hit since it's just a surface alpha blend.

Neither of these is a headline feature, but they're exactly the kind of polish that makes players feel like they're playing a finished game rather than a work-in-progress.

**Next up:** The dialogue system — the main menu character is about to start talking to you. 💬

---

## Devlog #7: Say Hello to Your Fighter 💬
**Date:** October 2026

The main menu character can finally talk back!

Inspired by the text boxes in Google's Champion Island Games, I built a dialogue box from scratch: a dark rounded panel with a name tab in the fighter's aura colour, a **typewriter effect** that reveals text letter by letter, and a little **typewriter "tick" sound** generated procedurally (no audio files needed, same as the rest of the game's SFX). Click the box to skip the typing or advance, and a blinking "click for next" hint tells you when it's ready.

Every fighter has their own voice:
- **Warlord** is proud and strict. **Berserker** just wants to smash things.
- **Void Mage** and **Wraith** are satirical and mysterious. **Shadowblade** is cunning and foxy.
- **The Shadow** taunts you with your own stats. **Iron Monk** is calm and drops advice on what to unlock next.
- **Oni Blade** is disciplined (and a bit funny) and teaches combo tips.

Some lines come with 1-2 choices, and the fighter reacts to what you pick. Lines also pull in your live stats (level, wins, losses, coins).

The best part: when you reach the level to unlock the **next fighter of the same class**, your current fighter tells you — and trash-talks the other classes. 😄

While testing I also spotted that the glow behind the fighter was a hard solid bar. Additive blending ignores alpha in pygame, so I pre-multiplied the colour and it's a soft glow again.

**Next up:** deciding how to ship the game — browser or desktop app.

---

## Devlog #8: Shipping It — Shadow Strike Becomes a Real App 📦
**Date:** October 2026

A game nobody can run isn't much of a game, so this update is all about getting Shadow Strike into players' hands.

**Browser or desktop?** I looked at both. A browser version (Pygame compiled to WebAssembly) sounds great, but my game leans on `scipy` for the sprite background removal and generates all its music and sound effects with `numpy` at startup. Neither works well in the browser, and getting around that would have meant changing how the game itself works. So I went with **desktop builds for Windows and Linux**. The game stays exactly as it is, and it runs at full speed.

**How it works:**
- The game is bundled with PyInstaller into a folder with an `.exe`. Players unzip it and play, with no Python needed.
- Save files now live in a proper per-user folder (`%APPDATA%\ShadowStrike`) instead of next to the game, so progress survives updates and a read-only install folder.
- If the game ever crashes, it writes a `crash.log` there. A windowed app has no console, so this is how I'll debug player reports.
- A GitHub Actions workflow builds the Windows and Linux versions automatically whenever I push a version tag like `v1.0.0`, and attaches them to a GitHub Release.

**A lesson from testing:** my first build crashed on launch. I'd tried to shrink it by excluding parts of scipy that I thought I didn't use, but `scipy.ndimage` quietly depends on them. The crash log caught it immediately, which proved the logging was worth adding. I removed the exclusions and the build runs fine, at the cost of a bigger download.

**Next up:** custom 8-bit icons for the menu, Armory and Skill Tree. 🎨
