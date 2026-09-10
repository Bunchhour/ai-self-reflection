"use client";
import React, { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { EmotionWheel, EmotionSelection } from "@/components/emotions/EmotionWheel";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function QuickPulsePage() {
  const router = useRouter();
  const [emotions, setEmotions] = useState<EmotionSelection[]>([]);
  const [moodScore, setMoodScore] = useState(75);
  const [energy, setEnergy] = useState(3);
  const [thought, setThought] = useState("");
  const [win, setWin] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await api.reflections.create({
        entry_mode: "quick_pulse",
        reported_emotions: emotions,
        mood_score: moodScore,
        energy_level: energy,
        answers: {
          "What's on your mind?": thought,
          "One win today": win,
        },
      });

      if (res.needs_followup) {
        router.push("/reflect/followup");
      } else {
        router.push("/reflect/result");
      }
    } catch (err: any) {
      setError(err.message || "Failed to save reflection");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">⚡ Quick Pulse Reflection</CardTitle>
          <p className="text-sm text-muted-foreground">
            A fast 1–2 minute check-in to calibrate your mood and focus on what matters today.
          </p>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-6 rounded-md bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Emotions */}
            <div className="space-y-3">
              <Label className="text-base font-semibold">How are you feeling right now?</Label>
              <EmotionWheel onChange={setEmotions} />
            </div>

            {/* Mood Score */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <Label className="text-base font-semibold">Overall Mood (1–100)</Label>
                <span className="font-bold text-primary">{moodScore}</span>
              </div>
              <input
                type="range"
                min="1"
                max="100"
                value={moodScore}
                onChange={(e) => setMoodScore(parseInt(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            {/* Energy Level */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <Label className="text-base font-semibold">Energy Level (1–5)</Label>
                <span className="font-bold text-primary">Level {energy}</span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                value={energy}
                onChange={(e) => setEnergy(parseInt(e.target.value))}
                className="w-full accent-primary"
              />
              <div className="flex justify-between text-2xl pt-1 px-1">
                <span title="Drained">😴</span>
                <span title="Low">😐</span>
                <span title="Balanced">🙂</span>
                <span title="High">😊</span>
                <span title="Electric">⚡</span>
              </div>
            </div>

            {/* One Thought */}
            <div className="space-y-2">
              <Label htmlFor="thought" className="text-base font-semibold">
                What's on your mind?
              </Label>
              <Textarea
                id="thought"
                placeholder="Share whatever thought or feeling is top of mind right now..."
                value={thought}
                onChange={(e) => setThought(e.target.value)}
                required
                className="min-h-[100px]"
              />
            </div>

            {/* Win of the Day */}
            <div className="space-y-2">
              <Label htmlFor="win" className="text-base font-semibold">
                One win from today
              </Label>
              <Input
                id="win"
                placeholder="Something that went well, however small..."
                value={win}
                onChange={(e) => setWin(e.target.value)}
                required
              />
            </div>

            <Button type="submit" disabled={loading} className="w-full text-base py-6">
              {loading ? "Analyzing & Saving..." : "Save Reflection"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
