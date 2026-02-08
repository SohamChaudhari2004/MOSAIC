"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Send,
  Paperclip,
  Play,
  X,
  Image as ImageIcon,
  Music,
} from "lucide-react";
import { ChatMessage } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";

interface ChatAreaProps {
  messages: ChatMessage[];
  onSendMessage: (message: string, file?: File) => void;
  isLoading: boolean;
}

// Extract ALL clip paths from message content (supports multiple clips)
const extractAllClips = (
  content: string,
): Array<{ videoId: string; clipName: string }> => {
  const clips: Array<{ videoId: string; clipName: string }> = [];

  // Match patterns like:
  // - clips_output\video_id\clip_1.mp4
  // - clips_output/video_id/clip_1.mp4
  // - D:\path\clips_output\video_id\clip_1.mp4
  // - Also handles escaped backslashes (\\)
  const patterns = [
    /clips_output[\\\/]+([a-zA-Z0-9_-]+)[\\\/]+(clip_\d+\.mp4)/gi,
    /clips_output[\\\\\/]+([a-zA-Z0-9_-]+)[\\\\\/]+(clip_\d+\.mp4)/gi,
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      const clipInfo = { videoId: match[1], clipName: match[2] };
      // Avoid duplicates
      if (
        !clips.some(
          (c) =>
            c.videoId === clipInfo.videoId && c.clipName === clipInfo.clipName,
        )
      ) {
        clips.push(clipInfo);
      }
    }
  }

  return clips;
};

