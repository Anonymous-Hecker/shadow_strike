"""
Dialogue Data - Per-character main menu dialogue lines.

Each character has a list of message dicts:
    {"text": str}                                   - plain message
    {"text": str, "choices": [{"label", "response"}]} - message with 1-2 options

Dynamic tags resolved at runtime by DialogueBox:
    {level} {wins} {losses} {coins} {gamer_id} {matches_played}
    {next} {next_lv}  (only in unlock hints - filled by build_messages)

All text is plain ASCII so it renders in any font.

Game facts used for tips (keep in sync with the game!):
    Keys (P1): J light, K heavy, L special, U super, ; block,
               F dash strike, G counter, H ground slam, N sweep
    Skill tree: Novice L1 (Dash Strike, Sweep), Adept L3 (Counter Strike,
                Ground Slam), Master L5 (Special Move, Ultra Hit),
                Shadow L8 (Shadow Step, Rage Form)
"""

CHAR_DIALOGUES = {

    # -- WARLORD ---------------------------------------------------------------
    "warrior": [
        {"text": "Stand straight, {gamer_id}. A warrior's posture speaks before his sword does."},
        {"text": "Level {level}. Respectable... for a recruit."},
        {
            "text": "Tell me - do you train every day?",
            "choices": [
                {"label": "Yes, always.",  "response": "Good. Weakness is a choice. Do not make it."},
                {"label": "...Sometimes.", "response": "Sometimes is the language of the defeated. Visit the Dojo."},
            ],
        },
        {"text": "{wins} victories. Each one earned in blood. Do not squander that legacy."},
        {"text": "The enemy does not rest. Neither should you. Step into the arena."},
    ],

    # -- BERSERKER -------------------------------------------------------------
    "berserker": [
        {"text": "RAAAAH - oh. Sorry. Thought you were an enemy."},
        {"text": "Level {level}. Ready to go again? I am ALWAYS ready."},
        {
            "text": "Want some power advice?",
            "choices": [
                {"label": "Yes, please.", "response": "Hit H for Ground Slam. Nothing says hello like a crater."},
                {"label": "I'm good.",    "response": "Your loss. Literally. You have {losses} of those already."},
            ],
        },
        {"text": "{wins} wins! That is {wins} times somebody felt my rage through you. Glorious."},
        {"text": "Stop thinking. Start smashing. Works for me every time."},
    ],

    # -- SHADOWBLADE (rogue) ---------------------------------------------------
    "rogue": [
        {"text": "Oh, {gamer_id}? Interesting name. Very... confident."},
        {"text": "I heard you lost {losses} times. Don't worry, I'll pretend I didn't."},
        {
            "text": "What matters more - looking cool or winning?",
            "choices": [
                {"label": "Looking cool.", "response": "Ha! I like you. Learn the Sweep (N). Coolest move in the game."},
                {"label": "Winning.",      "response": "Smart. But between us? You can do both."},
            ],
        },
        {"text": "{coins} coins just sitting there. Saving them, or afraid to spend?"},
        {"text": "Strike first. Strike hard. Never give them a second chance. That's the whole secret."},
    ],

    # -- KAGE (ninja) ----------------------------------------------------------
    "ninja": [
        {"text": "You did not see me come in, did you? Good. That means I'm doing my job."},
        {"text": "{wins} wins, {losses} losses. The losses are more useful. Study them."},
        {
            "text": "Speed or precision?",
            "choices": [
                {"label": "Speed.",     "response": "Dash Strike (F). Close the gap, strike, vanish."},
                {"label": "Precision.", "response": "Counter Strike (G). Bait them in, punish them hard."},
            ],
        },
        {"text": "Level {level}. The Shadow tier of the Skill Tree opens at level 8. That is where I live."},
        {"text": "A good ninja wins before the fight begins. Remember that."},
    ],

    # -- VOID MAGE -------------------------------------------------------------
    "mage": [
        {"text": "Ah, another one who thinks punching things is a strategy. How quaint."},
        {"text": "Level {level}. By my calculations, you've made {losses} mathematically avoidable mistakes."},
        {
            "text": "Have you unlocked the Special Move (L) in the Skill Tree?",
            "choices": [
                {"label": "What's that?", "response": "Magic, dear. The thing I was born with and you must purchase."},
                {"label": "Of course.",   "response": "Oh? Then why are you still losing? ...Kidding. Mostly."},
            ],
        },
        {"text": "I'd offer to teach you, but the gap between our intellects would be demoralising."},
        {"text": "Still, you show promise. For a non-mage. Truly an achievement."},
    ],

    # -- WRAITH (phantom) ------------------------------------------------------
    "phantom": [
        {"text": "You can see me? Interesting. Most only notice when it is too late."},
        {"text": "I have watched your {matches_played} battles from the other side. You fight with your eyes, not instinct."},
        {
            "text": "Do you fear losing?",
            "choices": [
                {"label": "Never.",     "response": "Liar. But I admire the confidence. Block with ; and breathe."},
                {"label": "A little.",  "response": "Good. Fear keeps you sharp. Use it."},
            ],
        },
        {"text": "{coins} coins. The living cling to gold. I find it... amusing."},
        {"text": "We are all fighting something, {gamer_id}. The arena just makes it visible."},
    ],

    # -- IRONCLAD (guardian) ---------------------------------------------------
    "guardian": [
        {"text": "Welcome back, {gamer_id}. The dojo has been quiet without you."},
        {"text": "Level {level}. The Adept tier unlocks at level 3: Counter Strike and Ground Slam. Prioritise them."},
        {
            "text": "What would you like guidance on?",
            "choices": [
                {"label": "Defence.", "response": "Block with ; just before impact. A shield raised late is no shield."},
                {"label": "Offence.", "response": "Ground Slam (H) breaks stances. Learn it and thank me later."},
            ],
        },
        {"text": "{wins} victories show consistency. Stay the course."},
        {"text": "Before you go, check the Armory. A well-equipped warrior fights smarter."},
    ],

    # -- IRON MONK -------------------------------------------------------------
    "monk": [
        {"text": "Breathe. You rushed in the moment you arrived. That habit will cost you."},
        {"text": "Level {level}. The river does not hurry, yet it carves the stone."},
        {
            "text": "Are you patient in your fights?",
            "choices": [
                {"label": "I try to be.", "response": "Then learn Counter Strike (G). Patience, rewarded."},
                {"label": "Not really.",  "response": "The Sweep (N) will help. It buys you a moment to think."},
            ],
        },
        {"text": "Your {losses} losses are not failures. They are corrections."},
        {"text": "If you have {coins} coins to spare, the Armory has gifts for the patient."},
    ],

    # -- THE SHADOW ------------------------------------------------------------
    "shadow": [
        {"text": "...I know your stats, {gamer_id}. All of them."},
        {"text": "Level {level}. {wins} wins, {losses} losses. The void sees everything."},
        {
            "text": "Your record is... concerning. Shall I continue?",
            "choices": [
                {"label": "Go ahead.",       "response": "You hesitate before attacking. They read you like a book."},
                {"label": "I'd rather not.", "response": "Denial. That explains the {losses} losses."},
            ],
        },
        {"text": "{coins} coins. Spend them. The dead have no use for currency."},
        {"text": "I don't taunt out of cruelty. You need the push. Now go."},
    ],

    # -- ONI BLADE (samurai) ---------------------------------------------------
    "samurai": [
        {"text": "Discipline separates a warrior from a brawler. {wins} wins - which are you?"},
        {"text": "Combos, {gamer_id}. Mash J three times, then finish with K. Simple. Deadly."},
        {
            "text": "Which is your favourite move?",
            "choices": [
                {"label": "Light attack.", "response": "A fine start. Chain them, then cancel into Dash Strike (F)."},
                {"label": "Heavy attack.", "response": "Power over finesse. Classic. Open with Dash Strike, finish heavy."},
            ],
        },
        {"text": "Level {level}. At level 5 the Master tier opens: Special Move and Ultra Hit."},
        {"text": "One more thing. The Sweep (N) is criminally underused. Consider it. *bows*"},
    ],
}


