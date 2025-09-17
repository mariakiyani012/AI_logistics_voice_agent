
# Test file: backend/test_agents_api.py
import asyncio
import httpx
import json

BASE_URL = "http://0.0.0.0:8000/api"

async def test_agents_api():
    """Test all agent API endpoints"""
    print("Testing Agent API Endpoints")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Get all agents
        print("\n1. Testing GET /agents")
        response = await client.get(f"{BASE_URL}/agents")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {data['total']} agents")
            for agent in data['agents'][:2]:  # Show first 2
                print(f"      - {agent['name']} ({agent['scenario_type']})")
        
        # Test 2: Create new agent
        print("\n2. Testing POST /agents")
        new_agent = {
            "name": "Test API Agent",
            "system_prompt": "Hello {driver_name}, this is a test call about load {load_number}. How are you doing?",
            "scenario_type": "dispatch",
            "voice_settings": {
                "voice": "male",
                "speed": 1.2,
                "interruption_sensitivity": 0.4
            }
        }
        
        response = await client.post(f"{BASE_URL}/agents", json=new_agent)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            created_agent = response.json()
            agent_id = created_agent['id']
            print(f"   ✅ Agent created: {created_agent['name']} (ID: {agent_id[:8]}...)")
        else:
            print(f"   ❌ Failed to create agent: {response.text}")
            return
        
        # Test 3: Get specific agent
        print("\n3. Testing GET /agents/{id}")
        response = await client.get(f"{BASE_URL}/agents/{agent_id}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            agent = response.json()
            print(f"   ✅ Retrieved agent: {agent['name']}")
            print(f"   ✅ Scenario type: {agent['scenario_type']}")
        
        # Test 4: Update agent
        print("\n4. Testing PUT /agents/{id}")
        update_data = {
            "name": "Updated Test API Agent",
            "voice_settings": {
                "voice": "female",
                "speed": 0.8
            }
        }
        
        response = await client.put(f"{BASE_URL}/agents/{agent_id}", json=update_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            updated_agent = response.json()
            print(f"   ✅ Agent updated: {updated_agent['name']}")
            print(f"   ✅ Voice settings updated: {updated_agent['voice_settings']}")
        
        # Test 5: Delete agent (soft delete)
        print("\n5. Testing DELETE /agents/{id}")
        response = await client.delete(f"{BASE_URL}/agents/{agent_id}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result['message']}")
        
        # Test 6: Verify soft delete
        print("\n6. Verifying soft delete...")
        response = await client.get(f"{BASE_URL}/agents")
        if response.status_code == 200:
            data = response.json()
            active_agents = [a for a in data['agents'] if a['is_active']]
            print(f"   ✅ Active agents after deletion: {len(active_agents)}")
        
        # Test 7: Error cases
        print("\n7. Testing error cases...")
        
        # Invalid agent creation (missing placeholders)
        invalid_agent = {
            "name": "Invalid Agent",
            "system_prompt": "Hello there, no placeholders here!",
            "scenario_type": "dispatch"
        }
        
        response = await client.post(f"{BASE_URL}/agents", json=invalid_agent)
        print(f"   Invalid agent creation status: {response.status_code}")
        if response.status_code == 422:
            print("   ✅ Properly rejected invalid prompt")
        
        # Non-existent agent
        response = await client.get(f"{BASE_URL}/agents/fake-id-123")
        print(f"   Non-existent agent status: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Properly returned 404 for non-existent agent")
    
    print("\n🎉 All API tests completed!")

if __name__ == "__main__":
    print("Make sure your FastAPI server is running on 0.0.0.0:8000")
    print("Press Enter to start tests...")
    input()
    asyncio.run(test_agents_api())