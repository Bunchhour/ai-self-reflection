import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Zap, MessageSquare, Compass, Clock } from "lucide-react";

export default function ReflectPage() {
  const modes = [
    {
      title: "Quick Pulse",
      time: "1–2 min",
      icon: Zap,
      badgeColor: "bg-amber-500/10 text-amber-600 border-amber-200",
      desc: "Fast emotional calibration, mood check, one thought, and your win of the day.",
      href: "/reflect/quick",
    },
    {
      title: "Guided Reflection",
      time: "5–7 min",
      icon: MessageSquare,
      badgeColor: "bg-blue-500/10 text-blue-600 border-blue-200",
      desc: "Structured conversational prompts with adaptive AI follow-up questions.",
      href: "/reflect/guided",
    },
    {
      title: "Deep Dive",
      time: "15+ min",
      icon: Compass,
      badgeColor: "bg-purple-500/10 text-purple-600 border-purple-200",
      desc: "Comprehensive 12-category reflection with auto-saving and full pattern extraction.",
      href: "/reflect/deep",
    },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Choose Your Reflection Mode</h1>
        <p className="text-muted-foreground">
          Select the depth that matches your current time and mental bandwidth.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {modes.map((mode) => {
          const Icon = mode.icon;
          return (
            <Card key={mode.title} className="flex flex-col justify-between hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between mb-2">
                  <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium ${mode.badgeColor}`}>
                    <Clock className="h-3 w-3" /> {mode.time}
                  </span>
                </div>
                <CardTitle className="text-xl">{mode.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{mode.desc}</p>
              </CardContent>
              <CardFooter>
                <Link href={mode.href} className="w-full">
                  <Button className="w-full">Start Reflection</Button>
                </Link>
              </CardFooter>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
