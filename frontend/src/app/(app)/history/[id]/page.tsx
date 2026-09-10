"use client";
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Trash2, Calendar, Sparkles } from "lucide-react";

export default function ReflectionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const { data: ref, isLoading } = useQuery({
    queryKey: ["reflection", id],
    queryFn: () => api.reflections.get(id),
    enabled: !!id,
  });

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this reflection?")) return;
    try {
      await api.reflections.delete(id);
      router.push("/history");
    } catch (e) {
      console.error(e);
    }
  };

  if (isLoading) {
    return <div className="text-center py-16 text-muted-foreground">Loading reflection details...</div>;
  }

  if (!ref) {
    return (
      <div className="text-center py-16 space-y-4">
        <p className="text-muted-foreground">Reflection not found.</p>
        <Button onClick={() => router.push("/history")}>Back to History</Button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => router.push("/history")} className="gap-2">
          <ArrowLeft className="h-4 w-4" /> Back to History
        </Button>
        <Button variant="destructive" size="sm" onClick={handleDelete} className="gap-1.5">
          <Trash2 className="h-4 w-4" /> Delete Entry
        </Button>
      </div>

      <div className="space-y-1">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Calendar className="h-4 w-4" />
          <span>{new Date(ref.date).toLocaleDateString(undefined, { weekday: "long", year: "numeric", month: "long", day: "numeric" })}</span>
        </div>
        <h1 className="text-3xl font-bold tracking-tight capitalize">{ref.entry_mode.replace("_", " ")} Entry</h1>
      </div>

      <div className="grid gap-6">
        {/* Synthesis */}
        {ref.ai_summary && (
          <Card className="border-primary/20 bg-primary/5">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <CardTitle className="text-base font-semibold">AI Synthesis</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed">{ref.ai_summary}</p>
            </CardContent>
          </Card>
        )}

        {/* Answers */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Your Responses</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {ref.answers && typeof ref.answers === "object" ? (
              Object.entries(ref.answers).map(([key, val]) => (
                <div key={key} className="space-y-1 border-b pb-3 last:border-b-0">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{key}</h4>
                  <p className="text-sm">{String(val)}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No recorded text responses.</p>
            )}

            {ref.followup_answers && (
              <div className="space-y-1 pt-3 border-t">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-primary">Follow-up Reflections</h4>
                <p className="text-sm">{ref.followup_answers}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Observations and Learnings */}
        {(ref.ai_what_went_well || ref.ai_what_was_learned || ref.ai_what_was_difficult) && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Insights Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2 text-sm">
              {ref.ai_what_went_well && (
                <div>
                  <span className="font-semibold text-green-600">What went well:</span>
                  <p className="text-muted-foreground mt-0.5">{ref.ai_what_went_well}</p>
                </div>
              )}
              {ref.ai_what_was_learned && (
                <div>
                  <span className="font-semibold text-blue-600">What was learned:</span>
                  <p className="text-muted-foreground mt-0.5">{ref.ai_what_was_learned}</p>
                </div>
              )}
              {ref.ai_what_was_difficult && (
                <div className="sm:col-span-2">
                  <span className="font-semibold text-amber-600">Difficulties & friction:</span>
                  <p className="text-muted-foreground mt-0.5">{ref.ai_what_was_difficult}</p>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
