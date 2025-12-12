import React from 'react';
import { MessageSquare, Plus } from 'lucide-react';
import '../styles/Chat.css';

const Sidebar = ({ history, onNewChat, isOpen }) => {
    return (
        <div className={`sidebar ${isOpen ? 'open' : ''}`}>
            <div className="sidebar-header">
                <div className="sidebar-title">
                    <MessageSquare size={24} color="#3b82f6" />
                    <span>FinanceBot</span>
                </div>
            </div>

            <button className="new-chat-btn" onClick={onNewChat}>
                <Plus size={18} />
                New Chat
            </button>

            <div className="history-list">
                {history.map((item, index) => (
                    <div key={index} className="history-item">
                        {item.question}
                    </div>
                ))}
                {history.length === 0 && (
                    <div style={{ padding: '1rem', color: '#64748b', fontSize: '0.9rem', textAlign: 'center' }}>
                        No history yet
                    </div>
                )}
            </div>
        </div>
    );
};

export default Sidebar;
