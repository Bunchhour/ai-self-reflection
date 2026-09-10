"use client";
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Sparkles, HelpCircle } from "lucide-react";

export default function FollowupPage() {
  const router = useRouter();
  const [answers, setAnswers] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const { data: today, isLoading } = useQuery({
    queryKey: ["today"],
    queryFn: api.reflections.today,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!today?.id) return;
    setError("");
    setLoading(true);

    try {
      await api.reflections.followup(today.id, {
        followup_answers: answers,
      });
      router.push("/reflect/result");
    } catch (err: any) {
      setError(err.message || "Failed to submit follow-up response");
      setLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-muted-foreground">Checking reflection state...</p>
      </div>
    );
  }

  if (!today) {
    return (
      <div className="text-center py-12 space-y-4">
        <h2 className="text-xl font-semibold">No active reflection for today</h2>
        <Button onClick={() => router.push("/reflect")}>Start Reflection</Button>
      </div>
    );
  }

  const questions = today.followup_questions || [
    "Could you expand on what triggered your strongest emotion today?",
    "How does today's experience connect with your larger priorities?",
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Card className="border-primary/20 bg-gradient-to-br from-card to-primary/5">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <CardTitle className="text-2xl">AI Follow-up Inquiries</CardTitle>
          </div>
          <p className="text-sm text-muted-foreground">
            The AI reflection engine identified key areas where exploring further will reveal deeper patterns.
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="rounded-xl border bg-card p-5 space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-primary">
              <HelpCircle className="h-4 w-4" /> Questions to ponder:
            </div>
            <ul className="space-y-2 text-sm">
              {questions.map((q: string, idx: number) => (
                <li key={idx} className="flex gap-2">
                  <span className="font-semibold text-primary">{idx + 1}.</span>
                  <span>{q}</span>
                </li>
              ))}
            </ul>
          </div>

          {error && (
            <div className="rounded-md bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="followup" className="text-sm font-medium">
                Your thoughts and deeper perspective:
              </label>
              <Textarea
                id="followup"
                placeholder="Share your deeper reflections here..."
                value={answers}
                onChange={(e) => setAnswers(e.target.value)}
                required
                className="min-h-[140px]"
              />
            </div>
            <div className="flex gap-3">
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? "Synthesizing Insights..." : "Submit Answers & View Insights"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
