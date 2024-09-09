import { useState, useEffect } from 'react';

export default function Home() {
    const [inputText, setInputText] = useState('');
    const [conversation, setConversation] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleTextSubmit = async () => {
        setIsLoading(true);
        const res = await fetch('http://localhost:8000/text-chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: inputText })
        });
        const data = await res.json();
        setConversation([...conversation, { user: inputText, assistant: data.reply }]);
        setInputText('');
        setIsLoading(false);
    };

    const handleVoiceSubmit = async () => {
        // Add voice input handling logic here
    };

    return (
        <div className="container">
            <div className="chat-window">
                {conversation.map((msg, idx) => (
                    <div key={idx} className="message">
                        <div className="user-msg">{msg.user}</div>
                        <div className="assistant-msg">{msg.assistant}</div>
                    </div>
                ))}
            </div>
            <div className="input-area">
                <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Type your message here"
                />
                <button onClick={handleTextSubmit} disabled={isLoading}>
                    {isLoading ? 'Loading...' : 'Send'}
                </button>
                <button onClick={handleVoiceSubmit}>🎤 Voice Input</button>
            </div>
        </div>
    );
}