# ---------------------------------------------------------------------------
# Unlock hints - shown when the player has reached the level to unlock the
# NEXT character of the same class. Each hero badmouths the rival classes.
# {next} / {next_lv} are filled in by build_messages().
# ---------------------------------------------------------------------------
UNLOCK_HINTS = {
    "warrior":   "{gamer_id}! You reached level {next_lv}. Unlock {next} - a true warrior. Forget those sneaky Rogues and chanting Mages. Good for nothing!",
    "rogue":     "Level {next_lv}, hmm? {next} is waiting for you. Skip the Warriors - all muscle, no brains. And the Mages? Just fancy fireworks.",
    "mage":      "Behold, level {next_lv}. Unlock {next}, the next of our order. Do NOT waste time with the Ninja or the Berserker. Good for nothing, both of them.",
    "guardian":  "You have reached level {next_lv}. {next} stands ready, our order's next. The Rogues and Berserkers? Reckless fools who forget to block.",
    "shadow":    "Level {next_lv}... {next} calls to you. Stay in the dark with us. The others are loud, bright and weak. Good for nothing.",
}

UNLOCK_HINT_KEY = {
    # character id -> key into UNLOCK_HINTS (per-class voice)
    "warrior": "warrior", "berserker": "warrior",
    "rogue": "rogue", "ninja": "rogue",
    "mage": "mage", "phantom": "mage",
    "guardian": "guardian", "monk": "guardian",
    "shadow": "shadow", "samurai": "shadow",
}


def _unlock_hint_message(char_id: str, level: int):
    """Return a hint message dict, or None if there is nothing to unlock."""
    try:
        from characters.character_data import get_character, get_characters_by_class
        me = get_character(char_id)
        mates = get_characters_by_class(me["class"])
    except Exception:
        return None

    my_lv = me.get("unlock_level", 1)
    # Next sibling in the same class that is now available but higher tier
    # than the one currently selected.
    candidates = [c for c in mates
                  if c["id"] != char_id
                  and c.get("unlock_level", 1) > my_lv
                  and c.get("unlock_level", 1) <= level]
    if not candidates:
        return None
    nxt = min(candidates, key=lambda c: c.get("unlock_level", 1))

    template = UNLOCK_HINTS.get(UNLOCK_HINT_KEY.get(char_id, char_id))
    if not template:
        return None
    text = (template.replace("{next}", nxt["name"].title())
                    .replace("{next_lv}", str(nxt.get("unlock_level", 1))))
    return {
        "text": text,
        "choices": [
            {"label": "I'll switch.",  "response": "Wise. Open Play and pick them in the character select."},
            {"label": "Maybe later.",  "response": "Hmph. Your choice. But the offer stands."},
        ],
    }


def get_dialogue(char_id: str) -> list:
    """Raw dialogue list for a character (fallback: warrior)."""
    return CHAR_DIALOGUES.get(char_id, CHAR_DIALOGUES["warrior"])


def build_messages(char_id: str, level: int) -> list:
    """Dialogue list with a level-aware unlock hint inserted as message #2."""
    msgs = list(get_dialogue(char_id))
    hint = _unlock_hint_message(char_id, level)
    if hint:
        msgs.insert(1, hint)
    return msgs
