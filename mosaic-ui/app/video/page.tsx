"use client";

import React, { useState, useEffect } from "react";
import Lottie from "lottie-react";
import loadingAnimation from "@/public/Loading.json";
import { CollapsibleSidebar } from "@/components/CollapsibleSidebar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Video,
  ChatMessage,
  getVideos,
  uploadVideo,
  sendChatMessage,
  getTaskStatus,
  uploadMedia,
} from "@/lib/api";
import {
  RefreshCw,
  Paperclip,
  Image as ImageIcon,
  Send,
  Video as VideoIcon,
  Search,
  Sparkles,
  FileText,
  Download,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function VideoAnalysisApp() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [currentVideo, setCurrentVideo] = useState<Video | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [input, setInput] = useState("");
  const [showChat, setShowChat] = useState(false);
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const promptSuggestions = [
    {
      title: "Find a specific scene in my video",
      description: "Search for moments using natural language",
      icon: Search,
    },
    {
      title: "Generate a summary of this video",
      description: "Get AI-powered insights and key points",
      icon: Sparkles,
    },
    {
      title: "Extract clips from specific timestamps",
      description: "Create clips based on what you're looking for",
      icon: VideoIcon,
    },
    {
      title: "Transcribe and analyze the content",
      description: "Get full text transcription with insights",
      icon: FileText,
    },
  ];

  useEffect(() => {
    loadVideos();
  }, []);

  // Cleanup object URLs to prevent memory leaks
  useEffect(() => {
    return () => {
      messages.forEach((message) => {
        if (message.imageUrl && message.imageUrl.startsWith("blob:")) {
          URL.revokeObjectURL(message.imageUrl);
        }
      });
    };
  }, [messages]);

  const loadVideos = async () => {
    try {
      const data = await getVideos();
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
        } else if (status.status === "failed") {
          clearInterval(interval);
          setIsUploading(false);
          alert("Video processing failed");
        }
      } catch {
        clearInterval(interval);
        setIsUploading(false);
      }
    }, 2000);
  };

  const handleSelectVideo = (video: Video) => {
    setCurrentVideo(video);
    setShowChat(true);
    setMessages([
      {
        role: "assistant",
        content: `Video "${video.filename || video.video_id}" is ready for analysis. What would you like to know?`,
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);
  };

  const handleStorageCleared = () => {
    setVideos([]);
    setCurrentVideo(null);
    setMessages([]);
    setShowChat(false);
    loadVideos();
  };

  const handleSendMessage = async () => {
    if (!input.trim() && !attachedFile) return;

    if (!currentVideo) {
      setMessages([
        {
          role: "assistant",
          content: "Please select a video from the library first.",
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
      setShowChat(true);
      return;
    }

    const text = input;
    setInput("");
    const file = attachedFile;
    setAttachedFile(null);

    let userContent = text;
    let imageUrl: string | undefined;
    let fileName: string | undefined;

    if (file) {
      const fileType = file.type.startsWith("image/") ? "Image" : "Audio";
      userContent = text || `Uploaded ${fileType.toLowerCase()}`;
      fileName = file.name;

      // Create object URL for image preview
      if (file.type.startsWith("image/")) {
        imageUrl = URL.createObjectURL(file);
      }
    }

    const newMessage: ChatMessage = {
      role: "user",
      content: userContent,
      timestamp: new Date().toLocaleTimeString(),
      imageUrl,
      fileName,
    };
    setMessages((prev) => [...prev, newMessage]);
    setShowChat(true);
    setIsChatLoading(true);

    try {
      let responseContent: string;

      if (file) {
        const uploadResult = await uploadMedia(file);
        const response = await sendChatMessage(
          currentVideo.video_id,
          text || "",
          uploadResult.media_path,
          uploadResult.media_type,
        );
        responseContent = response.response;
      } else {
        const response = await sendChatMessage(currentVideo.video_id, text);
        responseContent = response.response;
      }

      // Extract video clip path if present in response
      let videoUrl: string | undefined;
      // Match patterns like: clips_output\a49c37c0\clip_1.mp4 or clip_1.mp4
      const clipMatch =
        responseContent.match(/clips_output[\\\/](\w+)[\\\/](clip_\d+\.mp4)/) ||
        responseContent.match(/(clip_\d+\.mp4)/);

      if (clipMatch) {
        if (clipMatch.length === 3) {
          // Full path match with video ID
          const videoId = clipMatch[1];
          const clipFile = clipMatch[2];
          videoUrl = `http://localhost:8000/clips/${videoId}/${clipFile}`;
        } else {
          // Just filename match, use current video ID
          const clipFile = clipMatch[1];
          videoUrl = `http://localhost:8000/clips/${currentVideo.video_id}/${clipFile}`;
        }
      }

      const botMessage: ChatMessage = {
        role: "assistant",
        content: responseContent,
        timestamp: new Date().toLocaleTimeString(),
        videoUrl,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat failed:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "There was an error processing your request. Please try again.",
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handlePromptClick = (prompt: (typeof promptSuggestions)[0]) => {
    setInput(prompt.title);
  };

  const handleFileAttach = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAttachedFile(e.target.files[0]);
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <CollapsibleSidebar
        videos={videos}
        onSelectVideo={handleSelectVideo}
        onUpload={handleUpload}
        isUploading={isUploading}
        onStorageCleared={handleStorageCleared}
      />

      <div className="flex-1 flex flex-col relative">
        {!showChat ? (
          /* Welcome Screen */
          <div className="flex-1 overflow-y-auto">
            <div className="container max-w-4xl mx-auto px-4 py-12 md:py-20">
              <div className="mb-12">
                <h1 className="text-4xl md:text-6xl font-display font-normal mb-4">
                  Hi there, <span className="text-primary">User</span>
                </h1>
                <h2 className="text-3xl md:text-5xl font-display font-normal text-muted-foreground">
                  What would{" "}
                  <span className="text-foreground">like to know?</span>
                </h2>
                <p className="text-sm text-muted-foreground mt-4">
                  {currentVideo
                    ? `Analyzing: ${currentVideo.filename || currentVideo.video_id}`
                    : "Upload a video or select one from the library to begin"}
                </p>
              </div>

              <div className="grid gap-4 md:grid-cols-2 mb-8">
                {promptSuggestions.map((prompt, index) => (
                  <Card
                    key={index}
                    className="cursor-pointer hover:border-primary transition-all group"
                    onClick={() => handlePromptClick(prompt)}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <div className="p-3 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                          <prompt.icon className="h-6 w-6 text-primary" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium mb-1">{prompt.title}</h3>
                          <p className="text-sm text-muted-foreground">
                            {prompt.description}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <div className="flex justify-center">
                <Button variant="ghost" size="sm" className="gap-2">
                  <RefreshCw className="h-4 w-4" />
                  Refresh Prompts
                </Button>
              </div>
            </div>
          </div>
        ) : (
          /* Chat View */
          <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-4xl mx-auto space-y-4">
              <div className="flex items-center gap-2 mb-6">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowChat(false)}
                >
                  ← Back
                </Button>
                <Badge variant="secondary">
                  {currentVideo?.filename || currentVideo?.video_id}
                </Badge>
              </div>

              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg overflow-hidden ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-card border border-border"
                      }`}
                    >
                      {/* Image preview for user messages */}
                      {message.imageUrl && (
                        <div className="border-b border-border/50 bg-muted/50">
                          <img
                            src={message.imageUrl}
                            alt={message.fileName || "Uploaded image"}
                            className="w-full max-h-64 object-contain"
                          />
                          {message.fileName && (
                            <div className="px-4 py-2 flex items-center gap-2 text-xs opacity-80 bg-background/20">
                              <ImageIcon className="h-3 w-3" />
                              {message.fileName}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Video clip preview for assistant responses */}
                      {message.videoUrl && (
                        <div className="border-b border-border/50 bg-black">
                          <video
                            src={message.videoUrl}
                            controls
                            className="w-full max-h-96"
                            preload="metadata"
                          >
                            Your browser does not support the video tag.
                          </video>
                          <div className="px-4 py-2 flex items-center justify-between bg-black/50">
                            <div className="flex items-center gap-2 text-xs text-white">
                              <VideoIcon className="h-3 w-3" />
                              Generated Clip
                            </div>
                            <a
                              href={message.videoUrl}
                              download
                              className="flex items-center gap-1 text-xs text-primary hover:text-primary/80 transition-colors"
                            >
                              <Download className="h-3 w-3" />
                              Download
                            </a>
                          </div>
                        </div>
                      )}

                      <div className="p-4">
                        <p className="text-sm whitespace-pre-wrap">
                          {message.content}
                        </p>
                        <p className="text-xs mt-2 opacity-70">
                          {message.timestamp}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {isChatLoading && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-card border border-border rounded-lg p-8">
                    <div className="flex flex-col items-center gap-6">
                      <div className="w-32 h-32">
                        <Lottie
                          animationData={loadingAnimation}
                          loop={true}
                          autoplay={true}
                          style={{ width: "100%", height: "100%" }}
                        />
                      </div>
                      <motion.p
                        className="text-sm text-muted-foreground font-medium"
                        animate={{
                          opacity: [0.5, 1, 0.5],
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          ease: "easeInOut",
                        }}
                      >
                        Analyzing video...
                      </motion.p>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t bg-transparent">
          <div className="container max-w-4xl mx-auto px-4 py-6">
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                {/* <Button variant="outline" size="sm" className="gap-2 text-xs">
                  All Videos
                  <ChevronDown className="h-3 w-3" />
                </Button> */}
              </div>

              {attachedFile && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-3 p-3 border rounded-lg bg-card"
                >
                  <div className="flex items-center gap-3">
                    {attachedFile.type.startsWith("image/") ? (
                      <div className="relative w-16 h-16 rounded overflow-hidden bg-muted flex-shrink-0">
                        <img
                          src={URL.createObjectURL(attachedFile)}
                          alt="Preview"
                          className="w-full h-full object-cover"
                        />
                      </div>
                    ) : (
                      <div className="w-12 h-12 rounded bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <Paperclip className="h-6 w-6 text-primary" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {attachedFile.name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {attachedFile.type.startsWith("image/")
                          ? "Image"
                          : "Audio"}{" "}
                        • {(attachedFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 flex-shrink-0"
                      onClick={() => setAttachedFile(null)}
                    >
                      <span className="text-lg">×</span>
                    </Button>
                  </div>
                </motion.div>
              )}

              <div className="relative rounded-lg border bg-background focus-within:ring-2 focus-within:ring-ring">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask whatever you want..."
                  className="border-0 pr-32 focus-visible:ring-0 focus-visible:ring-offset-0"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                />

                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Paperclip className="h-4 w-4" />
                  </Button>
                  {/* <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <ImageIcon className="h-4 w-4" />
                  </Button> */}
                  <Button
                    size="icon"
                    className="h-8 w-8"
                    disabled={!input.trim() && !attachedFile}
                    onClick={handleSendMessage}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileAttach}
                  className="hidden"
                  accept="image/*,audio/*"
                />
              </div>

              <div className="flex justify-end mt-2">
                <span className="text-xs text-muted-foreground">
                  {input.length}/1000
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
