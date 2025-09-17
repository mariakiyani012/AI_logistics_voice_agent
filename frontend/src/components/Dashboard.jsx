import React, { useState } from 'react';
import { Settings, Phone, History, Menu, X } from 'lucide-react';
import AgentConfig from './AgentConfig';
import CallTrigger from './CallTrigger';
import CallHistory from './CallHistory';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('trigger');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const tabs = [
    { id: 'trigger', label: 'Trigger Call', icon: Phone, component: CallTrigger },
    { id: 'agents', label: 'Agent Config', icon: Settings, component: AgentConfig },
    { id: 'history', label: 'Call History', icon: History, component: CallHistory },
  ];

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || CallTrigger;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-800"
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <h1 className="text-2xl font-bold text-gray-800">AI Voice Agent Dashboard</h1>
          </div>
          <div className="hidden sm:flex items-center gap-2 text-sm text-gray-600">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            Backend Connected
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 
          w-64 bg-white border-r border-gray-200 transition-transform duration-300 ease-in-out
        `}>
          <nav className="mt-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    setSidebarOpen(false);
                  }}
                  className={`
                    w-full flex items-center gap-3 px-6 py-3 text-left transition-colors
                    ${activeTab === tab.id 
                      ? 'bg-blue-50 text-blue-600 border-r-2 border-blue-600' 
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
                    }
                  `}
                >
                  <Icon size={20} />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </aside>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div 
            className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main Content */}
        <main className="flex-1 lg:ml-0 p-6">
          <ActiveComponent />
        </main>
      </div>
    </div>
  );
};

export default Dashboard;