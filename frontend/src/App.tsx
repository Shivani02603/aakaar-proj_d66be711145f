import { useState } from 'react';
import ChatWindow from '@/components/ChatWindow';
import DocumentUploader from '@/components/DocumentUploader';
import SessionSidebar from '@/components/SessionSidebar';

const App = () => {
  const [activeSessionId, setActiveSessionId] = useState<string | undefined>(undefined);

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
  };

  return (
    <div className="h-screen flex flex-col">
      <header className="flex items-center justify-between px-4 py-2 bg-gray-800 text-white">
        <h1 className="text-lg font-bold">Aakaar Project</h1>
        <button
          onClick={() => setActiveSessionId(undefined)}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
        >
          New Chat
        </button>
      </header>
      <div className="flex flex-1">
        <aside className="w-64 bg-gray-100 border-r border-gray-300 flex flex-col">
          <SessionSidebar
            onSelectSession={handleSelectSession}
            activeSessionId={activeSessionId}
          />
          <div className="mt-auto p-4">
            <DocumentUploader sessionId={activeSessionId} />
          </div>
        </aside>
        <main className="flex-1 flex flex-col">
          <ChatWindow activeSessionId={activeSessionId} />
        </main>
      </div>
    </div>
  );
};

export default App;