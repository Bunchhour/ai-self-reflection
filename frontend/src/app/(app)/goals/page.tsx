"use client";
import React, { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Target, Sparkles, Check, X, Plus } from "lucide-react";

export default function GoalsPage() {
  const queryClient = useQueryClient();
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const { data: goals, isLoading: goalsLoading } = useQuery({
    queryKey: ["goals"],
    queryFn: api.goals.list,
  });

  const { data: interests, isLoading: interestsLoading } = useQuery({
    queryKey: ["interests"],
    queryFn: api.goals.interests,
  });

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setSubmitting(true);
    try {
      await api.goals.create({
        title: newTitle,
        description: newDesc,
      });
      setNewTitle("");
      setNewDesc("");
      setShowAddForm(false);
      queryClient.invalidateQueries({ queryKey: ["goals"] });
    } catch (e) {
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  };

  const handleInterestRespond = async (id: string, response: "acknowledged" | "dismissed") => {
    try {
      await api.goals.respondInterest(id, { response });
      queryClient.invalidateQueries({ queryKey: ["interests"] });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Goals & Emerging Interests</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Turn recurring themes from your reflections into conscious growth goals.
          </p>
        </div>
        <Button onClick={() => setShowAddForm((p) => !p)} className="gap-1.5">
          <Plus className="h-4 w-4" /> {showAddForm ? "Cancel" : "Add New Goal"}
        </Button>
      </div>

      {/* Interest Nudges */}
      {interests && interests.length > 0 && (
        <Card className="border-primary/20 bg-gradient-to-r from-card to-primary/5">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Emerging Interest Nudges</CardTitle>
            </div>
            <p className="text-xs text-muted-foreground">
              Topics mentioned frequently in your reflections with positive sentiment.
            </p>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            {interests.map((signal: any) => (
              <div
                key={signal.id}
                className="flex items-center justify-between p-3 rounded-lg border bg-background text-sm"
              >
                <div>
                  <div className="font-semibold">{signal.topic}</div>
                  <div className="text-xs text-muted-foreground">
                    Mentioned {signal.mention_count} times • {signal.domain || "Interest"}
                  </div>
                </div>
                <div className="flex gap-1.5">
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-8 px-2 text-xs"
                    onClick={() => handleInterestRespond(signal.id, "acknowledged")}
                  >
                    <Check className="h-3.5 w-3.5 mr-1" /> Save
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-8 px-2 text-xs text-muted-foreground"
                    onClick={() => handleInterestRespond(signal.id, "dismissed")}
                  >
                    <X className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Goal Creation Form */}
      {showAddForm && (
        <Card className="border-primary/30">
          <CardHeader>
            <CardTitle className="text-lg">Set a New Growth Goal</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateGoal} className="space-y-4">
              <div className="space-y-1">
                <label className="text-sm font-medium">Goal Title</label>
                <Input
                  placeholder="e.g. Meditate for 10 minutes every morning"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Description & Milestones</label>
                <Textarea
                  placeholder="Why is this goal important to you? What does progress look like?"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                />
              </div>
              <Button type="submit" disabled={submitting}>
                {submitting ? "Saving..." : "Create Goal"}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Goals List */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Target className="h-5 w-5 text-primary" /> Active Goals
        </h2>

        {goalsLoading ? (
          <div className="text-sm text-muted-foreground">Loading goals...</div>
        ) : !goals || goals.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent className="space-y-2">
              <p className="text-muted-foreground">No active goals yet.</p>
              <Button variant="outline" size="sm" onClick={() => setShowAddForm(true)}>
                Create your first goal
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {goals.map((g: any) => (
              <Card key={g.id}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base font-semibold">{g.title}</CardTitle>
                    <Badge variant="outline" className="capitalize text-xs">
                      {g.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">
                  <p>{g.description || "No description provided."}</p>
                  <p className="text-xs text-muted-foreground mt-3 pt-2 border-t">
                    Created {new Date(g.created_at).toLocaleDateString()}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
