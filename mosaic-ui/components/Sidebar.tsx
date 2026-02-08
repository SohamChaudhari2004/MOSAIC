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
    <div className="w-80 border-r border-border bg-black flex flex-col h-full relative z-10">
      <div className="p-4 border-b border-border">
        <h2 className="text-primary font-bold text-xl mb-4 tracking-widest uppercase">
          Video Library
        </h2>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="w-full bg-primary hover:bg-primary/90 text-white font-bold py-3 px-4 rounded transition-colors flex items-center justify-center gap-2 disabled:opacity-50 uppercase tracking-wide"
        >
          <Upload size={18} />
          {isUploading ? "Uploading..." : "Upload Video"}
        </button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept="video/*"
        />
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {videos.map((video) => (
          <motion.div
            key={video.video_id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="border border-border p-3 rounded cursor-pointer hover:border-primary hover:bg-primary/5 transition-all group"
            onClick={() => onSelectVideo(video)}
          >
            <div className="aspect-video bg-secondary mb-2 flex items-center justify-center relative overflow-hidden rounded">
              <Film
                className="text-primary/50 group-hover:text-primary/80 transition-colors"
                size={32}
              />
            </div>
            <h3 className="text-foreground text-sm font-medium truncate">
              {video.filename || video.video_id}
            </h3>
            <p className="text-xs text-muted-foreground mt-1">
              {video.video_id}
            </p>
            {video.created_at && (
              <p className="text-xs text-muted-foreground">
                {video.created_at}
              </p>
            )}
          </motion.div>
        ))}

        {videos.length === 0 && (
          <div className="text-center text-muted-foreground mt-10 text-sm">
            No videos uploaded yet
          </div>
        )}
      </div>

      {/* Clear Storage Section */}
      <div className="p-4 border-t border-border">
        {showConfirm ? (
          <div className="space-y-2">
            <p className="text-primary text-xs font-medium text-center uppercase">
              Delete All Data?
            </p>
            <div className="flex gap-2">
              <button
                onClick={handleClearStorage}
                disabled={isClearing}
                className="flex-1 bg-primary hover:bg-primary/90 text-white font-bold py-2 px-3 rounded text-sm transition-colors disabled:opacity-50 uppercase"
              >
                {isClearing ? "Clearing..." : "Confirm"}
              </button>
              <button
                onClick={() => setShowConfirm(false)}
                disabled={isClearing}
                className="flex-1 border border-border text-foreground font-bold py-2 px-3 rounded text-sm hover:bg-secondary transition-colors disabled:opacity-50 uppercase"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setShowConfirm(true)}
            className="w-full border border-border text-primary font-bold py-2 px-4 rounded hover:bg-primary/10 transition-colors flex items-center justify-center gap-2 uppercase tracking-wide"
          >
            <Trash2 size={18} />
            Clear Storage
          </button>
        )}
      </div>
    </div>
  );
};
