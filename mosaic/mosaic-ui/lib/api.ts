import axios from "axios";

const API_URL = "http://localhost:8000";

export interface Video {
  video_id: string;
  filename: string;
  processed: boolean;
  summary?: string;
  created_at?: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  response: string;
  video_id: string;
  metadata: any;
}

export const api = axios.create({
  baseURL: API_URL,
});

export const uploadVideo = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/upload-video", formData);
  return response.data;
};

export const getVideos = async () => {
  const response = await api.get("/videos");
  return response.data; // Assuming it returns a list of videos
};

export const getVideoInfo = async (videoId: string) => {
  const response = await api.get(`/videos/${videoId}`);
  return response.data;
};

export const sendChatMessage = async (
  videoId: string,
  message: string,
  mediaPath?: string,
  mediaType?: string,
) => {
  const payload: any = { video_id: videoId, message };
  if (mediaPath) payload.media_path = mediaPath;
  if (mediaType) payload.media_type = mediaType;
  const response = await api.post("/chat", payload);
  return response.data;
};

export const getTaskStatus = async (taskId: string) => {
  const response = await api.get(`/status/${taskId}`);
  return response.data;
};

export const clearStorage = async () => {
  const response = await api.post("/clear-storage");
  return response.data;
};

export const uploadMedia = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/upload-media", formData);
  return response.data;
};
