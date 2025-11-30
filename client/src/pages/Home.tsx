import { useEffect, useState } from "react";
import { createWebSocket, sendMessage } from "../api";

function Home() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [message, setMessage] = useState<string>("");
  const [messages, setMessages] = useState<string[]>([]);
  useEffect(() => {
    const load = async () => {
      const newSocket = await createWebSocket();
      setSocket(newSocket);
    };
    load();
  }, []);
  useEffect(() => {
    if (socket) {
      socket.onmessage = (event) => {
        console.log(event.data);
        setMessages((prev) => [...prev, event.data]);
      };
    }
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [socket]);

  console.log("messages", messages);
  return (
    <div>
      <h1>Home</h1>
      <input
        className="border-2 border-gray-300 rounded-md p-2"
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <button
        className="bg-blue-500 text-white rounded-md p-2"
        onClick={() => {
          sendMessage(message);

          setMessage("");
        }}
      >
        Send Message
      </button>
      <ul>
        {messages.map((message, index) => (
          <li key={index}>{message}</li>
        ))}
      </ul>
    </div>
  );
}

export default Home;
