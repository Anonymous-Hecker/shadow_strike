# Shadow Strike 🥋

Shadow Strike is an action-packed 2D fighting game built entirely in Python using the Pygame library. It blends classic arcade fighting mechanics with modern progression systems, featuring a roster of 10 unique fighters, a skill tree, dynamic particle effects, and a physics-based training dojo.

## 🌟 Key Features

* **10 Unique Fighters**: Choose from a diverse roster including Warrior, Ninja, Rogue, Mage, Berserker, Shadow, Guardian, Monk, Phantom, and Samurai. Each character has distinct base stats (HP, Stamina, Speed, Strength, Defense), critical hit traits, and attack ranges.
* **Deep Combat System**:
  * **Attacks**: Light, Heavy, Air, Special, and Super attacks.
  * **Mechanics**: Blocking, dodging, and a newly implemented **Sweep** move (disarms and stuns the opponent).
  * **Combos**: String together attacks to build combo multipliers and deal devastating damage.
* **Skill Tree Progression**: 
  * Earn coins through battles and level up to unlock new moves across 4 tiers: Novice, Adept, Master, and Shadow.
  * Unlockable abilities include Dash Strike, Ground Slam, Counter Strike, Shadow Step, and Rage Form.
* **Physics-Based Dojo**: A dedicated training area featuring a swinging punching bag with real pendulum physics that reacts proportionally to your hit strength.
* **Dynamic Arenas**: Fight in beautifully rendered environments like the Temple, Storm Castle, and Night Market, brought to life with custom particle systems (rain, sparks, lanterns).
* **AI Opponents**: Test your skills against computer-controlled fighters in single-player mode.

## 🛠️ Technical Highlights & Challenges

Building Shadow Strike involved solving several complex technical challenges, especially regarding asset management and game loop architecture:

### 1. The Sprite Transparency Problem (The "Ghost" Bug)
**The Issue:** The game utilizes AI-generated character sprite sheets. These sheets often came with non-uniform, gradient, or textured backgrounds (rather than pure green-screen or black). Standard thresholding or `set_colorkey()` made characters look like ghosts (hollowed out) or left ugly colored borders.
**The Solution:** We implemented a custom **connected-component flood-fill algorithm using `scipy.ndimage`**. By sampling the exact corner pixels of each individual animation cell and finding connected regions, we surgically removed the background while perfectly preserving the character's interior pixels—even if the character wore dark armor that matched the background color. We also added per-character tolerance overrides to handle tricky sprites.

### 2. Combat Facing Logic
**The Issue:** Initially, characters would face the direction they were moving. This meant if you backed away from an enemy to dodge, your character would turn their back to the opponent, breaking the fighting game immersion.
**The Solution:** We decoupled movement direction from sprite facing direction. The combat loop now recalculates relative positions (`face_opponent()`) every frame, ensuring fighters always keep their eyes on their target, regardless of their movement vector.

### 3. State Machine Architecture
To handle the complex interplay of animations, hitboxes, and invincibility frames, every fighter operates on a robust state machine (`idle`, `walk`, `jump`, `attack_light`, `hurt`, `dead`, etc.). This ensures smooth transitions and prevents buggy behavior like attacking while stunned or jumping while dead.

## 🚀 How to Run

1. Ensure you have Python 3.10+ installed.
2. Install the required dependencies:
   ```bash
   pip install pygame numpy scipy opencv-python
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## 🎮 Controls

### Player 1
* **Movement**: `W`, `A`, `S`, `D`
* **Light Attack**: `Q`
* **Heavy Attack**: `E`
* **Special**: `Z`
* **Super**: `X`
* **Sweep**: `N`
* **Block**: `Shift`
* **Dash**: `F`

### Player 2 (Local Multiplayer)
* **Movement**: Arrow Keys
* **Light Attack**: `Numpad 1`
* **Heavy Attack**: `Numpad 2`
* **Special**: `Numpad 4`
* **Super**: `Numpad 5`
* **Sweep**: `Numpad 7`
* **Block**: `Right Shift`
* **Dash**: `Numpad 8`

*Note: Global controls like Fullscreen (`F11`) and Pause (`ESC`) are also available.*
