# Gem Quest Adventure

A side-scrolling adventure for 1 to 6 players who take turns on one phone or
tablet. Each player picks a hero and their own age level. Everyone plays
Level 1, then everyone plays Level 2, and so on. Standings show after each
level and a podium at the end. A gem is worth 5 coins, and the most treasure
wins.

One self-contained `index.html` with no build step and no internet needed.
All the heroes, creatures, levels and music are original.

## The six levels (each one harder)

| # | Place | Collect | What makes it harder |
|---|---|---|---|
| 1 | Sunny Meadow | 🪙 coins | small gaps, low ledges |
| 2 | Whispering Woods | 🪙 coins | more and wider gaps, higher ledges |
| 3 | Canyon Hop | 🪙 coins | 3-wide gaps everywhere, tall stair-step ledges |
| 4 | Crystal Cave | 💎 gems | moving rafts across wide pools |
| 5 | Frosty Peaks | 💎 gems | slippery ice, faster rafts over 6-wide gaps |
| 6 | Octopus Cove | 💎 gems | small sea creatures (crabs, jellyfish, pufferfish), then the **Big Octopus** |

**The Big Octopus** has one blind eye, crossed out with an X. He bobs his
head up and down, sweeps a long tentacle along the sand, and lobs ink blobs.
Jump on his head when it comes down (the ledge next to him helps), and jump
over the tentacle. Beat him and he gives up, drops 5 gems, and lets you
through to the treasure chest.

**Small creatures:** jump on them and they float away. Bumping into them
from the side hurts.

**Wise Owl gates:** in every level, the Wise Owl's stone gates ask a question
at that player's own age level, in Math, Words, Science, World or Fun Facts.
A right answer wins 5 🪙 (or 1 💎 in gem levels). Either way, the gate opens
and you keep going.

## Age levels (picked per player)

| | 🐣 Little (4–6) | 🚀 Kid (8–12) | 🎓 Adult |
|---|---|---|---|
| Questions | read aloud, pictures, 3 big choices | times tables, spelling, science, capitals, history | algebra, vocabulary, chemistry, world capitals, literature |
| Hearts | none, so nothing to lose | 3 | 3 |
| Jumping | double jump, and hold JUMP to float down | double jump | single jump |
| Gaps | stepping stones in the plain gaps | | |
| Creatures and the Octopus | slower; Octopus needs 2 bounces | 3 bounces | faster; 4 bounces |

Falling in a gap brings you back to the last flag in a bubble. Out of hearts
means back to the flag, and you drop 3 coins (or 1 gem).

## Controls

| Action | Keyboard | Touch |
|---|---|---|
| Walk | ← → (or A D) | ◀ ▶ |
| Jump (press again in the air to double jump) | Space, Z or ↑ | JUMP |
| Pause (keep playing, start the level over, or save and quit) | P or Esc | II |
| Sound on/off | M | ♪ |

**Save and quit** from the pause menu (or just close the app between turns),
then tap **Keep Playing** on the title screen to continue with the next turn.

## Put it on an Android phone (works offline)

1. In this repository: Settings → Pages → Deploy from a branch → `main` → `/ (root)`.
2. On the phone, open `https://tazardous.github.io/gems/` in Chrome while online.
3. Let it load once. Then use ⋮ → **Install app** (or **Add to Home screen**).

If you installed the earlier board-game version, just open the app online
once and it updates itself.

## Updating

Edit the files, change `CACHE` in `sw.js` (for example `gq-v3`), then push.

## Making changes

- **Levels:** in `LEVELS`, near the top of the script. The fields are pits
  (`[x, width]`, or `[x, width, 'm']` for a pit with a moving raft),
  platforms (`[x0, x1, row]`), Owl gates, mushroom springs, flags, creatures
  (`[x, 'crab' | 'jelly' | 'puffer', lowest age level]`), and the boss arena.
  Coins and gems are placed automatically.
- **Age-level settings:** in `AGES`.
- **Questions:** the `L_*` (Little), `K_*` (Kid) and `A_*` (Adult) banks.
  A bank entry is `[question, right answer, wrong, wrong, wrong]`. Math
  questions are generated fresh each time.

## Testing

`tests/run.py` uses headless Chromium. It:

- checks 22,500 generated questions
- proves every coin and gem in every level can be reached with Adult jumping
- has a bot play all 6 levels at all 3 age levels (rafts and the Octopus fight included)
- tests the Octopus's attacks and defeat
- runs full 6-level adventures with 1, 3 and 6 players
- resumes a saved game
- checks screen sizes

`tests/shots.py <folder>` saves screenshots.

```
pip install playwright
python -m playwright install chromium
python tests/run.py
```
