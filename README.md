# Magic: The Gathering Set Generator

A AI-powered tool for generating complete Magic: The Gathering sets by using design skeletons. All rights reserved. This project is made for education porpuse only.

## 🎯 Features

### Professional Set Builder
- **Complete Set Design**: Generate all rarities (Common, Uncommon, Rare, Mythic) across all colors
- **Mark Rosewater's Skeleton**: Uses the official MTG design skeleton for balanced, professional sets
- **Slot-by-Slot Control**: Generate individual cards or entire sets with precise control
- **Real-time Progress**: Track your set completion with visual progress indicators

### Multiple Export Formats
- **JSON Export**: Complete set data with metadata
- **CSV Export**: Spreadsheet-compatible format for analysis
- **Cockatrice XML**: Import directly into Cockatrice for playtesting

### Theme-based Generation
- **AI-Powered Design**: Uses OpenAI's GPT models for balanced, flavorful cards
- **Thematic Coherence**: Every card fits your chosen theme perfectly
- **Professional Layout**: Cards displayed with proper MTG formatting and color-coding

### Two Generation Modes
- **Set Builder**: Professional skeleton-based design for complete sets
- **Quick Generator**: Fast commons generation for rapid prototyping

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key (entered through web interface)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd magic-set-creator
```

2. **Set up the backend:**
```bash
cd backend
pip install -r requirements.txt
```

3. **Get OpenAI API Key:**
You'll need an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys). You'll enter this in the web interface when using the application.

4. **Set up the frontend:**
```bash
cd ../frontend
npm install
```

### Running the Application

1. **Start the backend:**
```bash
cd backend
python app.py
```

2. **Start the frontend:**
```bash
cd frontend
npm start
```

3. **Open your browser to `http://localhost:3000`**

## 📖 Usage Guide

### Set Builder Mode (Recommended)

1. **Choose Set Builder** from the navigation
2. **Enter your OpenAI API key** in the provided field
3. **Enter your theme** (e.g., "Steampunk Inventors", "Underwater Civilization")
4. **Generate cards** either:
   - One at a time by clicking "Generate Card" on individual slots
   - All at once with "Generate All Cards"
5. **Track progress** with the built-in progress bar
6. **Export your set** in JSON, CSV, or Cockatrice format

### Quick Generator Mode

1. **Choose Quick Generator** for rapid prototyping
2. **Enter your OpenAI API key** in the provided field
3. **Enter a theme** and generate commons instantly
4. **Perfect for** initial concept testing and brainstorming

## 🎨 Design Skeleton

The application implements Mark Rosewater's complete design skeleton:

### Per Color (White, Blue, Black, Red, Green):
- **12 Common Creatures** (various mana values)
- **7 Common Spells** (removal, tricks, utility)
- **8 Uncommon Creatures** (flexible mana values)
- **5 Uncommon Spells** (more powerful effects)
- **10 Rares** (high-impact cards)
- **2 Mythics** (set-defining cards)

### Additional Slots:
- **10 Multicolor Signposts** (draft archetypes)
- **10 Multicolor Rares**
- **10 Multicolor Mythics**
- **6 Colorless Commons** (artifacts)
- **6 Colorless Uncommons**
- **3 Colorless Rares**
- **11 Common Lands** (fixing)
- **5 Uncommon Lands** (utility)

**Total: 298 cards** - A complete, balanced set ready for play!

## 🔧 API Reference

### Core Endpoints

#### `GET /api/skeleton`
Returns the complete design skeleton structure.

#### `POST /api/generate-card`
Generate a single card for a specific slot.
```json
{
  "theme": "Steampunk Inventors",
  "color": "white",
  "rarity": "common", 
  "slot_id": "CW01",
  "slot_data": { "mana_value": 1, "description": "1 MV" },
  "apiKey": "sk-..."
}
```

#### `POST /api/generate-full-set`
Generate all cards for a complete set.
```json
{
  "theme": "Underwater Civilization",
  "apiKey": "sk-..."
}
```

#### `POST /api/export-set`
Export a set in various formats.
```json
{
  "set_data": { /* complete set data */ },
  "theme": "Theme Name",
  "format": "json" // or "csv" or "cockatrice"
}
```

### Legacy Endpoints

#### `POST /api/generate-set`
Quick commons generation (backwards compatibility).

#### `GET /api/health`
Health check endpoint.

## 🎭 Example Themes

### Fantasy Themes
- Steampunk Inventors
- Underwater Civilization
- Desert Nomads
- Haunted Library
- Crystal Caves
- Mushroom Forest

### Sci-Fi Themes
- Space Pirates
- Time Travelers
- Cyberpunk Hackers
- Robot Uprising
- Alien Invasion

### Abstract Themes
- Mathematical Concepts
- Musical Harmony
- Emotional Spectrum
- Weather Patterns
- Geological Forces

## 🏗️ Technical Architecture

### Backend (Python/Flask)
- **set_skeleton.py**: Complete MTG design skeleton implementation
- **card_generator.py**: AI-powered card generation with skeleton integration
- **export_utils.py**: Multi-format export functionality
- **app.py**: REST API with comprehensive endpoints

### Frontend (React)
- **SetBuilder.js**: Professional set building interface
- **CardDisplay.js**: MTG-style card rendering
- **ThemeInput.js**: Theme selection and quick generation

### AI Integration
- **Two-stage generation**: Skeleton analysis → Card creation
- **Context-aware prompts**: Each slot gets specialized generation prompts
- **Fallback handling**: Graceful degradation if API fails
- **Thematic consistency**: All cards maintain theme coherence

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- **New export formats** (MTGO, Arena, etc.)
- **Advanced filtering** and search
- **Set statistics** and analysis
- **Playtesting integration**
- **Custom skeleton** modifications

## 📄 License

This project is for educational and personal use. Magic: The Gathering is a trademark of Wizards of the Coast.

## 🙏 Acknowledgments

- **Mark Rosewater** for the official design skeleton framework
- **Wizards of the Coast** for Magic: The Gathering
- **OpenAI** for GPT models enabling AI card generation