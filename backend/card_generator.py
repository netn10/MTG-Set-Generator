import openai
import json
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging for card generation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CardGenerator:
    def __init__(self, socketio=None):
        self.socketio = socketio
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Disable automatic retries to fail fast on quota errors and avoid repeated 429s
        try:
            print("Using OpenAI API key: ", api_key[:10] + "...")
            self.client = openai.OpenAI(api_key=api_key, max_retries=0)
        except TypeError:
            # Fallback if installed SDK version doesn't support max_retries kwarg
            self.client = openai.OpenAI(api_key=api_key)

        # Define model fallback chain (in order of preference)
        self.model_fallback_chain = [
            "gpt-4o-mini",  # Cheapest and fastest
            "gpt-4o",  # More capable
            "gpt-4-turbo",  # Fallback
            "gpt-4",  # Last resort
            "gpt-3.5-turbo",  # Final fallback
        ]
        self.current_model_index = 0

    def _is_insufficient_quota_error(self, error: Exception) -> bool:
        """Best-effort detection of insufficient quota errors from the OpenAI SDK."""
        message = str(error).lower()
        return (
            "insufficient_quota" in message
            or "you exceeded your current quota" in message
            or "status code: 429" in message
            and "quota" in message
        )

    def _get_current_model(self):
        """Get the current model to use from the fallback chain"""
        if self.current_model_index < len(self.model_fallback_chain):
            return self.model_fallback_chain[self.current_model_index]
        return self.model_fallback_chain[
            -1
        ]  # Use last model if we've exhausted the chain

    def _try_next_model(self):
        """Switch to the next model in the fallback chain"""
        if self.current_model_index < len(self.model_fallback_chain) - 1:
            self.current_model_index += 1
            logger.info(f"Switching to fallback model: {self._get_current_model()}")
            return True
        else:
            logger.warning("All models exhausted")
            return False

    def _make_api_request(self, messages, temperature=1.0):
        """Make an API request with automatic model fallback on quota errors"""
        while self.current_model_index < len(self.model_fallback_chain):
            current_model = self._get_current_model()
            try:
                # Log the API key being used (first 10 chars for security)
                api_key_used = os.getenv("OPENAI_API_KEY", "NOT_SET")
                logger.info(
                    f"Using OpenAI API key: {api_key_used[:10]}..."
                    if api_key_used != "NOT_SET"
                    else "API key not set!"
                )
                logger.info(f"Making API request with model: {current_model}")

                response = self.client.chat.completions.create(
                    model=current_model,
                    messages=messages,
                    temperature=temperature,
                )
                return response

            except Exception as e:
                if self._is_insufficient_quota_error(e):
                    logger.warning(
                        f"Quota exceeded for model {current_model}: {str(e)}"
                    )
                    if not self._try_next_model():
                        raise e  # Re-raise if no more models to try
                else:
                    # For non-quota errors, just re-raise immediately
                    raise e

        # If we get here, all models have been exhausted
        raise Exception("All models in fallback chain have exceeded quota")

    def _emit_card_generated(self, color, rarity, slot_id, card):
        """Emit card via WebSocket when generated"""
        if self.socketio:
            try:
                # Clean the card data before emission to avoid serialization issues
                clean_card = {
                    "name": card.get("name", "Unknown"),
                    "mana_cost": card.get("mana_cost", ""),
                    "type": card.get("type", ""),
                    "power": card.get("power"),
                    "toughness": card.get("toughness"),
                    "rules_text": card.get("rules_text", ""),
                    "flavor_text": card.get("flavor_text", ""),
                    "rarity": card.get("rarity", "Common"),
                    "slot_id": card.get("slot_id", slot_id),
                    "generated_for_theme": card.get("generated_for_theme", ""),
                    "error": card.get("error"),  # Include error if present
                }

                # Remove None values
                clean_card = {k: v for k, v in clean_card.items() if v is not None}

                self.socketio.emit(
                    "card_generated",
                    {
                        "color": color,
                        "rarity": rarity,
                        "slot_id": slot_id,
                        "card": clean_card,
                    },
                )
                logger.info(
                    f"WebSocket: Emitted card {clean_card.get('name', 'Unknown')} to frontend"
                )
            except Exception as e:
                logger.error(f"WebSocket: Failed to emit card: {e}")
                # Log the problematic data for debugging
                logger.debug(f"WebSocket: Problematic card data: {card}")
        else:
            logger.debug("WebSocket: No socketio instance available for card emission")

    def generate_commons(self, theme):
        """Generate a full set of commons based on the theme and ChatGPT-generated design skeleton"""
        # First, generate a design skeleton based on the theme
        design_skeleton = self._generate_design_skeleton(theme)

        commons = []
        for color in ["white", "blue", "black", "red", "green"]:
            color_commons = self._generate_color_commons(color, theme, design_skeleton)
            commons.extend(color_commons)

        # Add colorless commons - generate them individually since they don't follow the same pattern
        colorless_commons = self._generate_colorless_commons(theme)
        commons.extend(colorless_commons)

        return commons

    def _generate_colorless_commons(self, theme):
        """Generate colorless common cards based on the theme"""
        colorless_commons = []

        # Simple templates for colorless commons (6 cards total)
        colorless_templates = [
            {
                "mana_value": 1,
                "type": "artifact",
                "description": "1 MV artifact creature or utility artifact",
            },
            {
                "mana_value": 2,
                "type": "artifact",
                "description": "2 MV artifact creature or utility artifact",
            },
            {
                "mana_value": 3,
                "type": "artifact",
                "description": "3 MV artifact creature",
            },
            {
                "mana_value": 4,
                "type": "artifact",
                "description": "4 MV artifact creature",
            },
            {"mana_value": 1, "type": "equipment", "description": "Equipment"},
            {
                "mana_value": 2,
                "type": "utility",
                "description": "Utility artifact or mana production",
            },
        ]

        for i, template in enumerate(colorless_templates, 1):
            card = self._generate_colorless_card(
                template, theme, f"colorless_common_{i}"
            )
            colorless_commons.append(card)

        return colorless_commons

    def _generate_colorless_card(self, template, theme, card_id):
        """Generate a single colorless card"""
        prompt = f"""
        Create a Magic: The Gathering colorless common card with the following specifications:
        
        Theme: {theme}
        Template: {template['description']}
        Mana Value: {template['mana_value']}
        Type: {template['type']}
        
        The card should:
        1. Fit the {theme} theme perfectly with creative, immersive flavor
        2. Be a colorless artifact, Equipment, or colorless creature
        3. Be appropriate for common rarity with balanced power level
        4. Have a memorable, thematic name and evocative flavor text
        5. Use generic mana costs only (no colored mana)
        6. Follow established colorless design principles
        
        Return the card in this JSON format:
        {{
            "name": "Card Name",
            "mana_cost": "2",
            "type": "Artifact — Equipment",
            "power": 2,
            "toughness": 1,
            "rules_text": "Card abilities text",
            "flavor_text": "Flavor text here",
            "rarity": "Common"
        }}
        
        For non-creatures, omit power/toughness fields.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Magic: The Gathering card designer specializing in creating balanced colorless cards. Focus on making artifacts and Equipment that feel unique and thematic while maintaining balance.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=1,
            )

            card_json = response.choices[0].message.content
            # Extract JSON from response
            start = card_json.find("{")
            end = card_json.rfind("}") + 1
            card_data = json.loads(card_json[start:end])

            return card_data

        except Exception as e:
            # Re-raise the exception instead of returning a fallback card
            raise e

    def _generate_design_skeleton(self, theme):
        """Generate a design skeleton using ChatGPT based on the theme"""
        prompt = f"""
        Create a Magic: The Gathering design skeleton for commons that fits the "{theme}" theme.
        
        For each color (white, blue, black, red, green), provide:
        - 5 creature templates with mana costs and power/toughness
        - 3 spell templates with mana costs and general effects
        
        The skeleton should:
        1. Reflect the {theme} theme in the types of effects and mechanics
        2. Follow Mark Rosewater's design principles for commons
        3. Have appropriate mana costs and stats for each color
        4. Include both vanilla creatures and creatures with simple abilities
        5. Include a mix of instants, sorceries, and enchantments for spells
        
        Return the skeleton in this JSON format:
        {{
            "white": {{
                "creatures": ["1W 2/1 vanilla", "2W 2/3 vanilla", "3W 3/4 vanilla", "1W 1/1 with simple ability", "2W 2/2 with simple ability"],
                "spells": ["1W instant - effect description", "2W sorcery - effect description", "1W enchantment - effect description"]
            }},
            "blue": {{ ... }},
            "black": {{ ... }},
            "red": {{ ... }},
            "green": {{ ... }}
        }}
        
        Make sure the skeleton is thematically appropriate for "{theme}".
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Magic: The Gathering set designer. Create balanced, thematic design skeletons that follow established design principles.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=1,
            )

            skeleton_json = response.choices[0].message.content
            # Extract JSON from response
            start = skeleton_json.find("{")
            end = skeleton_json.rfind("}") + 1
            design_skeleton = json.loads(skeleton_json[start:end])

            return design_skeleton

        except Exception as e:
            print(f"Failed to generate design skeleton: {e}")
            # Re-raise the exception instead of returning a fallback skeleton
            raise e

    def _generate_color_commons(self, color, theme, design_skeleton):
        """Generate commons for a specific color"""
        skeleton = design_skeleton[color]
        color_commons = []

        # Generate creatures
        for creature_template in skeleton["creatures"]:
            card = self._generate_card(creature_template, color, theme, "creature")
            color_commons.append(card)

        # Generate spells
        for spell_template in skeleton["spells"]:
            card = self._generate_card(spell_template, color, theme, "spell")
            color_commons.append(card)

        return color_commons

    def _generate_card(self, template, color, theme, card_type):
        """Generate a single card using ChatGPT"""
        prompt = f"""
        Create a Magic: The Gathering common card with the following specifications:
        
        Theme: {theme}
        Color: {color}
        Template: {template}
        Type: {card_type}
        
        The card should:
        1. Fit the {theme} theme perfectly with creative, immersive flavor
        2. Follow the mana cost and stats from the template
        3. Be appropriate for common rarity but INTERESTING and engaging to play
        4. Have a memorable, thematic name and evocative flavor text
        5. Include meaningful gameplay decisions or synergies
        6. Use modern Magic design principles with creative mechanics
        
        Make the card INTERESTING by including:
        - Unique or flavorful abilities that create gameplay decisions
        - Synergies with other cards or strategies
        - Creative interpretations of the theme
        - Abilities that feel impactful even at common rarity
        - Flavorful creature types and spell effects
        
        Return the card in this JSON format:
        {{
            "name": "Card Name",
            "mana_cost": "1W",
            "type": "Creature — Human Soldier",
            "power": 2,
            "toughness": 1,
            "rules_text": "Card abilities text",
            "flavor_text": "Flavor text here",
            "rarity": "Common"
        }}
        
        For non-creatures, omit power/toughness fields.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Magic: The Gathering card designer specializing in creating engaging, flavorful cards that players love to play with. Focus on making every card feel unique and interesting while maintaining balance.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=1,
            )

            card_json = response.choices[0].message.content
            # Extract JSON from response
            start = card_json.find("{")
            end = card_json.rfind("}") + 1
            card_data = json.loads(card_json[start:end])

            return card_data

        except Exception as e:
            # Re-raise the exception instead of returning a fallback card
            raise e

    def generate_skeleton_card(self, theme, color, rarity, slot_id, slot_data):
        """Generate a card based on skeleton slot specifications"""
        start_time = datetime.now()
        logger.info(
            f"Starting card generation for slot {slot_id} - {color} {rarity} with theme '{theme}'"
        )
        logger.info(f"Slot data: {slot_data}")

        # Build detailed prompt based on slot data
        color_identity = "colorless" if color == "colorless" else color

        prompt = f"""
        Create a Magic: The Gathering {rarity} card with the following specifications:
        
        Theme: {theme}
        Color: {color_identity}
        Slot ID: {slot_id}
        Slot Requirements: {slot_data.get('description', '')}
        
        Additional Context:
        - Mana Value: {slot_data.get('mana_value', 'flexible')}
        - Card Type: {slot_data.get('type', 'flexible')}
        
        The card should:
        1. Perfectly fit the "{theme}" theme with creative, immersive flavor
        2. Meet the specific requirements of slot {slot_id}
        3. Be appropriate for {rarity} rarity with balanced power level
        4. Follow Mark Rosewater's design principles and modern Magic templating
        5. Have properly costed stats and effects following established curves
        6. Include a memorable, thematic name and evocative flavor text
        7. Adhere to the color pie and rarity expectations strictly
        
        Balance and Design Guidelines:
        - Follow established mana cost to power/toughness ratios (e.g., 1-mana: 2/1 or 1/2, 2-mana: 2/2 or 3/1, etc.)
        - {rarity.title()} rarity should have appropriate complexity and power level
        - Abilities should be costed fairly according to Magic's established precedents
        - Avoid overpowered effects that break Limited or Constructed formats
        - Ensure the card fits within {color}'s slice of the color pie
        - Create meaningful gameplay decisions without being overly complex
        
        {"For colorless cards, use generic mana costs and focus on artifacts, Equipment, or colorless creatures with unique abilities." if color == "colorless" else ""}
        
        CRITICAL BALANCE REQUIREMENTS:
        - Creatures: Follow the "Vanilla Test" - stats should be reasonable even without abilities
        - 1-mana creatures: Usually 2/1, 1/2, or 1/1 with upside
        - 2-mana creatures: Usually 2/2, 3/1, 1/3, or 2/1 with ability
        - 3-mana creatures: Usually 3/3, 4/2, 2/4, or 3/2 with ability
        - Higher costs: Scale appropriately with more stats or powerful abilities
        - Spells: Cost effects fairly based on existing Magic cards
        - Avoid "strictly better" versions of existing cards
        
        Return the card in this JSON format:
        {{
            "name": "Card Name",
            "mana_cost": "1W",
            "type": "Creature — Human Soldier",
            "power": 2,
            "toughness": 1,
            "rules_text": "Card abilities text",
            "flavor_text": "Flavor text here",
            "rarity": "{rarity.title()}"
        }}
        
        For non-creatures, omit power/toughness fields.
        """

        try:
            logger.info(f"Sending API request for card {slot_id}...")
            response = self._make_api_request(
                [
                    {
                        "role": "system",
                        "content": "You are an expert Magic: The Gathering card designer with deep knowledge of game balance, the color pie, and rarity expectations. Create cards that are perfectly balanced according to established Magic design principles. Every card must pass the 'vanilla test' for stats and be appropriately costed. Prioritize balance and playability over flashy effects. Follow Mark Rosewater's design philosophy strictly.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=1.0,
            )

            card_json = response.choices[0].message.content
            logger.info(f"Received API response for card {slot_id}, parsing JSON...")

            # Extract JSON from response
            start = card_json.find("{")
            end = card_json.rfind("}") + 1

            if start == -1 or end == 0:
                raise ValueError("No valid JSON found in response")

            card_data = json.loads(card_json[start:end])

            # Add metadata
            card_data["slot_id"] = slot_id
            card_data["generated_for_theme"] = theme

            generation_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Successfully generated card '{card_data.get('name', 'Unknown')}' for slot {slot_id} in {generation_time:.2f}s"
            )

            # Emit the card via WebSocket immediately after generation
            self._emit_card_generated(color, rarity, slot_id, card_data)

            return card_data

        except Exception as e:
            generation_time = (datetime.now() - start_time).total_seconds()
            logger.error(
                f"Failed to generate card for slot {slot_id} after {generation_time:.2f}s: {str(e)}"
            )
            # Re-raise the exception instead of returning a fallback card
            raise e

    def generate_batch_cards(self, theme, card_requests):
        """Generate multiple cards in a single API call for maximum efficiency"""
        if not card_requests:
            return {}

        start_time = datetime.now()
        logger.info(
            f"Starting TRUE BATCH generation of {len(card_requests)} cards for theme '{theme}' in SINGLE API CALL"
        )

        # Log the cards being generated
        for i, (color, rarity, slot_id, slot_data) in enumerate(card_requests, 1):
            logger.info(f"  Batch card {i}: {slot_id} ({color} {rarity})")

        # Build comprehensive batch prompt
        batch_prompt = f"""
        Create exactly {len(card_requests)} Magic: The Gathering cards for the "{theme}" theme in a single response.
        
        IMPORTANT: You must create exactly {len(card_requests)} cards, one for each specification below.
        
        Cards to generate:
        """

        for i, req in enumerate(card_requests, 1):
            color, rarity, slot_id, slot_data = req
            color_identity = "colorless" if color == "colorless" else color
            batch_prompt += f"""
        
        Card {i} (Slot ID: {slot_id}):
        - Theme: {theme}
        - Color: {color_identity}
        - Rarity: {rarity}
        - Slot ID: {slot_id}
        - Requirements: {slot_data.get('description', 'Generic slot')}
        - Mana Value: {slot_data.get('mana_value', 'flexible')}
        - Card Type: {slot_data.get('type', 'flexible')}
        """

        batch_prompt += f"""
        
        DESIGN REQUIREMENTS:
        1. Each card must perfectly fit the "{theme}" theme with immersive flavor
        2. Follow Mark Rosewater's design principles and modern Magic templating
        3. Be appropriate for the specified rarity with balanced power level
        4. Have memorable, thematic names and evocative flavor text
        5. Create meaningful gameplay decisions without being overly complex
        
        CRITICAL BALANCE REQUIREMENTS:
        - Creatures: Follow the "Vanilla Test" - stats must be reasonable even without abilities
        - 1-mana creatures: Usually 2/1, 1/2, or 1/1 with upside
        - 2-mana creatures: Usually 2/2, 3/1, 1/3, or 2/1 with ability
        - 3-mana creatures: Usually 3/3, 4/2, 2/4, or 3/2 with ability
        - Higher costs: Scale appropriately with more stats or powerful abilities
        - Spells: Cost effects fairly based on existing Magic cards
        - Avoid "strictly better" versions of existing cards
        - Respect each color's slice of the color pie strictly
        - Match rarity expectations for complexity and power level
        
        For colorless cards, use generic mana costs and focus on artifacts, Equipment, or colorless creatures.
        
        CRITICAL: Return exactly {len(card_requests)} cards as a JSON array. Each card must include the slot_id field.
        
        Format:
        [
            {{
                "slot_id": "{card_requests[0][2]}",
                "name": "Card Name",
                "mana_cost": "1W",
                "type": "Creature — Human Soldier",
                "power": 2,
                "toughness": 1,
                "rules_text": "Card abilities text",
                "flavor_text": "Flavor text here",
                "rarity": "{card_requests[0][1].title()}"
            }},
            {{
                "slot_id": "{card_requests[1][2] if len(card_requests) > 1 else 'example'}",
                "name": "Another Card Name",
                "mana_cost": "2U",
                "type": "Instant",
                "rules_text": "Card effect",
                "flavor_text": "Flavor text",
                "rarity": "{card_requests[1][1].title() if len(card_requests) > 1 else 'Common'}"
            }}
        ]
        
        For non-creatures, omit power/toughness fields.
        ENSURE: Each card has a unique slot_id matching the specifications above.
        """

        try:
            logger.info(f"Sending SINGLE API request for {len(card_requests)} cards...")
            response = self._make_api_request(
                [
                    {
                        "role": "system",
                        "content": "You are an expert Magic: The Gathering card designer specializing in batch card creation. You excel at creating multiple balanced, thematic cards in a single response. Always return exactly the number of cards requested in valid JSON array format. Every creature must have appropriate stats for its mana cost, and every spell must be fairly costed according to established Magic design principles.",
                    },
                    {"role": "user", "content": batch_prompt},
                ],
                temperature=0.9,
            )  # Slightly lower temperature for more consistent JSON formatting

            response_text = response.choices[0].message.content
            logger.info("Received batch API response, parsing JSON array...")

            # Extract JSON array from response with better error handling
            start = response_text.find("[")
            end = response_text.rfind("]") + 1

            if start == -1 or end == 0:
                logger.error("No valid JSON array found in response")
                logger.debug(f"Response text: {response_text[:500]}...")
                raise ValueError("No valid JSON array found in response")

            json_text = response_text[start:end]
            cards_data = json.loads(json_text)

            if not isinstance(cards_data, list):
                raise ValueError("Response is not a JSON array")

            # Create result dictionary keyed by slot_id
            result = {}
            expected_cards = len(card_requests)
            actual_cards = len(cards_data)

            logger.info(
                f"Expected {expected_cards} cards, received {actual_cards} cards"
            )

            for i, card_data in enumerate(cards_data):
                if isinstance(card_data, dict):
                    # Ensure slot_id is present
                    if "slot_id" not in card_data and i < len(card_requests):
                        card_data["slot_id"] = card_requests[i][2]

                    if "slot_id" in card_data:
                        card_data["generated_for_theme"] = theme
                        result[card_data["slot_id"]] = card_data
                        logger.info(
                            f"Parsed batch card {i+1}: '{card_data.get('name', 'Unknown')}' for slot {card_data['slot_id']}"
                        )

                        # Find the corresponding request to get color and rarity info for WebSocket
                        if i < len(card_requests):
                            color, rarity, slot_id, slot_data = card_requests[i]
                            self._emit_card_generated(color, rarity, slot_id, card_data)
                    else:
                        logger.warning(f"Card {i+1} missing slot_id: {card_data}")

            generation_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Successfully generated {len(result)} cards in SINGLE BATCH API CALL in {generation_time:.2f}s"
            )
            logger.info(
                f"Batch efficiency: {len(result)/generation_time:.1f} cards/second"
            )

            # If we didn't get all expected cards, raise an error
            if len(result) < expected_cards:
                missing_slots = [
                    slot_id
                    for _, _, slot_id, _ in card_requests
                    if slot_id not in result
                ]
                raise ValueError(
                    f"Batch generated {len(result)}/{expected_cards} cards, missing slots: {missing_slots}"
                )

            return result

        except Exception as e:
            generation_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Batch generation failed after {generation_time:.2f}s: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            # Re-raise the exception instead of falling back to individual generation
            raise e

    def generate_complete_set(self, theme, skeleton):
        """Generate all cards for a complete set using true batch processing"""
        start_time = datetime.now()
        logger.info(
            f"Starting complete set generation for theme '{theme}' using TRUE BATCH PROCESSING"
        )
        complete_set = {}

        # Handle both skeleton objects and direct skeleton data
        if hasattr(skeleton, "get_skeleton_data"):
            skeleton_data = skeleton.get_skeleton_data()
        elif hasattr(skeleton, "get_commons_only"):
            skeleton_data = skeleton.get_commons_only()
        else:
            skeleton_data = skeleton

        # Collect all card requests for batch processing
        all_requests = []

        # Initialize complete_set structure
        for color_name, color_data in skeleton_data.items():
            complete_set[color_name] = {}

            if color_name in ["multicolor", "colorless", "lands"]:
                # Handle special sections
                for rarity_name, rarity_data in color_data.items():
                    complete_set[color_name][rarity_name] = {}

                    if isinstance(rarity_data, list):
                        for slot in rarity_data:
                            if isinstance(slot, dict) and "id" in slot:
                                all_requests.append(
                                    (color_name, rarity_name, slot["id"], slot)
                                )
            else:
                # Handle regular colors
                for rarity_name, rarity_data in color_data.items():
                    complete_set[color_name][rarity_name] = {}

                    if isinstance(rarity_data, dict) and not isinstance(
                        rarity_data, list
                    ):
                        # Handle common/uncommon with creatures/spells structure
                        for card_type, cards in rarity_data.items():
                            if isinstance(cards, list):
                                for slot in cards:
                                    if isinstance(slot, dict) and "id" in slot:
                                        all_requests.append(
                                            (color_name, rarity_name, slot["id"], slot)
                                        )
                    elif isinstance(rarity_data, list):
                        # Handle rare/mythic as direct lists
                        for slot in rarity_data:
                            if isinstance(slot, dict) and "id" in slot:
                                all_requests.append(
                                    (color_name, rarity_name, slot["id"], slot)
                                )

        # Process requests in TRUE batches - generate multiple cards per API call
        total_cards = len(all_requests)
        batch_size = 15  # Optimal batch size for GPT-4 to handle reliably
        logger.info(
            f"Processing {total_cards} cards in TRUE BATCHES of {batch_size}..."
        )

        for i in range(0, len(all_requests), batch_size):
            batch_requests = all_requests[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_cards + batch_size - 1) // batch_size

            logger.info(
                f"Processing TRUE BATCH {batch_num}/{total_batches} ({len(batch_requests)} cards in single API call)"
            )

            # Use the actual batch generation method that generates multiple cards in one API call
            batch_cards = self.generate_batch_cards(theme, batch_requests)

            # Place generated cards in the correct positions
            for color_name, rarity_name, slot_id, slot_data in batch_requests:
                if slot_id in batch_cards:
                    complete_set[color_name][rarity_name][slot_id] = batch_cards[
                        slot_id
                    ]
                else:
                    # If batch generation missed this card, raise an error
                    raise ValueError(f"Batch generation missed card {slot_id}")

        generation_time = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Completed TRUE BATCH set generation for '{theme}' in {generation_time:.2f}s ({total_cards} cards)"
        )
        return complete_set

    def generate_complete_set_large_batches(self, theme, skeleton):
        """Generate all cards using large batches for maximum efficiency"""
        start_time = datetime.now()
        logger.info(f"Starting LARGE BATCH set generation for theme '{theme}'")
        complete_set = {}

        # Handle both skeleton objects and direct skeleton data
        if hasattr(skeleton, "get_skeleton_data"):
            skeleton_data = skeleton.get_skeleton_data()
        elif hasattr(skeleton, "get_commons_only"):
            skeleton_data = skeleton.get_commons_only()
        else:
            skeleton_data = skeleton

        # Collect all card requests for batch processing
        all_requests = []

        # Initialize complete_set structure
        for color_name, color_data in skeleton_data.items():
            complete_set[color_name] = {}

            if color_name in ["multicolor", "colorless", "lands"]:
                # Handle special sections
                for rarity_name, rarity_data in color_data.items():
                    complete_set[color_name][rarity_name] = {}

                    if isinstance(rarity_data, list):
                        for slot in rarity_data:
                            if isinstance(slot, dict) and "id" in slot:
                                all_requests.append(
                                    (color_name, rarity_name, slot["id"], slot)
                                )
            else:
                # Handle regular colors
                for rarity_name, rarity_data in color_data.items():
                    complete_set[color_name][rarity_name] = {}

                    if isinstance(rarity_data, dict) and not isinstance(
                        rarity_data, list
                    ):
                        # Handle common/uncommon with creatures/spells structure
                        for card_type, cards in rarity_data.items():
                            if isinstance(cards, list):
                                for slot in cards:
                                    if isinstance(slot, dict) and "id" in slot:
                                        all_requests.append(
                                            (color_name, rarity_name, slot["id"], slot)
                                        )
                    elif isinstance(rarity_data, list):
                        # Handle rare/mythic as direct lists
                        for slot in rarity_data:
                            if isinstance(slot, dict) and "id" in slot:
                                all_requests.append(
                                    (color_name, rarity_name, slot["id"], slot)
                                )

        # Process requests in LARGE batches for maximum efficiency
        total_cards = len(all_requests)
        batch_size = 25  # Large batch size for maximum efficiency
        logger.info(
            f"Processing {total_cards} cards in LARGE BATCHES of {batch_size}..."
        )

        for i in range(0, len(all_requests), batch_size):
            batch_requests = all_requests[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_cards + batch_size - 1) // batch_size

            logger.info(
                f"Processing LARGE BATCH {batch_num}/{total_batches} ({len(batch_requests)} cards in single API call)"
            )

            # Use the batch generation method for maximum efficiency
            batch_cards = self.generate_batch_cards(theme, batch_requests)

            # Place generated cards in the correct positions
            for color_name, rarity_name, slot_id, slot_data in batch_requests:
                if slot_id in batch_cards:
                    complete_set[color_name][rarity_name][slot_id] = batch_cards[
                        slot_id
                    ]
                else:
                    # If batch generation missed this card, raise an error
                    raise ValueError(f"Large batch generation missed card {slot_id}")

        generation_time = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Completed LARGE BATCH set generation for '{theme}' in {generation_time:.2f}s ({total_cards} cards)"
        )
        logger.info(
            f"Average efficiency: {total_cards/generation_time:.1f} cards/second"
        )
        return complete_set
