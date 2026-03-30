'use client';

import React, { useState, useEffect } from 'react';
import CommentForm from './CommentForm';
import CommentItem from './CommentItem';
import LoginPrompt from './LoginPrompt';
import { isAuthenticated } from '../lib/auth';
import { API_BASE_URL } from '../lib/config';


interface Comment {
  id: string;
  user_id: string;
  user_persona_id: string;
  persona_name: string;
  avatar_color: string;
  event_id: string;
  parent_id: string | null;
  content: string;
  is_deleted: boolean;
  is_edited: boolean;
  like_count: number;
  dislike_count: number;
  reply_count: number;
  created_at: string;
  updated_at: string;
  is_verified?: boolean;
  stakeholder_name?: string | null;
  verification_level?: 'verified' | 'declared' | null;
}

interface CommentSectionProps {
  eventId: string;
  threadId?: string;
}

const COMMENTS_PER_PAGE = 10;

// Build a nested tree from flat comment list
function buildCommentTree(comments: Comment[]): { topLevel: Comment[]; childMap: Map<string, Comment[]> } {
  const childMap = new Map<string, Comment[]>();
  const topLevel: Comment[] = [];

  // Index all comments by id for parent lookups
  const commentById = new Map<string, Comment>();
  comments.forEach(c => commentById.set(c.id, c));

  comments.forEach(c => {
    if (!c.parent_id) {
      topLevel.push(c);
    } else {
      const existing = childMap.get(c.parent_id) || [];
      existing.push(c);
      childMap.set(c.parent_id, existing);
    }
  });

  // Sort top-level by newest first, replies by oldest first (conversation order)
  topLevel.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  childMap.forEach(replies => {
    replies.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
  });

  return { topLevel, childMap };
}

// Flatten deep replies: collect all descendants beyond maxDepth into flat list
function getNestedReplies(commentId: string, childMap: Map<string, Comment[]>, depth: number, maxDepth: number): Comment[] {
  const direct = childMap.get(commentId) || [];
  if (depth >= maxDepth) {
    // Flatten all descendants
    const flat: Comment[] = [];
    const queue = [...direct];
    while (queue.length > 0) {
      const c = queue.shift()!;
      flat.push(c);
      const children = childMap.get(c.id) || [];
      queue.push(...children);
    }
    return flat;
  }
  return direct;
}

export default function CommentSection({ eventId, threadId }: CommentSectionProps) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loginRequiredForMore, setLoginRequiredForMore] = useState(false);
  const [displayCount, setDisplayCount] = useState(COMMENTS_PER_PAGE);

  useEffect(() => {
    const checkAuth = () => setIsLoggedIn(isAuthenticated());
    checkAuth();
    const interval = setInterval(checkAuth, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchComments = async () => {
    try {
      const limit = isLoggedIn ? 100 : 20;
      const endpoint = threadId
        ? `${API_BASE_URL}/api/comments/thread/${threadId}?limit=${limit}`
        : `${API_BASE_URL}/api/comments/event/${eventId}?limit=${limit}`;
      const response = await fetch(endpoint);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setComments(data.items || []);
      setTotal(data.total || 0);
      setHasMore(data.has_more || false);
      setLoginRequiredForMore(data.login_required_for_more || false);
    } catch (err) {
      console.error('Failed to fetch comments:', err);
      setError('Failed to load comments');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (eventId) fetchComments();
  }, [eventId, isLoggedIn]);

  const handleCommentSuccess = () => {
    fetchComments();
  };

  const handleDelete = (commentId: string) => {
    setComments(prev => prev.filter(c => c.id !== commentId));
  };

  // Build comment tree
  const { topLevel, childMap } = buildCommentTree(comments);
  const commentById = new Map<string, Comment>();
  comments.forEach(c => commentById.set(c.id, c));

  const visibleTopLevel = topLevel.slice(0, displayCount);
  const hasMoreToShow = topLevel.length > displayCount;

  return (
    <div className="bg-white rounded-2xl border border-stone-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-stone-100 bg-stone-50/50">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-stone-900">
            Discussion <span className="text-stone-400 font-normal text-sm">({total})</span>
          </h2>
        </div>
      </div>

      <div className="px-6 py-4">
        {/* Top-level comment form */}
        <CommentForm
          eventId={eventId}
          threadId={threadId}
          onSuccess={handleCommentSuccess}
        />

        {/* Divider */}
        {topLevel.length > 0 && <div className="border-t border-stone-100 mt-4 mb-2"></div>}

        {/* Comments */}
        {isLoading ? (
          <div className="space-y-4 py-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="animate-pulse flex space-x-3">
                <div className="w-8 h-8 bg-stone-200 rounded-full flex-shrink-0"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-3 bg-stone-200 rounded w-1/4"></div>
                  <div className="h-3 bg-stone-200 rounded w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-stone-600 text-sm">{error}</p>
            <button onClick={fetchComments} className="mt-2 text-sm text-blue-600 hover:underline">Try again</button>
          </div>
        ) : topLevel.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-stone-500 text-sm">No comments yet. Be the first to share your perspective!</p>
          </div>
        ) : (
          <div>
            <div className="divide-y divide-stone-50">
              {visibleTopLevel.map(comment => (
                <CommentItem
                  key={comment.id}
                  comment={comment}
                  childMap={childMap}
                  commentById={commentById}
                  onCommentAdded={handleCommentSuccess}
                  onDelete={handleDelete}
                  depth={0}
                  maxDepth={2}
                  eventId={eventId}
                  threadId={threadId}
                />
              ))}
            </div>

            {/* Load more comments */}
            {hasMoreToShow && (
              <div className="mt-4 text-center">
                <button
                  onClick={() => setDisplayCount(prev => prev + COMMENTS_PER_PAGE)}
                  className="px-5 py-2 bg-stone-100 text-stone-600 rounded-full text-sm font-medium hover:bg-stone-200 transition-colors"
                >
                  Show more ({topLevel.length - displayCount} remaining)
                </button>
              </div>
            )}

            {!isLoggedIn && loginRequiredForMore && (
              <LoginPrompt total={total} shown={comments.length} />
            )}

            {isLoggedIn && hasMore && (
              <div className="mt-4 text-center">
                <button
                  onClick={fetchComments}
                  className="px-5 py-2 bg-stone-100 text-stone-600 rounded-full text-sm font-medium hover:bg-stone-200 transition-colors"
                >
                  Load more from server ({total - comments.length} remaining)
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
