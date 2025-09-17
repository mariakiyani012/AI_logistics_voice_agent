
import React, { useState, useEffect } from 'react';
import { Phone, Clock, User, FileText, Eye, X } from 'lucide-react';
import { getCalls, getCallSummary } from '../services/api';

const CallHistory = () => {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCall, setSelectedCall] = useState(null);
  const [callSummary, setCallSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);

  useEffect(() => {
    fetchCalls();
  }, []);

  const fetchCalls = async () => {
    try {
      setLoading(true);
      const response = await getCalls();
      setCalls(response.calls);
    } catch (err) {
      setError('Failed to fetch calls');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (call) => {
    setSelectedCall(call);
    setSummaryLoading(true);
    setCallSummary(null);

    try {
      const summary = await getCallSummary(call.id);
      setCallSummary(summary);
    } catch (err) {
      console.error('Failed to fetch summary:', err);
      setCallSummary({ error: 'Summary not available' });
    } finally {
      setSummaryLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      'in_progress': 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="flex justify-center p-8">Loading call history...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Call History</h2>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="grid gap-4">
        {calls.map((call) => (
          <div key={call.id} className="bg-white rounded-lg border shadow-sm p-6">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-4 mb-3">
                  <div className="flex items-center gap-2">
                    <User size={18} className="text-gray-500" />
                    <span className="font-semibold">{call.driver_name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone size={18} className="text-gray-500" />
                    <span className="text-gray-600">{call.driver_phone}</span>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(call.status)}`}>
                    {call.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">Load Number:</span> {call.load_number}
                  </div>
                  <div>
                    <span className="font-medium">Agent:</span> {call.agents?.name || 'N/A'}
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock size={16} />
                    <span>{formatDate(call.created_at)}</span>
                  </div>
                  <div>
                    <span className="font-medium">Type:</span> {call.agents?.scenario_type || 'N/A'}
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleViewDetails(call)}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 flex items-center gap-2"
              >
                <Eye size={18} />
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>

      {calls.length === 0 && !loading && (
        <div className="text-center py-12">
          <Phone size={48} className="mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600">No calls found. Trigger your first call to see it here!</p>
        </div>
      )}

      {/* Call Details Modal */}
      {selectedCall && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold">Call Details</h3>
              <button
                onClick={() => setSelectedCall(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X size={24} />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-6 mb-6">
              <div>
                <h4 className="font-semibold text-gray-800 mb-3">Call Information</h4>
                <div className="space-y-2 text-sm">
                  <div><span className="font-medium">Driver:</span> {selectedCall.driver_name}</div>
                  <div><span className="font-medium">Phone:</span> {selectedCall.driver_phone}</div>
                  <div><span className="font-medium">Load Number:</span> {selectedCall.load_number}</div>
                  <div><span className="font-medium">Status:</span> {selectedCall.status}</div>
                  <div><span className="font-medium">Started:</span> {formatDate(selectedCall.created_at)}</div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-800 mb-3">Agent Information</h4>
                <div className="space-y-2 text-sm">
                  <div><span className="font-medium">Agent:</span> {selectedCall.agents?.name || 'N/A'}</div>
                  <div><span className="font-medium">Type:</span> {selectedCall.agents?.scenario_type || 'N/A'}</div>
                  <div><span className="font-medium">Call ID:</span> {selectedCall.id.slice(0, 8)}...</div>
                </div>
              </div>
            </div>

            {/* Transcript Section */}
            {selectedCall.transcript && (
              <div className="mb-6">
                <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <FileText size={18} />
                  Transcript
                </h4>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <pre className="whitespace-pre-wrap text-sm">{selectedCall.transcript}</pre>
                </div>
              </div>
            )}

            {/* Summary Section */}
            <div>
              <h4 className="font-semibold text-gray-800 mb-3">Call Summary</h4>
              {summaryLoading ? (
                <div className="flex justify-center p-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                </div>
              ) : callSummary?.error ? (
                <div className="bg-yellow-50 p-4 rounded-lg text-yellow-700">
                  {callSummary.error}
                </div>
              ) : callSummary ? (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                    {callSummary.call_outcome && (
                      <div><span className="font-medium">Outcome:</span> {callSummary.call_outcome}</div>
                    )}
                    {callSummary.driver_status && (
                      <div><span className="font-medium">Driver Status:</span> {callSummary.driver_status}</div>
                    )}
                    {callSummary.current_location && (
                      <div><span className="font-medium">Location:</span> {callSummary.current_location}</div>
                    )}
                    {callSummary.eta && (
                      <div><span className="font-medium">ETA:</span> {callSummary.eta}</div>
                    )}
                    {callSummary.emergency_type && (
                      <div><span className="font-medium">Emergency Type:</span> {callSummary.emergency_type}</div>
                    )}
                    {callSummary.emergency_location && (
                      <div><span className="font-medium">Emergency Location:</span> {callSummary.emergency_location}</div>
                    )}
                  </div>
                  
                  <div className="mt-4">
                    <span className="font-medium">Structured Data:</span>
                    <pre className="mt-2 text-xs bg-white p-3 rounded border overflow-x-auto">
                      {JSON.stringify(callSummary.structured_data, null, 2)}
                    </pre>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CallHistory;