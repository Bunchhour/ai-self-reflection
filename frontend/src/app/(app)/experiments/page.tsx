"use client";
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { FlaskConical, Check, X, Star, Calendar } from "lucide-react";

export default function ExperimentsPage() {
  const queryClient = useQueryClient();
  const [reviewingExp, setReviewingExp] = useState<any | null>(null);
  const [rating, setRating] = useState(5);
  const [feedback, setFeedback] = useState("");
  const [tried, setTried] = useState(true);

  const { data: experiments, isLoading } = useQuery({
    queryKey: ["experiments"],
    queryFn: api.experiments.list,
  });

  const { data: stats } = useQuery({
    queryKey: ["experimentStats"],
    queryFn: api.experiments.stats,
  });

  const handleRespond = async (id: string, status: "accepted" | "skipped") => {
    try {
      await api.experiments.respond(id, { status });
      queryClient.invalidateQueries({ queryKey: ["experiments"] });
      queryClient.invalidateQueries({ queryKey: ["pendingExp"] });
    } catch (e) {
      console.error(e);
    }
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewingExp) return;

    try {
      await api.experiments.review(reviewingExp.id, {
        rating,
        feedback,
        tried,
      });
      setReviewingExp(null);
      setFeedback("");
      queryClient.invalidateQueries({ queryKey: ["experiments"] });
      queryClient.invalidateQueries({ queryKey: ["experimentStats"] });
    } catch (e) {
      console.error(e);
    }
  };

  const statusColors: Record<string, string> = {
    pending: "bg-amber-500/10 text-amber-600 border-amber-200",
    accepted: "bg-blue-500/10 text-blue-600 border-blue-200",
    completed: "bg-green-500/10 text-green-600 border-green-200",
    skipped: "bg-muted text-muted-foreground border-border",
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Micro-Experiments</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Turn self-reflection into small, low-risk daily actions and track what actually works.
          </p>
        </div>
        {stats && (
          <div className="flex items-center gap-4 text-sm bg-card border rounded-lg px-4 py-2">
            <div>
              <span className="text-muted-foreground">Total:</span>{" "}
              <span className="font-bold">{stats.total || 0}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Completed:</span>{" "}
              <span className="font-bold text-green-600">{stats.completed || 0}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Avg Rating:</span>{" "}
              <span className="font-bold text-primary">{stats.average_rating || 0}/5</span>
            </div>
          </div>
        )}
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-muted-foreground">Loading experiments...</div>
      ) : !experiments || experiments.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent className="space-y-3">
            <FlaskConical className="h-10 w-10 text-muted-foreground mx-auto" />
            <p className="text-muted-foreground">
              No experiments generated yet. Complete a daily reflection to receive AI-suggested experiments.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {experiments.map((exp: any) => (
            <Card key={exp.id} className="flex flex-col justify-between">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between gap-2">
                  <Badge variant="outline" className={`capitalize ${statusColors[exp.status] || ""}`}>
                    {exp.status}
                  </Badge>
                  {exp.category && (
                    <Badge variant="secondary" className="capitalize text-xs">
                      {exp.category}
                    </Badge>
                  )}
                </div>
                <CardTitle className="text-base font-semibold mt-2">{exp.description}</CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-muted-foreground space-y-2">
                <div className="flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5" />
                  <span>Created {new Date(exp.created_at).toLocaleDateString()}</span>
                </div>

                {exp.status === "completed" && (
                  <div className="pt-2 border-t space-y-1">
                    <div className="flex items-center gap-1 text-amber-500 font-semibold">
                      <span>Rating: {exp.user_rating}/5</span>
                      <Star className="h-3.5 w-3.5 fill-amber-500" />
                    </div>
                    {exp.user_feedback && <p className="italic">"{exp.user_feedback}"</p>}
                  </div>
                )}
              </CardContent>
              <CardFooter className="pt-2 border-t">
                {exp.status === "pending" && (
                  <div className="flex gap-2 w-full">
                    <Button
                      size="sm"
                      className="w-full gap-1"
                      onClick={() => handleRespond(exp.id, "accepted")}
                    >
                      <Check className="h-3.5 w-3.5" /> Accept
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="w-full gap-1"
                      onClick={() => handleRespond(exp.id, "skipped")}
                    >
                      <X className="h-3.5 w-3.5" /> Skip
                    </Button>
                  </div>
                )}
                {exp.status === "accepted" && (
                  <Button
                    size="sm"
                    className="w-full"
                    onClick={() => setReviewingExp(exp)}
                  >
                    Log Review & Results
                  </Button>
                )}
                {exp.status === "completed" && (
                  <span className="text-xs text-green-600 font-medium">Completed & logged</span>
                )}
                {exp.status === "skipped" && (
                  <span className="text-xs text-muted-foreground">Skipped</span>
                )}
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* Review Dialog */}
      <Dialog open={!!reviewingExp} onOpenChange={(open) => !open && setReviewingExp(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Review Experiment</DialogTitle>
            <DialogDescription>{reviewingExp?.description}</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleReviewSubmit} className="space-y-4 pt-2">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="tried"
                checked={tried}
                onChange={(e) => setTried(e.target.checked)}
                className="h-4 w-4 rounded"
              />
              <label htmlFor="tried" className="text-sm font-medium">
                I tried this experiment today
              </label>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">How effective was it? ({rating}/5)</label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setRating(s)}
                    className="p-1"
                  >
                    <Star
                      className={`h-6 w-6 ${
                        rating >= s ? "text-amber-500 fill-amber-500" : "text-muted-foreground"
                      }`}
                    />
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Notes & Feedback</label>
              <Textarea
                placeholder="What did you observe? Did it help your focus or mood?"
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
              />
            </div>

            <Button type="submit" className="w-full">
              Complete Review
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
