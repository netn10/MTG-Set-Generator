"""
MTG Set Design Skeleton Parser and Data Structure
Based on Mark Rosewater's set skeleton framework
"""


class SetSkeleton:
    def __init__(self):
        self.skeleton_data = {
            "white": {
                "common": {
                    "creatures": [
                        {"id": "CW01", "mana_value": 1, "description": "1 MV"},
                        {
                            "id": "CW02",
                            "mana_value": [1, 2],
                            "description": "1 or 2 MV (don't pick 2 for this and CW06)",
                        },
                        {"id": "CW03", "mana_value": 2, "description": "2 MV"},
                        {"id": "CW04", "mana_value": 2, "description": "2 MV"},
                        {"id": "CW05", "mana_value": 2, "description": "2 MV"},
                        {
                            "id": "CW06",
                            "mana_value": [2, 3],
                            "description": "2 or 3 MV",
                        },
                        {"id": "CW07", "mana_value": 3, "description": "3 MV"},
                        {"id": "CW08", "mana_value": 3, "description": "3 MV"},
                        {"id": "CW09", "mana_value": 4, "description": "4 MV"},
                        {"id": "CW10", "mana_value": 4, "description": "4 MV"},
                        {"id": "CW11", "mana_value": 5, "description": "5 MV"},
                        {
                            "id": "CW12",
                            "mana_value": [5, 6],
                            "description": "5 or 6 MV",
                        },
                    ],
                    "spells": [
                        {
                            "id": "CW13",
                            "type": "removal",
                            "description": "Small removal (usually damage to an attacker or blocker)",
                        },
                        {
                            "id": "CW14",
                            "type": "lockdown",
                            "description": "Can't attack or block (sometimes also stops activated abilities, usually an Aura)",
                        },
                        {
                            "id": "CW15",
                            "type": "removal",
                            "description": "Destroy large/tapped creature",
                        },
                        {
                            "id": "CW16",
                            "type": "combat_trick",
                            "description": "Combat trick (usually +2/+2 or smaller)",
                        },
                        {
                            "id": "CW17",
                            "type": "aura_equipment",
                            "description": "Positive Aura/Equipment",
                        },
                        {
                            "id": "CW18",
                            "type": "team_pump",
                            "description": "Go-wide team-pump effect",
                        },
                        {
                            "id": "CW19",
                            "type": "removal",
                            "description": "Destroy artifact/enchantment (oftentimes, it can destroy either)",
                        },
                    ],
                    "keywords": {
                        "defender": {
                            "count": [0, 1],
                            "note": "this isn't counted as a creature",
                        },
                        "first_strike": {
                            "count": [0, 1],
                            "note": "only on your turn or on attack",
                        },
                        "flash": {"count": [0, 1]},
                        "flying": {
                            "count": [2, 3],
                            "note": "try not to repeat stats, you want a mix of different powers",
                        },
                        "indestructible": {
                            "count": [0, 1],
                            "note": "only granted temporarily by a spell",
                        },
                        "lifelink": {"count": 1, "note": "power 3 or less"},
                        "vigilance": {"count": 2},
                        "ward": {"count": [0, 1], "note": "costs mana"},
                    },
                },
                "uncommon": {
                    "creatures": [
                        {"id": "UW01", "mana_value": 1, "description": "1 MV"},
                        {"id": "UW02", "mana_value": 2, "description": "2 MV"},
                        {
                            "id": "UW03",
                            "mana_value": [2, 3],
                            "description": "2 or 3 MV",
                        },
                        {"id": "UW04", "mana_value": 3, "description": "3 MV"},
                        {"id": "UW05", "mana_value": 4, "description": "4 MV"},
                        {"id": "UW06", "mana_value": 5, "description": "5 MV"},
                        {
                            "id": "UW07",
                            "mana_value": "any",
                            "description": "Any MV (no more than two creatures at uncommon should have the same MV)",
                        },
                        {
                            "id": "UW08",
                            "mana_value": "any",
                            "description": "Any MV (no more than two creatures at uncommon should have the same MV)",
                        },
                    ],
                    "spells": [
                        {
                            "id": "UW09",
                            "type": "removal",
                            "description": "Creature removal (usually very efficient)",
                        },
                        {
                            "id": "UW10",
                            "type": "non_creature",
                            "description": "Non-creature",
                        },
                        {
                            "id": "UW11",
                            "type": "non_creature",
                            "description": "Non-creature",
                        },
                        {
                            "id": "UW12",
                            "type": "non_creature",
                            "description": "Non-creature",
                        },
                        {
                            "id": "UW13",
                            "type": "non_creature",
                            "description": "Non-creature",
                        },
                    ],
                    "keywords": {
                        "defender": {
                            "count": [0, 1],
                            "note": "not counted as a creature",
                        },
                        "double_strike": {
                            "count": [0, 1],
                            "note": "if you use double strike, you often won't use first strike",
                        },
                        "first_strike": {"count": [0, 1]},
                        "flash": {"count": [0, 1]},
                        "flying": {
                            "count": 2,
                            "note": "fliers of different powers, one is usually larger, like an Angel",
                        },
                        "indestructible": {"count": [0, 1]},
                        "lifelink": {"count": 1},
                        "vigilance": {"count": [1, 2]},
                        "ward": {"count": [0, 1], "note": "costs mana"},
                    },
                    "spell_options": [
                        "An effect that exiles a permanent (or some subset) while it's on the battlefield",
                        "Making multiple creature tokens",
                        "Permanent team boosting (with enchantment or +1/+1 counters)",
                        "Life gain (often repeatable)",
                        "Interactions with Equipment and/or Vehicles",
                        "Enchantment with static rules-setting ability",
                        "An Aura or Equipment",
                    ],
                },
                "rare": [
                    {"id": "RW01", "mana_value": "any", "description": "Any MV"},
                    {"id": "RW02", "mana_value": "any", "description": "Any MV"},
                    {"id": "RW03", "mana_value": "any", "description": "Any MV"},
                    {"id": "RW04", "mana_value": "any", "description": "Any MV"},
                    {"id": "RW05", "mana_value": "any", "description": "Any MV"},
                    {"id": "RW06", "mana_value": "any", "description": "Any MV"},
                    {
                        "id": "RW07",
                        "type": "non_creature",
                        "description": "Non-Creature",
                    },
                    {
                        "id": "RW08",
                        "type": "non_creature",
                        "description": "Non-Creature",
                    },
                    {
                        "id": "RW09",
                        "type": "non_creature",
                        "description": "Non-Creature",
                    },
                    {
                        "id": "RW10",
                        "type": "non_creature",
                        "description": "Non-Creature",
                    },
                ],
                "mythic": [
                    {"id": "MW01", "description": "Anything"},
                    {"id": "MW02", "description": "Anything"},
                ],
            },
            "blue": {
                "common": {
                    "creatures": [
                        {"id": "CU01", "mana_value": 1, "description": "1 MV"},
                        {"id": "CU02", "mana_value": 2, "description": "2 MV"},
                        {"id": "CU03", "mana_value": 2, "description": "2 MV"},
                        {"id": "CU04", "mana_value": 3, "description": "3 MV"},
                        {"id": "CU05", "mana_value": 3, "description": "3 MV"},
                        {"id": "CU06", "mana_value": 4, "description": "4 MV"},
                        {"id": "CU07", "mana_value": 4, "description": "4 MV"},
                        {"id": "CU08", "mana_value": 5, "description": "5 MV"},
                        {
                            "id": "CU09",
                            "mana_value": "6+",
                            "description": "6+ MV (this, or sometimes CU08, often has some attacking restriction)",
                        },
                        {
                            "id": "CU10",
                            "type": "special",
                            "description": "Either 0 power creature, creature with defender, or non-creature",
                        },
                    ],
                    "spells": [
                        {
                            "id": "CU11",
                            "type": "counterspell",
                            "description": "Counterspell that can counter anything (what R&D calls a 'hard counter')",
                        },
                        {
                            "id": "CU12",
                            "type": "counterspell",
                            "description": "Counterspell with some restriction (what R&D calls a 'soft counter')",
                        },
                        {"id": "CU13", "type": "aura", "description": "Lockdown Aura"},
                        {
                            "id": "CU14",
                            "type": "card_draw",
                            "description": "Card drawing (usually no more than three cards)",
                        },
                        {
                            "id": "CU15",
                            "type": "cantrip",
                            "description": "Cantrip/card filtering (aka drawing some number of cards and then discarding)",
                        },
                        {
                            "id": "CU16",
                            "type": "bounce",
                            "description": "Bounce spell (usually returning a creature or nonland permanent to top or bottom of library, owner's choice)",
                        },
                        {
                            "id": "CU17",
                            "type": "aura_trick",
                            "description": "Positive Aura or combat trick",
                        },
                        {
                            "id": "CU18",
                            "type": "disruption",
                            "description": "Disrupt opposing creatures (freezing, tapping, lowering power, etc.)",
                        },
                        {"id": "CU19", "type": "anything", "description": "Anything"},
                    ],
                    "keywords": {
                        "defender": {
                            "count": [0, 1],
                            "note": "this isn't counted as a creature",
                        },
                        "flash": {"count": 1},
                        "flying": {
                            "count": 3,
                            "note": "try not to repeat stats, you want a mix of different powers",
                        },
                        "hexproof": {
                            "count": [0, 1],
                            "note": "used sparingly, only on small creatures at common, no evasion",
                        },
                        "vigilance": {"count": [1, 2]},
                        "ward": {"count": [0, 1], "note": "costs mana"},
                    },
                    "notes": [
                        "Blue is more likely to have a greater number of creatures with tap abilities at common than other colors"
                    ],
                },
                "uncommon": {
                    "creatures": [
                        {"id": "UU01", "mana_value": [1, 2], "description": "1 or 2MV"},
                        {"id": "UU02", "mana_value": 2, "description": "2 MV"},
                        {"id": "UU03", "mana_value": 3, "description": "3 MV"},
                        {"id": "UU04", "mana_value": "any", "description": "Any MV"},
                        {"id": "UU05", "mana_value": 4, "description": "4 MV"},
                        {"id": "UU06", "mana_value": 5, "description": "5 MV"},
                        {
                            "id": "UU07",
                            "mana_value": "any",
                            "description": "Any MV (no MV should be on more than two uncommon creatures)",
                        },
                    ],
                    "spells": [
                        {"id": "UU08", "type": "card_draw", "description": "Card draw"},
                        {
                            "id": "UU09",
                            "type": "counterspell",
                            "description": "Counterspell",
                        },
                        {
                            "id": "UU10",
                            "type": "non_creature",
                            "description": "Non-creature",
                        },
                        {
                            "id": "UU11",
                            "type": "non_creature",
                            "description": "Non-creature",
                        },
                        {
                            "id": "UU12",
                            "type": "non_creature",
                            "description": "Non-creature",
                        },
                        {
                            "id": "UU13",
                            "type": "non_creature",
                            "description": "Non-creature",
                        },
                    ],
                    "keywords": {
                        "defender": {
                            "count": [0, 1],
                            "note": "this isn't counted as a creature",
                        },
                        "flash": {"count": [0, 1]},
                        "flying": {
                            "count": [2, 3],
                            "note": "try not to repeat stats, at least one is usually larger",
                        },
                        "hexproof": {
                            "count": [0, 1],
                            "note": "can appear on slightly larger creature at uncommon, sometimes conditional",
                        },
                        "vigilance": {"count": [1, 2]},
                        "ward": {"count": [0, 1], "note": "costs mana"},
                    },
                    "spell_options": [
                        "Card draw (either drawing more cards than at common or repeatable)",
                        "Creature stealing (usually with some limitations)",
                        "Milling effect (most often repeatable)",
                        "Bouncing multiple targets (returning things to their owner's hand)",
                        "Freezing multiple targets (tapping things that don't untap next turn)",
                        "Creature transformation",
                        "Tapping or untapping permanents (often repeatable)",
                        "An Aura or Equipment",
                        "Phasing out a creature or permanents",
                    ],
                },
                "rare": [
                    {"id": "RU01", "mana_value": "any", "description": "Any MV"},
                    {"id": "RU02", "mana_value": "any", "description": "Any MV"},
                    {"id": "RU03", "mana_value": "any", "description": "Any MV"},
                    {"id": "RU04", "mana_value": "any", "description": "Any MV"},
                    {"id": "RU05", "mana_value": "any", "description": "Any MV"},
                    {
                        "id": "RU06",
                        "type": "non_creature",
                        "description": "Non-Creature",
                    },
                    {
                        "id": "RU07",
                        "type": "non_creature",
                        "description": "Non-Creature",
                    },
                    {
                        "id": "RU08",
                        "type": "non_creature",
                        "description": "Non-Creature",
                    },
                    {
                        "id": "RU09",
                        "type": "non_creature",
                        "description": "Non-Creature",
                    },
                    {
                        "id": "RU10",
                        "type": "non_creature",
                        "description": "Non-Creature",
                    },
                ],
                "mythic": [
                    {"id": "MU01", "description": "Anything"},
                    {"id": "MU02", "description": "Anything"},
                ],
            },
        }

        # Continue with other colors...
        self._add_remaining_colors()
        self._add_multicolor_and_artifacts()

    def _add_remaining_colors(self):
        """Add black, red, and green color data"""
        # Black
        self.skeleton_data["black"] = {
            "common": {
                "creatures": [
                    {"id": "CB01", "mana_value": 1, "description": "1 MV"},
                    {"id": "CB02", "mana_value": 2, "description": "2 MV"},
                    {"id": "CB03", "mana_value": 2, "description": "2 MV"},
                    {"id": "CB04", "mana_value": [2, 3], "description": "2 or 3 MV"},
                    {"id": "CB05", "mana_value": 3, "description": "3 MV"},
                    {"id": "CB06", "mana_value": 3, "description": "3 MV"},
                    {"id": "CB07", "mana_value": 4, "description": "4 MV"},
                    {"id": "CB08", "mana_value": 4, "description": "4 MV"},
                    {"id": "CB09", "mana_value": 5, "description": "5 MV"},
                    {"id": "CB10", "mana_value": "6+", "description": "6+ MV"},
                ],
                "spells": [
                    {
                        "id": "CB11",
                        "type": "removal",
                        "description": "Removal spell, can kill anything",
                    },
                    {
                        "id": "CB12",
                        "type": "removal",
                        "description": "Removal spell, can kill small things",
                    },
                    {
                        "id": "CB13",
                        "type": "removal",
                        "description": "Removal spell, edict (forced sacrifice), or conditional",
                    },
                    {
                        "id": "CB14",
                        "type": "removal",
                        "description": "Removal spell, limitations, different from the others, usually weaker",
                    },
                    {
                        "id": "CB15",
                        "type": "card_draw",
                        "description": "Card draw (for some resource in addition to mana, usually life)",
                    },
                    {
                        "id": "CB16",
                        "type": "recursion",
                        "description": "Return creature card from graveyard to hand (one or two creatures)",
                    },
                    {
                        "id": "CB17",
                        "type": "discard",
                        "description": "Discard (one or two cards, if you choose what gets discarded, not land)",
                    },
                    {
                        "id": "CB18",
                        "type": "aura_trick",
                        "description": "Positive Aura or combat trick",
                    },
                    {"id": "CB19", "type": "anything", "description": "Anything"},
                ],
                "keywords": {
                    "deathtouch": {"count": 1},
                    "defender": {
                        "count": [0, 1],
                        "note": "this isn't counted as a creature",
                    },
                    "flash": {"count": 1, "note": "on a low toughness creature"},
                    "flying": {
                        "count": [1, 2],
                        "note": "at different powers, meant to be weaker in general than white or blue fliers",
                    },
                    "haste": {"count": [0, 1]},
                    "indestructible": {
                        "count": [0, 1],
                        "note": "only granted temporarily by an activation or spell",
                    },
                    "lifelink": {
                        "count": 1,
                        "note": "usually bigger than on white common",
                    },
                    "menace": {"count": [1, 2]},
                    "ward": {"count": [0, 1], "note": "paying life or discard a card"},
                },
            },
            "uncommon": {
                "creatures": [
                    {"id": "UB01", "mana_value": [1, 2], "description": "1 or 2MV"},
                    {"id": "UB02", "mana_value": 2, "description": "2 MV"},
                    {"id": "UB03", "mana_value": 3, "description": "3 MV"},
                    {"id": "UB04", "mana_value": 4, "description": "4 MV"},
                    {"id": "UB05", "mana_value": 5, "description": "5 MV"},
                    {
                        "id": "UB06",
                        "mana_value": "any",
                        "description": "Any MV (no more than two creatures at uncommon should have the same MV)",
                    },
                    {
                        "id": "UB07",
                        "mana_value": "any",
                        "description": "Any MV (no more than two creatures at uncommon should have the same MV)",
                    },
                ],
                "spells": [
                    {"id": "UB08", "type": "removal", "description": "Removal"},
                    {"id": "UB09", "type": "reanimation", "description": "Reanimation"},
                    {
                        "id": "UB10",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                    {
                        "id": "UB11",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                    {
                        "id": "UB12",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                    {
                        "id": "UB13",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                ],
            },
            "rare": [
                {"id": "RB01", "mana_value": "any", "description": "Any MV"},
                {"id": "RB02", "mana_value": "any", "description": "Any MV"},
                {"id": "RB03", "mana_value": "any", "description": "Any MV"},
                {"id": "RB04", "mana_value": "any", "description": "Any MV"},
                {"id": "RB05", "mana_value": "any", "description": "Any MV"},
                {"id": "RB06", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RB07", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RB08", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RB09", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RB10", "type": "non_creature", "description": "Non-Creature"},
            ],
            "mythic": [
                {"id": "MB01", "type": "planeswalker", "description": "Planeswalker"},
                {
                    "id": "MB02",
                    "type": "non_planeswalker",
                    "description": "Non-Planeswalker",
                },
            ],
        }

        # Red
        self.skeleton_data["red"] = {
            "common": {
                "creatures": [
                    {"id": "CR01", "mana_value": 1, "description": "1 MV"},
                    {"id": "CR02", "mana_value": 2, "description": "2 MV"},
                    {"id": "CR03", "mana_value": 2, "description": "2 MV"},
                    {"id": "CR04", "mana_value": 2, "description": "2 MV"},
                    {"id": "CR05", "mana_value": 3, "description": "3 MV"},
                    {"id": "CR06", "mana_value": 3, "description": "3 MV"},
                    {"id": "CR07", "mana_value": 4, "description": "4 MV"},
                    {"id": "CR08", "mana_value": 4, "description": "4 MV"},
                    {"id": "CR09", "mana_value": 5, "description": "5 MV"},
                    {"id": "CR10", "mana_value": "5+", "description": "5+ MV"},
                ],
                "spells": [
                    {
                        "id": "CR11",
                        "type": "damage",
                        "description": "Efficient direct-damage spell (usually one of this and CB12 is any target)",
                    },
                    {
                        "id": "CR12",
                        "type": "damage",
                        "description": "Other direct-damage spell",
                    },
                    {
                        "id": "CR13",
                        "type": "steal_damage",
                        "description": "Steal effect/inefficient direct damage",
                    },
                    {
                        "id": "CR14",
                        "type": "pump_destruction",
                        "description": "Team pump (power greater than toughness)/land destruction",
                    },
                    {
                        "id": "CR15",
                        "type": "cantrip",
                        "description": "Cantrip (draw a card rider)/card filtering (usually rummaging—discard and draw)",
                    },
                    {
                        "id": "CR16",
                        "type": "aura_equipment",
                        "description": "Positive Aura or Equipment",
                    },
                    {
                        "id": "CR17",
                        "type": "combat_trick",
                        "description": "Combat trick",
                    },
                    {
                        "id": "CR18",
                        "type": "misc",
                        "description": "Can't block/destroy artifact/direct damage to player",
                    },
                    {"id": "CR19", "type": "anything", "description": "Anything"},
                ],
                "keywords": {
                    "defender": {
                        "count": [0, 1],
                        "note": "this isn't counted as a creature",
                    },
                    "first_strike": {
                        "count": [0, 1],
                        "note": "only on your turn or on attack",
                    },
                    "haste": {"count": [1, 2]},
                    "menace": {"count": [1, 2]},
                    "reach": {"count": 1},
                    "trample": {"count": [1, 2]},
                    "ward": {"count": [0, 1], "note": "paying life or discard a card"},
                },
            },
            "uncommon": {
                "creatures": [
                    {"id": "UR01", "mana_value": [1, 2], "description": "1 or 2MV"},
                    {"id": "UR02", "mana_value": 2, "description": "2 MV"},
                    {"id": "UR03", "mana_value": "any", "description": "Any MV"},
                    {"id": "UR04", "mana_value": 3, "description": "3 MV"},
                    {"id": "UR05", "mana_value": 4, "description": "4MV"},
                    {"id": "UR06", "mana_value": "5+", "description": "5+ MV"},
                    {
                        "id": "UR07",
                        "mana_value": "any",
                        "description": "Any MV (no more than two creatures at uncommon should have the same MV)",
                    },
                ],
                "spells": [
                    {
                        "id": "UR08",
                        "type": "damage",
                        "description": "Direct damage (most often any target)",
                    },
                    {
                        "id": "UR09",
                        "type": "sweeper",
                        "description": "Small sweeper/multi-target direct damage",
                    },
                    {
                        "id": "UR10",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                    {
                        "id": "UR11",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                    {
                        "id": "UR12",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                    {
                        "id": "UR13",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                ],
            },
            "rare": [
                {"id": "RR01", "mana_value": "any", "description": "Any MV"},
                {"id": "RR02", "mana_value": "any", "description": "Any MV"},
                {"id": "RR03", "mana_value": "any", "description": "Any MV"},
                {"id": "RR04", "mana_value": "any", "description": "Any MV"},
                {"id": "RR05", "mana_value": "any", "description": "Any MV"},
                {"id": "RR06", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RR07", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RR08", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RR09", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RR10", "type": "non_creature", "description": "Non-Creature"},
            ],
            "mythic": [
                {"id": "MR01", "type": "planeswalker", "description": "Planeswalker"},
                {
                    "id": "MR02",
                    "type": "non_planeswalker",
                    "description": "Non-Planeswalker",
                },
            ],
        }

        # Green
        self.skeleton_data["green"] = {
            "common": {
                "creatures": [
                    {"id": "CG01", "mana_value": 1, "description": "1 MV"},
                    {"id": "CG02", "mana_value": 2, "description": "2 MV"},
                    {"id": "CG03", "mana_value": 2, "description": "2 MV"},
                    {"id": "CG04", "mana_value": 3, "description": "3 MV"},
                    {"id": "CG05", "mana_value": 3, "description": "3 MV"},
                    {"id": "CG06", "mana_value": [3, 4], "description": "3 OR 4 MV"},
                    {"id": "CG07", "mana_value": 4, "description": "4 MV"},
                    {"id": "CG08", "mana_value": 4, "description": "4 MV"},
                    {"id": "CG09", "mana_value": 5, "description": "5 MV"},
                    {"id": "CG10", "mana_value": [5, 6], "description": "5 OR 6 MV"},
                    {"id": "CG11", "mana_value": "6+", "description": "6+ MV"},
                ],
                "spells": [
                    {
                        "id": "CG12",
                        "type": "fight",
                        "description": "Fight or bite (dealing damage equal to power)",
                    },
                    {
                        "id": "CG13",
                        "type": "pump",
                        "description": "Power/toughness pumping (usually on an instant)",
                    },
                    {
                        "id": "CG14",
                        "type": "fight_trick",
                        "description": "Another combat trick / fight or bite (slightly less effective compared to CG12)",
                    },
                    {
                        "id": "CG15",
                        "type": "cantrip",
                        "description": "Cantrip/card filtering",
                    },
                    {
                        "id": "CG16",
                        "type": "aura_equipment",
                        "description": "Positive Aura or Equipment",
                    },
                    {"id": "CG17", "type": "anti_flying", "description": "Anti-flying"},
                    {
                        "id": "CG18",
                        "type": "ramp",
                        "description": "Mana ramp (usually fetching land, but sometimes an Aura)",
                    },
                    {
                        "id": "CG19",
                        "type": "removal",
                        "description": "Artifact or enchantment destruction",
                    },
                ],
                "keywords": {
                    "deathtouch": {"count": 1, "note": "usually on a smaller creature"},
                    "defender": {
                        "count": [0, 1],
                        "note": "this isn't counted as a creature",
                    },
                    "flash": {
                        "count": [0, 1],
                        "note": "usually on a creature with power 3 or higher",
                    },
                    "haste": {"count": [0, 1], "note": "usually on a larger creature"},
                    "hexproof": {
                        "count": [0, 1],
                        "note": "usually on a small or medium creature without evasion",
                    },
                    "reach": {"count": [1, 2]},
                    "trample": {"count": [1, 2]},
                    "vigilance": {"count": [1, 2]},
                    "ward": {
                        "count": [0, 1],
                        "note": "costs mana, green is the color most likely to have ward at common",
                    },
                },
            },
            "uncommon": {
                "creatures": [
                    {"id": "UG01", "mana_value": [1, 2], "description": "1 or 2MV"},
                    {"id": "UG02", "mana_value": 2, "description": "2 MV"},
                    {"id": "UG03", "mana_value": 3, "description": "3 MV"},
                    {"id": "UG04", "mana_value": 4, "description": "4 MV"},
                    {"id": "UG05", "mana_value": 5, "description": "5 MV"},
                    {"id": "UG06", "mana_value": "6+", "description": "6+ MV"},
                    {
                        "id": "UG07",
                        "mana_value": "any",
                        "description": "Any MV (no more than two creatures at uncommon should have the same MV)",
                    },
                    {
                        "id": "UG08",
                        "mana_value": "any",
                        "description": "Any MV (no more than two creatures at uncommon should have the same MV)",
                    },
                ],
                "spells": [
                    {
                        "id": "UG09",
                        "type": "ramp",
                        "description": "Mana ramp (usually creating more mana than mana-ramp commons)",
                    },
                    {
                        "id": "UG10",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                    {
                        "id": "UG11",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                    {
                        "id": "UG12",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                    {
                        "id": "UG13",
                        "type": "non_creature",
                        "description": "Non-creature",
                    },
                ],
            },
            "rare": [
                {"id": "RG01", "mana_value": "any", "description": "Any MV"},
                {"id": "RG02", "mana_value": "any", "description": "Any MV"},
                {"id": "RG03", "mana_value": "any", "description": "Any MV"},
                {"id": "RG04", "mana_value": "any", "description": "Any MV"},
                {"id": "RG05", "mana_value": "any", "description": "Any MV"},
                {"id": "RG06", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RG07", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RG08", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RG09", "type": "non_creature", "description": "Non-Creature"},
                {"id": "RG10", "type": "non_creature", "description": "Non-Creature"},
            ],
            "mythic": [
                {"id": "MG01", "description": "Anything"},
                {"id": "MG02", "description": "Anything"},
            ],
        }

    def _add_multicolor_and_artifacts(self):
        """Add multicolor and artifact data"""
        self.skeleton_data["multicolor"] = {
            "uncommon_signposts": [
                {"id": "UZ01", "colors": ["W", "U"], "description": "WU Signpost"},
                {"id": "UZ02", "colors": ["W", "B"], "description": "WB Signpost"},
                {"id": "UZ03", "colors": ["U", "B"], "description": "UB Signpost"},
                {"id": "UZ04", "colors": ["U", "R"], "description": "UR Signpost"},
                {"id": "UZ05", "colors": ["B", "R"], "description": "BR Signpost"},
                {"id": "UZ06", "colors": ["B", "G"], "description": "BG Signpost"},
                {"id": "UZ07", "colors": ["R", "G"], "description": "RG Signpost"},
                {"id": "UZ08", "colors": ["R", "W"], "description": "RW Signpost"},
                {"id": "UZ09", "colors": ["G", "W"], "description": "GW Signpost"},
                {"id": "UZ10", "colors": ["G", "U"], "description": "GU Signpost"},
            ],
            "rare": [
                {"id": "RZ01", "colors": ["W", "U"], "description": "Anything WU"},
                {"id": "RZ02", "colors": ["W", "B"], "description": "Anything WB"},
                {"id": "RZ03", "colors": ["U", "B"], "description": "Anything UB"},
                {"id": "RZ04", "colors": ["U", "R"], "description": "Anything UR"},
                {"id": "RZ05", "colors": ["B", "R"], "description": "Anything BR"},
                {"id": "RZ06", "colors": ["B", "G"], "description": "Anything BG"},
                {"id": "RZ07", "colors": ["R", "G"], "description": "Anything RG"},
                {"id": "RZ08", "colors": ["R", "W"], "description": "Anything RW"},
                {"id": "RZ09", "colors": ["G", "W"], "description": "Anything GW"},
                {"id": "RZ10", "colors": ["U", "G"], "description": "Anything UG"},
            ],
            "mythic": [
                {"id": "MZ01", "description": "Anything Multicolored"},
                {"id": "MZ02", "description": "Anything Multicolored"},
                {"id": "MZ03", "description": "Anything Multicolored"},
                {"id": "MZ04", "description": "Anything Multicolored"},
                {"id": "MZ05", "description": "Anything Multicolored"},
                {"id": "MZ06", "description": "Anything Multicolored"},
                {"id": "MZ07", "description": "Anything Multicolored"},
                {"id": "MZ08", "description": "Anything Multicolored"},
                {"id": "MZ09", "description": "Anything Multicolored"},
                {"id": "MZ10", "description": "Anything Multicolored"},
            ],
        }

        self.skeleton_data["colorless"] = {
            "common": [
                {"id": "CA01", "mana_value": [1, 2], "description": "1 or 2 MV"},
                {"id": "CA02", "mana_value": [3, 4], "description": "3 or 4 MV"},
                {"id": "CA03", "mana_value": [5, 6], "description": "5 or 6 MV"},
                {"id": "CA04", "type": "equipment", "description": "Equipment"},
                {"id": "CA05", "type": "removal", "description": "Removal"},
                {"id": "CA06", "type": "mana", "description": "Mana production"},
            ],
            "uncommon": [
                {"id": "UA01", "mana_value": [1, 2], "description": "1 or 2 MV"},
                {"id": "UA02", "mana_value": [3, 4], "description": "3 or 4 MV"},
                {"id": "UA03", "mana_value": [5, 6], "description": "5 or 6 MV"},
                {
                    "id": "UA04",
                    "type": "removal",
                    "description": "Removal (often conditional and usually costed somewhat inefficiently)",
                },
                {"id": "UA05", "type": "non_creature", "description": "Non-creature"},
                {"id": "UA06", "type": "equipment", "description": "Equipment"},
            ],
            "rare": [
                {"id": "RA02", "type": "artifact", "description": "Artifact"},
                {"id": "RA03", "type": "artifact", "description": "Artifact"},
                {"id": "RA04", "type": "equipment", "description": "Equipment"},
            ],
            "keywords": {
                "defender": {
                    "count": [0, 1],
                    "note": "this isn't counted as a creature",
                },
                "flash": {
                    "count": [0, 1],
                    "note": "usually on a creature with power 3 or higher",
                },
                "flying": {"count": 1},
                "haste": {"count": [0, 1]},
                "trample": {"count": [0, 1]},
                "vigilance": {"count": [0, 1]},
                "ward": {"count": [0, 1], "note": "any cost"},
            },
        }

        self.skeleton_data["lands"] = {
            "common": [
                {
                    "id": "CL01",
                    "colors": ["W", "U"],
                    "description": "WU Fixing (can be cut)",
                },
                {
                    "id": "CL02",
                    "colors": ["W", "B"],
                    "description": "WB Fixing (can be cut)",
                },
                {
                    "id": "CL03",
                    "colors": ["U", "B"],
                    "description": "UB Fixing (can be cut)",
                },
                {
                    "id": "CL04",
                    "colors": ["U", "R"],
                    "description": "UR Fixing (can be cut)",
                },
                {
                    "id": "CL05",
                    "colors": ["B", "R"],
                    "description": "BR Fixing (can be cut)",
                },
                {
                    "id": "CL06",
                    "colors": ["B", "G"],
                    "description": "BG Fixing (can be cut)",
                },
                {
                    "id": "CL07",
                    "colors": ["R", "G"],
                    "description": "RG Fixing (can be cut)",
                },
                {
                    "id": "CL08",
                    "colors": ["R", "W"],
                    "description": "RW Fixing (can be cut)",
                },
                {
                    "id": "CL09",
                    "colors": ["G", "W"],
                    "description": "GW Fixing (can be cut)",
                },
                {
                    "id": "CL010",
                    "colors": ["G", "U"],
                    "description": "GU Fixing (can be cut)",
                },
                {
                    "id": "CL11",
                    "type": "fixing",
                    "description": "Basic Land Fetch/Pick a color fixing (can be cut)",
                },
            ],
            "uncommon": [
                {
                    "id": "UL01",
                    "type": "utility",
                    "description": "Utility Land (can be cut)",
                },
                {
                    "id": "UL02",
                    "type": "utility",
                    "description": "Utility Land (can be cut)",
                },
                {
                    "id": "UL03",
                    "type": "utility",
                    "description": "Utility Land (can be cut)",
                },
                {
                    "id": "UL04",
                    "type": "utility",
                    "description": "Utility Land (can be cut)",
                },
                {
                    "id": "UL05",
                    "type": "utility",
                    "description": "Utility Land (can be cut)",
                },
            ],
        }

    def get_skeleton_data(self):
        """Return the complete skeleton data"""
        return self.skeleton_data

    def get_color_data(self, color, rarity=None):
        """Get data for a specific color and optionally rarity"""
        if color not in self.skeleton_data:
            return None

        if rarity:
            return self.skeleton_data[color].get(rarity, None)

        return self.skeleton_data[color]

    def get_total_cards_count(self):
        """Calculate total number of cards in the skeleton"""
        total = 0
        for color_name, color_data in self.skeleton_data.items():
            if color_name in ["multicolor", "colorless", "lands"]:
                for rarity_data in color_data.values():
                    if isinstance(rarity_data, list):
                        total += len(rarity_data)
            else:
                for rarity_name, rarity_data in color_data.items():
                    if isinstance(rarity_data, dict):
                        for card_type, cards in rarity_data.items():
                            if isinstance(cards, list):
                                total += len(cards)
                    elif isinstance(rarity_data, list):
                        total += len(rarity_data)
        return total

    def export_skeleton_summary(self):
        """Export a summary of the skeleton structure"""
        summary = {
            "total_cards": self.get_total_cards_count(),
            "colors": {},
            "multicolor": len(self.skeleton_data["multicolor"]["uncommon_signposts"])
            + len(self.skeleton_data["multicolor"]["rare"])
            + len(self.skeleton_data["multicolor"]["mythic"]),
            "colorless": len(self.skeleton_data["colorless"]["common"])
            + len(self.skeleton_data["colorless"]["uncommon"])
            + len(self.skeleton_data["colorless"]["rare"]),
            "lands": len(self.skeleton_data["lands"]["common"])
            + len(self.skeleton_data["lands"]["uncommon"]),
        }

        for color in ["white", "blue", "black", "red", "green"]:
            if color in self.skeleton_data:
                color_total = 0
                for rarity_name, rarity_data in self.skeleton_data[color].items():
                    if isinstance(rarity_data, dict):
                        for card_type, cards in rarity_data.items():
                            if isinstance(cards, list):
                                color_total += len(cards)
                    elif isinstance(rarity_data, list):
                        color_total += len(rarity_data)
                summary["colors"][color] = color_total

        return summary

    def get_commons_only(self):
        """Get only common cards from all colors including colorless (102 cards total)"""
        commons = {}

        for color in ["white", "blue", "black", "red", "green"]:
            if color in self.skeleton_data and "common" in self.skeleton_data[color]:
                commons[color] = {"common": self.skeleton_data[color]["common"]}

        # Add colorless commons
        if (
            "colorless" in self.skeleton_data
            and "common" in self.skeleton_data["colorless"]
        ):
            commons["colorless"] = {"common": self.skeleton_data["colorless"]["common"]}

        return commons
