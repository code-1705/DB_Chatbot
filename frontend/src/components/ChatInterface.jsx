import React, { useState, useEffect, useRef } from 'react';
import { Send, Menu, Bot, Building2 } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';
import MessageBubble from './MessageBubble';
import '../styles/Chat.css';

const BASE_URL = '';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [userId, setUserId] = useState('');
    const [selectedCompany, setSelectedCompany] = useState('Google');
    const messagesEndRef = useRef(null);

    // Initialize Session
    useEffect(() => {
        let storedId = localStorage.getItem('chat_user_id');
        if (!storedId) {
            storedId = uuidv4();
            localStorage.setItem('chat_user_id', storedId);
        }
        setUserId(storedId);
        fetchHistory(storedId);
    }, []);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const fetchHistory = async (uid) => {
        try {
            const res = await fetch(`${BASE_URL}/history/${uid}`);
            if (res.ok) {
                const data = await res.json();
                const historyList = data.history || [];

                // ALSO restore them to the main chat window
                const restoredMessages = [];
                historyList.forEach(item => {
                    if (item.question) {
                        restoredMessages.push({ role: 'user', content: item.question });
                    }
                    if (item.answer) {
                        restoredMessages.push({ role: 'assistant', content: item.answer });
                    }
                });
                setMessages(restoredMessages);
            }
        } catch (err) {
            console.error("Failed to load history", err);
        }
    };

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            // Using relative URL which is proxied
            const res = await fetch(`${BASE_URL}/chat/${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMsg.content,
                    company: selectedCompany
                }),
            });

            if (!res.ok) {
                // Try to get error text if available
                const errText = await res.text();
                throw new Error(`Server Error (${res.status}): ${errText || res.statusText}`);
            }

            const data = await res.json();

            // Validate response data
            if (!data || !data.response) {
                throw new Error('Invalid response format from server');
            }

            const aiMsg = { role: 'assistant', content: data.response };
            setMessages(prev => [...prev, aiMsg]);

            // Refresh history
            fetchHistory(userId);
        } catch (error) {
            console.error("Chat Error:", error);
            // Safe fallback message
            const errorMsg = { role: 'assistant', content: `**Error**: ${error.message}. Please try again.` };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="app-container">
            <div className="chat-area">
                <header className="chat-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div>
                            <div style={{ fontWeight: '600' }}>Sales Assistant</div>
                            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Connected to MongoDB</div>
                        </div>
                    </div>

                    <div className="company-selector">
                        <Building2 size={16} color="#94a3b8" />
                        <select
                            value={selectedCompany}
                            onChange={(e) => setSelectedCompany(e.target.value)}
                            className="company-select"
                        >
                            <option value="Google">Google</option>
                            <option value="Microsoft">Microsoft</option>
                            <option value="Apple">Apple</option>
                            <option value="Tesla">Tesla</option>
                            <option value="Amazon">Amazon</option>
                        </select>
                    </div>
                </header>

                <div className="messages-container">
                    {messages.length === 0 && (
                        <div style={{ textAlign: 'center', marginTop: '20vh', color: '#64748b' }}>
                            <h2>Welcome!</h2>
                            <p>Ask me about sales data for <b>{selectedCompany}</b>.</p>
                            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                                <span style={{ background: '#1e293b', padding: '0.5rem 1rem', borderRadius: '20px', fontSize: '0.85rem' }}>"Show me sales for {selectedCompany}"</span>
                                <span style={{ background: '#1e293b', padding: '0.5rem 1rem', borderRadius: '20px', fontSize: '0.85rem' }}>"Total revenue trend?"</span>
                            </div>
                        </div>
                    )}

                    {messages.map((msg, idx) => (
                        <MessageBubble key={idx} message={msg} />
                    ))}

                    {isLoading && (
                        <div className="message-wrapper ai">
                            <div className="avatar">
                                <Bot size={20} color="#3b82f6" />
                            </div>
                            <div className="message-content">
                                <div className="typing-indicator">
                                    <div className="dot"></div>
                                    <div className="dot"></div>
                                    <div className="dot"></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="input-area">
                    <div className="input-container">
                        <input
                            type="text"
                            className="chat-input"
                            placeholder={`Ask about ${selectedCompany} sales...`}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyPress}
                            disabled={isLoading}
                        />
                        <button
                            className="send-btn"
                            onClick={handleSend}
                            disabled={!input.trim() || isLoading}
                        >
                            <Send size={20} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
