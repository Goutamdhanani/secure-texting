<<<<<<< Updated upstream
import { useState, useEffect, useCallback } from 'react';
import type { CommandItem } from './types';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Conversation } from './components/Conversation';
import { CommandPalette } from './components/CommandPalette';
import { useApp } from './context/AppContext';
import './App.css';

function App() {
  const {
    currentUser,
    users,
    selectedUser,
    selectedUserId,
    messages,
    isLoading,
    error,
    selectUser,
    sendMessage,
    addUser,
    getLastMessage,
  } = useApp();

=======
import React, { useState, useEffect, useCallback } from "react";
import type { User, Message, CommandItem } from "./types";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { Conversation } from "./components/Conversation";
import { CommandPalette } from "./components/CommandPalette";
import {
  listUsers,
  createUser,
  getConversation,
  sendMessage as apiSendMessage,
  type ApiUser,
  type ApiMessage,
} from "./api/api";
import "./App.css";

/** Convert ApiUser -> UI User */
function toUiUser(apiUser: ApiUser): User {
  return {
    id: String(apiUser.id),
    username: apiUser.name,
    status: "online",
  };
}

/** Convert ApiMessage -> UI Message */
function toUiMessage(apiMessage: ApiMessage): Message {
  return {
    id: String(apiMessage.id),
    content: apiMessage.decrypted ?? "",
    senderId: String(apiMessage.sender_id),
    receiverId: String(apiMessage.recipient_id),
    timestamp: new Date(apiMessage.timestamp),
    status: "delivered",
    encrypted: true,
  };
}

function App(): JSX.Element {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string | undefined>();
  const [messages, setMessages] = useState<Record<string, Message[]>>({});
>>>>>>> Stashed changes
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

<<<<<<< Updated upstream
  const currentUserId = currentUser?.id || '';

  // Filter out the current user from the contacts list
  const contactUsers = users.filter((u) => u.id !== currentUser?.id);

  // Keyboard shortcut for command palette
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSelectUser = useCallback((userId: string) => {
    selectUser(userId);
    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
      setIsSidebarOpen(false);
=======
  const selectedUser = users.find((u) => u.id === selectedUserId);
  const currentUserId = currentUser?.id ?? "";

  // load users on mount
  useEffect(() => {
    let mounted = true;
    async function fetchUsers() {
      try {
        setIsLoading(true);
        const apiUsers = await listUsers();
        if (!mounted) return;
        const uiUsers = apiUsers.map(toUiUser);
        setUsers(uiUsers);
        // auto-select first user as current user if none set
        if (uiUsers.length > 0 && !currentUser) {
          setCurrentUser(uiUsers[0]);
        }
        setError(null);
      } catch (err: any) {
        console.error("Failed to fetch users:", err);
        setError("Failed to load users");
      } finally {
        if (mounted) setIsLoading(false);
      }
    }
    fetchUsers();
    return () => {
      mounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // fetch conversation when selection changes
  useEffect(() => {
    if (!selectedUserId || !currentUser) return;
    let mounted = true;
    async function fetchConversation() {
      try {
        setIsLoading(true);
        const apiMessages = await getConversation(
          parseInt(currentUser.id, 10),
          parseInt(selectedUserId, 10)
        );
        if (!mounted) return;
        const uiMessages = apiMessages.map(toUiMessage);
        setMessages((prev) => ({ ...prev, [selectedUserId]: uiMessages }));
      } catch (err) {
        console.error("Failed to fetch conversation:", err);
        // don't show global error for conversation fetch
      } finally {
        if (mounted) setIsLoading(false);
      }
    }
    // small decrypting shimmer UX delay
    const t = setTimeout(fetchConversation, 150);
    return () => {
      mounted = false;
      clearTimeout(t);
    };
  }, [selectedUserId, currentUser]);

  const contactUsers = users.filter((u) => u.id !== currentUser?.id);

  // Add new user handler (create via API)
  const handleAddUser = useCallback(async () => {
    const name = prompt("Enter the name for the new contact:");
    if (!name || !name.trim()) return;
    try {
      setIsLoading(true);
      const newUser = await createUser(name.trim());
      const uiUser = toUiUser(newUser);
      setUsers((prev) => [...prev, uiUser]);
      setError(null);
    } catch (err) {
      console.error("Failed to add user:", err);
      setError("Failed to add user");
    } finally {
      setIsLoading(false);
>>>>>>> Stashed changes
    }
  }, [selectUser]);

  // send message (optimistic UI)
  const handleSendMessage = useCallback(
    async (content: string) => {
<<<<<<< Updated upstream
      await sendMessage(content);
    },
    [sendMessage]
  );

  // Handle adding a new user
  const handleAddUser = useCallback(async () => {
    const name = prompt('Enter the name for the new contact:');
    if (!name || !name.trim()) return;
    await addUser(name);
  }, [addUser]);
=======
      if (!selectedUserId || !currentUser) return;
      const tempId = `m${Date.now()}`;
      const newMessage: Message = {
        id: tempId,
        content,
        senderId: currentUser.id,
        receiverId: selectedUserId,
        timestamp: new Date(),
        status: "sending",
        encrypted: true,
      };
      // optimistic append
      setMessages((prev) => ({
        ...prev,
        [selectedUserId]: [...(prev[selectedUserId] || []), newMessage],
      }));
      try {
        await apiSendMessage(parseInt(currentUser.id, 10), parseInt(selectedUserId, 10), content);
        // replace temp message status to sent -> delivered
        setMessages((prev) => ({
          ...prev,
          [selectedUserId]: prev[selectedUserId]?.map((m) =>
            m.id === tempId ? { ...m, status: "delivered" } : m
          ) || [],
        }));
        setError(null);
      } catch (err) {
        console.error("Failed to send message:", err);
        setMessages((prev) => ({
          ...prev,
          [selectedUserId]: prev[selectedUserId]?.map((m) =>
            m.id === tempId ? { ...m, status: "error" } : m
          ) || [],
        }));
        setError("Failed to send message");
      }
    },
    [selectedUserId, currentUser]
  );

  const getLastMessage = useCallback(
    (userId: string) => {
      const userMessages = messages[userId];
      if (!userMessages || userMessages.length === 0) return undefined;
      const lastMsg = userMessages[userMessages.length - 1];
      const timeStr = new Date(lastMsg.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
      return {
        text: lastMsg.content.length > 30 ? `${lastMsg.content.slice(0, 30)}...` : lastMsg.content,
        timestamp: timeStr,
      };
    },
    [messages]
  );

  const handleSelectUser = useCallback((userId: string) => {
    setSelectedUserId(userId);
    if (window.innerWidth <= 768) setIsSidebarOpen(false);
  }, []);
>>>>>>> Stashed changes

  const commands: CommandItem[] = [
    {
      id: "add-user",
      label: "Add new contact",
      icon: "M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z",
      shortcut: "⌘+N",
      action: () => {
        setIsCommandPaletteOpen(false);
        handleAddUser();
      },
    },
    // ... other commands omitted for brevity; keep same as before
  ];

  return (
    <div className="app">
      <div className="particles">{Array.from({ length: 10 }).map((_, i) => <div key={i} className="particle" />)}</div>

      <Header isConnected={users.length > 0 && !error} />

      <main className="mainContent">
        <Sidebar
          users={contactUsers}
          selectedUserId={selectedUserId}
          onSelectUser={handleSelectUser}
          onAddUser={handleAddUser}
          getLastMessage={getLastMessage}
          isOpen={isSidebarOpen}
        />

        <Conversation
          user={selectedUser}
          messages={selectedUserId ? messages[selectedUserId] || [] : []}
          currentUserId={currentUserId}
          onSendMessage={handleSendMessage}
          onBack={() => setIsSidebarOpen(true)}
          isLoading={isLoading}
        />
      </main>

      <CommandPalette isOpen={isCommandPaletteOpen} onClose={() => setIsCommandPaletteOpen(false)} commands={commands} />
    </div>
  );
}

export default App;
