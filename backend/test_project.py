# backend/test_project.py
import asyncio
import httpx
import json
import websockets
from datetime import datetime

# Test Configuration
BASE_URL = "http://localhost:8000"
NGROK_URL = "https://4dac8660024a.ngrok-free.app"  # Replace with your actual ngrok URL

class ProjectTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_agent_id = None
        self.test_call_id = None
        
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Starting AI Voice Agent Test Suite")
        print("=" * 50)
        
        # Test sequence
        await self.test_1_health_check()
        await self.test_2_database_connection()
        await self.test_3_retell_connection()
        await self.test_4_create_agent()
        await self.test_5_trigger_call()
        await self.test_6_webhook_simulation()
        await self.test_7_websocket_connection()
        await self.test_8_cleanup()
        
        print("\n✅ Test suite completed!")
    
    async def test_1_health_check(self):
        """Test basic API health"""
        print("\n1. Testing API Health...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                assert response.status_code == 200
                print(f"   ✅ API is healthy: {response.json()}")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
    
    async def test_2_database_connection(self):
        """Test database connectivity"""
        print("\n2. Testing Database Connection...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/test-db")
                if response.status_code == 200:
                    print(f"   ✅ Database connected: {response.json()}")
                else:
                    print(f"   ⚠️ Database connection issue: {response.text}")
        except Exception as e:
            print(f"   ❌ Database test failed: {e}")
    
    async def test_3_retell_connection(self):
        """Test Retell AI connection"""
        print("\n3. Testing Retell AI Connection...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/calls/retell-info")
                data = response.json()
                if data.get("success"):
                    print(f"   ✅ Retell connected: {data.get('data', {}).get('phone_numbers_count', 0)} phone numbers")
                    if data.get("data", {}).get("warnings"):
                        print(f"   ⚠️ Warnings: {data['data']['warnings']}")
                else:
                    print(f"   ❌ Retell connection failed: {data.get('message')}")
        except Exception as e:
            print(f"   ❌ Retell test failed: {e}")
    
    async def test_4_create_agent(self):
        """Test agent creation"""
        print("\n4. Testing Agent Creation...")
        try:
            agent_data = {
                "name": f"Test Agent {datetime.now().strftime('%H%M%S')}",
                "system_prompt": "You are a logistics assistant helping driver {driver_name} with load {load_number}. Ask for their current location and ETA.",
                "scenario_type": "dispatch",
                "voice_settings": {"voice": "male", "speed": 1.0}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/agents/", json=agent_data)
                if response.status_code == 201:
                    agent = response.json()
                    self.test_agent_id = agent["id"]
                    print(f"   ✅ Agent created: {agent['name']} ({self.test_agent_id[:8]}...)")
                else:
                    print(f"   ❌ Agent creation failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Agent creation test failed: {e}")
    
    async def test_5_trigger_call(self):
        """Test call triggering"""
        print("\n5. Testing Call Trigger...")
        if not self.test_agent_id:
            print("   ⚠️ Skipping call test - no agent created")
            return
            
        try:
            call_data = {
                "agent_id": self.test_agent_id,
                "driver_name": "John Doe",
                "driver_phone": "+923494785382",  # Test number
                "load_number": "LD-12345"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.base_url}/api/calls/trigger", json=call_data)
                if response.status_code == 201:
                    call = response.json()
                    self.test_call_id = call["id"]
                    print(f"   ✅ Call triggered: {call['status']} ({self.test_call_id[:8]}...)")
                else:
                    print(f"   ❌ Call trigger failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Call trigger test failed: {e}")
    
    
    async def test_6_webhook_simulation(self):
        """Test webhook handling"""
        print("\n6. Testing Webhook Simulation...")
        if not self.test_call_id:
            print("   ⚠️ Skipping webhook test - no call created")
            return
            
        try:
            # Create separate clients for each request
            async with httpx.AsyncClient() as client:
                # Simulate call_started webhook
                webhook_data = {
                    "event": "call_started",
                    "call": {
                        "call_id": "retell_test_123",
                        "from_number": "+1234567890",
                        "to_number": "+0987654321",
                        "start_timestamp": datetime.now().isoformat(),
                        "metadata": {"call_id": self.test_call_id}
                    }
                }
                
                response = await client.post(f"{self.base_url}/webhook/retell", json=webhook_data)
                if response.status_code == 200:
                    print("   ✅ Webhook call_started processed")
                else:
                    print(f"   ❌ Webhook failed: {response.text}")
                    
            # NEW CLIENT for second request
            async with httpx.AsyncClient() as client:
                # Simulate call_ended webhook
                webhook_data["event"] = "call_ended"
                webhook_data["call"]["transcript"] = "Hello, this is a test call transcript."
                webhook_data["call"]["call_status"] = "completed"
                webhook_data["call"]["disconnection_reason"] = "agent_hangup"
                
                response = await client.post(f"{self.base_url}/webhook/retell", json=webhook_data)
                if response.status_code == 200:
                    print("   ✅ Webhook call_ended processed")
                else:
                    print(f"   ❌ Webhook call_ended failed: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Webhook simulation failed: {e}")
    
    async def test_7_websocket_connection(self):
        """Test WebSocket connectivity"""
        print("\n7. Testing WebSocket Connection...")
        try:
            # Test ping-pong
            ws_url = f"ws://localhost:8000/llm-websocket"
            
            async with websockets.connect(ws_url) as websocket:
                # Send ping
                ping_message = {
                    "interaction_type": "ping",
                    "call_id": "test_call"
                }
                await websocket.send(json.dumps(ping_message))
                
                # Wait for pong
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get("response_type") == "pong":
                    print("   ✅ WebSocket ping-pong successful")
                else:
                    print(f"   ❌ Unexpected WebSocket response: {response_data}")
                    
        except asyncio.TimeoutError:
            print("   ❌ WebSocket timeout - check if endpoint is running")
        except Exception as e:
            print(f"   ❌ WebSocket test failed: {e}")
    
    async def test_8_cleanup(self):
        """Clean up test data"""
        print("\n8. Cleaning up test data...")
        try:
            if self.test_agent_id:
                async with httpx.AsyncClient() as client:
                    response = await client.delete(f"{self.base_url}/api/agents/{self.test_agent_id}")
                    if response.status_code == 200:
                        print("   ✅ Test agent deleted")
                    else:
                        print(f"   ⚠️ Could not delete test agent: {response.text}")
        except Exception as e:
            print(f"   ⚠️ Cleanup failed: {e}")
    
    async def test_call_flow(self):
        """Test complete call flow with actual Retell integration"""
        print("\n🔄 Testing Complete Call Flow...")
        if not self.test_agent_id:
            print("   ⚠️ No agent available for call flow test")
            return
            
        try:
            call_data = {
                "agent_id": self.test_agent_id,
                "driver_name": "Test Driver",
                "driver_phone": "+1234567890",  # Use a test number or your number
                "load_number": "TEST-001"
            }
            
            print("   📞 Triggering real call...")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.base_url}/api/calls/trigger", json=call_data)
                
                if response.status_code == 201:
                    call = response.json()
                    call_id = call["id"]
                    print(f"   ✅ Call initiated: {call_id[:8]}...")
                    
                    # Monitor call status
                    for i in range(10):  # Check for 30 seconds
                        await asyncio.sleep(3)
                        status_response = await client.get(f"{self.base_url}/api/calls/{call_id}")
                        if status_response.status_code == 200:
                            call_status = status_response.json()
                            print(f"   📊 Call status: {call_status['status']}")
                            if call_status['status'] in ['completed', 'failed']:
                                break
                        else:
                            print(f"   ❌ Could not get call status")
                            break
                else:
                    print(f"   ❌ Call flow test failed: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Call flow test error: {e}")

# Quick individual tests
async def quick_test_retell():
    """Quick Retell connection test"""
    print("🔗 Quick Retell Test...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/calls/retell-info")
            data = response.json()
            print(f"Success: {data.get('success')}")
            if data.get('data'):
                print(f"Phone numbers: {data['data'].get('phone_numbers_count', 0)}")
                print(f"Can make calls: {data['data'].get('can_make_calls', False)}")
    except Exception as e:
        print(f"Error: {e}")

async def quick_test_database():
    """Quick database test"""
    print("🗄️ Quick Database Test...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/test-db")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

# Main execution
if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Full test suite")
    print("2. Quick Retell test")
    print("3. Quick database test")
    print("4. Real call flow test")
    
    choice = input("Enter choice (1-4): ")
    
    if choice == "1":
        tester = ProjectTester()
        asyncio.run(tester.run_all_tests())
    elif choice == "2":
        asyncio.run(quick_test_retell())
    elif choice == "3":
        asyncio.run(quick_test_database())
    elif choice == "4":
        tester = ProjectTester()
        asyncio.run(tester.test_4_create_agent())
        asyncio.run(tester.test_call_flow())
    else:
        print("Invalid choice")