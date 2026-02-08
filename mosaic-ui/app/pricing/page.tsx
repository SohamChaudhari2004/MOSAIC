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
import { Check, ArrowRight } from "lucide-react";

export default function PricingPage() {
  const plans = [
    {
      name: "Starter",
      price: "$0",
      description: "Perfect for trying out Mosaic",
      features: [
        "5 videos per month",
        "Basic AI analysis",
        "10 GB storage",
        "Email support",
        "Community access",
      ],
      cta: "Start Free",
      popular: false,
    },
    {
      name: "Professional",
      price: "$49",
      description: "For professionals and small teams",
      features: [
        "100 videos per month",
        "Advanced AI models",
        "500 GB storage",
        "Priority support",
        "API access",
        "Team collaboration",
        "Custom integrations",
      ],
      cta: "Start Trial",
      popular: true,
    },
    {
      name: "Enterprise",
      price: "Custom",
      description: "For large organizations",
      features: [
        "Unlimited videos",
        "Premium AI models",
        "Unlimited storage",
        "24/7 dedicated support",
        "Full API access",
        "Advanced security",
        "Custom deployment",
        "SLA guarantee",
      ],
      cta: "Contact Sales",
      popular: false,
    },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground relative">
      <Navigation />

      {/* Hero Section */}
      <section className="container py-20 md:py-32 relative z-10">
        <div className="mx-auto max-w-4xl text-center">
          <Badge className="mb-4" variant="secondary">
            Pricing
          </Badge>
          <h1 className="mb-6 text-5xl md:text-7xl font-display font-normal tracking-tight">
            Simple, transparent pricing
          </h1>
          <p className="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground">
            Choose the plan thats right for you. All plans include access to our
            core features.
          </p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="container pb-20 md:pb-32 relative z-10">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-8 lg:grid-cols-3">
            {plans.map((plan, index) => (
              <Card
                key={index}
                className={`relative ${
                  plan.popular
                    ? "border-primary border-2 shadow-lg"
                    : "border-2"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <Badge className="px-4">Most Popular</Badge>
                  </div>
                )}
                <CardHeader>
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                  <div className="mt-4">
                    <span className="text-5xl font-display font-normal">
                      {plan.price}
                    </span>
                    {plan.price !== "Custom" && (
                      <span className="text-muted-foreground">/month</span>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  <ul className="space-y-3">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start gap-2">
                        <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Link href="/video" className="block">
                    <Button
                      className="w-full gap-2"
                      variant={plan.popular ? "default" : "outline"}
                    >
                      {plan.cta}
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="container py-20 bg-muted/30 relative z-10">
        <div className="mx-auto max-w-3xl">
          <h2 className="text-3xl font-display font-normal mb-12 text-center">
            Frequently Asked Questions
          </h2>
          <div className="space-y-8">
            {[
              {
                question: "Can I change plans later?",
                answer:
                  "Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.",
              },
              {
                question: "What payment methods do you accept?",
                answer:
                  "We accept all major credit cards, PayPal, and bank transfers for enterprise plans.",
              },
              {
                question: "Is there a free trial?",
                answer:
                  "Yes! All paid plans come with a 14-day free trial. No credit card required.",
              },
              {
                question: "What happens when I reach my limit?",
                answer:
                  "We'll notify you before you reach your limit. You can upgrade anytime to continue without interruption.",
              },
            ].map((faq, index) => (
              <div key={index}>
                <h3 className="text-xl font-semibold mb-2">{faq.question}</h3>
                <p className="text-muted-foreground">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="container py-20 md:py-32 relative z-10">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-4xl md:text-5xl font-display font-normal mb-6">
            Still have questions?
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Our team is here to help you find the perfect plan
          </p>
          <Button size="lg" variant="outline">
            Contact Sales
          </Button>
        </div>
      </section>
    </div>
  );
}
