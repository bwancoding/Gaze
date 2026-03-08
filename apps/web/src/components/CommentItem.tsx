'use client';

import React, { useState } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

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
}

interface CommentItemProps {
  comment: Comment;
  onReply: (commentId: string, personaName: string) => void;
  onDelete: (commentId: string) => void;
  depth: number;
  currentUser?: {
    id: string;
    email: string;
  };
}

// 头像颜色映射
const avatarColors: Record<string, string> = {
  blue: 'bg-blue-500',
  red: 'bg-red-500',
  green: 'bg-green-500',
  yellow: 'bg-yellow-500',
  purple: 'bg-purple-500',
  pink: 'bg-pink-500',
  indigo: 'bg-indigo-500',
  teal: 'bg-teal-500',
  gray: 'bg-gray-500',
};

export default function CommentItem({ comment, onReply, depth, currentUser }: CommentItemProps) {
  const [likes, setLikes] = useState(comment.like_count);
  const [dislikes, setDislikes] = useState(comment.dislike_count);
  const [hasLiked, setHasLiked] = useState(false);
  const [hasDisliked, setHasDisliked] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const isOwner = currentUser?.id === comment.user_id;

  const handleLike = async () => {
    if (hasLiked) return;

    // Optimistic update
    setLikes(prev => prev + 1);
    setHasLiked(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/comments/${comment.id}/like?action=like`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        // Rollback on failure
        setLikes(prev => prev - 1);
        setHasLiked(false);
      }
    } catch (err) {
      console.error('Failed to like comment:', err);
      // Rollback on error
      setLikes(prev => prev - 1);
      setHasLiked(false);
    }
  };

  const handleDislike = async () => {
    if (hasDisliked) return;

    // Optimistic update
    setDislikes(prev => prev + 1);
    setHasDisliked(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/comments/${comment.id}/like?action=dislike`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        // Rollback on failure
        setDislikes(prev => prev - 1);
        setHasDisliked(false);
      }
    } catch (err) {
      console.error('Failed to dislike comment:', err);
      // Rollback on error
      setDislikes(prev => prev - 1);
      setHasDisliked(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this comment?')) return;

    setIsDeleting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/comments/${comment.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        // 通知父组件更新状态
        onDelete(comment.id);
      } else {
        setIsDeleting(false);
        alert('Failed to delete comment');
      }
    } catch (err) {
      console.error('Failed to delete comment:', err);
      setIsDeleting(false);
      alert('Failed to delete comment');
    }
  };

  const timeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  if (comment.is_deleted) {
    return (
      <div className="py-4 px-4 bg-stone-50 rounded-lg border border-stone-200 opacity-50">
        <p className="text-stone-500 italic text-sm">[Deleted]</p>
      </div>
    );
  }

  return (
    <div className={`py-4 ${depth > 0 ? 'border-l-2 border-stone-100 pl-4' : ''}`}>
      <div className="flex items-start space-x-3">
        {/* 头像 */}
        <div className={`w-10 h-10 rounded-full ${avatarColors[comment.avatar_color] || 'bg-gray-500'} flex items-center justify-center text-white font-bold text-sm flex-shrink-0`}>
          {comment.persona_name.charAt(0).toUpperCase()}
        </div>

        {/* 评论内容 */}
        <div className="flex-1 min-w-0">
          {/* 评论头信息 */}
          <div className="flex items-center space-x-2 mb-2">
            <span className="font-semibold text-stone-900">
              {comment.persona_name}
            </span>
            {comment.is_verified && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                ✓ Verified
              </span>
            )}
            <span className="text-stone-500 text-sm">·</span>
            <span className="text-stone-500 text-sm">
              {timeAgo(comment.created_at)}
            </span>
            {comment.is_edited && (
              <span className="text-stone-400 text-xs">(edited)</span>
            )}
          </div>

          {/* 评论正文 */}
          <p className="text-stone-800 leading-relaxed mb-3">
            {comment.content}
          </p>

          {/* 操作按钮 */}
          <div className="flex items-center space-x-4">
            <button
              onClick={handleLike}
              disabled={hasLiked}
              className={`flex items-center space-x-1 text-sm transition-colors ${
                hasLiked ? 'text-blue-600' : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              <svg className="w-4 h-4" fill={hasLiked ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
              </svg>
              <span>{likes}</span>
            </button>

            <button
              onClick={handleDislike}
              disabled={hasDisliked}
              className={`flex items-center space-x-1 text-sm transition-colors ${
                hasDisliked ? 'text-red-600' : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              <svg className="w-4 h-4" fill={hasDisliked ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.095c.5 0 .905-.405.905-.905 0-.714.211-1.412.608-2.006L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
              </svg>
              <span>{dislikes}</span>
            </button>

            <button
              onClick={() => onReply(comment.id, comment.persona_name)}
              className="flex items-center space-x-1 text-sm text-stone-500 hover:text-stone-700 transition-colors"
            >
              <span>Reply</span>
            </button>

            {isOwner && (
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="flex items-center space-x-1 text-sm text-red-500 hover:text-red-700 transition-colors disabled:opacity-50"
              >
                <span>Delete</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
