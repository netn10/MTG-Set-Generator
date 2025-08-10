#!/usr/bin/env python3
"""
Demo script showing the MTG Set Generator capabilities
"""

import sys
import os

sys.path.append("backend")

from set_skeleton import SetSkeleton
from card_generator import CardGenerator
from export_utils import SetExporter


def main():
    print("🎴 MTG Set Generator Demo")
    print("=" * 50)

    # Initialize components
    print("Initializing components...")
    skeleton = SetSkeleton()
    generator = CardGenerator()
    exporter = SetExporter()

    print(f"✓ Skeleton loaded with {skeleton.get_total_cards_count()} total slots")
    print(f"✓ Card generator ready")
    print(f"✓ Export utilities ready")
    print()

    # Show skeleton summary
    print("📊 Skeleton Summary:")
    summary = skeleton.export_skeleton_summary()
    print(f"  Total cards: {summary['total_cards']}")
    print(f"  Colors: {sum(summary['colors'].values())} cards")
    print(f"  Multicolor: {summary['multicolor']} cards")
    print(f"  Colorless: {summary['colorless']} cards")
    print(f"  Lands: {summary['lands']} cards")
    print()

    # Show color breakdown
    print("🎨 Per-Color Breakdown:")
    for color, count in summary["colors"].items():
        print(f"  {color.title()}: {count} cards")
    print()

    # Show some example slots
    print("🔍 Example Slots (White Commons):")
    white_common = skeleton.get_color_data("white", "common")
    for i, creature in enumerate(white_common["creatures"][:3]):
        print(f"  {creature['id']}: {creature['description']}")
    print("  ...")
    print()

    print("🚀 Ready to generate! Use the web interface to create your themed sets.")
    print("   1. Start the backend: cd backend && python app.py")
    print("   2. Start the frontend: cd frontend && npm start")
    print("   3. Open http://localhost:3000")


if __name__ == "__main__":
    main()
