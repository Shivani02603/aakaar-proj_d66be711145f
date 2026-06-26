import React, { useEffect, useRef, useState } from 'react';
import { getMessages, queryAI } from '@/src/lib/aiApi';
import MessageBubble from '@/src/components/MessageBubble';
import TypingIndicator from '@/src/components/TypingIndicator';

interface ChatWindowProps {
  sessionId: string | null;
}

interface Message {
  id: string;
  role: string;
  content: string;
  sources?: string[];
}

const ChatWindow: React.FC<ChatWindowProps> = ({ sessionId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      return;
    }

    const fetchMessages = async () => {
      setLoading(true);
      setError(null);
      try {
        const fetchedMessages = await getMessages(sessionId);
        setMessages(fetchedMessages.map((msg: any) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          sources: msg.citations || [],
        })));
      } catch (err) {
        setError('Failed to load messages.');
      } finally {
        setLoading(false);
      }
    };

    fetchMessages();
  }, [sessionId]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !sessionId || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuery('');
    setLoading(true);
    setError(null);

    try {
      const response = await queryAI(query, sessionId);
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError('Failed to fetch response.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-100">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {!sessionId ? (
          <div className="text-center text-gray-500">No session selected.</div>
        ) : messages.length === 0 ? (
          <div className="text-center text-gray-500">No messages yet.</div>
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={message.id}
              role={message.role}
              content={message.content}
              sources={message.sources}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      {error && <div className="text-red-500 text-center p-2">{error}</div>}
      <form
        onSubmit={handleSubmit}
        className="flex items-center p-4 border-t bg-white"
      >
        <textarea
          className="flex-1 border rounded-md p-2 resize-none focus:outline-none focus:ring focus:ring-blue-300"
          rows={1}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
          onKeyDown={(e) => {
            if (e.ctrlKey && e.key === 'Enter') {
              handleSubmit(e);
            }
          }}
        />
        <button
          type="submit"
          className="ml-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300"
          disabled={loading}
        >
          Send
        </button>
      </form>
      {loading && <TypingIndicator />}
    </div>
  );
};

export default ChatWindow;