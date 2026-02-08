"use client";

import React, { useRef, useState } from "react";
import { Upload, Film, Trash2, ChevronLeft, ChevronRight, Home, Search, FolderOpen, Clock, Moon, Sun } from "lucide-react";
import { Video, clearStorage } from "@/lib/api";
import { motion } from "framer-motion";
import { useTheme } from "@/components/ThemeProvider";

interface CollapsibleSidebarProps {
  videos: Video[];
  onSelectVideo: (video: Video) => void;
  onUpload: (file: File) => void;
  isUploading: boolean;
  onStorageCleared?: () => void;
}

export const CollapsibleSidebar: React.FC<CollapsibleSidebarProps> = ({
  videos,
  onSelectVideo,
  onUpload,
  isUploading,
  onStorageCleared,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isClearing, setIsClearing] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { theme, toggleTheme } = useTheme();

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
    <>
      <motion.div
        initial={false}
        animate={{ width: isCollapsed ? "64px" : "320px" }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="border-r border-border bg-background/50 backdrop-blur-sm flex flex-col h-full relative z-20"
      >
        {/* Header with collapse button */}
        <div className="p-4 border-b border-border flex items-center justify-between">
          {!isCollapsed && (
            <h2 className="text-foreground font-semibold text-sm uppercase tracking-wide">
              Video Library
            </h2>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 hover:bg-muted rounded-lg transition-colors ml-auto"
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronLeft className="h-4 w-4 text-muted-foreground" />
            )}
          </button>
        </div>

        {/* Icon Navigation when collapsed */}
        {isCollapsed ? (
          <div className="flex-1 flex flex-col items-center py-4 gap-4">
            <button
              onClick={() => setIsCollapsed(false)}
              className="p-3 hover:bg-muted rounded-lg transition-colors"
              title="Home"
            >
              <Home className="h-5 w-5 text-muted-foreground" />
            </button>
            <button
              onClick={() => setIsCollapsed(false)}
              className="p-3 hover:bg-muted rounded-lg transition-colors"
              title="Search"
            >
              <Search className="h-5 w-5 text-muted-foreground" />
            </button>
            <button
              onClick={() => setIsCollapsed(false)}
              className="p-3 hover:bg-muted rounded-lg transition-colors"
              title="Videos"
            >
              <FolderOpen className="h-5 w-5 text-muted-foreground" />
            </button>
            <button
              onClick={() => setIsCollapsed(false)}
              className="p-3 hover:bg-muted rounded-lg transition-colors"
              title="Recent"
            >
              <Clock className="h-5 w-5 text-muted-foreground" />
            </button>
            <div className="flex-1" />
            <button
              onClick={toggleTheme}
              className="p-3 hover:bg-muted rounded-lg transition-colors"
              title={theme === "light" ? "Dark mode" : "Light mode"}
            >
              {theme === "light" ? (
                <Moon className="h-5 w-5 text-muted-foreground" />
              ) : (
                <Sun className="h-5 w-5 text-muted-foreground" />
              )}
            </button>
          </div>
        ) : (
          <>
            {/* Upload Button */}
            <div className="p-4">
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
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

            {/* Videos List */}
            <div className="flex-1 overflow-y-auto px-4 space-y-2">
              {videos.map((video) => (
                <motion.div
                  key={video.video_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="border border-border bg-card p-3 rounded-lg cursor-pointer hover:border-primary hover:bg-accent/50 transition-all group"
                  onClick={() => onSelectVideo(video)}
                >
                  <div className="aspect-video bg-muted mb-2 flex items-center justify-center relative overflow-hidden rounded">
                    <Film
                      className="text-muted-foreground group-hover:text-primary transition-colors"
                      size={24}
                    />
                  </div>
                  <h3 className="text-foreground text-sm font-medium truncate">
                    {video.filename || video.video_id}
                  </h3>
                  <p className="text-xs text-muted-foreground mt-1 truncate">
                    {video.video_id}
                  </p>
                </motion.div>
              ))}

              {videos.length === 0 && (
                <div className="text-center text-muted-foreground mt-10 text-sm">
                  No videos yet
                </div>
              )}
            </div>

            {/* Theme Toggle & Clear Storage */}
            <div className="p-4 border-t border-border space-y-2">
              <button
                onClick={toggleTheme}
                className="w-full border border-border hover:bg-accent text-foreground font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {theme === "light" ? (
                  <>
                    <Moon size={18} />
                    Dark Mode
                  </>
                ) : (
                  <>
                    <Sun size={18} />
                    Light Mode
                  </>
                )}
              </button>

              {showConfirm ? (
                <div className="space-y-2">
                  <p className="text-destructive text-xs font-medium text-center">
                    Delete all data?
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={handleClearStorage}
                      disabled={isClearing}
                      className="flex-1 bg-destructive hover:bg-destructive/90 text-destructive-foreground font-medium py-2 px-3 rounded-lg text-sm transition-colors disabled:opacity-50"
                    >
                      {isClearing ? "Clearing..." : "Confirm"}
                    </button>
                    <button
                      onClick={() => setShowConfirm(false)}
                      disabled={isClearing}
                      className="flex-1 border border-border text-foreground font-medium py-2 px-3 rounded-lg text-sm hover:bg-accent transition-colors disabled:opacity-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setShowConfirm(true)}
                  className="w-full border border-border hover:bg-accent text-muted-foreground font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <Trash2 size={18} />
                  Clear Storage
                </button>
              )}
            </div>
          </>
        )}
      </motion.div>
    </>
  );
};
