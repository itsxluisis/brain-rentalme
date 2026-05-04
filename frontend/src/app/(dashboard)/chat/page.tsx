"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Send, Trash2, MessageSquare, BookOpen } from "lucide-react";
import { listSessions, createSession, deleteSession, getMessages, renameSession } from "@/lib/api/chat";
import type { ChatSession, ChatMessage, SearchResult } from "@/lib/api/chat";
import Link from "next/link";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
const WS_BASE = BACKEND_URL.replace(/^http/, "ws");

interface StreamMessage {
  role: "user" | "assistant";
  content: string;
  sources?: SearchResult[];
  streaming?: boolean;
}

function SourceCard({ source }: { source: SearchResult }) {
  const href = source.entity_type === "property"
    ? `/propiedades/${source.entity_id}`
    : `/sistemas/${source.entity_id}`;

  return (
    <div className="flex items-start gap-2 rounded-sm border border-surface-border bg-surface-hover p-2 text-xs">
      <BookOpen className="mt-0.5 h-3 w-3 shrink-0 text-accent/60" />
      <div>
        <Link href={href} className="font-medium text-accent/80 hover:text-accent">
          {source.entity_name ?? source.entity_id.slice(0, 8)}
        </Link>
        <p className="text-white/40">{source.title}</p>
        <p className="mt-0.5 text-white/55 leading-relaxed">{source.content_preview.slice(0, 120)}…</p>
      </div>
      <span className="ml-auto shrink-0 text-white/25">{Math.round(source.score * 100)}%</span>
    </div>
  );
}

function MessageBubble({ msg }: { msg: StreamMessage }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] ${isUser ? "order-2" : "order-1"}`}>
        <div
          className={`rounded-card px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? "bg-accent/15 text-white/90"
              : "border border-surface-border bg-surface text-white/80"
          }`}
        >
          {msg.content}
          {msg.streaming && (
            <span className="ml-1 inline-block h-3 w-0.5 animate-pulse bg-accent" />
          )}
        </div>
        {msg.sources && msg.sources.length > 0 && (
          <div className="mt-2 space-y-1.5">
            {msg.sources.slice(0, 3).map((s) => (
              <SourceCard key={s.block_id} source={s} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatPage() {
  const queryClient = useQueryClient();
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<StreamMessage[]>([]);
  const [input, setInput] = useState("");
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const { data: sessions = [] } = useQuery({
    queryKey: ["chat-sessions"],
    queryFn: listSessions,
  });

  // Load history when switching sessions
  const { data: history } = useQuery({
    queryKey: ["chat-messages", activeSessionId],
    queryFn: () => getMessages(activeSessionId!),
    enabled: !!activeSessionId,
  });

  useEffect(() => {
    if (history) {
      setMessages(history.map((m) => ({
        role: m.role,
        content: m.content,
        sources: m.sources ?? undefined,
      })));
    }
  }, [history]);

  const connectWs = useCallback((sessionId: string) => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    const ws = new WebSocket(`${WS_BASE}/api/v1/chat/sessions/${sessionId}/ws`);
    ws.onopen = () => setWsConnected(true);
    ws.onclose = () => setWsConnected(false);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "sources") {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant" && last.streaming) {
            return [...prev.slice(0, -1), { ...last, sources: data.sources }];
          }
          return [...prev, { role: "assistant", content: "", sources: data.sources, streaming: true }];
        });
      } else if (data.type === "chunk") {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant" && last.streaming) {
            return [...prev.slice(0, -1), { ...last, content: last.content + data.text }];
          }
          return [...prev, { role: "assistant", content: data.text, streaming: true }];
        });
      } else if (data.type === "done") {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant") {
            return [...prev.slice(0, -1), { ...last, streaming: false }];
          }
          return prev;
        });
        queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
        queryClient.invalidateQueries({ queryKey: ["chat-messages", sessionId] });
      }
    };
    wsRef.current = ws;
  }, [queryClient]);

  const createMutation = useMutation({
    mutationFn: () => createSession("all"),
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
      setActiveSessionId(session.id);
      setMessages([]);
      connectWs(session.id);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteSession(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
      if (activeSessionId === id) {
        setActiveSessionId(null);
        setMessages([]);
        wsRef.current?.close();
      }
    },
  });

  function selectSession(session: ChatSession) {
    if (session.id === activeSessionId) return;
    setActiveSessionId(session.id);
    setMessages([]);
    connectWs(session.id);
  }

  function sendMessage() {
    if (!input.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    const text = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    wsRef.current.send(JSON.stringify({ message: text }));
    setInput("");
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    return () => wsRef.current?.close();
  }, []);

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Session sidebar */}
      <div className="flex w-64 shrink-0 flex-col gap-2">
        <button
          onClick={() => createMutation.mutate()}
          disabled={createMutation.isPending}
          className="flex items-center gap-2 rounded-input border border-surface-border px-3 py-2 text-sm text-white/55 hover:border-accent/50 hover:text-accent"
        >
          <Plus className="h-3.5 w-3.5" />
          Nueva conversación
        </button>

        <div className="flex-1 space-y-1 overflow-y-auto">
          {sessions.length === 0 ? (
            <p className="py-4 text-center text-xs text-white/25">Sin conversaciones</p>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`group flex cursor-pointer items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors ${
                  session.id === activeSessionId
                    ? "bg-accent/10 text-accent"
                    : "text-white/60 hover:bg-white/5"
                }`}
                onClick={() => selectSession(session)}
              >
                <div className="flex min-w-0 items-center gap-2">
                  <MessageSquare className="h-3.5 w-3.5 shrink-0" />
                  <span className="truncate">{session.title ?? "Nueva conversación"}</span>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); deleteMutation.mutate(session.id); }}
                  className="hidden shrink-0 rounded p-0.5 text-white/25 hover:text-red-400 group-hover:block"
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Chat area */}
      <div className="glass-card flex flex-1 flex-col overflow-hidden">
        {!activeSessionId ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-3">
            <MessageSquare className="h-10 w-10 text-white/15" />
            <p className="text-sm text-white/30">Crea o selecciona una conversación</p>
            <button
              onClick={() => createMutation.mutate()}
              className="rounded-input bg-accent px-4 py-2 text-sm text-white hover:bg-accent-hover"
            >
              Empezar a chatear
            </button>
          </div>
        ) : (
          <>
            {/* Messages */}
            <div className="flex-1 space-y-4 overflow-y-auto p-6">
              {messages.length === 0 && (
                <p className="text-center text-sm text-white/25">
                  Haz una pregunta sobre tus propiedades o sistemas.
                </p>
              )}
              {messages.map((msg, i) => (
                <MessageBubble key={i} msg={msg} />
              ))}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="border-t border-surface-border p-4">
              <div className="flex gap-2">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                  placeholder="Escribe tu pregunta..."
                  className="flex-1 rounded-input border border-surface-border bg-surface-hover px-4 py-2.5 text-sm text-white/90 outline-none focus:border-accent placeholder:text-white/25"
                />
                <button
                  onClick={sendMessage}
                  disabled={!input.trim() || !wsConnected}
                  className="flex items-center gap-1.5 rounded-input bg-accent px-4 py-2.5 text-sm text-white hover:bg-accent-hover disabled:opacity-40"
                >
                  <Send className="h-3.5 w-3.5" />
                </button>
              </div>
              {!wsConnected && activeSessionId && (
                <p className="mt-1.5 text-xs text-amber-400/60">Reconectando…</p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
