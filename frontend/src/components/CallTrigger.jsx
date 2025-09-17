
import React, { useState, useEffect } from 'react';
import { Phone, Send } from 'lucide-react';
import { getAgents, triggerCall } from '../services/api';

const CallTrigger = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    agent_id: '',
    driver_name: '',
    driver_phone: '',
    load_number: ''
  });

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await getAgents();
      setAgents(response.agents);
      if (response.agents.length > 0) {
        setFormData(prev => ({ ...prev, agent_id: response.agents[0].id }));
      }
    } catch (err) {
      setError('Failed to fetch agents');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const result = await triggerCall(formData);
      setSuccess(`Call triggered successfully! Call ID: ${result.id}`);
      
      // Reset form
      setFormData({
        agent_id: agents.length > 0 ? agents[0].id : '',
        driver_name: '',
        driver_phone: '',
        load_number: ''
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to trigger call');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center gap-3 mb-6">
          <Phone className="text-blue-500" size={28} />
          <h2 className="text-2xl font-bold text-gray-800">Trigger Test Call</h2>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Agent
            </label>
            <select
              value={formData.agent_id}
              onChange={(e) => setFormData({...formData, agent_id: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">Choose an agent...</option>
              {agents.map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.name} ({agent.scenario_type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Driver Name
            </label>
            <input
              type="text"
              value={formData.driver_name}
              onChange={(e) => setFormData({...formData, driver_name: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., John Smith"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Driver Phone Number
            </label>
            <input
              type="tel"
              value={formData.driver_phone}
              onChange={(e) => setFormData({...formData, driver_phone: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., +1234567890"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Load Number
            </label>
            <input
              type="text"
              value={formData.load_number}
              onChange={(e) => setFormData({...formData, load_number: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., LOAD-7891-B"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 text-white px-6 py-4 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 text-lg font-semibold"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Triggering Call...
              </>
            ) : (
              <>
                <Send size={24} />
                Start Test Call
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CallTrigger;