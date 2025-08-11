#!/usr/bin/env python3
"""
Simple test script to verify the API key functionality works
"""

import requests
import json


def test_api_key_required():
    """Test that API endpoints require an API key"""

    # Test generate-card endpoint without API key
    print("Testing generate-card endpoint without API key...")
    response = requests.post(
        "http://localhost:5000/api/generate-card",
        json={
            "theme": "test theme",
            "color": "white",
            "rarity": "common",
            "slot_id": "test_slot",
            "slot_data": {"description": "test card"},
        },
    )

    if response.status_code == 400 and "API key is required" in response.json().get(
        "error", ""
    ):
        print("✅ generate-card correctly requires API key")
    else:
        print(f"❌ generate-card failed: {response.status_code} - {response.json()}")

    # Test generate-set-concept endpoint without API key
    print("Testing generate-set-concept endpoint without API key...")
    response = requests.post(
        "http://localhost:5000/api/generate-set-concept", json={"pitch": "test pitch"}
    )

    if response.status_code == 400 and "API key is required" in response.json().get(
        "error", ""
    ):
        print("✅ generate-set-concept correctly requires API key")
    else:
        print(
            f"❌ generate-set-concept failed: {response.status_code} - {response.json()}"
        )

    print("\nAPI key requirement tests completed!")


if __name__ == "__main__":
    test_api_key_required()
