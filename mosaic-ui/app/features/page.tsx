"use client";

import React from "react";
import Link from "next/link";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Video,
  Sparkles,
  Search,
  Zap,
  MessageSquare,
  Clock,
  Database,
  Shield,
  Globe,
  Cpu,
  Eye,
  FileText,
  ArrowRight,
} from "lucide-react";

export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-background text-foreground relative">
      <Navigation />

      {/* Hero Section */}
      <section className="container py-20 md:py-32 relative z-10">
        <div className="mx-auto max-w-4xl text-center">
          <Badge className="mb-4" variant="secondary">
            Features
          </Badge>
          <h1 className="mb-6 text-5xl md:text-7xl font-display font-normal tracking-tight">
            Powerful video intelligence
            <br />
            at your fingertips
          </h1>
          <p className="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground">
            Discover all the capabilities that make Mosaic the most advanced
            video analysis platform available.
          </p>
        </div>
      </section>

      {/* Core Features */}
      <section className="container py-20 relative z-10">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-3xl font-display font-normal mb-12 text-center">
            Core Features
          </h2>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: Video,
                title: "Advanced Video Processing",
                description:
                  "Extract frames, analyze content, and process videos with state-of-the-art AI models.",
              },
              {
                icon: Search,
                title: "Semantic Search",
                description:
                  "Find exact moments using natural language. No need to remember timestamps.",
              },
              {
                icon: MessageSquare,
                title: "Intelligent Chat",
                description:
                  "Have conversations about your video content with our AI assistant.",
              },
              {
                icon: Eye,
                title: "Visual Analysis",
                description:
                  "Automatic object detection, scene recognition, and visual content understanding.",
              },
              {
                icon: FileText,
                title: "Transcription & Captions",
                description:
                  "Automatic speech recognition and caption generation for all your videos.",
              },
              {
                icon: Clock,
                title: "Timeline Navigation",
                description:
                  "Jump to any moment instantly with our intelligent timeline interface.",
              },
              {
                icon: Database,
                title: "Smart Indexing",
                description:
                  "All your videos are automatically indexed for instant search and retrieval.",
              },
              {
                icon: Cpu,
                title: "GPU Acceleration",
                description:
                  "Blazing fast processing with GPU support for demanding workloads.",
              },
              {
                icon: Shield,
                title: "Enterprise Security",
                description:
                  "Bank-level encryption and security for your sensitive video content.",
              },
            ].map((feature, index) => (
              <Card key={index} className="border-2">
                <CardHeader>
                  <div className="mb-4 rounded-lg bg-primary/10 w-12 h-12 flex items-center justify-center">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* AI Capabilities */}
      <section className="container py-20 bg-muted/30 relative z-10">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-3xl font-display font-normal mb-12 text-center">
            AI-Powered Capabilities
          </h2>
          <div className="grid gap-8 lg:grid-cols-2">
            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">
                    Computer Vision
                  </h3>
                  <p className="text-muted-foreground">
                    Detect objects, people, text, and scenes automatically with
                    our advanced computer vision models.
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <MessageSquare className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">
                    Natural Language
                  </h3>
                  <p className="text-muted-foreground">
                    Ask questions in plain English and get accurate answers
                    about your video content.
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">
                    Real-time Processing
                  </h3>
                  <p className="text-muted-foreground">
                    Get instant results with our optimized processing pipeline
                    and smart caching.
                  </p>
                </div>
              </div>
            </div>
            <div className="rounded-lg bg-gradient-to-br from-primary/10 to-primary/5 p-8 flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4">🎬</div>
                <p className="text-muted-foreground">
                  Built on cutting-edge AI models from leading research labs
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="container py-20 md:py-32 relative z-10">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-4xl md:text-5xl font-display font-normal mb-6">
            Ready to experience it?
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Start analyzing your videos with AI today
          </p>
          <Link href="/video">
            <Button size="lg" className="gap-2 bg-primary hover:bg-primary/90">
              Get Started Free
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
