
const testFrontendAPI = async () => {
  const baseURL = 'http://0.0.0.0:8000/api';
  
  try {
    // Test health check
    const health = await fetch(`${baseURL.replace('/api', '')}/health`);
    console.log('Health check:', await health.json());
    
    // Test get agents
    const agents = await fetch(`${baseURL}/agents`);
    console.log('Agents:', await agents.json());
    
    // Test get calls
    const calls = await fetch(`${baseURL}/calls`);
    console.log('Calls:', await calls.json());
    
    console.log('✅ All API tests passed!');
  } catch (error) {
    console.error('❌ API test failed:', error);
  }
};