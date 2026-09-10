"use client";
import React, { useState } from "react";
import { cn } from "@/lib/utils";

const CORE_EMOTIONS = [
  "Joy",
  "Gratitude",
  "Calm",
  "Trust",
  "Anticipation",
  "Surprise",
  "Sadness",
  "Fear",
  "Anger",
  "Overwhelmed",
];

export interface EmotionSelection {
  emotion: string;
  intensity: number;
}

export function EmotionWheel({
  onChange,
}: {
  onChange: (emotions: EmotionSelection[]) => void;
}) {
  const [selected, setSelected] = useState<EmotionSelection[]>([]);

  const toggleEmotion = (emotion: string) => {
    let next: EmotionSelection[];
    if (selected.some((e) => e.emotion === emotion)) {
      next = selected.filter((e) => e.emotion !== emotion);
    } else {
      next = [...selected, { emotion, intensity: 2 }];
    }
    setSelected(next);
    onChange(next);
  };

  const updateIntensity = (emotion: string, intensity: number) => {
    const next = selected.map((e) =>
      e.emotion === emotion ? { ...e, intensity } : e
    );
    setSelected(next);
    onChange(next);
  };

  const intensityLabels: Record<number, string> = {
    1: "Mild",
    2: "Moderate",
    3: "Strong",
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap gap-2">
        {CORE_EMOTIONS.map((emotion) => {
          const isSelected = selected.some((e) => e.emotion === emotion);
          return (
            <button
              key={emotion}
              type="button"
              onClick={() => toggleEmotion(emotion)}
              className={cn(
                "px-4 py-2 rounded-full border text-sm font-medium transition-all",
                isSelected
                  ? "bg-primary text-primary-foreground border-primary shadow-sm scale-105"
                  : "bg-background text-foreground hover:bg-muted"
              )}
            >
              {emotion}
            </button>
          );
        })}
      </div>

      {selected.length > 0 && (
        <div className="space-y-3 rounded-xl border bg-muted/30 p-4">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Adjust Emotion Intensities
          </h4>
          <div className="space-y-3">
            {selected.map((item) => (
              <div key={item.emotion} className="flex items-center justify-between gap-4">
                <span className="text-sm font-medium w-28">{item.emotion}</span>
                <input
                  type="range"
                  min="1"
                  max="3"
                  value={item.intensity}
                  onChange={(e) => updateIntensity(item.emotion, parseInt(e.target.value))}
                  className="w-full max-w-[180px] accent-primary"
                />
                <span className="text-xs font-semibold text-muted-foreground w-16 text-right">
                  {intensityLabels[item.intensity] || "Moderate"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
