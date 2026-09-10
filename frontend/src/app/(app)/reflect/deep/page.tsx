"use client";
import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { EmotionWheel, EmotionSelection } from "@/components/emotions/EmotionWheel";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Save, Check } from "lucide-react";

const CATEGORIES = [
  { id: "mindset", name: "Mental Clarity & State of Mind", placeholder: "What is your internal dialogue like today?" },
  { id: "work", name: "Work & Professional Execution", placeholder: "What projects or tasks did you push forward?" },
  { id: "challenges", name: "Obstacles & Friction Points", placeholder: "Where did you feel blocked or drained?" },
  { id: "wins", name: "Key Wins & Celebrations", placeholder: "What went exceptionally well?" },
  { id: "health", name: "Physical Health & Body Vitality", placeholder: "Sleep, nutrition, movement, stress levels..." },
  { id: "relationships", name: "Social Connections & Relationships", placeholder: "Conversations that inspired or tested you..." },
  { id: "learning", name: "Insights & Learnings", placeholder: "What did today teach you?" },
  { id: "habits", name: "Habits & Routine Integrity", placeholder: "Did your rituals hold up today?" },
  { id: "finances", name: "Financial Awareness", placeholder: "Money decisions or thoughts today..." },
  { id: "creative", name: "Creativity & Play", placeholder: "Moments of playfulness, beauty, or creativity..." },
  { id: "tomorrow", name: "Tomorrow's Core Intention", placeholder: "What is the single most important focus tomorrow?" },
  { id: "venting", name: "Unfiltered Stream of Consciousness", placeholder: "Freely vent anything unsaid..." },
];

export default function DeepDivePage() {
  const router = useRouter();
  const [emotions, setEmotions] = useState<EmotionSelection[]>([]);
  const [moodScore, setMoodScore] = useState(70);
  const [energyLevel, setEnergyLevel] = useState(3);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [savedTime, setSavedTime] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load from sessionStorage on mount
  useEffect(() => {
    try {
      const saved = sessionStorage.getItem("reflect_deep_dive_draft");
      if (saved) {
        const parsed = JSON.parse(saved);
        setAnswers(parsed.answers || {});
        if (parsed.moodScore) setMoodScore(parsed.moodScore);
        if (parsed.energyLevel) setEnergyLevel(parsed.energyLevel);
        setSavedTime("Loaded from draft");
      }
    } catch {}
  }, []);

  // Auto-save to sessionStorage
  const handleAnswerChange = (categoryId: string, val: string) => {
    const next = { ...answers, [categoryId]: val };
    setAnswers(next);
    try {
      sessionStorage.setItem(
        "reflect_deep_dive_draft",
        JSON.stringify({ answers: next, moodScore, energyLevel })
      );
      setSavedTime("Draft auto-saved");
    } catch {}
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const formattedAnswers: Record<string, string> = {};
      CATEGORIES.forEach((cat) => {
        if (answers[cat.id]) {
          formattedAnswers[cat.name] = answers[cat.id];
        }
      });

      const res = await api.reflections.create({
        entry_mode: "deep_dive",
        reported_emotions: emotions,
        mood_score: moodScore,
        energy_level: energyLevel,
        answers: formattedAnswers,
      });

      sessionStorage.removeItem("reflect_deep_dive_draft");

      if (res.needs_followup) {
        router.push("/reflect/followup");
      } else {
        router.push("/reflect/result");
      }
    } catch (err: any) {
      setError(err.message || "Failed to submit deep dive reflection");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">📝 Deep Dive Reflection</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Comprehensive 12-category exploration with continuous session auto-save.
          </p>
        </div>
        {savedTime && (
          <div className="inline-flex items-center gap-1.5 text-xs text-muted-foreground bg-muted px-3 py-1 rounded-full">
            <Save className="h-3.5 w-3.5 text-green-600" />
            {savedTime}
          </div>
        )}
      </div>

      {error && (
        <div className="rounded-md bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive text-center">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Emotional Baseline Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Emotional Calibration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <Label className="font-semibold">Core Emotions</Label>
              <EmotionWheel onChange={setEmotions} />
            </div>

            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Mood Score: {moodScore}</Label>
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

              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Energy Level: Level {energyLevel}</Label>
                </div>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={energyLevel}
                  onChange={(e) => setEnergyLevel(parseInt(e.target.value))}
                  className="w-full accent-primary"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 12 Categories */}
        <div className="space-y-6">
          {CATEGORIES.map((cat, idx) => (
            <Card key={cat.id}>
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-semibold flex items-center gap-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-primary text-xs font-bold">
                    {idx + 1}
                  </span>
                  {cat.name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  placeholder={cat.placeholder}
                  value={answers[cat.id] || ""}
                  onChange={(e) => handleAnswerChange(cat.id, e.target.value)}
                  className="min-h-[90px]"
                />
              </CardContent>
            </Card>
          ))}
        </div>

        <Button type="submit" disabled={loading} className="w-full text-base py-6">
          {loading ? "Synthesizing Reflection..." : "Submit Deep Dive Reflection"}
        </Button>
      </form>
    </div>
  );
}
