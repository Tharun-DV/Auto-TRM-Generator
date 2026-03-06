#!/usr/bin/env python3
"""Test script for draft management functionality."""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the required modules before importing app
import unittest.mock as mock

# Mock Slack modules
sys.modules['slack_bolt'] = mock.MagicMock()
sys.modules['slack_bolt.adapter.socket_mode'] = mock.MagicMock()
sys.modules['slack_sdk.web.client'] = mock.MagicMock()
sys.modules['confluence_integration'] = mock.MagicMock()

# Now import draft functions from app
from app import (
    save_draft, 
    load_draft, 
    delete_draft, 
    has_draft, 
    get_draft_timestamp,
    trm_session_data,
    DRAFTS_DIR
)

def test_draft_functionality():
    """Test all draft management functions."""
    print("🧪 Testing Draft Management Functionality\n")
    
    # Test user ID
    test_user_id = "U_TEST_USER"
    
    # Clean up any existing test draft
    if has_draft(test_user_id):
        delete_draft(test_user_id)
        print("🧹 Cleaned up existing test draft")
    
    # Test 1: Check no draft exists initially
    print("✅ Test 1: No draft exists initially")
    assert has_draft(test_user_id) == False, "Draft should not exist initially"
    assert load_draft(test_user_id) is None, "Load should return None when no draft exists"
    print("   ✓ Passed\n")
    
    # Test 2: Create session data and save draft
    print("✅ Test 2: Save draft")
    trm_session_data[test_user_id] = {
        "metadata": {
            "week_number": "10",
            "date_range": "Mar 2 to Mar 8",
            "oncall": "<@U123456>",
            "oncall_names": "Test User"
        },
        "issues": [
            {"theme": "Compute", "description": "High CPU usage"}
        ],
        "metrics": [
            {"metric_name": "P1 Alerts", "last_week": "5", "current_week": "8", "delta": "+3"}
        ],
        "alerts": [],
        "cost": [],
        "outages": [],
        "tickets": [],
        "action_items": []
    }
    
    result = save_draft(test_user_id)
    assert result == True, "Save should return True"
    assert has_draft(test_user_id) == True, "Draft should exist after save"
    print("   ✓ Draft saved successfully\n")
    
    # Test 3: Load draft and verify data
    print("✅ Test 3: Load draft")
    loaded_draft = load_draft(test_user_id)
    assert loaded_draft is not None, "Load should return data"
    assert "data" in loaded_draft, "Draft should have 'data' key"
    assert "timestamp" in loaded_draft, "Draft should have 'timestamp' key"
    assert "last_saved" in loaded_draft, "Draft should have 'last_saved' key"
    
    # Verify data integrity
    assert loaded_draft["data"]["metadata"]["week_number"] == "10"
    assert len(loaded_draft["data"]["issues"]) == 1
    assert loaded_draft["data"]["issues"][0]["theme"] == "Compute"
    assert len(loaded_draft["data"]["metrics"]) == 1
    print("   ✓ Draft loaded successfully")
    print(f"   ✓ Last saved: {loaded_draft['last_saved']}\n")
    
    # Test 4: Get timestamp
    print("✅ Test 4: Get timestamp")
    timestamp = get_draft_timestamp(test_user_id)
    assert timestamp is not None, "Timestamp should exist"
    assert isinstance(timestamp, str), "Timestamp should be a string"
    print(f"   ✓ Timestamp: {timestamp}\n")
    
    # Test 5: Verify file exists on disk
    print("✅ Test 5: Verify file on disk")
    draft_path = os.path.join(DRAFTS_DIR, f"{test_user_id}.json")
    assert os.path.exists(draft_path), "Draft file should exist on disk"
    
    # Read and verify JSON structure
    with open(draft_path, 'r') as f:
        file_data = json.load(f)
    assert "data" in file_data
    assert "timestamp" in file_data
    print(f"   ✓ File exists at: {draft_path}\n")
    
    # Test 6: Delete draft
    print("✅ Test 6: Delete draft")
    result = delete_draft(test_user_id)
    assert result == True, "Delete should return True"
    assert has_draft(test_user_id) == False, "Draft should not exist after delete"
    assert not os.path.exists(draft_path), "Draft file should be deleted from disk"
    print("   ✓ Draft deleted successfully\n")
    
    # Test 7: Verify cleanup
    print("✅ Test 7: Verify cleanup")
    assert load_draft(test_user_id) is None, "Load should return None after delete"
    assert get_draft_timestamp(test_user_id) is None, "Timestamp should be None after delete"
    print("   ✓ Cleanup verified\n")
    
    # Clean up session data
    if test_user_id in trm_session_data:
        del trm_session_data[test_user_id]
    
    print("=" * 50)
    print("🎉 All Tests Passed!")
    print("=" * 50)
    print("\n✅ Draft management functionality is working correctly!")

if __name__ == "__main__":
    try:
        test_draft_functionality()
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
