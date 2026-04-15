'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { API_BASE_URL } from './config';

/**
 * Track a long-running admin background task.
 *
 * The admin pipeline / seed-interactions endpoints return immediately
 * (fire-and-forget asyncio.create_task), so the frontend never sees
 * when the work is actually done. The backend task_tracker writes
 * status to an in-memory dict exposed at GET /api/admin/tasks/status;
 * this hook polls that endpoint after a trigger and surfaces elapsed
 * time + completion.
 *
 * Usage:
 *   const task = useAdminTask('pipeline');
 *   async function run() {
 *     task.begin();                          // start local timer + polling
 *     const res = await fetch('.../refresh', { method: 'POST' });
 *     if (!res.ok) task.abort();             // rollback local state on HTTP failure
 *   }
 *   // In JSX: {task.running ? `Running ${task.elapsedLabel}` : ...}
 *   // task.justFinished is true for ~6s after completion
 */

type TaskStatus = {
  status: 'running' | 'done' | 'error';
  started_at: string;
  finished_at: string | null;
  duration_seconds: number | null;
  result: Record<string, unknown> | null;
  error: string | null;
};

type AllTasks = Record<string, TaskStatus>;

export type UseAdminTask = {
  running: boolean;
  justFinished: boolean;
  elapsedSeconds: number;
  elapsedLabel: string;     // "0:42"
  lastDurationLabel: string | null;  // "1:23" — only set after a successful run
  error: string | null;
  result: Record<string, unknown> | null;
  begin: () => void;
  abort: () => void;
  dismiss: () => void;      // hide the "just finished" badge
};

function formatSeconds(secs: number): string {
  const s = Math.max(0, Math.round(secs));
  const m = Math.floor(s / 60);
  const rem = s % 60;
  return `${m}:${rem.toString().padStart(2, '0')}`;
}

export function useAdminTask(taskName: string): UseAdminTask {
  // localRunning is set by begin() so the UI shows "Running 0:00" even
  // before the first poll returns. It flips to false when the poll sees
  // the task completed, or abort() is called.
  const [localRunning, setLocalRunning] = useState(false);
  const [remoteStatus, setRemoteStatus] = useState<TaskStatus | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [justFinished, setJustFinished] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [lastDurationLabel, setLastDurationLabel] = useState<string | null>(null);

  const beganAtRef = useRef<number | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const justFinishedTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const getAuth = (): HeadersInit => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (typeof window !== 'undefined') {
      const storedAuth = localStorage.getItem('admin_auth');
      if (storedAuth) {
        try {
          const { username, password } = JSON.parse(storedAuth);
          headers['Authorization'] = 'Basic ' + btoa(`${username}:${password}`);
        } catch {
          // ignore
        }
      }
    }
    return headers;
  };

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    if (tickRef.current) {
      clearInterval(tickRef.current);
      tickRef.current = null;
    }
  }, []);

  const running = localRunning || remoteStatus?.status === 'running';

  // Local elapsed timer — ticks every second while running
  useEffect(() => {
    if (!running) return;
    if (tickRef.current) return;
    tickRef.current = setInterval(() => {
      const start = beganAtRef.current ?? Date.now();
      setElapsedSeconds((Date.now() - start) / 1000);
    }, 1000);
    return () => {
      if (tickRef.current) {
        clearInterval(tickRef.current);
        tickRef.current = null;
      }
    };
  }, [running]);

  // Poll status endpoint while running
  useEffect(() => {
    if (!running) return;
    if (pollRef.current) return;

    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/admin/tasks/status`, {
          headers: getAuth(),
        });
        if (!res.ok) return;
        const data: AllTasks = await res.json();
        const t = data[taskName];
        if (!t) return;
        setRemoteStatus(t);

        // Prefer the backend-reported started_at for elapsed if it's older
        // than our local begin (e.g. someone else triggered the task from
        // another tab and we started polling mid-run).
        if (t.started_at) {
          const remoteStart = new Date(t.started_at).getTime();
          if (!beganAtRef.current || remoteStart < beganAtRef.current) {
            beganAtRef.current = remoteStart;
          }
        }

        if (t.status === 'done') {
          setLocalRunning(false);
          setResult(t.result);
          setError(null);
          setLastDurationLabel(
            t.duration_seconds != null ? formatSeconds(t.duration_seconds) : null
          );
          setJustFinished(true);
          if (justFinishedTimerRef.current) clearTimeout(justFinishedTimerRef.current);
          justFinishedTimerRef.current = setTimeout(() => setJustFinished(false), 8000);
          stopPolling();
        } else if (t.status === 'error') {
          setLocalRunning(false);
          setError(t.error || 'Task failed');
          setResult(null);
          setLastDurationLabel(
            t.duration_seconds != null ? formatSeconds(t.duration_seconds) : null
          );
          setJustFinished(true);
          if (justFinishedTimerRef.current) clearTimeout(justFinishedTimerRef.current);
          justFinishedTimerRef.current = setTimeout(() => setJustFinished(false), 12000);
          stopPolling();
        }
      } catch {
        // network blip — just wait for the next poll
      }
    };

    poll();
    pollRef.current = setInterval(poll, 2500);
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [running, taskName, stopPolling]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling();
      if (justFinishedTimerRef.current) clearTimeout(justFinishedTimerRef.current);
    };
  }, [stopPolling]);

  const begin = useCallback(() => {
    beganAtRef.current = Date.now();
    setElapsedSeconds(0);
    setLocalRunning(true);
    setJustFinished(false);
    setError(null);
    setResult(null);
    setLastDurationLabel(null);
    setRemoteStatus(null);
  }, []);

  const abort = useCallback(() => {
    setLocalRunning(false);
    setJustFinished(false);
    stopPolling();
  }, [stopPolling]);

  const dismiss = useCallback(() => {
    setJustFinished(false);
    if (justFinishedTimerRef.current) clearTimeout(justFinishedTimerRef.current);
  }, []);

  return {
    running,
    justFinished,
    elapsedSeconds,
    elapsedLabel: formatSeconds(elapsedSeconds),
    lastDurationLabel,
    error,
    result,
    begin,
    abort,
    dismiss,
  };
}
