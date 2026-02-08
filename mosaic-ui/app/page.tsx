"use client";

import React, { useState, useEffect } from "react";
import { Sidebar } from "@/components/Sidebar";
import { ChatArea } from "@/components/ChatArea";
import {
  Video,
  ChatMessage,
  getVideos,
  uploadVideo,
  sendChatMessage,
  getTaskStatus,
  uploadMedia,
} from "@/lib/api";

export default function Home() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [currentVideo, setCurrentVideo] = useState<Video | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      const data = await getVideos();
      // Ensure data is an array
      if (Array.isArray(data)) {
        setVideos(data);
      } else if (data && Array.isArray(data.videos)) {
        setVideos(data.videos);
      } else {
        console.error("Unexpected video data format:", data);
        setVideos([]);
      }
    } catch (error) {
      console.error("Failed to load videos:", error);
    }
  };

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const response = await uploadVideo(file);
      // Start polling for status
      pollStatus(response.task_id);
    } catch (error) {
      console.error("Upload failed:", error);
      setIsUploading(false);
    }
  };

  const pollStatus = async (taskId: string) => {
    const interval = setInterval(async () => {
      try {
        const status = await getTaskStatus(taskId);
        if (status.status === "completed") {
          clearInterval(interval);
          setIsUploading(false);
          loadVideos();
          // Optionally select the new video
        } else if (status.status === "failed") {
          clearInterval(interval);
          setIsUploading(false);
          alert("Video processing failed");
        }
      } catch (error) {
        clearInterval(interval);
        setIsUploading(false);
      }
    }, 2000);
  };

  const handleSelectVideo = (video: Video) => {
    setCurrentVideo(video);
    setMessages([
      {
        role: "assistant",
        content: `I am ready to analyze video ${video.filename || video.video_id}. What would you like to know?`,
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);
  };

  const handleStorageCleared = () => {
    // Reset all state after storage is cleared
    setVideos([]);
    setCurrentVideo(null);
    setMessages([]);
    loadVideos(); // Reload to confirm empty state
  };

  const handleSendMessage = async (text: string, file?: File) => {
    if (!currentVideo) {
      setMessages((prev) => [
        ...prev,
        {
          role: "user",
          content: file
            ? `[${file.type.startsWith("image/") ? "Image" : "Audio"}: ${file.name}] ${text}`
            : text,
          timestamp: new Date().toLocaleTimeString(),
        },
        {
          role: "assistant",
          content:
            "I'm sorry, Dave. You haven't selected a video stream yet. Please select a video from the library.",
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
      return;
    }

    // Build user message content (show attachment info)
    let userContent = text;
    if (file) {
      const fileType = file.type.startsWith("image/") ? "Image" : "Audio";
      userContent = `[${fileType}: ${file.name}]${text ? " " + text : ""}`;
    }

    const newMessage: ChatMessage = {
      role: "user",
      content: userContent,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, newMessage]);
    setIsChatLoading(true);

    try {
      let responseContent: string;

      if (file) {
        // Step 1: Upload the media file
        const uploadResult = await uploadMedia(file);

        // Extract server filename from media_path for display
        const serverFilename =
          uploadResult.media_path.split(/[\\\/]/).pop() || file.name;

        // Update user message to include server filename for rendering
        const updatedUserContent = `[${uploadResult.media_type === "image" ? "Image" : "Audio"}: ${file.name}|${serverFilename}]${text ? " " + text : ""}`;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: updatedUserContent,
          };
          return updated;
        });

        // Step 2: Send chat message through the agent, with media context
        const response = await sendChatMessage(
          currentVideo.video_id,
          text || "",
          uploadResult.media_path,
          uploadResult.media_type,
        );
        responseContent = response.response;
      } else {
        // Regular text chat through the agent
        const response = await sendChatMessage(currentVideo.video_id, text);
        responseContent = response.response;
      }

      const botMessage: ChatMessage = {
        role: "assistant",
        content: responseContent,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat failed:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I'm afraid I can't do that, Dave. There was an error processing your request.",
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <main className="flex h-screen bg-black text-white overflow-hidden">
      <div className="flex-1 flex relative">
        {/* Main Chat Area */}
        <ChatArea
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isChatLoading}
        />

        {/* Sidebar on the right */}
        <Sidebar
          videos={videos}
          onSelectVideo={handleSelectVideo}
          onUpload={handleUpload}
          isUploading={isUploading}
          onStorageCleared={handleStorageCleared}
        />
      </div>
    </main>
  );
}
