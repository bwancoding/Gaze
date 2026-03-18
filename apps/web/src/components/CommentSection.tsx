'use client';

import React, { useState, useEffect } from 'react';
import CommentForm from './CommentForm';
import CommentItem from './CommentItem';
import LoginPrompt from './LoginPrompt';
import { isAuthenticated } from '../lib/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  replies?: Comment[];
}

interface CommentSectionProps {
  eventId: string;
  threadId?: string;
}

export default function CommentSection({ eventId, threadId }: CommentSectionProps) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [replyTo, setReplyTo] = useState<{ id: string; personaName: string } | null>(null);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loginRequiredForMore, setLoginRequiredForMore] = useState(false);

  // Check authentication status
  useEffect(() => {
    const checkAuth = () => {
      setIsLoggedIn(isAuthenticated());
    };
    
    checkAuth();
    
    // Check authentication status every 5 seconds
    const interval = setInterval(checkAuth, 5000);
    
    return () => clearInterval(interval);
  }, []);

  // Fetch comments list
  const fetchComments = async () => {
    try {
      const limit = isLoggedIn ? 50 : 20;
      const endpoint = threadId
        ? `${API_BASE_URL}/api/comments/thread/${threadId}?limit=${limit}`
        : `${API_BASE_URL}/api/comments/event/${eventId}?limit=${limit}`;
      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
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
    if (eventId) {
      fetchComments();
    }
  }, [eventId, isLoggedIn]);

  // Handle successful comment submission
  const handleCommentSuccess = () => {
    fetchComments();
    setReplyTo(null);
  };

  // Handle reply
  const handleReply = (commentId: string, personaName: string) => {
    setReplyTo({ id: commentId, personaName });
  };

  // Cancel reply
  const handleCancelReply = () => {
    setReplyTo(null);
  };

  // Handle deletion (real-time update)
  const handleDelete = (commentId: string) => {
    // Remove the comment from the list
    setComments(prev => prev.filter(c => c.id !== commentId));
  };

  // Get top-level comments
  const topLevelComments = comments.filter(c => !c.parent_id);

  // Get replies
  const getReplies = (parentId: string) => {
    return comments.filter(c => c.parent_id === parentId);
  };

  return (
    <div className="bg-white rounded-2xl border border-stone-200 p-6 md:p-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-stone-900 mb-2">
          Comments ({total})
        </h2>
        <p className="text-stone-600 text-sm">
          Share your perspective on this event
        </p>
      </div>

      {/* Comment form */}
      <div className="mb-8">
        <CommentForm
          eventId={eventId}
          threadId={threadId}
          onSuccess={handleCommentSuccess}
          parentId={replyTo?.id}
          onCancel={replyTo ? handleCancelReply : undefined}
        />
      </div>

      {/* Comments list */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse flex space-x-4">
              <div className="w-10 h-10 bg-stone-200 rounded-full"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-stone-200 rounded w-1/4"></div>
                <div className="h-4 bg-stone-200 rounded w-3/4"></div>
              </div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">😕</div>
          <p className="text-stone-600">{error}</p>
        </div>
      ) : topLevelComments.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">💬</div>
          <p className="text-stone-600 mb-2">No comments yet</p>
          <p className="text-sm text-stone-500">Be the first to share your perspective!</p>
        </div>
      ) : (
        <div>
          <div className="space-y-6">
            {topLevelComments.map(comment => (
              <div key={comment.id}>
                <CommentItem
                  comment={comment}
                  onReply={handleReply}
                  onDelete={handleDelete}
                  depth={0}
                />
                {/* Nested replies */}
                {getReplies(comment.id).length > 0 && (
                  <div className="ml-12 mt-4 space-y-4 border-l-2 border-stone-100 pl-6">
                    {getReplies(comment.id).map(reply => (
                      <CommentItem
                        key={reply.id}
                        comment={reply}
                        onReply={handleReply}
                        onDelete={handleDelete}
                        depth={1}
                      />
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Not logged in + more comments available -> show login prompt */}
          {!isLoggedIn && loginRequiredForMore && (
            <LoginPrompt
              total={total}
              shown={comments.length}
            />
          )}

          {/* Logged in + more available -> show load more */}
          {isLoggedIn && hasMore && (
            <div className="mt-6 text-center">
              <button
                onClick={() => fetchComments()}
                className="px-6 py-3 bg-stone-100 text-stone-700 rounded-full font-medium hover:bg-stone-200 transition-colors"
              >
                Load More ({total - comments.length} remaining)
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
