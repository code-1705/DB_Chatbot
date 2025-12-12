import React from 'react';
import { User, Bot } from 'lucide-react';
import { marked } from 'marked';
import '../styles/Chat.css';

const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';

    // Render markdown safely
    const renderContent = () => {
        if (isUser) return message.content;
        const html = marked.parse(message.content || "");
        return <div dangerouslySetInnerHTML={{ __html: html }} />;
    };

    return (
        <div className={`message-wrapper ${isUser ? 'user' : 'ai'}`}>
            <div className="avatar">
                {isUser ? <User size={20} color="#fff" /> : <Bot size={20} color="#3b82f6" />}
            </div>
            <div className="message-content">
                {renderContent()}
            </div>
        </div>
    );
};

export default MessageBubble;