// Remove clip paths from message and clean up the output
const cleanMessageContent = (content: string, hasClips: boolean): string => {
  if (!hasClips) return content;

  let cleaned = content;
  // Remove file path mentions
  cleaned = cleaned.replace(
    /You can find (it|them) (here|at):?[^.]*\.mp4[`]?\.?/gi,
    "",
  );
  cleaned = cleaned.replace(/`[^`]*clips_output[^`]*\.mp4`/gi, "");
  cleaned = cleaned.replace(/\[[^\]]*clips_output[^\]]*\.mp4[^\]]*\]/gi, "");
  // Remove standalone paths
  cleaned = cleaned.replace(/[A-Z]:[\\\/][^\s]*clips_output[^\s]*\.mp4/gi, "");
  cleaned = cleaned.trim();

  // Clean up any trailing colons or punctuation artifacts
  cleaned = cleaned.replace(/:\s*$/, ".");
  cleaned = cleaned.replace(/\s+\./g, ".");

  return cleaned;
};

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  onSendMessage,
  isLoading,
}) => {
  const [input, setInput] = useState("");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAttachedFile(file);

    // Generate preview for images
    if (file.type.startsWith("image/")) {
      const url = URL.createObjectURL(file);
      setFilePreview(url);
    } else {
      setFilePreview(null);
    }

    // Reset input so the same file can be re-selected
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const removeAttachment = () => {
    if (filePreview) {
      URL.revokeObjectURL(filePreview);
    }
    setAttachedFile(null);
    setFilePreview(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((!input.trim() && !attachedFile) || isLoading) return;

    onSendMessage(input, attachedFile || undefined);
    setInput("");
    removeAttachment();
  };

  const getFileTypeLabel = (file: File): string => {
    if (file.type.startsWith("image/")) return "IMAGE";
    if (file.type.startsWith("audio/")) return "AUDIO";
    return "FILE";
  };

  // Extract media attachment info from user message content
  const extractMediaAttachment = (
    content: string,
  ): { type: string; filename: string; serverFilename: string } | null => {
    // Pattern: [Image: original.png|server_id_original.png] or [Audio: file.mp3|server_id_file.mp3]
    const match = content.match(/\[(Image|Audio):\s*([^|]+)\|([^\]]+)\]/);
    if (match) {
      return {
        type: match[1].toLowerCase(),
        filename: match[2].trim(),
        serverFilename: match[3].trim(),
      };
    }
    return null;
  };

  // Remove media attachment tag from display text
  const cleanUserMessage = (content: string): string => {
    return content.replace(/\[(Image|Audio):[^\]]+\]\s*/, "").trim();
  };

  return (
    <div className="flex-1 flex flex-col h-full relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 pointer-events-none opacity-20">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 border border-hal-red rounded-full opacity-20 animate-pulse" />
        <div className="absolute bottom-1/3 right-1/3 w-64 h-64 border border-hal-red rounded-full opacity-10" />
        {/* Add more geometric shapes if needed */}
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6 z-10">
        <AnimatePresence>
          {messages.map((msg, index) => {
            const clips =
              msg.role === "assistant" ? extractAllClips(msg.content) : [];
            const mediaAttachment =
              msg.role === "user" ? extractMediaAttachment(msg.content) : null;
            const displayContent =
              msg.role === "assistant"
                ? cleanMessageContent(msg.content, clips.length > 0)
                : cleanUserMessage(msg.content);

            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className={clsx(
                  "max-w-2xl w-full p-4 rounded-lg border relative",
                  msg.role === "assistant"
                    ? "bg-red-950/30 border-hal-red/50 text-red-100 self-start mr-auto"
                    : "bg-slate-800/50 border-slate-600 text-slate-100 self-end ml-auto",
                )}
              >
                <div className="flex items-center gap-2 mb-2 opacity-70 text-xs font-mono uppercase">
                  <div
                    className={clsx(
                      "w-2 h-2 rounded-full",
                      msg.role === "assistant"
                        ? "bg-red-500 animate-pulse"
                        : "bg-blue-400",
                    )}
                  />
                  {msg.role === "assistant" ? "HAL 9000" : "USER"}
                </div>

                {/* Render media attachment thumbnail for user messages */}
                {mediaAttachment && (
                  <div className="mb-3">
                    {mediaAttachment.type === "image" ? (
                      <div className="inline-block border-2 border-blue-400/50 rounded-lg overflow-hidden">
                        <img
                          src={`http://localhost:8000/media/${mediaAttachment.serverFilename}`}
                          alt={mediaAttachment.filename}
                          width={120}
                          height={120}
                          className="object-cover"
                        />
                      </div>
                    ) : (
                      <div className="inline-flex items-center gap-2 bg-slate-700/50 border border-blue-400/50 rounded-lg px-3 py-2">
                        <Music size={16} className="text-blue-400" />
                        <span className="text-xs font-mono text-blue-400">
                          AUDIO: {mediaAttachment.filename}
                        </span>
                      </div>
                    )}
                  </div>
                )}

                <p className="font-mono leading-relaxed whitespace-pre-wrap">
                  {displayContent}
                </p>

                {/* Render video clips if present */}
                {clips.length > 0 && (
                  <div className="mt-4 space-y-3">
                    {clips.map((clip, clipIndex) => (
                      <div
                        key={clipIndex}
                        className="rounded-lg overflow-hidden border border-hal-red/30 bg-black"
                      >
                        <div className="flex items-center gap-2 px-3 py-2 bg-red-950/50 border-b border-hal-red/30">
                          <Play size={14} className="text-hal-red" />
                          <span className="text-xs font-mono text-hal-red">
                            {clips.length > 1
                              ? `CLIP ${clipIndex + 1} OF ${clips.length}`
                              : "GENERATED CLIP"}
                          </span>
                        </div>
                        <video
                          controls
                          className="w-full max-h-64"
                          src={`http://localhost:8000/clips/${clip.videoId}/${clip.clipName}`}
                        >
                          Your browser does not support the video tag.
                        </video>
                      </div>
                    ))}
                  </div>
                )}

                <div className="text-right text-[10px] opacity-50 mt-2 font-mono">
                  {msg.timestamp}
                </div>
              </motion.div>
            );
          })}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-red-950/30 border border-hal-red/50 text-red-100 p-4 rounded-lg max-w-2xl mr-auto"
            >
              <div className="flex items-center gap-2 mb-2 opacity-70 text-xs font-mono uppercase">
                <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                HAL 9000
              </div>
              <p className="font-mono animate-pulse">ANALYZING INPUT...</p>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-hal-border bg-black z-20">
        {/* Attachment preview */}
        {attachedFile && (
          <div className="max-w-4xl mx-auto mb-3">
            <div className="inline-flex items-center gap-2 bg-slate-800/80 border border-hal-red/30 rounded-lg px-3 py-2">
              {filePreview ? (
                <img
                  src={filePreview}
                  alt="preview"
                  width={48}
                  height={48}
                  className="w-12 h-12 object-cover rounded"
                />
              ) : attachedFile.type.startsWith("audio/") ? (
                <div className="w-12 h-12 bg-red-950/50 rounded flex items-center justify-center">
                  <Music size={20} className="text-hal-red" />
                </div>
              ) : (
                <div className="w-12 h-12 bg-slate-700 rounded flex items-center justify-center">
                  <Paperclip size={20} className="text-slate-400" />
                </div>
              )}
              <div className="flex flex-col">
                <span className="text-xs font-mono text-hal-red">
                  {getFileTypeLabel(attachedFile)}
                </span>
                <span className="text-xs font-mono text-slate-400 truncate max-w-[200px]">
                  {attachedFile.name}
                </span>
              </div>
              <button
                onClick={removeAttachment}
                className="ml-2 p-1 text-slate-400 hover:text-red-500 transition-colors"
              >
                <X size={16} />
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-4 max-w-4xl mx-auto">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            accept="image/*,audio/*"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className={clsx(
              "p-3 transition-colors border rounded bg-hal-panel",
              attachedFile
                ? "text-hal-red border-hal-red"
                : "text-hal-border hover:text-hal-red border-hal-border",
            )}
            title="Attach image or audio file"
          >
            <Paperclip size={20} className="cursor-pointer" />
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              attachedFile
                ? `Search video with ${getFileTypeLabel(attachedFile).toLowerCase()}...`
                : "Enter your message, Dave..."
            }
            className="flex-1 bg-slate-900/50 border border-slate-700 rounded p-3 text-white font-mono focus:outline-none focus:border-hal-red focus:ring-1 focus:ring-hal-red transition-all"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || (!input.trim() && !attachedFile)}
            className="p-3 bg-hal-red text-black rounded hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-bold"
          >
            <Send size={20} />
          </button>
        </form>
        <div className="text-center mt-2 text-[10px] text-hal-red/50 font-mono tracking-widest">
          SYSTEM STATUS: OPERATIONAL | LOGIC CIRCUITS: FUNCTIONING NORMALLY |
          IMAGE & AUDIO SEARCH: ACTIVE
        </div>
      </div>
    </div>
  );
};
