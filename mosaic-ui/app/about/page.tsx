"use client";

import React from "react";
import Link from "next/link";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Heart, Zap, Users } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background text-foreground relative">
      <Navigation />

      {/* Hero Section */}
      <section className="container py-20 md:py-32 relative z-10">
        <div className="mx-auto max-w-4xl text-center">
          <Badge className="mb-4" variant="secondary">
            About Us
          </Badge>
          <h1 className="mb-6 text-5xl md:text-7xl font-display font-normal tracking-tight">
            Making video intelligence
            <br />
            <span className="bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              accessible to everyone
            </span>
          </h1>
          <p className="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground">
            We believe that understanding video content should be as easy as
            having a conversation. That&apos;s why we built Mosaic.
          </p>
        </div>
      </section>

      {/* Mission Section */}
      <section className="container py-20 relative z-10">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-12 lg:grid-cols-2 items-center">
            <div>
              <h2 className="text-4xl font-display font-normal mb-6">
                Our Mission
              </h2>
              <p className="text-lg text-muted-foreground mb-4">
                Video is one of the richest forms of information, yet it remains
                difficult to search, analyze, and extract insights from.
                We&apos;re changing that.
              </p>
              <p className="text-lg text-muted-foreground mb-6">
                Mosaic empowers individuals and teams to unlock the full
                potential of their video content through advanced AI technology
                that&apos;s both powerful and intuitive.
              </p>
            </div>
            <div className="rounded-lg bg-gradient-to-br from-primary/20 to-primary/5 p-12 flex items-center justify-center">
              <div className="text-center">
                <div className="text-8xl mb-4">🎯</div>
                <p className="text-xl font-display">
                  Democratizing video intelligence
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="container py-20 bg-muted/30 relative z-10">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-3xl font-display font-normal mb-12 text-center">
            Our Values
          </h2>
          <div className="grid gap-8 md:grid-cols-3">
            <Card className="border-2">
              <CardContent className="pt-6">
                <div className="mb-4 rounded-lg bg-primary/10 w-12 h-12 flex items-center justify-center">
                  <Heart className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">User-First</h3>
                <p className="text-muted-foreground">
                  Every feature we build starts with understanding our
                  users&apos; needs and challenges.
                </p>
              </CardContent>
            </Card>
            <Card className="border-2">
              <CardContent className="pt-6">
                <div className="mb-4 rounded-lg bg-primary/10 w-12 h-12 flex items-center justify-center">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Innovation</h3>
                <p className="text-muted-foreground">
                  We constantly push the boundaries of what&apos;s possible with
                  AI and video technology.
                </p>
              </CardContent>
            </Card>
            <Card className="border-2">
              <CardContent className="pt-6">
                <div className="mb-4 rounded-lg bg-primary/10 w-12 h-12 flex items-center justify-center">
                  <Users className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Collaboration</h3>
                <p className="text-muted-foreground">
                  Great insights come from teams working together. We make that
                  easy.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="container py-20 relative z-10">
        <div className="mx-auto max-w-4xl">
          <h2 className="text-3xl font-display font-normal mb-8 text-center">
            Built on Cutting-Edge Technology
          </h2>
          <p className="text-lg text-muted-foreground text-center mb-12">
            Mosaic leverages the latest advances in artificial intelligence,
            computer vision, and natural language processing to deliver
            unparalleled video understanding.
          </p>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="p-6 rounded-lg border-2">
              <h3 className="text-xl font-semibold mb-2">
                Advanced Computer Vision
              </h3>
              <p className="text-muted-foreground">
                State-of-the-art models for object detection, scene recognition,
                and visual content analysis.
              </p>
            </div>
            <div className="p-6 rounded-lg border-2">
              <h3 className="text-xl font-semibold mb-2">
                Natural Language AI
              </h3>
              <p className="text-muted-foreground">
                Powerful language models that understand context and provide
                accurate, relevant answers.
              </p>
            </div>
            <div className="p-6 rounded-lg border-2">
              <h3 className="text-xl font-semibold mb-2">
                Scalable Infrastructure
              </h3>
              <p className="text-muted-foreground">
                Built to handle videos of any size with GPU acceleration and
                intelligent caching.
              </p>
            </div>
            <div className="p-6 rounded-lg border-2">
              <h3 className="text-xl font-semibold mb-2">
                Privacy-First Design
              </h3>
              <p className="text-muted-foreground">
                Your data stays secure with enterprise-grade encryption and
                privacy controls.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="container py-20 md:py-32 relative z-10">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-4xl md:text-5xl font-display font-normal mb-6">
            Join us on this journey
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Experience the future of video intelligence today
          </p>
          <Link href="/video">
            <Button size="lg" className="gap-2 bg-primary hover:bg-primary/90">
              Get Started
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
