import { useState } from "react";

function App() {
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);

  const sendMessage = async () => {
    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    });
    const data = await res.json();
    setChat([...chat, { user: input, bot: data.reply }]);
    setInput("");
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Company Chatbot</h2>
      {chat.map((msg, i) => (
        <div key={i}>
          <p><strong>You:</strong> {msg.user}</p>
          <p><strong>Bot:</strong> {msg.bot}</p>
        </div>
      ))}
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        style={{ width: "300px", marginRight: "10px" }}
        placeholder="Type a message..."
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default App;
