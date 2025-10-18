# 🎨 The Art Dealer Game

A fun, educational card-based pattern recognition game built with **Python** and **Pygame**.  
This project teaches logic, arithmetic, and pattern discovery through interactive gameplay designed for students from **K–8** levels.

---

## 📋 Overview

In **The Art Dealer Game**, the player acts as a “collector” trying to buy artworks (cards) that match the secret **pattern** known only to the dealer.

The player:
- Picks **exactly 4 cards** from a 3×4 grid.  
- Chooses a **pattern** they believe fits the dealer’s secret rule.  
- Submits their guess and receives feedback.  
- Learns through reasoning, elimination, and discovery.

The game supports multiple grade levels:
- **K–2** → Basic color and suit patterns  
- **3–5** → Arithmetic and prime-based logic patterns  
- **6–8** → Complex logic (color, arithmetic, and composite rules)

---

## 🧠 Gameplay Rules

1. Choose your **grade level** on the main menu.  
2. The game deals **12 random cards**.  
3. Select **exactly four** cards that you think fit the dealer’s secret rule.  
4. From the **“Select Pattern”** dropdown, pick the pattern you want to test.  
5. Press **EVALUATE** to check if your 4 cards fit that pattern.  
6. Press **SUBMIT GUESS** to see if your pattern matches the dealer’s secret rule.  
7. You get up to **3 guesses per round**. After that, the dealer’s pattern is revealed, and a new round starts.  
8. Use **RESTART** to shuffle a new set of cards, or **BACK** to return to the main menu.

---

## 🃏 Example Patterns

- all red  
- all black  
- all hearts  
- all queens  
- all face cards  
- all even values  
- all single-digit primes  
- sum to 9  
- sum to 21  
- ace and a black jack  
- all red face cards  
- all black aces  
- all multiples of 3  

---

## ⚙️ Requirements

- **Python 3.10+** (tested on 3.11–3.13)  
- **Pygame 2.6.1+**

---

## 📦 Installation

1. **Clone or download** this project:
   ```bash
   git clone https://github.com/<yourusername>/art-dealer-game.git
   cd art-dealer-game
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure your folder structure looks like this:
   ```
   art-dealer/
     main.py
     game_engine.py
     ui_manager.py
     requirements.txt
     assets/
       cards/
         ace_of_hearts.png
         2_of_spades.png
         ...
       balloons/
         balloons.png
       sounds/
         bg_music.mp3
         sfx_click.wav
         sfx_success.wav
   ```

---

## ▶️ Running the Game

```bash
python main.py
```

---

## 🎮 Controls

| Action | Description |
|--------|--------------|
| **Click on cards** | Select or deselect them (max 4) |
| **EVALUATE** | Checks if your selected 4 cards fit the chosen pattern |
| **SUBMIT GUESS** | Tests if your pattern matches the dealer’s rule |
| **RESTART** | Starts a new round with fresh cards |
| **BACK** | Returns to the level selection menu |
| **EXIT GAME** | Closes the game safely |

---

## 🧩 Educational Value

This project was designed for classroom learning and gamified math exploration.  
It helps students:
- Identify number and suit patterns  
- Practice arithmetic through card combinations  
- Build deductive reasoning  
- Engage in visual learning with interactive feedback  

---

## 🛠️ Developer Notes

- Built entirely using **Pygame** — no external frameworks required.  
- The dealer’s pattern is randomly chosen **at the start of each round**, ensuring replayability.  
- Patterns are dynamically filtered to ensure at least one possible valid solution exists on the board.  
- The game logic is cleanly modularized into:
  - `main.py` → Game loop and UI flow  
  - `ui_manager.py` → UI components and sound management  
  - `game_engine.py` → Game rules, patterns, and logic  

---

