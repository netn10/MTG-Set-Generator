"""
Export utilities for MTG sets
"""

import json
import csv
import io
from datetime import datetime


class SetExporter:
    def __init__(self):
        pass

    def export_to_json(self, set_data, theme, metadata=None):
        """Export set to JSON format"""
        export_data = {
            "theme": theme,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "total_cards": self._count_cards(set_data),
            "cards": self._flatten_set_data(set_data),
        }
        return json.dumps(export_data, indent=2)

    def export_to_csv(self, set_data, theme):
        """Export set to CSV format"""
        output = io.StringIO()
        fieldnames = [
            "slot_id",
            "color",
            "rarity",
            "name",
            "mana_cost",
            "type",
            "power",
            "toughness",
            "rules_text",
            "flavor_text",
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        cards = self._flatten_set_data(set_data)
        for card in cards:
            writer.writerow(
                {
                    "slot_id": card.get("slot_id", ""),
                    "color": card.get("color", ""),
                    "rarity": card.get("rarity", ""),
                    "name": card.get("name", ""),
                    "mana_cost": card.get("mana_cost", ""),
                    "type": card.get("type", ""),
                    "power": card.get("power", ""),
                    "toughness": card.get("toughness", ""),
                    "rules_text": card.get("rules_text", ""),
                    "flavor_text": card.get("flavor_text", ""),
                }
            )

        return output.getvalue()

    def export_to_cockatrice(self, set_data, theme):
        """Export set to Cockatrice XML format"""
        cards = self._flatten_set_data(set_data)

        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<cockatrice_carddatabase version="4">
    <sets>
        <set>
            <name>{theme}</name>
            <longname>{theme} Set</longname>
            <settype>Custom</settype>
            <releasedate>{datetime.now().strftime('%Y-%m-%d')}</releasedate>
        </set>
    </sets>
    <cards>
"""

        for card in cards:
            rarity_map = {
                "common": "common",
                "uncommon": "uncommon",
                "rare": "rare",
                "mythic": "mythic",
            }

            xml_content += f"""        <card>
            <name>{self._escape_xml(card.get('name', ''))}</name>
            <set>{theme}</set>
            <color>{self._get_color_identity(card.get('mana_cost', ''))}</color>
            <manacost>{self._escape_xml(card.get('mana_cost', ''))}</manacost>
            <type>{self._escape_xml(card.get('type', ''))}</type>
            <text>{self._escape_xml(card.get('rules_text', ''))}</text>
"""

            if card.get("power") is not None and card.get("toughness") is not None:
                xml_content += f"""            <pt>{card.get('power')}/{card.get('toughness')}</pt>
"""

            xml_content += f"""            <rarity>{rarity_map.get(card.get('rarity', '').lower(), 'common')}</rarity>
        </card>
"""

        xml_content += """    </cards>
</cockatrice_carddatabase>"""

        return xml_content

    def _count_cards(self, set_data):
        """Count total cards in set"""
        count = 0
        for color_data in set_data.values():
            for rarity_data in color_data.values():
                for card in rarity_data.values():
                    if card is not None:
                        count += 1
        return count

    def _flatten_set_data(self, set_data):
        """Flatten set data into a list of cards"""
        cards = []
        for color_name, color_data in set_data.items():
            for rarity_name, rarity_data in color_data.items():
                for slot_id, card in rarity_data.items():
                    if card is not None:
                        card_export = {
                            "slot_id": slot_id,
                            "color": color_name,
                            "rarity": rarity_name,
                            **card,
                        }
                        cards.append(card_export)
        return cards

    def _escape_xml(self, text):
        """Escape XML special characters"""
        if not text:
            return ""
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def _get_color_identity(self, mana_cost):
        """Extract color identity from mana cost"""
        if not mana_cost:
            return ""

        colors = []
        if "W" in mana_cost:
            colors.append("W")
        if "U" in mana_cost:
            colors.append("U")
        if "B" in mana_cost:
            colors.append("B")
        if "R" in mana_cost:
            colors.append("R")
        if "G" in mana_cost:
            colors.append("G")

        return "".join(colors)
