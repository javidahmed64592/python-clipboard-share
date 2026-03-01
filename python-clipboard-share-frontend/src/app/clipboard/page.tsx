"use client";

import { useCallback, useEffect, useState } from "react";

import {
  addClipboardEntry,
  deleteClipboardEntry,
  getClipboardHistory,
  modifyClipboardEntry,
} from "@/lib/api";
import type { ClipboardHistoryEntry } from "@/lib/types";

export default function ClipboardPage() {
  const [entries, setEntries] = useState<ClipboardHistoryEntry[]>([]);
  const [selectedEntry, setSelectedEntry] =
    useState<ClipboardHistoryEntry | null>(null);
  const [isNewEntry, setIsNewEntry] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const loadHistory = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await getClipboardHistory();
      setEntries(response.history.entries);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load clipboard history",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleSelectEntry = (entry: ClipboardHistoryEntry) => {
    setSelectedEntry(entry);
    setIsNewEntry(false);
    setTitle(entry.title);
    setContent(entry.content);
    setError(null);
  };

  const handleNewEntry = () => {
    setSelectedEntry(null);
    setIsNewEntry(true);
    setTitle("");
    setContent("");
    setError(null);
  };

  const handleSave = async () => {
    if (!title.trim() || !content.trim()) {
      setError("Title and content are required");
      return;
    }

    setIsSaving(true);
    setError(null);
    try {
      if (isNewEntry) {
        const response = await addClipboardEntry(title, content);
        await loadHistory();
        setIsNewEntry(false);
        setSelectedEntry({ id: response.id, title, content });
      } else if (selectedEntry) {
        await modifyClipboardEntry(selectedEntry.id, title, content);
        const updated = { ...selectedEntry, title, content };
        setSelectedEntry(updated);
        await loadHistory();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save entry");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedEntry) return;

    setIsDeleting(true);
    setError(null);
    try {
      await deleteClipboardEntry(selectedEntry.id);
      await loadHistory();
      setSelectedEntry(null);
      setIsNewEntry(false);
      setTitle("");
      setContent("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete entry");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCopy = async () => {
    if (!content) return;
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isEditorDirty = selectedEntry
    ? title !== selectedEntry.title || content !== selectedEntry.content
    : title.trim() !== "" || content.trim() !== "";

  return (
    <div className="flex h-[calc(100vh-10rem)] gap-4">
      {/* Left Panel — Entry List */}
      <div className="flex w-56 flex-shrink-0 flex-col gap-2">
        <button
          onClick={handleNewEntry}
          className="w-full rounded-lg border border-neon-green bg-background-secondary px-3 py-2 text-sm font-medium text-neon-green transition-all hover:bg-neon-green hover:text-background"
        >
          + New Entry
        </button>

        <div className="flex-1 overflow-y-auto rounded-lg border border-terminal-border">
          {isLoading ? (
            <div className="flex items-center justify-center p-8">
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-neon-green border-t-transparent" />
            </div>
          ) : entries.length === 0 ? (
            <p className="p-4 text-center text-xs text-text-muted">
              No entries yet
            </p>
          ) : (
            entries.map((entry) => {
              const isActive = selectedEntry?.id === entry.id;
              return (
                <button
                  key={entry.id}
                  onClick={() => handleSelectEntry(entry)}
                  className={`w-full border-b border-terminal-border p-3 text-left transition-all last:border-0 hover:bg-background-tertiary ${
                    isActive
                      ? "border-l-2 border-l-neon-green bg-background-tertiary"
                      : ""
                  }`}
                >
                  <div className="truncate text-sm font-medium text-text-secondary">
                    {entry.title}
                  </div>
                  <div className="mt-0.5 truncate text-xs text-text-muted">
                    {entry.content}
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Right Panel — Editor */}
      <div className="flex flex-1 flex-col gap-3">
        {!selectedEntry && !isNewEntry ? (
          <div className="flex flex-1 items-center justify-center rounded-lg border border-terminal-border">
            <div className="text-center text-text-muted">
              <div className="mb-2 text-4xl">📋</div>
              <p className="text-sm">Select an entry or create a new one</p>
            </div>
          </div>
        ) : (
          <>
            {/* Title Input */}
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Entry title..."
              className="rounded-lg border border-terminal-border bg-terminal-bg px-4 py-2 text-sm text-text-secondary placeholder-text-muted focus:border-neon-green focus:outline-none"
            />

            {/* Content Textarea */}
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste or type clipboard content here..."
              className="flex-1 resize-none rounded-lg border border-terminal-border bg-terminal-bg px-4 py-3 font-mono text-sm text-text-secondary placeholder-text-muted focus:border-neon-green focus:outline-none"
            />

            {/* Error */}
            {error && (
              <div className="rounded-lg border border-neon-red bg-terminal-bg p-3">
                <p className="text-sm text-neon-red">❌ {error}</p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2">
              <button
                onClick={handleCopy}
                disabled={!content}
                className="rounded-lg border border-terminal-border bg-background-secondary px-4 py-2 text-sm text-text-secondary transition-all hover:border-neon-blue hover:text-neon-blue disabled:cursor-not-allowed disabled:opacity-40"
              >
                {copied ? "✓ Copied" : "Copy"}
              </button>

              <button
                onClick={handleSave}
                disabled={isSaving || !isEditorDirty}
                className="rounded-lg bg-neon-green px-4 py-2 text-sm font-medium text-background transition-all hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSaving ? "Saving..." : isNewEntry ? "Save" : "Update"}
              </button>

              {!isNewEntry && selectedEntry && (
                <button
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="ml-auto rounded-lg border border-neon-red bg-background-secondary px-4 py-2 text-sm text-neon-red transition-all hover:bg-neon-red hover:text-background disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isDeleting ? "Deleting..." : "Delete"}
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
