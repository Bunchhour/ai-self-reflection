"use client";
import React, { useState } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import { api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Download, Trash2, Shield, User as UserIcon } from "lucide-react";

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const [exporting, setExporting] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleExport = async () => {
    setExporting(true);
    try {
      const data = await api.user.export();
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `reflectai-export-${new Date().toISOString().split("T")[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Export failed", e);
    } finally {
      setExporting(false);
    }
  };

  const handleDeleteAccount = async () => {
    setDeleting(true);
    try {
      await api.user.deleteAccount();
      logout();
    } catch (e) {
      console.error("Delete failed", e);
      setDeleting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings & Privacy</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Manage your account profile, export your personal records, and privacy preferences.
        </p>
      </div>

      <div className="grid gap-6">
        {/* Profile Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <UserIcon className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Account Profile</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Full Name</div>
                <div className="text-base font-medium mt-1">{user?.name}</div>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Email</div>
                <div className="text-base font-medium mt-1">{user?.email}</div>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">User ID</div>
                <div className="text-xs font-mono text-muted-foreground mt-1 truncate">{user?.id}</div>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Account Created</div>
                <div className="text-base font-medium mt-1">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "Recent"}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Data Ownership / Export */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Download className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Data Ownership & Portability</CardTitle>
            </div>
            <p className="text-sm text-muted-foreground">
              You own all your personal data. Export your entire history including reflections, emotions, and goals at any time in JSON format.
            </p>
          </CardHeader>
          <CardContent>
            <Button variant="outline" onClick={handleExport} disabled={exporting} className="gap-2">
              <Download className="h-4 w-4" /> {exporting ? "Exporting..." : "Export All Data (JSON)"}
            </Button>
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card className="border-destructive/30">
          <CardHeader>
            <div className="flex items-center gap-2 text-destructive">
              <Shield className="h-5 w-5" />
              <CardTitle className="text-lg">Danger Zone</CardTitle>
            </div>
            <p className="text-sm text-muted-foreground">
              Permanently remove your account and all associated reflections, vector embeddings, and metrics. This action is irreversible.
            </p>
          </CardHeader>
          <CardContent>
            <Button variant="destructive" onClick={() => setDeleteOpen(true)} className="gap-2">
              <Trash2 className="h-4 w-4" /> Delete Account & Wipe Data
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Confirmation Dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Account Deletion</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete your account? All your reflections, micro-experiments, emotion logs, and stats will be permanently wiped with cascade deletion.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteAccount} disabled={deleting}>
              {deleting ? "Deleting..." : "Permanently Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
