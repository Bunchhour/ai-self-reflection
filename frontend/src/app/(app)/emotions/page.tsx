"use client";
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Smile, Activity, Calendar, Compass } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function EmotionsPage() {
  const [range, setRange] = useState("7d");

  const { data: logs, isLoading: logsLoading } = useQuery({
    queryKey: ["emotionTrends", range],
    queryFn: () => api.emotions.trends(range),
  });

  const { data: triggers } = useQuery({
    queryKey: ["emotionTriggers"],
    queryFn: api.emotions.triggers,
  });

  // Prepare chart data grouping intensity by date
  const chartData = React.useMemo(() => {
    if (!logs || !Array.isArray(logs)) return [];
    const grouped: Record<string, { date: string; intensity: number; count: number }> = {};
    logs.forEach((item: any) => {
      const d = item.date;
      if (!grouped[d]) {
        grouped[d] = { date: d, intensity: item.intensity, count: 1 };
      } else {
        grouped[d].intensity += item.intensity;
        grouped[d].count += 1;
      }
    });
    return Object.values(grouped).map((g) => ({
      date: g.date,
      avgIntensity: Math.round((g.intensity / g.count) * 10) / 10,
    }));
  }, [logs]);

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Emotional Landscape</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Track mood variations, intensity shifts, and correlated triggers over time.
          </p>
        </div>
        <div className="flex gap-2">
          {["7d", "30d", "90d"].map((r) => (
            <Button
              key={r}
              size="sm"
              variant={range === r ? "default" : "outline"}
              onClick={() => setRange(r)}
            >
              {r.toUpperCase()}
            </Button>
          ))}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Trend Chart */}
        <Card className="md:col-span-2">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Emotion Intensity Trend</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="h-64 pt-4">
            {chartData.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                No emotional log data for this range yet. Complete daily reflections to view trends.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 5]} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="avgIntensity"
                    name="Avg Intensity"
                    stroke="hsl(var(--primary))"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Breakdown Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Smile className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Recent Emotions</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            {logsLoading ? (
              <div className="text-sm text-muted-foreground">Loading emotions...</div>
            ) : !logs || logs.length === 0 ? (
              <div className="text-sm text-muted-foreground">No emotions logged in this period.</div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {logs.slice(0, 15).map((log: any, idx: number) => (
                  <Badge key={idx} variant="secondary" className="gap-1.5 py-1">
                    <span>{log.emotion}</span>
                    <span className="text-xs text-muted-foreground font-mono">({log.intensity}/3)</span>
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Triggers Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Compass className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">AI-Correlated Emotional Triggers</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            As you log reflections, the memory service correlates repeated scenarios with emotional shifts to surface trigger correlations automatically.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
