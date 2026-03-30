'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, fetchWithAuth } from '../lib/auth';
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

interface CommentItemProps {
  comment: Comment;
  childMap: Map<string, Comment[]>;
  commentById: Map<string, Comment>;
  onCommentAdded: () => void;
  onDelete: (commentId: string) => void;
  depth: number;
  maxDepth: number;
  eventId: string;
  threadId?: string;
  currentUser?: { id: string; email: string };
}

const avatarColors: Record<string, { bg: string; text: string }> = {
  blue: { bg: 'bg-blue-100', text: 'text-blue-600' },
  red: { bg: 'bg-red-100', text: 'text-red-600' },
  green: { bg: 'bg-green-100', text: 'text-green-600' },
  yellow: { bg: 'bg-yellow-100', text: 'text-yellow-600' },
  purple: { bg: 'bg-purple-100', text: 'text-purple-600' },
  pink: { bg: 'bg-pink-100', text: 'text-pink-600' },
  indigo: { bg: 'bg-indigo-100', text: 'text-indigo-600' },
  teal: { bg: 'bg-teal-100', text: 'text-teal-600' },
  gray: { bg: 'bg-gray-100', text: 'text-gray-600' },
  orange: { bg: 'bg-orange-100', text: 'text-orange-600' },
};

function timeAgo(dateString: string) {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// Collect all descendants flat (for comments beyond maxDepth)
function collectDescendantsFlat(commentId: string, childMap: Map<string, Comment[]>): Comment[] {
  const flat: Comment[] = [];
  const queue = [...(childMap.get(commentId) || [])];
  while (queue.length > 0) {
    const c = queue.shift()!;
    flat.push(c);
    const children = childMap.get(c.id) || [];
    queue.push(...children);
  }
  flat.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
  return flat;
}

export default function CommentItem({
  comment, childMap, commentById, onCommentAdded, onDelete,
  depth, maxDepth, eventId, threadId, currentUser
}: CommentItemProps) {
  const router = useRouter();
  const [likes, setLikes] = useState(comment.like_count);
  const [dislikes, setDislikes] = useState(comment.dislike_count);
  const [userVote, setUserVote] = useState<'like' | 'dislike' | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [isSubmittingReply, setIsSubmittingReply] = useState(false);
  const [replyError, setReplyError] = useState<string | null>(null);
  const [personas, setPersonas] = useState<any[]>([]);
  const [selectedPersona, setSelectedPersona] = useState('');
  const [showReplies, setShowReplies] = useState(depth < 1); // Auto-expand first level
  const replyInputRef = useRef<HTMLTextAreaElement>(null);

  const isOwner = currentUser?.id === comment.user_id;
  const directReplies = childMap.get(comment.id) || [];
  const totalDescendants = countDescendants(comment.id, childMap);
  const colors = avatarColors[comment.avatar_color] || avatarColors.gray;

  // Find who this comment is replying to (for flat display with @mention)
  const replyToName = comment.parent_id ? commentById.get(comment.parent_id)?.persona_name : null;

  useEffect(() => {
    if (showReplyForm) {
      if (personas.length === 0) {
        fetchWithAuth(`${API_BASE_URL}/api/personas`)
          .then(r => r.ok ? r.json() : Promise.reject())
          .then(data => {
            const items = data.items || [];
            setPersonas(items);
            if (items.length > 0) setSelectedPersona(items[0].id);
          })
          .catch(() => {});
      }
      setTimeout(() => replyInputRef.current?.focus(), 100);
    }
  }, [showReplyForm]);

  const handleVote = async (action: 'like' | 'dislike') => {
    const token = localStorage.getItem('access_token');
    if (!token) { router.push('/auth/login'); return; }

    const oldLikes = likes, oldDislikes = dislikes, oldVote = userVote;
    if (userVote === action) {
      if (action === 'like') setLikes(prev => Math.max(0, prev - 1));
      else setDislikes(prev => Math.max(0, prev - 1));
      setUserVote(null);
    } else {
      if (userVote === 'like') setLikes(prev => Math.max(0, prev - 1));
      if (userVote === 'dislike') setDislikes(prev => Math.max(0, prev - 1));
      if (action === 'like') setLikes(prev => prev + 1);
      else setDislikes(prev => prev + 1);
      setUserVote(action);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/comments/${comment.id}/vote?action=${action}`, {
        method: 'POST', headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setLikes(data.like_count); setDislikes(data.dislike_count); setUserVote(data.user_vote);
      } else { setLikes(oldLikes); setDislikes(oldDislikes); setUserVote(oldVote); }
    } catch { setLikes(oldLikes); setDislikes(oldDislikes); setUserVote(oldVote); }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this comment?')) return;
    setIsDeleting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/comments/${comment.id}`, {
        method: 'DELETE', headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
      });
      if (response.ok) onDelete(comment.id);
      else { setIsDeleting(false); alert('Failed to delete comment'); }
    } catch { setIsDeleting(false); alert('Failed to delete comment'); }
  };

  const handleReplyClick = () => {
    if (!isAuthenticated()) { router.push('/auth/login'); return; }
    setShowReplyForm(!showReplyForm);
    setReplyError(null);
  };

  const handleSubmitReply = async () => {
    if (!replyContent.trim()) return;
    if (!selectedPersona) { setReplyError('Please create a persona first in your profile'); return; }

    setIsSubmittingReply(true);
    setReplyError(null);

    try {
      const endpoint = threadId
        ? `${API_BASE_URL}/api/comments/thread/${threadId}`
        : `${API_BASE_URL}/api/comments`;
      const bodyData: any = {
        user_persona_id: selectedPersona,
        content: replyContent.trim(),
        parent_id: comment.id,
      };
      if (!threadId) bodyData.event_id = eventId;

      const response = await fetchWithAuth(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to post reply');
      }

      setReplyContent('');
      setShowReplyForm(false);
      setShowReplies(true);
      onCommentAdded();
    } catch (err: any) {
      setReplyError(err.message || 'Failed to post reply');
    } finally {
      setIsSubmittingReply(false);
    }
  };

  const handleReplyKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmitReply();
    }
    if (e.key === 'Escape') setShowReplyForm(false);
  };

  if (comment.is_deleted) {
    return (
      <div className="py-2">
        <p className="text-stone-400 italic text-xs">[This comment has been deleted]</p>
      </div>
    );
  }

  const isNested = depth > 0;
  const isAtMaxDepth = depth >= maxDepth;

  // At max depth, render flat list with @mentions instead of nesting further
  if (isAtMaxDepth && directReplies.length > 0) {
    const flatReplies = collectDescendantsFlat(comment.id, childMap);
    return (
      <div>
        <SingleComment
          comment={comment}
          replyToName={replyToName}
          isNested={isNested}
          likes={likes}
          dislikes={dislikes}
          userVote={userVote}
          handleVote={handleVote}
          handleReplyClick={handleReplyClick}
          handleDelete={handleDelete}
          isOwner={isOwner}
          isDeleting={isDeleting}
          showReplyForm={showReplyForm}
          replyContent={replyContent}
          setReplyContent={setReplyContent}
          replyInputRef={replyInputRef}
          handleReplyKeyDown={handleReplyKeyDown}
          handleSubmitReply={handleSubmitReply}
          isSubmittingReply={isSubmittingReply}
          replyError={replyError}
          setShowReplyForm={setShowReplyForm}
          personas={personas}
          selectedPersona={selectedPersona}
          setSelectedPersona={setSelectedPersona}
          colors={colors}
        />
        {/* Flat replies with @mention */}
        {flatReplies.map(reply => (
          <CommentItem
            key={reply.id}
            comment={reply}
            childMap={new Map()} // No more nesting
            commentById={commentById}
            onCommentAdded={onCommentAdded}
            onDelete={onDelete}
            depth={depth}
            maxDepth={maxDepth}
            eventId={eventId}
            threadId={threadId}
            currentUser={currentUser}
          />
        ))}
      </div>
    );
  }

  return (
    <div>
      <SingleComment
        comment={comment}
        replyToName={replyToName}
        isNested={isNested}
        likes={likes}
        dislikes={dislikes}
        userVote={userVote}
        handleVote={handleVote}
        handleReplyClick={handleReplyClick}
        handleDelete={handleDelete}
        isOwner={isOwner}
        isDeleting={isDeleting}
        showReplyForm={showReplyForm}
        replyContent={replyContent}
        setReplyContent={setReplyContent}
        replyInputRef={replyInputRef}
        handleReplyKeyDown={handleReplyKeyDown}
        handleSubmitReply={handleSubmitReply}
        isSubmittingReply={isSubmittingReply}
        replyError={replyError}
        setShowReplyForm={setShowReplyForm}
        personas={personas}
        selectedPersona={selectedPersona}
        setSelectedPersona={setSelectedPersona}
        colors={colors}
      />

      {/* Nested replies */}
      {directReplies.length > 0 && (
        <div className={depth === 0 ? 'ml-10' : 'ml-8'}>
          {/* Show/hide replies toggle */}
          {!showReplies ? (
            <button
              onClick={() => setShowReplies(true)}
              className="flex items-center space-x-1.5 text-xs text-blue-600 hover:text-blue-800 font-medium py-1.5 transition-colors"
            >
              <svg className="w-3 h-3 transform -rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
              <span>{totalDescendants} {totalDescendants === 1 ? 'reply' : 'replies'}</span>
            </button>
          ) : (
            <div>
              <button
                onClick={() => setShowReplies(false)}
                className="flex items-center space-x-1.5 text-xs text-stone-400 hover:text-stone-600 font-medium py-1.5 transition-colors"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
                <span>Hide replies</span>
              </button>

              <div className="border-l-2 border-stone-200 pl-3">
                {directReplies.map(reply => (
                  <CommentItem
                    key={reply.id}
                    comment={reply}
                    childMap={childMap}
                    commentById={commentById}
                    onCommentAdded={onCommentAdded}
                    onDelete={onDelete}
                    depth={depth + 1}
                    maxDepth={maxDepth}
                    eventId={eventId}
                    threadId={threadId}
                    currentUser={currentUser}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Count all descendants recursively
function countDescendants(commentId: string, childMap: Map<string, Comment[]>): number {
  const direct = childMap.get(commentId) || [];
  let count = direct.length;
  for (const child of direct) {
    count += countDescendants(child.id, childMap);
  }
  return count;
}

// The actual comment rendering (extracted to avoid duplication)
function SingleComment({
  comment, replyToName, isNested, likes, dislikes, userVote,
  handleVote, handleReplyClick, handleDelete, isOwner, isDeleting,
  showReplyForm, replyContent, setReplyContent, replyInputRef,
  handleReplyKeyDown, handleSubmitReply, isSubmittingReply, replyError,
  setShowReplyForm, personas, selectedPersona, setSelectedPersona, colors,
}: any) {
  return (
    <div className="group">
      <div className="flex items-start space-x-2.5 py-3">
        {/* Avatar */}
        <div className={`${isNested ? 'w-6 h-6 text-[10px]' : 'w-8 h-8 text-sm'} rounded-full ${colors.bg} ${colors.text} flex items-center justify-center font-bold flex-shrink-0 mt-0.5`}>
          {comment.persona_name.charAt(0).toUpperCase()}
        </div>

        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center flex-wrap gap-x-1.5 gap-y-0.5">
            <span className={`font-semibold text-stone-900 ${isNested ? 'text-xs' : 'text-sm'}`}>
              {comment.persona_name}
            </span>
            {comment.verification_level === 'verified' && comment.stakeholder_name && (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-blue-600 border border-blue-200">
                <svg className="w-2.5 h-2.5 mr-0.5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
                {comment.stakeholder_name}
              </span>
            )}
            {comment.verification_level === 'declared' && comment.stakeholder_name && (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-stone-100 text-stone-500 border border-stone-200">
                {comment.stakeholder_name}
              </span>
            )}
            {comment.is_verified && !comment.verification_level && (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-blue-600 border border-blue-200">
                Verified
              </span>
            )}
            {replyToName && (
              <span className="text-stone-400 text-xs">
                <span className="mx-0.5">&#8594;</span>
                <span className="text-stone-500 font-medium">@{replyToName}</span>
              </span>
            )}
            <span className="text-stone-400 text-xs">· {timeAgo(comment.created_at)}</span>
            {comment.is_edited && <span className="text-stone-400 text-[10px]">(edited)</span>}
          </div>

          {/* Content */}
          <p className={`text-stone-700 leading-relaxed mt-1 ${isNested ? 'text-[13px]' : 'text-[14px]'}`}>
            {comment.content}
          </p>

          {/* Actions */}
          <div className="flex items-center space-x-3 mt-1.5">
            <button
              onClick={() => handleVote('like')}
              className={`flex items-center space-x-0.5 text-xs transition-colors ${
                userVote === 'like' ? 'text-blue-600 font-semibold' : 'text-stone-400 hover:text-stone-600'
              }`}
            >
              <svg className="w-3.5 h-3.5" fill={userVote === 'like' ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
              {likes > 0 && <span>{likes}</span>}
            </button>

            <button
              onClick={() => handleVote('dislike')}
              className={`flex items-center space-x-0.5 text-xs transition-colors ${
                userVote === 'dislike' ? 'text-red-600 font-semibold' : 'text-stone-400 hover:text-stone-600'
              }`}
            >
              <svg className="w-3.5 h-3.5" fill={userVote === 'dislike' ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
              {dislikes > 0 && <span>{dislikes}</span>}
            </button>

            <button
              onClick={handleReplyClick}
              className={`flex items-center space-x-1 text-xs transition-colors ${
                showReplyForm ? 'text-blue-600 font-semibold' : 'text-stone-400 hover:text-blue-600'
              }`}
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
              </svg>
              <span>Reply</span>
            </button>

            {isOwner && (
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="text-xs text-stone-400 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100 disabled:opacity-50"
              >
                Delete
              </button>
            )}
          </div>

          {/* Inline reply form */}
          {showReplyForm && (
            <div className="mt-3">
              <div className="bg-stone-50 rounded-xl border border-stone-200 overflow-hidden">
                {personas.length > 1 && (
                  <div className="px-3 pt-2 flex items-center space-x-1.5">
                    <span className="text-[10px] text-stone-500 mr-1">as</span>
                    {personas.map((p: any) => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => setSelectedPersona(p.id)}
                        className={`px-2 py-0.5 rounded-full text-[11px] font-medium transition-colors ${
                          selectedPersona === p.id
                            ? 'bg-stone-900 text-white'
                            : 'bg-white text-stone-600 border border-stone-200 hover:bg-stone-100'
                        }`}
                      >
                        {p.persona_name}
                      </button>
                    ))}
                  </div>
                )}
                <textarea
                  ref={replyInputRef}
                  value={replyContent}
                  onChange={(e: any) => setReplyContent(e.target.value)}
                  onKeyDown={handleReplyKeyDown}
                  placeholder={`Reply to ${comment.persona_name}...`}
                  rows={2}
                  className="w-full px-3 py-2 bg-transparent text-sm resize-none focus:outline-none placeholder-stone-400"
                  maxLength={5000}
                />
                {replyError && (
                  <div className="px-3 pb-1">
                    <p className="text-xs text-red-500">{replyError}</p>
                  </div>
                )}
                <div className="flex items-center justify-between px-3 pb-2">
                  <span className="text-[10px] text-stone-400">
                    {replyContent.length > 0 && `${replyContent.length}/5000 · `}Cmd+Enter to submit
                  </span>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => { setShowReplyForm(false); setReplyContent(''); }}
                      className="px-3 py-1 text-xs text-stone-500 hover:text-stone-700 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSubmitReply}
                      disabled={isSubmittingReply || !replyContent.trim()}
                      className="px-3 py-1 bg-stone-900 text-white text-xs rounded-full font-medium hover:bg-stone-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                    >
                      {isSubmittingReply ? '...' : 'Reply'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
