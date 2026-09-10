"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/components/providers/AuthProvider";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { Flame, Shield, TrendingUp, Sparkles, CheckCircle2, ArrowRight } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["stats"],
    queryFn: api.stats.get,
  });

  const { data: today, isLoading: todayLoading } = useQuery({
    queryKey: ["today"],
    queryFn: async () => {
      try {
        return await api.reflections.today();
      } catch {
        return null;
      }
    },
  });

  const { data: pendingExp, isLoading: expLoading } = useQuery({
    queryKey: ["pendingExp"],
    queryFn: async () => {
      try {
        return await api.experiments.pending();
      } catch {
        return null;
      }
    },
  });

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Welcome back, {user?.name?.split(" ")[0] || "there"} 👋
        </h1>
        <p className="text-muted-foreground mt-1">
          Here is your reflection pulse and self-awareness overview.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Current Streak
            </CardTitle>
            <Flame className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {statsLoading ? "..." : `${stats?.current_streak || 0} days`}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Longest: {stats?.longest_streak || 0} days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Growth Score
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary">
              {statsLoading ? "..." : `${stats?.growth_score || 0}/100`}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Total reflections: {stats?.total_reflections || 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Streak Shields
            </CardTitle>
            <Shield className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {statsLoading ? "..." : `${stats?.streak_shields || 0}`}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Auto-protects streak if you miss a day
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Today's Reflection Card */}
      <Card className="border-primary/20 bg-gradient-to-r from-card to-primary/5">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <CardTitle className="text-xl">Today's Daily Reflection</CardTitle>
              <p className="text-sm text-muted-foreground">
                {today
                  ? "You've recorded your reflection for today."
                  : "Pause for a moment and check in with yourself."}
              </p>
            </div>
            {today && (
              <Badge variant="outline" className="gap-1 bg-green-500/10 text-green-600 border-green-200">
                <CheckCircle2 className="h-3.5 w-3.5" /> Completed
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {!today ? (
            <Link href="/reflect">
              <Button className="gap-2">
                Start Today's Reflection <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          ) : today.needs_followup ? (
            <Link href="/reflect/followup">
              <Button variant="secondary" className="gap-2">
                Continue Follow-up Questions <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          ) : (
            <Link href="/reflect/result">
              <Button variant="outline" className="gap-2">
                <Sparkles className="h-4 w-4 text-primary" /> View Today's Insights
              </Button>
            </Link>
          )}
        </CardContent>
      </Card>

      {/* Pending Experiment Alert */}
      {pendingExp && (
        <Card className="border-l-4 border-l-accent bg-accent/5">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Active Experiment Check-in</CardTitle>
              <Badge variant="secondary">{pendingExp.category || "growth"}</Badge>
            </div>
            <p className="text-muted-foreground text-sm mt-1">{pendingExp.description}</p>
          </CardHeader>
          <CardContent>
            <Link href="/experiments">
              <Button size="sm" variant="default">
                Review & Log Result
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
