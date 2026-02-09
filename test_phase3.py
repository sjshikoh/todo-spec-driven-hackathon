#!/usr/bin/env python3
"""
Test script for Phase III implementation.
Tests AI endpoints without requiring OpenAI API key.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_ai_health():
    """Test AI health endpoint"""
    print("Testing /ai/health endpoint...")
    response = requests.get(f"{BASE_URL}/ai/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_root():
    """Test root endpoint"""
    print("Testing / endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Phase III Integration Test")
    print("=" * 60)
    print()

    try:
        test_root()
        test_ai_health()
        print("✓ All tests passed!")
    except Exception as e:
        print(f"✗ Test failed: {e}")
