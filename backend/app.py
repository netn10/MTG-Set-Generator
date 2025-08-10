from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_socketio import SocketIO
import openai
from openai import RateLimitError
import os
import json
from dotenv import load_dotenv
from card_generator import CardGenerator
from set_skeleton import SetSkeleton
from export_utils import SetExporter

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    ping_timeout=120,
    ping_interval=30,
    logger=False,  # Reduce logging noise
    engineio_logger=False,
    async_mode="threading",
)

# Check if API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY not found in environment variables")
    print("Make sure your .env file exists and contains OPENAI_API_KEY=your_key_here")
    exit(1)

# Initialize OpenAI client
openai.api_key = api_key

# Define model fallback chain for set concept generation
MODEL_FALLBACK_CHAIN = [
    "gpt-4o-mini",  # Cheapest and fastest
    "gpt-4o",  # More capable
    "gpt-4-turbo",  # Fallback
    "gpt-4",  # Last resort
    "gpt-3.5-turbo",  # Final fallback
]
current_model_index = 0


def _is_insufficient_quota_error(error):
    """Best-effort detection of insufficient quota errors from the OpenAI SDK."""
    message = str(error).lower()
    return (
        "insufficient_quota" in message
        or "you exceeded your current quota" in message
        or "status code: 429" in message
        and "quota" in message
    )


def _make_api_request_with_fallback(messages, temperature=0.8):
    """Make an API request with automatic model fallback on quota errors"""
    global current_model_index

    while current_model_index < len(MODEL_FALLBACK_CHAIN):
        current_model = MODEL_FALLBACK_CHAIN[current_model_index]
        try:
            # Log the API key being used (first 10 chars for security)
            api_key_used = os.getenv("OPENAI_API_KEY", "NOT_SET")
            print(
                f"Using OpenAI API key: {api_key_used[:10]}..."
                if api_key_used != "NOT_SET"
                else "API key not set!"
            )
            print(f"Making set concept API request with model: {current_model}")

            response = openai.chat.completions.create(
                model=current_model,
                messages=messages,
                temperature=temperature,
            )
            return response

        except RateLimitError as e:
            if _is_insufficient_quota_error(e):
                print(f"Quota exceeded for model {current_model}: {str(e)}")
                if current_model_index < len(MODEL_FALLBACK_CHAIN) - 1:
                    current_model_index += 1
                    print(
                        f"Switching to fallback model: {MODEL_FALLBACK_CHAIN[current_model_index]}"
                    )
                else:
                    print("All models exhausted for set concept generation")
                    raise e
            else:
                raise e
        except Exception as e:
            # For non-quota errors, just re-raise immediately
            raise e

    # If we get here, all models have been exhausted
    raise Exception("All models in fallback chain have exceeded quota")


# Initialize components
set_skeleton = SetSkeleton()
set_exporter = SetExporter()

# Initialize card generator with socketio after socketio is created
card_generator = None


def get_card_generator():
    """Get the card generator, initializing it if needed"""
    global card_generator
    if card_generator is None:
        card_generator = CardGenerator(socketio)
    return card_generator


