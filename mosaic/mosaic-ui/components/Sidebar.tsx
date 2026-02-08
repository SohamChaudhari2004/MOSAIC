"use client";

import React, { useRef, useState } from "react";
import { Upload, Film, Trash2 } from "lucide-react";
import { Video, clearStorage } from "@/lib/api";
import { motion } from "framer-motion";

interface SidebarProps {
  videos: Video[];
  onSelectVideo: (video: Video) => void;
  onUpload: (file: File) => void;
  isUploading: boolean;
  onStorageCleared?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  videos,
  onSelectVideo,
  onUpload,
  isUploading,
  onStorageCleared,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isClearing, setIsClearing] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  const handleClearStorage = async () => {
    setIsClearing(true);
    try {
      await clearStorage();
      setShowConfirm(false);
      if (onStorageCleared) {
        onStorageCleared();
      }
    } catch (error) {
      console.error("Failed to clear storage:", error);
      alert("Failed to clear storage. Please try again.");
    } finally {
      setIsClearing(false);
    }
  };

  return (
    <div className="w-80 border-l border-hal-border bg-black flex flex-col h-full">
      <div className="p-4 border-b border-hal-border">
        <h2 className="text-hal-red font-bold text-xl mb-4 tracking-widest">
          VIDEO LIBRARY
        </h2>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="w-full bg-hal-red text-black font-bold py-2 px-4 rounded bg-red-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
        >
          <Upload size={18} />
          {isUploading ? "UPLOADING..." : "UPLOAD VIDEO"}
        </button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept="video/*"
        />
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {videos.map((video) => (
          <motion.div
            key={video.video_id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="border border-hal-border p-2 rounded cursor-pointer hover:bg-hal-dark-red transition-colors group"
            onClick={() => onSelectVideo(video)}
          >
            <div className="aspect-video bg-gray-900 mb-2 flex items-center justify-center relative overflow-hidden">
              {/* Placeholder for thumbnail if available, or icon */}
              <Film
                className="text-hal-red opacity-50 group-hover:opacity-100 transition-opacity"
                size={32}
              />
              <div className="absolute inset-0 bg-red-900/10 group-hover:bg-red-900/20 transition-colors" />
            </div>
            <h3 className="text-hal-red text-sm font-mono truncate">
              {video.filename || video.video_id}
            </h3>
            <p className="text-xs text-red-800 font-mono">
              {video.created_at || "Unknown Date"}
            </p>
          </motion.div>
        ))}

        {videos.length === 0 && (
          <div className="text-center text-red-900 mt-10 font-mono text-sm">
            NO DATA STREAMS DETECTED
          </div>
        )}
      </div>

      {/* Clear Storage Section */}
      <div className="p-4 border-t border-hal-border">
        {showConfirm ? (
          <div className="space-y-2">
            <p className="text-red-500 text-xs font-mono text-center">
              DELETE ALL DATA?
            </p>
            <div className="flex gap-2">
              <button
                onClick={handleClearStorage}
                disabled={isClearing}
                className="flex-1 bg-red-700 hover:bg-red-600 text-white font-bold py-2 px-3 rounded text-sm transition-colors disabled:opacity-50"
              >
                {isClearing ? "CLEARING..." : "CONFIRM"}
              </button>
              <button
                onClick={() => setShowConfirm(false)}
                disabled={isClearing}
                className="flex-1 border border-hal-border text-red-500 font-bold py-2 px-3 rounded text-sm hover:bg-red-900/20 transition-colors disabled:opacity-50"
              >
                CANCEL
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setShowConfirm(true)}
            className="w-full border border-red-700 text-red-500 font-bold py-2 px-4 rounded hover:bg-red-900/20 transition-colors flex items-center justify-center gap-2"
          >
            <Trash2 size={18} />
            CLEAR STORAGE
          </button>
        )}
      </div>
    </div>
  );
};
