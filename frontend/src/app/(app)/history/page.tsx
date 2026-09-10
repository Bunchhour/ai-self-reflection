"use client";
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Calendar, ArrowRight, Sparkles } from "lucide-react";

export default function HistoryPage() {
  const { data: reflections, isLoading } = useQuery({
    queryKey: ["reflections"],
    queryFn: () => api.reflections.list(0, 30),
  });

  const { data: weeklySummary } = useQuery({
    queryKey: ["weeklySummary"],
    queryFn: api.reflections.weekly,
  });

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Reflection History</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Review your past reflections, emotional trends, and personal evolution.
        </p>
      </div>

      {/* Weekly AI Synthesis Banner */}
      {weeklySummary?.summary && (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              <CardTitle className="text-base font-semibold">Weekly AI Summary</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-foreground leading-relaxed">{weeklySummary.summary}</p>
          </CardContent>
        </Card>
      )}

      {/* Reflection Entries List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-12 text-muted-foreground">Loading reflections...</div>
        ) : !reflections || reflections.length === 0 ? (
          <div className="text-center py-12 space-y-3 border rounded-xl bg-card">
            <p className="text-muted-foreground">No reflections recorded yet.</p>
            <Link href="/reflect">
              <Button>Start Your First Reflection</Button>
            </Link>
          </div>
        ) : (
          reflections.map((ref: any) => (
            <Card key={ref.id} className="hover:shadow-sm transition-shadow">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-primary" />
                    <span className="font-semibold text-base">
                      {new Date(ref.date).toLocaleDateString(undefined, {
                        weekday: "long",
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="capitalize">
                      {ref.entry_mode.replace("_", " ")}
                    </Badge>
                    {ref.mood_score && (
                      <Badge variant="secondary">Mood: {ref.mood_score}/100</Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {ref.ai_summary || "Entry answers recorded."}
                </p>
                <div className="flex justify-end">
                  <Link href={`/history/${ref.id}`}>
                    <Button variant="ghost" size="sm" className="gap-1.5 text-xs">
                      View Details <ArrowRight className="h-3.5 w-3.5" />
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
