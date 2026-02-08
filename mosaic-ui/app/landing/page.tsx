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
  Shield,
  Users,
  ArrowRight,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground relative">
      <Navigation />

      {/* Hero Section */}
      <section className="container relative overflow-hidden py-20 md:py-32 z-10">
        <div className="mx-auto max-w-4xl text-center">
          <Badge className="mb-4" variant="secondary">
            <Sparkles className="mr-1 h-3 w-3" />
            AI-Powered Video Analysis
          </Badge>
          <h1 className="mb-6 text-5xl md:text-7xl font-display font-normal tracking-tight">
            Unlock insights from
            <br />
            <span className="bg-linear-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              your videos
            </span>
          </h1>
          <p className="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground">
            Mosaic transforms how you interact with video content. Ask
            questions, find moments, and discover insights with our advanced AI
            technology.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/video">
              <Button
                size="lg"
                className="gap-2 bg-primary hover:bg-primary/90"
              >
                Start Analyzing
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/features">
              <Button
                size="lg"
                variant="outline"
                className="border-border hover:bg-secondary"
              >
                Learn More
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container py-20 md:py-32 relative z-10">
        <div className="mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-normal mb-4">
              Everything you need
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Powerful features to help you understand and navigate your video
              content
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: Video,
                title: "Smart Video Processing",
                description:
                  "Automatically extract and analyze frames from your videos with advanced AI models.",
              },
              {
                icon: Search,
                title: "Semantic Search",
                description:
                  "Find exact moments in your videos using natural language queries.",
              },
              {
                icon: Sparkles,
                title: "AI Conversations",
                description:
                  "Chat with your videos and get intelligent answers about their content.",
              },
              {
                icon: Zap,
                title: "Lightning Fast",
                description:
                  "Process videos quickly with optimized GPU acceleration and caching.",
              },
              {
                icon: Shield,
                title: "Secure & Private",
                description:
                  "Your videos stay on your infrastructure. We respect your privacy.",
              },
              {
                icon: Users,
                title: "Team Collaboration",
                description:
                  "Share insights and collaborate with your team on video analysis.",
              },
            ].map((feature, index) => (
              <Card key={index} className="border-2">
                <CardHeader>
                  <div className="mb-2 rounded-lg bg-primary/10 w-12 h-12 flex items-center justify-center">
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

      {/* How It Works */}
      <section className="container py-20 md:py-32 bg-muted/30 relative z-10">
        <div className="mx-auto max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-display font-normal mb-4">
              How it works
            </h2>
            <p className="text-lg text-muted-foreground">
              Get started in three simple steps
            </p>
          </div>
          <div className="space-y-8">
            {[
              {
                step: "01",
                title: "Upload Your Video",
                description:
                  "Simply drag and drop your video files. We support all common formats.",
              },
              {
                step: "02",
                title: "AI Processing",
                description:
                  "Our AI analyzes your video, extracting frames and understanding content.",
              },
              {
                step: "03",
                title: "Ask Questions",
                description:
                  "Chat with your video content and get instant, accurate answers.",
              },
            ].map((item, index) => (
              <div key={index} className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-16 h-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-display">
                  {item.step}
                </div>
                <div>
                  <h3 className="text-2xl font-display font-normal mb-2">
                    {item.title}
                  </h3>
                  <p className="text-muted-foreground">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container py-20 md:py-32 relative z-10">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-4xl md:text-5xl font-display font-normal mb-6">
            Ready to get started?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of users who are already unlocking insights from
            their videos
          </p>
          <Link href="/video">
            <Button size="lg" className="gap-2 bg-primary hover:bg-primary/90">
              Start Free Trial
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t relative z-10">
        <div className="container py-12">
          <div className="grid gap-8 md:grid-cols-4">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="h-8 w-8 rounded-lg bg-primary" />
                <span className="text-xl font-display font-semibold">
                  Mosaic
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                AI-powered video analysis platform
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>
                  <Link href="/features">Features</Link>
                </li>
                <li>
                  <Link href="/pricing">Pricing</Link>
                </li>
                <li>
                  <Link href="/app">Try Now</Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>
                  <Link href="/about">About</Link>
                </li>
                <li>
                  <Link href="/contact">Contact</Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>
                  <Link href="/privacy">Privacy</Link>
                </li>
                <li>
                  <Link href="/terms">Terms</Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t text-center text-sm text-muted-foreground">
            <p>&copy; 2026 Mosaic. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
