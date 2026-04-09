# Stakeholder Certification & Structured Discussion Flow

## Design Principles
- **Self-declaration first**: Lower the barrier. Users declare "I am [Stakeholder]" and can immediately comment with a "Self-declared" badge. They can later upgrade to "Verified" by submitting proof.
- **AI as framework, real voices supplement**: AI-generated perspectives serve as the structural backbone. Real human voices from declared/verified stakeholders are embedded under the corresponding AI perspective.
- **Combined display**: A dedicated "Stakeholder Voices" panel with featured voices, plus badges in regular comments.

---

## Phase 1: Backend — Quick Self-Declaration API (Minimal)

### 1.1 Add self-declaration endpoint
**File**: `apps/api/app/routes/personas.py`

Add a new simplified endpoint `POST /api/personas/quick-declare` that:
- Takes `event_id`, `stakeholder_id`, and optional `persona_id`
- If no `persona_id`, auto-creates a persona or uses the user's default
- Creates an `EventStakeholderVerification` with `proof_type='self_declaration'` and `status='declared'` (new status — instant, no admin review needed)
- Returns immediately with the verification info

### 1.2 Add "declared" status
**File**: `apps/api/app/models/personas.py`

The existing `status` field supports: `pending`, `approved`, `rejected`. Add `declared` as a valid status:
- `declared` = self-declared, no proof submitted, shown with "Self-declared" badge
- `approved` = admin-verified or proof-verified, shown with "Verified" badge

### 1.3 Add endpoint to fetch stakeholder comments
**File**: `apps/api/app/routes/comments.py`

Add `GET /api/comments/event/{event_id}/by-stakeholder` that:
- Fetches comments from users who have `declared` or `approved` verification for this event
- Groups them by `stakeholder_id`
- Returns `{ stakeholder_id: string, stakeholder_name: string, comments: Comment[], verification_level: 'declared' | 'verified' }[]`

### 1.4 Enhance comment response with stakeholder info
**File**: `apps/api/app/routes/comments.py`

Modify `check_verified_status()` to also return the stakeholder name and verification level (`declared` or `verified`), not just a boolean. Update comment serialization to include:
- `stakeholder_name`: e.g. "Iranian Civilians"
- `verification_level`: `null` | `'declared'` | `'verified'`

---

## Phase 2: Frontend — Perspectives Tab Redesign

### 2.1 Redesign Perspectives Tab as "Stakeholder Voices"
**File**: `apps/web/src/app/events/[id]/page.tsx`

Restructure the Perspectives tab:

```
[Stakeholder Voices]

For each AI-generated stakeholder perspective:
┌──────────────────────────────────────────┐
│ 🔵 Iranian Civilians                     │
│ ┌─ AI Analysis ─────────────────────────┐│
│ │ [AI perspective text from analysis]    ││
│ │ • Key argument 1                       ││
│ │ • Key argument 2                       ││
│ │ 🤖 AI-generated from source articles  ││
│ └────────────────────────────────────────┘│
│                                           │
│ 💬 Real Voices (2)                       │
│ ┌─ Comment from verified user ──────────┐│
│ │ 👤 Ali R. [✓ Verified]  · 2h ago      ││
│ │ "As someone living in Tehran..."       ││
│ └────────────────────────────────────────┘│
│ ┌─ Comment from declared user ──────────┐│
│ │ 👤 Sarah M. [Self-declared]  · 5h ago ││
│ │ "My family in Iran says..."            ││
│ └────────────────────────────────────────┘│
│                                           │
│ [🙋 I am an Iranian Civilian — Speak Up] │
└──────────────────────────────────────────┘
```

### 2.2 "I Am [Stakeholder]" Button + Inline Declaration Modal
**File**: New component `apps/web/src/components/StakeholderDeclare.tsx`

When user clicks "I am [Stakeholder Name]":
1. If not logged in → redirect to login with return URL
2. If logged in → show inline modal:
   - Select existing persona or auto-create
   - Optional: "Why are you this stakeholder?" (1 sentence, optional)
   - Submit → calls `POST /api/personas/quick-declare`
   - Immediately shows comment form below that stakeholder section
3. After declaration, the "I am..." button changes to "Write as [Stakeholder Name]" and expands comment form

### 2.3 Stakeholder Badge on Comments
**File**: `apps/web/src/components/CommentItem.tsx`

Enhance the existing verified badge to show two levels:
- `verification_level === 'verified'`: Blue badge "✓ Verified [Stakeholder Name]"
- `verification_level === 'declared'`: Gray badge "Self-declared [Stakeholder Name]"
- No verification: No badge (regular commenter)

---

## Phase 3: Frontend — Comment Section Enhancement

### 3.1 Update CommentSection with stakeholder filter
**File**: `apps/web/src/components/CommentSection.tsx`

Add optional filter tabs at the top of Discussion:
- "All" | "Stakeholder Voices Only" | by specific stakeholder name
- When filtering, only show comments from declared/verified users of that stakeholder type

### 3.2 Update CommentForm to show declaration status
**File**: `apps/web/src/components/CommentForm.tsx`

If the user has a declaration for this event, show their stakeholder badge above the comment form:
- "Commenting as [Persona Name] · [✓ Verified Iranian Civilian]"

---

## Implementation Order

1. **Phase 1.1-1.2**: Backend quick-declare + declared status (~30 min)
2. **Phase 1.3-1.4**: Backend stakeholder comments API (~20 min)
3. **Phase 2.1**: Frontend perspectives tab redesign (~45 min)
4. **Phase 2.2**: Frontend declare modal component (~30 min)
5. **Phase 2.3**: Frontend comment badge enhancement (~15 min)
6. **Phase 3.1-3.2**: Comment section filter + form update (~20 min)

Total: ~6 files modified, ~2 new components

## What We're NOT Doing (Keep Simple)
- No AI auto-review of self-declarations (can add later)
- No proof upload in the quick flow (existing verify page handles this)
- No real-time updates (standard page refresh)
- No separate "Stakeholder Voices" page (everything on event detail)