@app.route("/api/skeleton", methods=["GET"])
def get_skeleton():
    """Return the complete set skeleton structure"""
    try:
        skeleton_data = set_skeleton.get_skeleton_data()
        return jsonify(skeleton_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/skeleton/commons", methods=["GET"])
def get_commons_skeleton():
    """Return only the commons skeleton structure (101 cards)"""
    try:
        commons_data = set_skeleton.get_commons_only()
        return jsonify(commons_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-card", methods=["POST"])
def generate_card():
    """Generate a single card for a specific slot"""
    try:
        data = request.json
        theme = data.get("theme", "")
        color = data.get("color", "")
        rarity = data.get("rarity", "")
        slot_id = data.get("slot_id", "")
        slot_data = data.get("slot_data", {})

        if not all([theme, color, rarity, slot_id]):
            return (
                jsonify({"error": "Theme, color, rarity, and slot_id are required"}),
                400,
            )

        print(
            f"API: Generating single card: {slot_id} ({color} {rarity}) for theme: {theme}"
        )
        print(f"API: Request data - slot_data: {slot_data}")

        # Validate slot_data is a dictionary
        if not isinstance(slot_data, dict):
            print(
                f"API: Warning: slot_data is not a dict: {type(slot_data)} - {slot_data}"
            )
            slot_data = {"description": str(slot_data) if slot_data else "Generic slot"}

        # Generate card using the enhanced card generator
        print("API: Starting card generation process...")
        card = get_card_generator().generate_skeleton_card(
            theme, color, rarity, slot_id, slot_data
        )

        print(f"API: Successfully generated card: {card.get('name', 'Unknown')}")
        if card.get("error"):
            print(f"API: Warning: Card generated with error: {card.get('error')}")

        # Emit card via WebSocket if connected
        if socketio:
            socketio.emit(
                "card_generated",
                {"color": color, "rarity": rarity, "slot_id": slot_id, "card": card},
            )
            print(f"WebSocket: Emitted card {card.get('name', 'Unknown')} to frontend")

        return jsonify({"success": True, "card": card})

    except Exception as e:
        print(f"API: Error generating single card: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-full-set", methods=["POST"])
def generate_full_set():
    """Generate all cards for a complete set using improved batch processing"""
    try:
        data = request.json
        theme = data.get("theme", "")
        use_parallel = data.get("use_parallel", False)

        if not theme:
            return jsonify({"error": "Theme is required"}), 400

        print(f"Generating full set for theme: {theme} (parallel: {use_parallel})")

        # Generate complete set using batch processing
        complete_set = get_card_generator().generate_complete_set(theme, set_skeleton)

        print(
            f"Successfully generated {len(complete_set)} color sections using batch processing"
        )
        return jsonify({"success": True, "set": complete_set, "theme": theme})

    except Exception as e:
        print(f"Error generating full set: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-commons-only", methods=["POST"])
def generate_commons_only():
    """Generate only common cards (101 cards total) using improved batch processing"""
    try:
        data = request.json
        theme = data.get("theme", "")
        use_parallel = data.get("use_parallel", False)

        if not theme:
            return jsonify({"error": "Theme is required"}), 400

        print(f"Generating commons only for theme: {theme} (parallel: {use_parallel})")

        # Get commons skeleton and generate cards
        commons_skeleton_data = set_skeleton.get_commons_only()
        print(f"Commons skeleton has {len(commons_skeleton_data)} colors")

        # Generate commons using batch processing
        commons_set = get_card_generator().generate_complete_set(
            theme, commons_skeleton_data
        )

        print(
            f"Successfully generated commons set with {len(commons_set)} color sections using batch processing"
        )
        return jsonify({"success": True, "set": commons_set, "theme": theme})

    except Exception as e:
        print(f"Error generating commons set: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/export-set", methods=["POST"])
def export_set():
    """Export a set in various formats"""
    try:
        data = request.json
        set_data = data.get("set_data", {})
        theme = data.get("theme", "")
        set_concept = data.get("set_concept", {})
        export_format = data.get("format", "json")

        if not set_data:
            return jsonify({"error": "Set data is required"}), 400

        if export_format == "json":
            export_content = set_exporter.export_to_json(set_data, theme, set_concept)
            return Response(export_content, mimetype="application/json")
        elif export_format == "csv":
            set_name = set_concept.get("name", theme) if set_concept else theme
            export_content = set_exporter.export_to_csv(set_data, set_name)
            return Response(export_content, mimetype="text/csv")
        elif export_format == "cockatrice":
            set_name = set_concept.get("name", theme) if set_concept else theme
            export_content = set_exporter.export_to_cockatrice(set_data, set_name)
            return Response(export_content, mimetype="application/xml")
        else:
            return (
                jsonify(
                    {
                        "error": "Unsupported export format. Use 'json', 'csv', or 'cockatrice'"
                    }
                ),
                400,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-set", methods=["POST"])
def generate_set():
    """Legacy endpoint for backwards compatibility"""
    try:
        data = request.json
        theme = data.get("theme", "")

        if not theme:
            return jsonify({"error": "Theme is required"}), 400

        # Generate commons based on design skeleton
        commons = get_card_generator().generate_commons(theme)

        return jsonify({"success": True, "theme": theme, "commons": commons})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-full-set-ultra-fast", methods=["POST"])
def generate_full_set_ultra_fast():
    """Generate all cards using ultra-fast batch processing"""
    try:
        data = request.json
        theme = data.get("theme", "")

        if not theme:
            return jsonify({"error": "Theme is required"}), 400

        print(f"Generating full set ULTRA FAST for theme: {theme}")

        # Use the large batch processing for maximum speed
        complete_set = get_card_generator().generate_complete_set_large_batches(
            theme, set_skeleton
        )

        print(f"Successfully generated {len(complete_set)} color sections ULTRA FAST")
        return jsonify({"success": True, "set": complete_set, "theme": theme})

    except Exception as e:
        print(f"Error generating full set ultra fast: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-commons-only-ultra-fast", methods=["POST"])
def generate_commons_only_ultra_fast():
    """Generate only common cards using ultra-fast mega batch processing"""
    try:
        data = request.json
        theme = data.get("theme", "")

        if not theme:
            return jsonify({"error": "Theme is required"}), 400

        print(f"Generating commons only ULTRA FAST for theme: {theme}")

        # Get commons skeleton and generate cards with mega batches
        commons_skeleton_data = set_skeleton.get_commons_only()
        print(f"Commons skeleton has {len(commons_skeleton_data)} colors")

        commons_set = get_card_generator().generate_complete_set_large_batches(
            theme, commons_skeleton_data
        )

        print(
            f"Successfully generated commons set ULTRA FAST with {len(commons_set)} color sections"
        )
        return jsonify({"success": True, "set": commons_set, "theme": theme})

    except Exception as e:
        print(f"Error generating commons set ultra fast: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-full-set-large-batches", methods=["POST"])
def generate_full_set_large_batches():
    """Generate all cards using large batch processing for maximum efficiency"""
    try:
        data = request.json
        theme = data.get("theme", "")

        if not theme:
            return jsonify({"error": "Theme is required"}), 400

        print(f"Generating full set with LARGE BATCHES for theme: {theme}")

        # Generate complete set using large batch processing
        complete_set = get_card_generator().generate_complete_set_large_batches(
            theme, set_skeleton
        )

        print(
            f"Successfully generated {len(complete_set)} color sections with LARGE BATCHES"
        )
        return jsonify({"success": True, "set": complete_set, "theme": theme})

    except Exception as e:
        print(f"Error generating full set with large batches: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-commons-only-large-batches", methods=["POST"])
def generate_commons_only_large_batches():
    """Generate only common cards using large batch processing"""
    try:
        data = request.json
        theme = data.get("theme", "")

        if not theme:
            return jsonify({"error": "Theme is required"}), 400

        print(f"Generating commons only with LARGE BATCHES for theme: {theme}")

        # Get commons skeleton and generate cards with large batches
        commons_skeleton_data = set_skeleton.get_commons_only()
        print(f"Commons skeleton has {len(commons_skeleton_data)} colors")

        commons_set = get_card_generator().generate_complete_set_large_batches(
            theme, commons_skeleton_data
        )

        print(
            f"Successfully generated commons set with LARGE BATCHES with {len(commons_set)} color sections"
        )
        return jsonify({"success": True, "set": commons_set, "theme": theme})

    except Exception as e:
        print(f"Error generating commons set with large batches: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-full-set-batched-50", methods=["POST"])
def generate_full_set_batched_50():
    """Generate all cards in large batches with real-time updates"""
    try:
        data = request.json
        theme = data.get("theme", "")

        if not theme:
            return jsonify({"error": "Theme is required"}), 400

        print(f"Generating full set in large batches for theme: {theme}")

        # Generate complete set using large batch processing
        complete_set = get_card_generator().generate_complete_set_large_batches(
            theme, set_skeleton
        )

        print(
            f"Successfully generated {len(complete_set)} color sections in large batches"
        )
        return jsonify({"success": True, "set": complete_set, "theme": theme})

    except Exception as e:
        print(f"Error generating full set in large batches: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-commons-only-batched-50", methods=["POST"])
def generate_commons_only_batched_50():
    """Generate only common cards in large batches with real-time updates"""
    try:
        data = request.json
        theme = data.get("theme", "")

        if not theme:
            return jsonify({"error": "Theme is required"}), 400

        print(f"Generating commons only in large batches for theme: {theme}")

        # Get commons skeleton and generate cards in large batches
        commons_skeleton_data = set_skeleton.get_commons_only()
        print(f"Commons skeleton has {len(commons_skeleton_data)} colors")

        commons_set = get_card_generator().generate_complete_set_large_batches(
            theme, commons_skeleton_data
        )

        print(
            f"Successfully generated commons set with {len(commons_set)} color sections in large batches"
        )
        return jsonify({"success": True, "set": commons_set, "theme": theme})

    except Exception as e:
        print(f"Error generating commons set in large batches: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-set-stream", methods=["POST"])
def generate_set_stream():
    """Generate cards with streaming updates as each card is completed"""
    try:
        data = request.json
        theme = data.get("theme", "")
        set_type = data.get("set_type", "full")  # 'full' or 'commons'
        # Note: parallel processing not yet implemented for streaming
        # use_parallel = data.get("use_parallel", True)

        if not theme:
            return jsonify({"error": "Theme is required"}), 400

        def generate():
            try:
                # Send initial status
                yield f"data: {json.dumps({'type': 'status', 'message': 'Starting generation...', 'theme': theme})}\n\n"

                # Get skeleton data
                if set_type == "commons":
                    skeleton_data = set_skeleton.get_commons_only()
                else:
                    skeleton_data = set_skeleton.get_skeleton_data()

                # Send skeleton structure
                yield f"data: {json.dumps({'type': 'skeleton', 'skeleton': skeleton_data})}\n\n"

                # For now, we'll use sequential generation for streaming
                # TODO: Implement proper streaming for parallel generation
                for color_name, color_data in skeleton_data.items():
                    for rarity_name, rarity_data in color_data.items():
                        # Handle different skeleton structures
                        slots_to_process = []
                        if isinstance(rarity_data, list):
                            slots_to_process = rarity_data
                        elif isinstance(rarity_data, dict):
                            for card_type, type_data in rarity_data.items():
                                if isinstance(type_data, list):
                                    slots_to_process.extend(type_data)

                        for slot in slots_to_process:
                            try:
                                card = get_card_generator().generate_skeleton_card(
                                    theme, color_name, rarity_name, slot["id"], slot
                                )
                                update = {
                                    "type": "card",
                                    "color": color_name,
                                    "rarity": rarity_name,
                                    "slot_id": slot["id"],
                                    "card": card,
                                }
                                yield f"data: {json.dumps(update)}\n\n"
                            except Exception as e:
                                error_update = {
                                    "type": "error",
                                    "color": color_name,
                                    "rarity": rarity_name,
                                    "slot_id": slot["id"],
                                    "error": str(e),
                                }
                                yield f"data: {json.dumps(error_update)}\n\n"

                # Send completion status
                yield f"data: {json.dumps({'type': 'complete', 'message': 'Generation complete!'})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            },
        )

    except Exception as e:
        print(f"Error in streaming generation: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-set-concept", methods=["POST"])
def generate_set_concept():
    """Generate a full set concept from a pitch using ChatGPT"""
    try:
        data = request.json
        pitch = data.get("pitch", "")

        if not pitch.strip():
            return jsonify({"error": "Pitch is required"}), 400

        print(f"Generating set concept from pitch: {pitch}")

        try:
            # Generate set concept using OpenAI with model fallback
            response = _make_api_request_with_fallback(
                [
                    {
                        "role": "system",
                        "content": """You are an expert Magic: The Gathering set designer. Given a brief pitch for a set, expand it into a comprehensive set concept with detailed descriptions and archetypes.

Your response should be a JSON object with the following structure:
{
    "name": "Set Name",
    "description": "Detailed 2-3 paragraph description of the set's world, story, and themes",
    "mechanics": ["List of 3-5 key mechanics for the set"],
    "archetypes": [
        {
            "colors": "WU",
            "name": "Archetype Name",
            "description": "What this archetype does and how it plays",
            "key_cards": ["Examples of cards this archetype wants"]
        }
    ],
    "flavor_themes": ["List of major flavor themes"],
    "design_notes": "Additional design considerations and goals"
}

CRITICAL REQUIREMENT: You MUST create exactly 10 archetypes, one for each two-color combination in Magic:
- WU (White-Blue)
- UB (Blue-Black) 
- BR (Black-Red)
- RG (Red-Green)
- GW (Green-White)
- WB (White-Black)
- UR (Blue-Red)
- BG (Black-Green)
- RW (Red-White)
- GU (Green-Blue)

Each archetype should have a distinct identity that fits the set's theme and creates interesting draft decisions. Focus on creating a cohesive, flavorful set that would be fun to draft and play.""",
                    },
                    {
                        "role": "user",
                        "content": f"Create a comprehensive Magic: The Gathering set concept from this pitch: {pitch}\n\nRemember: You must include exactly 10 archetypes covering all two-color pairs (WU, UB, BR, RG, GW, WB, UR, BG, RW, GU). Each should be thematically appropriate and mechanically distinct.",
                    },
                ],
                temperature=0.8,
            )

            concept_json = response.choices[0].message.content

        except RateLimitError as e:
            print(f"OpenAI quota exceeded: {str(e)}")
            # Return a mock concept when quota is exceeded
            mock_concept = {
                "name": f"{pitch.title()} Set",
                "description": f"A Magic: The Gathering set based on the theme of '{pitch}'. This set explores new mechanical territory while maintaining the beloved aspects of Magic gameplay. The world is rich with opportunities for both competitive and casual play, featuring innovative mechanics that create fresh strategic decisions.",
                "mechanics": [
                    "Adapt",
                    "Investigate",
                    "Prowess",
                    "Scry",
                    "Token Generation",
                ],
                "archetypes": [
                    {
                        "colors": "WU",
                        "name": "Control",
                        "description": "Counter spells and card draw",
                        "key_cards": ["Counterspell variants", "Card draw spells"],
                    },
                    {
                        "colors": "UB",
                        "name": "Mill",
                        "description": "Library destruction strategy",
                        "key_cards": ["Mill spells", "Graveyard value"],
                    },
                    {
                        "colors": "BR",
                        "name": "Aggro",
                        "description": "Fast aggressive creatures",
                        "key_cards": ["Cheap creatures", "Burn spells"],
                    },
                    {
                        "colors": "RG",
                        "name": "Ramp",
                        "description": "Big creatures and mana acceleration",
                        "key_cards": ["Mana dorks", "Large threats"],
                    },
                    {
                        "colors": "GW",
                        "name": "Tokens",
                        "description": "Create multiple small creatures",
                        "key_cards": ["Token makers", "Anthem effects"],
                    },
                    {
                        "colors": "WB",
                        "name": "Lifegain",
                        "description": "Gain life and drain opponents",
                        "key_cards": ["Lifegain spells", "Life drain"],
                    },
                    {
                        "colors": "UR",
                        "name": "Spells",
                        "description": "Instant and sorcery synergies",
                        "key_cards": ["Cheap spells", "Spell payoffs"],
                    },
                    {
                        "colors": "BG",
                        "name": "Graveyard",
                        "description": "Utilize the graveyard as resource",
                        "key_cards": ["Self-mill", "Recursion"],
                    },
                    {
                        "colors": "RW",
                        "name": "Equipment",
                        "description": "Artifacts that enhance creatures",
                        "key_cards": ["Equipment", "Equipment matters"],
                    },
                    {
                        "colors": "GU",
                        "name": "Ramp",
                        "description": "Accelerate into big spells",
                        "key_cards": ["Ramp spells", "Big payoffs"],
                    },
                ],
                "flavor_themes": [
                    pitch.title(),
                    "Adventure",
                    "Discovery",
                    "Magic",
                    "Wonder",
                ],
                "design_notes": f"This set concept was generated as a fallback due to API limitations. The theme '{pitch}' offers rich design space for a full Magic set.",
            }
            print(
                f"Returning mock concept due to API quota limits: {mock_concept['name']}"
            )
            return jsonify(
                {
                    "success": True,
                    "concept": mock_concept,
                    "note": "Generated with fallback system due to API limits",
                }
            )

        except Exception as api_error:
            print(f"OpenAI API error: {str(api_error)}")
            raise api_error

        # Extract JSON from response
        start = concept_json.find("{")
        end = concept_json.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No valid JSON found in response")

        concept_data = json.loads(concept_json[start:end])

        print(
            f"Successfully generated set concept: {concept_data.get('name', 'Unknown')}"
        )
        return jsonify({"success": True, "concept": concept_data})

    except Exception as e:
        print(f"Error generating set concept: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})


@socketio.on("connect")
def handle_connect():
    print("Client connected to WebSocket")
    # Send a test message to confirm connection
    socketio.emit(
        "connection_confirmed", {"message": "WebSocket connection established"}
    )


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected from WebSocket")


def initialize_card_generator():
    """Initialize the card generator with socketio reference"""
    global card_generator
    card_generator = CardGenerator(socketio)


if __name__ == "__main__":
    # Initialize card generator with socketio reference
    initialize_card_generator()
    socketio.run(app, debug=True, port=5000)
