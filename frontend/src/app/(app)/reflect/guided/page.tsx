"use client";
import React, { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { EmotionWheel, EmotionSelection } from "@/components/emotions/EmotionWheel";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { ArrowLeft, ArrowRight, Sparkles } from "lucide-react";

const STEPS = [
  {
    id: "emotions",
    title: "Emotional Baseline",
    subtitle: "Identify what emotions are present for you today.",
  },
  {
    id: "focus",
    title: "Main Focus & Wins",
    subtitle: "What demanded most of your energy today, and what went well?",
    question: "What was your main focus today, and what accomplishment are you proud of?",
    placeholder: "I spent my time on... and I felt great about...",
  },
  {
    id: "friction",
    title: "Challenges & Friction",
    subtitle: "Where did you feel resistance or difficulty?",
    question: "What felt heavy, frustrating, or challenging today?",
    placeholder: "The biggest friction was...",
  },
  {
    id: "learning",
    title: "Key Learning & Tomorrow",
    subtitle: "What insight will you carry forward?",
    question: "What did you learn about yourself or your work today, and what is your priority tomorrow?",
    placeholder: "I realized that... so tomorrow I want to...",
  },
];

export default function GuidedReflectionPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [emotions, setEmotions] = useState<EmotionSelection[]>([]);
  const [moodScore, setMoodScore] = useState(70);
  const [energyLevel, setEnergyLevel] = useState(3);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnswerChange = (stepId: string, val: string) => {
    setAnswers((prev) => ({ ...prev, [stepId]: val }));
  };

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const handleSubmit = async () => {
    setError("");
    setLoading(true);

    try {
      const formattedAnswers: Record<string, string> = {
        "Main Focus and Wins": answers["focus"] || "",
        "Challenges and Friction": answers["friction"] || "",
        "Key Learnings and Priority": answers["learning"] || "",
      };

      const res = await api.reflections.create({
        entry_mode: "guided",
        reported_emotions: emotions,
        mood_score: moodScore,
        energy_level: energyLevel,
        answers: formattedAnswers,
      });

      if (res.needs_followup) {
        router.push("/reflect/followup");
      } else {
        router.push("/reflect/result");
      }
    } catch (err: any) {
      setError(err.message || "Failed to save guided reflection");
      setLoading(false);
    }
  };

  const step = STEPS[currentStep];
  const progress = ((currentStep + 1) / STEPS.length) * 100;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="space-y-2">
        <div className="flex justify-between items-center text-sm font-medium text-muted-foreground">
          <span>Step {currentStep + 1} of {STEPS.length}</span>
          <span>{Math.round(progress)}% Completed</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <CardTitle className="text-xl">{step.title}</CardTitle>
          </div>
          <p className="text-sm text-muted-foreground">{step.subtitle}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="rounded-md bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive text-center">
              {error}
            </div>
          )}

          {step.id === "emotions" ? (
            <div className="space-y-6">
              <div className="space-y-3">
                <Label className="font-semibold">Select your emotions today</Label>
                <EmotionWheel onChange={setEmotions} />
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <Label className="font-semibold">Mood Score (1–100)</Label>
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
              <div className="space-y-3">
                <div className="flex justify-between">
                  <Label className="font-semibold">Energy Level (1–5)</Label>
                  <span className="font-bold text-primary">Level {energyLevel}</span>
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
          ) : (
            <div className="space-y-3">
              <Label className="text-base font-semibold">{step.question}</Label>
              <Textarea
                placeholder={step.placeholder}
                value={answers[step.id] || ""}
                onChange={(e) => handleAnswerChange(step.id, e.target.value)}
                className="min-h-[160px] text-base"
              />
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-between pt-4 border-t">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStep === 0 || loading}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" /> Back
          </Button>

          {currentStep < STEPS.length - 1 ? (
            <Button onClick={handleNext} className="gap-2">
              Next <ArrowRight className="h-4 w-4" />
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={loading} className="gap-2">
              {loading ? "Processing..." : "Complete Reflection"}
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
