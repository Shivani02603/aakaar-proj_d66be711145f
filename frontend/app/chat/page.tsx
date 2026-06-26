'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import SessionSidebar from '@/components/SessionSidebar';
import DocumentUploader from '@/components/DocumentUploader';
import ChatWindow from '@/components/ChatWindow';

export default function ChatPage() {
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  return (
    <div className="h-screen flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 text-white">
        <h1 className="text-lg font-bold">Aakaar Project</h1>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-500 hover:bg-red-600 rounded text-sm"
        >
          Logout
        </button>
      </div>
      <div className="flex flex-1">
        <div className="w-64 bg-gray-100 border-r border-gray-300">
          <SessionSidebar
            onSelectSession={handleSelectSession}
            activeSessionId={activeSessionId || undefined}
          />
          <DocumentUploader />
        </div>
        <div className="flex-1">
          <ChatWindow activeSessionId={activeSessionId} />
        </div>
      </div>
    </div>
  );
}