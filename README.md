# Gem Quest

A treasure-trail board game for 1 to 6 players, passed around one phone or
tablet. Roll the die, hop along the trail, answer a question at **your own
level**, and collect coins 🪙 and gems 💎. When someone reaches the castle 🏰,
everyone else gets one last turn. Then the player with the most treasure wins.

One self-contained `index.html` with no build step and no internet needed. It
uses the device's own fonts, emoji and voice.

## Levels (picked separately for each player)

| Level | For | What the questions are like |
|---|---|---|
| 🐣 Little | ages 4–6 | counting pictures, adding small numbers, first letters, rhymes, opposites, colors, shapes, animals, nursery rhymes. Read aloud with 3 big answer buttons. |
| 🚀 Kid | ages 8–12 | times tables, division, 3-digit math, fractions, place value, word problems, spelling, synonyms, homophones, planets, the body, capitals, U.S. history, art and music |
| 🎓 Adult | grown-ups | percentages, algebra, primes, number patterns, vocabulary, hard spellings, idioms, chemistry and biology, world and state capitals, history, literature, painters, composers |

Every player plays at their own level for the same rewards, so a 5-year-old
and Grandpa can play fairly at the same table.

## Spaces

| Space | What happens |
|---|---|
| ➕ 🔤 🔬 🌍 ⭐ Math, Words, Science, World, Fun Facts | Answer a question in that subject. Right = 3 🪙 |
| 💎 Gem | A gem question in any subject. Right = 1 💎 |
| 🍀 Lucky clover | Free 2 🪙 |
| 🎁 Treasure chest | A surprise: a gem or 3 to 5 coins |
| 🌀 Whoosh | Zoom ahead 3 spaces |
| 🏰 Castle | First to arrive gets 2 💎 + 5 🪙, and everyone else gets one last turn. Anyone else who makes it gets 1 💎 |

A gem is worth 5 coins. A wrong answer just shows the right one. Little players
still get 1 🪙 for trying. Questions don't repeat within a game.

**Game length:** Short (28 spaces), Medium (40) or Long (52).

**Read aloud:** Little-level questions and their answers are read out
automatically. The 🔊 button on any question reads it again, and the 🔊 button
on the side turns the voice off. 🎵 turns sounds off. 🏠 saves the game, and
**Keep Playing** on the title screen picks it back up, even after closing the app.

## Put it on an Android phone (works offline)

1. In this repository: Settings → Pages → Deploy from a branch → `main` → `/ (root)`.
2. On the phone, open `https://tazardous.github.io/gems/` in Chrome while online.
3. Let it load once. Then use ⋮ → **Install app** (or **Add to Home screen**).

After that it opens like an app and runs with no internet.

## Updating

Edit the files, change `CACHE` in `sw.js` (for example `gq-v2`), then push. The
next time the phone opens the game online, it picks up the new version.

## Adding questions

Question banks are near the top of the script in `index.html`. `L_*` arrays
are Little, `K_*` are Kid and `A_*` are Adult. A bank entry is
`[question, right answer, wrong, wrong, wrong]`. Little entries have 2 wrong
answers and an optional picture: `{pic:'🐄'}`. Math questions are generated
fresh each time, so they never run out.

## Testing

`tests/run.py` uses headless Chromium. It generates 22,500 questions and checks
each one, including recomputing every generated math answer. Then it plays full
games with 1 to 6 players at mixed levels on every board length, checks that a
saved game resumes after a reload, and checks the layout on phone and tablet
sizes in both orientations. `tests/shots.py <folder>` saves screenshots.

```
pip install playwright
python -m playwright install chromium
python tests/run.py
```
