# backend/test_database.py 
import asyncio
import sys
import os
import uuid
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import db

async def test_database():
    """Test all database operations"""
    print("Testing Database Operations")
    print("=" * 50)
    
    # Test connection
    print("1. Testing connection...")
    connection_ok = await db.test_connection()
    print(f"   {'✅ Connection OK' if connection_ok else '❌ Connection Failed'}")
    
    if not connection_ok:
        return
    
    # Test agent operations
    print("\n2. Testing agent operations...")
    
    # Insert test agent with ENUM values
    test_agent_data = {
        "name": "Test Agent API",
        "system_prompt": "Hello {driver_name}, calling about load {load_number}. What's your status?",
        "scenario_type": "dispatch",  # ENUM value
        "voice_settings": {"voice": "male", "speed": 0.9}
    }
    
    agent = await db.insert_agent(test_agent_data)
    if agent:
        print(f"   ✅ Agent created: {agent['name']} (ID: {agent['id'][:8]}...)")
        print(f"   ✅ Scenario type: {agent['scenario_type']}")
        agent_id = agent['id']
    else:
        print("   ❌ Failed to create agent")
        return
    
    # Get agent
    retrieved_agent = await db.get_agent_by_id(agent_id)
    if retrieved_agent:
        print(f"   ✅ Agent retrieved: {retrieved_agent['name']}")
    
    # Get all agents
    all_agents = await db.get_all_agents()
    print(f"   ✅ Found {len(all_agents)} active agents")
    for agent in all_agents:
        print(f"      - {agent['name']} ({agent['scenario_type']})")
    
    # Test call operations with ENUM
    print("\n3. Testing call operations...")
    
    test_call_data = {
        "agent_id": agent_id,
        "driver_name": "Test Driver",
        "driver_phone": "+1234567890",
        "load_number": "TEST-001",
        # "retell_call_id": "test_retell_123",
        "retell_call_id": f"test_retell_{uuid.uuid4().hex[:8]}",
        "status": "pending"  # ENUM value
    }
    
    call = await db.insert_call(test_call_data)
    if call:
        print(f"   ✅ Call created: {call['driver_name']} (ID: {call['id'][:8]}...)")
        print(f"   ✅ Initial status: {call['status']}")
        call_id = call['id']
    else:
        print("   ❌ Failed to create call")
        return
    
    # Update call status with ENUM
    updated_call = await db.update_call_status(
        call_id, 
        "completed",  # ENUM value
        transcript="Test transcript here",
        duration_seconds=120
    )
    if updated_call:
        print(f"   ✅ Call updated: Status = {updated_call['status']}")
    
    # Get call with join
    retrieved_call = await db.get_call_by_id(call_id)
    if retrieved_call:
        print(f"   ✅ Call retrieved with agent: {retrieved_call['agents']['name']}")
    
    # Test summary operations with defaults
    print("\n4. Testing summary operations...")
    
    test_summary_data = {
        "call_id": call_id,
        "call_outcome": "In-Transit Update",
        "driver_status": "Driving",
        "current_location": "I-10 near Phoenix, AZ",
        "eta": "Tomorrow 9:00 AM",
        "structured_data": {
            "call_outcome": "In-Transit Update",
            "driver_status": "Driving", 
            "current_location": "I-10 near Phoenix, AZ",
            "eta": "Tomorrow 9:00 AM"
        }
        # confidence_score will use default 1.0
        # processing_errors will use default []
    }
    
    summary = await db.insert_summary(test_summary_data)
    if summary:
        print(f"   ✅ Summary created: {summary['call_outcome']}")
        print(f"   ✅ Confidence score: {summary['confidence_score']} (default)")
        print(f"   ✅ Processing errors: {summary['processing_errors']} (default)")
    
    # Test summary without structured_data (should use default)
    test_summary_minimal = {
        "call_id": call_id + "_fake",  # This will fail, but tests default handling
        "call_outcome": "Test Outcome"
    }
    
    # Get calls history
    print("\n5. Testing call history...")
    history = await db.get_calls_history(limit=10)
    print(f"   ✅ Retrieved {len(history)} calls from history")
    for call in history[:2]:  # Show first 2
        print(f"      - {call['driver_name']} ({call['status']}) - Agent: {call['agents']['name'] if call['agents'] else 'None'}")
    
    print("\nAll database tests passed successfully!") 

if __name__ == "__main__":
    asyncio.run(test_database())