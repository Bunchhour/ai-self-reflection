import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Sparkles, Brain, Compass, ShieldCheck } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="flex h-16 items-center justify-between border-b px-8">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold">
            R
          </div>
          <span className="text-xl font-bold tracking-tight text-primary">ReflectAI</span>
        </div>
        <div className="space-x-4">
          <Link href="/login">
            <Button variant="ghost">Sign In</Button>
          </Link>
          <Link href="/register">
            <Button>Get Started</Button>
          </Link>
        </div>
      </header>

      <main className="flex-1">
        <section className="flex flex-col items-center justify-center px-4 py-24 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border bg-muted/50 px-4 py-1.5 text-sm font-medium mb-6">
            <Sparkles className="h-4 w-4 text-primary" /> Powered by LangGraph & Groq AI
          </div>
          <h1 className="max-w-4xl text-5xl font-extrabold tracking-tight sm:text-6xl mb-6">
            Master Your Mind with <span className="text-primary">Adaptive Reflection</span>
          </h1>
          <p className="max-w-2xl text-xl text-muted-foreground mb-10">
            Daily pulse check-ins, emotion tracking, cross-session pattern detection, and personalized micro-experiments that help you build lasting self-awareness.
          </p>
          <div className="flex gap-4">
            <Link href="/register">
              <Button size="lg" className="text-base px-8">
                Start Your Journey
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="text-base px-8">
                Sign In
              </Button>
            </Link>
          </div>
        </section>

        <section className="border-t bg-muted/20 py-20 px-8">
          <div className="max-w-6xl mx-auto grid gap-8 md:grid-cols-3">
            <div className="p-6 rounded-xl border bg-card shadow-sm space-y-3">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Brain className="h-5 w-5" />
              </div>
              <h3 className="text-xl font-semibold">Adaptive Modes</h3>
              <p className="text-muted-foreground text-sm">
                From a 1-minute Quick Pulse to deep 12-category dives, reflect on your terms while AI prompts intelligent follow-ups.
              </p>
            </div>
            <div className="p-6 rounded-xl border bg-card shadow-sm space-y-3">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Compass className="h-5 w-5" />
              </div>
              <h3 className="text-xl font-semibold">Semantic Vector Memory</h3>
              <p className="text-muted-foreground text-sm">
                Powered by pgvector and embeddings, the platform connects your thoughts over weeks to spot recurring behavioral patterns.
              </p>
            </div>
            <div className="p-6 rounded-xl border bg-card shadow-sm space-y-3">
              <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <h3 className="text-xl font-semibold">Micro-Experiments</h3>
              <p className="text-muted-foreground text-sm">
                Turn reflective insights into action with AI-suggested daily experiments you can accept, modify, and review.
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        © {new Date().getFullYear()} ReflectAI Platform. All rights reserved.
      </footer>
    </div>
  );
}
