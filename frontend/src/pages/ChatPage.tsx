import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { sendChatMessage, Message } from "../api/ai";

export default function ChatPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hi! I'm ArogyaMitra, your AI fitness coach. How can I help you crush your goals today?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    const userMsg: Message = { role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const history = [...messages, userMsg].filter(m => m.role !== "system");
      const reply = await sendChatMessage(history);
      setMessages(prev => [...prev, { role: "assistant", content: reply }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: "assistant", content: "I'm having trouble connecting right now. Stick to your basics: stay hydrated and rest well!" }]);
    } finally {
      setLoading(false);
    }
  };

  const formatText = (text: string) => {
    return text.split('\n').map((line, i) => {
      const parts = line.split(/(\*\*.*?\*\*)/g).map((part, j) => {
         if (part.startsWith('**') && part.endsWith('**')) {
             return <strong key={j} className="text-cyan-300 font-bold">{part.slice(2, -2)}</strong>;
         }
         return part;
      });
      return <p key={i} className="min-h-[1.5rem] leading-relaxed">{parts}</p>;
    });
  };

  const suggestions = [
    "How is my progress?",
    "Improve my squat form",
    "What should I eat today?",
    "Am I losing weight?"
  ];

  return (
    <div className="flex h-screen flex-col bg-gradient-to-br from-gray-900 via-gray-950 to-black">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/10 bg-white/5 px-6 py-4 backdrop-blur-lg shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-cyan-900/50 border border-cyan-500/30 text-xl shadow-[0_0_15px_rgba(34,211,238,0.2)]">
            🤖
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">ArogyaMitra AI</h1>
            <p className="text-xs text-green-400 flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse"></span>
              Online
            </p>
          </div>
        </div>
        <button onClick={() => navigate("/dashboard")} className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-cyan-200 hover:bg-white/10">← Dashboard</button>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 scroll-smooth">
        <div className="mx-auto max-w-4xl space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] md:max-w-[75%] rounded-2xl p-4 shadow-xl backdrop-blur-md ${
                msg.role === "user" 
                  ? "bg-cyan-600/20 border border-cyan-500/30 text-white rounded-br-none" 
                  : "bg-white/5 border border-white/10 text-cyan-50 rounded-bl-none"
              }`}>
                {formatText(msg.content)}
                <p className={`text-[10px] mt-2 opacity-50 ${msg.role === "user" ? "text-right" : "text-left"}`}>
                  {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white/5 border border-white/10 rounded-2xl rounded-bl-none p-4 backdrop-blur-md flex gap-2 items-center h-12">
                <span className="h-2 w-2 rounded-full bg-cyan-400 animate-bounce"></span>
                <span className="h-2 w-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                <span className="h-2 w-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '0.4s' }}></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-white/10 bg-black/50 p-4 backdrop-blur-xl shrink-0 pb-8 md:pb-4">
        <div className="mx-auto max-w-4xl space-y-3">
          {messages.length < 3 && (
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s, i) => (
                <button key={i} onClick={() => handleSend(s)} className="rounded-full border border-cyan-500/30 bg-cyan-900/20 px-3 py-1 text-xs text-cyan-300 hover:bg-cyan-900/40 transition-colors">
                  {s}
                </button>
              ))}
            </div>
          )}
          <div className="flex gap-3 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend(input)}
              placeholder="Ask ArogyaMitra anything..."
              className="flex-1 rounded-xl border border-white/10 bg-gray-900 pl-4 pr-16 py-4 text-white placeholder:text-gray-500 focus:border-cyan-500 focus:outline-none shadow-inner"
            />
            <button
              onClick={() => handleSend(input)}
              disabled={loading || !input.trim()}
              className="absolute right-2 top-2 bottom-2 rounded-lg bg-cyan-600 px-6 font-semibold text-white transition-colors hover:bg-cyan-500 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
