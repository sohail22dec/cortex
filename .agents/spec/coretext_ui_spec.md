# Coretext UI Specification

**Product:** Coretext\
**Type:** Corrective RAG / Agentic RAG application\
**Document:** UI/UX Design Specification\
**Theme:** Dark mode\
**Primary platform:** Desktop web application

------------------------------------------------------------------------

## 1. Product Overview

Coretext is a conversational RAG application that allows users to upload
documents and ask questions about their knowledge base.

The interface should feel familiar to users of modern AI assistants such
as ChatGPT and Gemini, while providing dedicated functionality for
document management and RAG transparency.

### Core principles

-   Simple and familiar chat experience
-   Dark-first visual design
-   Documents should be accessible without permanently occupying the
    main workspace
-   Fast access to conversations
-   Clear document upload and management
-   Minimal visual clutter
-   RAG activity should be visible but not overwhelming
-   Responsive and accessible UI

------------------------------------------------------------------------

# 2. Main Application Layout

The application uses three primary UI areas:

1.  **Left sidebar** --- navigation and conversations
2.  **Main chat area** --- conversation and message composer
3.  **Documents drawer** --- hidden by default and opened on demand

### Default state

The Documents drawer is **closed by default**.

``` text
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  LEFT SIDEBAR       MAIN CHAT WORKSPACE                              │
│                                                                      │
│  Coretext           Chat header                                     │
│  New Chat            ──────────────────────────────────────────────  │
│                      Conversation                                    │
│  Conversations       Conversation                                    │
│  • Chat 1            Conversation                                    │
│  • Chat 2                                                            │
│  • Chat 3            ──────────────────────────────────────────────  │
│                      Message composer                                │
│                                                                      │
│  Profile                                                             │
└──────────────────────────────────────────────────────────────────────┘
```

When the user clicks the **Documents** button, a drawer slides in from
the right.

``` text
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  LEFT SIDEBAR       MAIN CHAT              DOCUMENTS DRAWER          │
│                                                                      │
│                      Chat                  ┌───────────────────────┐  │
│                      Content               │ Documents        X    │  │
│                                            │                       │  │
│                                            │ Search                │  │
│                                            │                       │  │
│                                            │ File 1                │  │
│                                            │ File 2                │  │
│                                            │ File 3                │  │
│                                            │                       │  │
│                                            │ Upload document       │  │
│                                            └───────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 3. Visual Design

## 3.1 Theme

Coretext should use a premium dark SaaS aesthetic.

### Background

-   Primary background: near-black / deep navy
-   Secondary surfaces: slightly lighter charcoal
-   Cards: dark elevated surfaces
-   Borders: subtle low-contrast borders

### Accent

Use a purple/violet accent as the primary brand color.

The accent should be used for:

-   Primary buttons
-   Active navigation
-   Focus states
-   Send button
-   Selected document controls
-   Important RAG status indicators

Avoid excessive use of gradients.

------------------------------------------------------------------------

# 4. Typography

Recommended font:

-   Inter
-   Geist
-   SF Pro style fallback

### Typography hierarchy

  Element               Recommended size     Weight
  ------------------- ------------------ ----------
  Application logo              20--24px        600
  Page/chat title               16--18px        600
  Message text                  15--16px        400
  Sidebar item                      14px   400--500
  Metadata                      12--13px        400
  Button text                   13--14px        500
  Document filename                 14px        500

The UI should prioritize readability rather than extremely small text.

------------------------------------------------------------------------

# 5. Left Sidebar

The sidebar is always visible on desktop.

## 5.1 Branding

Top section:

-   Coretext logo/icon
-   Product name: **Coretext**
-   Subtitle: **Corrective RAG**

Example:

``` text
✦ Coretext
  Corrective RAG
```

------------------------------------------------------------------------

## 5.2 New Chat

Large primary button:

``` text
+  New Chat
```

Keyboard shortcut may be displayed:

``` text
⌘ K
```

or:

``` text
Ctrl K
```

The button should be visually prominent.

------------------------------------------------------------------------

# 6. Conversation List

Section title:

``` text
Conversations
```

Include a search icon.

Each conversation item contains:

-   Chat icon
-   Conversation title
-   Relative timestamp or date

Example:

``` text
▣  What is RAG and how does it work?
   2:31 PM

▣  Explain LangGraph with example
   Yesterday

▣  Best practices for chunking documents
   May 26
```

## Active conversation

The selected conversation should have:

-   Slightly brighter background
-   Purple accent/icon
-   Rounded container

------------------------------------------------------------------------

# 7. User Profile Section

The profile section stays at the bottom of the left sidebar.

It should contain:

-   Avatar
-   User name
-   Email
-   Dropdown indicator

Example:

``` text
┌─────────────────────────────┐
│  ◉  Sohel Islam          ˅  │
│     sohel@example.com       │
└─────────────────────────────┘
```

Below the profile:

### Plan card

``` text
Free Plan
Upgrade for more limits

██████░░░░░░

2.4k / 10k messages used

[ Upgrade ]
```

Then navigation actions:

-   Settings
-   Help & Docs
-   Sign out

------------------------------------------------------------------------

# 8. Main Chat Area

The main chat workspace occupies the remaining screen.

## 8.1 Chat Header

The header should contain:

Left:

``` text
What is RAG and how does it work? ˅
```

Right:

-   Share
-   Star / favorite
-   More actions
-   Documents button

The Documents button is important.

### Documents button

It should be represented by a document icon.

Example:

``` text
[ 📄 ]
```

Clicking it opens the Documents drawer.

The drawer should **not** be visible in the default state.

------------------------------------------------------------------------

# 9. User Message

User messages should appear aligned to the right.

Example:

``` text
                         ┌──────────────────────────────┐
                         │ What is RAG and how does it │
                         │ work?                        │
                         └──────────────────────────────┘
                                             ◉
```

Include:

-   User avatar
-   Timestamp

------------------------------------------------------------------------

# 10. Assistant Message

Assistant responses should appear aligned to the left.

Example:

``` text
✦

┌─────────────────────────────────────────────┐
│ RAG (Retrieval-Augmented Generation) is    │
│ a technique that combines retrieval with   │
│ language generation...                     │
│                                             │
│ Here's how it works:                       │
│                                             │
│ 1. Retrieval                                │
│ 2. Augmentation                             │
│ 3. Generation                               │
│                                             │
│ Sources                                     │
│ [RAG Paper] [LangChain Docs] [+2 more]      │
│                                             │
│ ✓ Retrieved 5 chunks                        │
└─────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 11. RAG Transparency

Because Coretext is a Corrective / Agentic RAG application, the UI
should expose useful retrieval information without overwhelming normal
users.

## Recommended status

At the bottom of an assistant response:

``` text
● Retrieved 5 chunks
```

or:

``` text
✓ Answer grounded in 5 retrieved chunks
```

Potential future states:

``` text
Searching documents...
Retrieving relevant chunks...
Evaluating retrieved context...
Correcting retrieval...
Generating answer...
```

These states can be shown during generation.

------------------------------------------------------------------------

# 12. Sources

Assistant responses should support a Sources section.

Example:

``` text
Sources

[ RAG Paper (2020) · PDF ]
[ LangChain Docs · Web ]
[ LlamaIndex Guide · Web ]
[ +2 more ]
```

Clicking a source should open the corresponding document/source preview.

------------------------------------------------------------------------

# 13. Message Actions

Every assistant response can include:

-   Copy
-   Like
-   Dislike
-   Regenerate
-   More

Example:

``` text
□   👍   👎   ⋮
```

These controls should remain visually subtle.

------------------------------------------------------------------------

# 14. Chat Composer

The composer is fixed near the bottom of the main chat area.

Example:

``` text
┌─────────────────────────────────────────────────────────────┐
│ Ask anything about your documents...                        │
│                                                             │
│  📎   ↑   ▦   ◉   ⚙                              ➤          │
└─────────────────────────────────────────────────────────────┘
```

## Composer functionality

The composer should support:

-   Text input
-   Upload attachment
-   Upload document
-   Select/search documents
-   Optional web search
-   Optional advanced settings
-   Send

### Placeholder

``` text
Ask anything about your documents...
```

------------------------------------------------------------------------

# 15. Document Drawer

## Critical UX requirement

The Documents section must **not** permanently occupy screen space.

It should be a slide-out drawer.

### Default

``` text
Documents drawer = CLOSED
```

### On click

The drawer slides in from the right.

Recommended width:

-   Desktop: 360--420px

The main chat should remain visible behind it.

------------------------------------------------------------------------

# 16. Documents Drawer Header

Header:

``` text
Documents                                      X
```

Below it:

Tabs:

``` text
My Documents       Upload New
```

Alternative:

``` text
Documents
────────────────────
[ Search documents... ]
```

------------------------------------------------------------------------

# 17. Document Search

The drawer should include a search field:

``` text
🔍 Search documents...
```

Users can search by:

-   Filename
-   File type
-   Metadata

------------------------------------------------------------------------

# 18. Document Upload

Upload area:

``` text
┌─────────────────────────────────────┐
│              ↑                      │
│       Upload documents              │
│                                     │
│  Drag & drop or click to upload     │
│                                     │
│       [ Upload Document ]            │
└─────────────────────────────────────┘
```

Supported initial formats:

-   PDF
-   DOCX
-   TXT

The maximum file size should be configurable.

------------------------------------------------------------------------

# 19. Document List

Each document card should contain:

-   File type icon
-   Filename
-   Number of chunks
-   File size
-   Upload date
-   More actions button

Example:

``` text
┌─────────────────────────────────────┐
│ 📄  RAG_Research_Paper.pdf       ⋮ │
│     128 chunks · 2.4 MB             │
│     May 28, 2025                    │
└─────────────────────────────────────┘
```

------------------------------------------------------------------------

# 20. Document Actions

Clicking the three-dot menu should show:

``` text
Open
Preview
Rename
Use in chat
Download
Delete
```

For delete:

``` text
Delete document?

This will remove the document from your
knowledge base and it will no longer be
available for retrieval.

[ Cancel ] [ Delete ]
```

------------------------------------------------------------------------

# 21. Deleted Documents

The document drawer should provide access to deleted documents.

Example:

``` text
[ 🗑 Manage deleted documents ]
```

This can open a separate view/modal containing:

-   Deleted documents
-   Deleted date
-   Restore
-   Permanently delete

------------------------------------------------------------------------

# 22. Document Processing States

Uploaded documents should show processing status.

### Uploading

``` text
Uploading...
██████████░░░░ 72%
```

### Processing

``` text
Processing document...
Extracting text
Creating chunks
Generating embeddings
Indexing
```

### Ready

``` text
✓ Ready
128 chunks
```

### Failed

``` text
⚠ Processing failed
[ Retry ]
```

------------------------------------------------------------------------

# 23. Corrective RAG / Agentic RAG Status

Coretext can expose a lightweight retrieval pipeline indicator.

Example:

``` text
Retrieval
   ↓
Relevance Check
   ↓
Correction
   ↓
Generation
```

However, this should be optional.

The default chat should remain clean.

A user can click:

``` text
View retrieval details
```

to open a detailed panel.

------------------------------------------------------------------------

# 24. Retrieval Details Panel

For advanced users, show:

``` text
Retrieval Details

Query
"What is RAG?"

Retrieved chunks
5

Relevant
4 / 5

Corrected
1

Final context
4 chunks

Model
GPT-5.x

Latency
1.82s
```

Potential additional information:

-   Retrieval score
-   Reranker score
-   Selected chunks
-   Rejected chunks
-   Correction reason

------------------------------------------------------------------------

# 25. Empty State

When a user starts a new chat and has no documents:

``` text
                    ✦

             Welcome to Coretext

       Ask questions about your knowledge
       base using Corrective RAG.

       Upload documents to get started.

            [ Upload Documents ]

       or

       Ask a general question below
```

Composer remains visible.

------------------------------------------------------------------------

# 26. Empty Documents State

When there are no uploaded documents:

``` text
No documents yet

Upload PDFs, DOCX, or TXT files to
build your knowledge base.

[ Upload Document ]
```

------------------------------------------------------------------------

# 27. Responsive Behavior

## Desktop

Show:

-   Full conversation sidebar
-   Main chat
-   Documents drawer when opened

## Tablet

Sidebar may collapse.

Documents drawer remains a right-side drawer.

## Mobile

Use:

-   Collapsible navigation
-   Full-screen chat
-   Full-screen document manager/modal

The Documents drawer should not shrink the chat to an unusable width.

------------------------------------------------------------------------

# 28. Accessibility

Requirements:

-   Keyboard navigation
-   Visible focus states
-   Accessible labels for icon buttons
-   Sufficient contrast
-   Screen-reader labels
-   Confirmation before destructive actions
-   Escape key closes drawers/modals
-   Enter sends message
-   Shift + Enter creates a new line

------------------------------------------------------------------------

# 29. Interaction Rules

### New Chat

Creates a new conversation.

### Conversation click

Loads the selected conversation.

### Documents button

Opens the Documents drawer.

### Close Documents

Closes the drawer.

### Upload

Starts document upload and processing.

### Document click

Opens document preview/details.

### Delete

Shows confirmation before deletion.

### Send

Submits the message and begins the RAG pipeline.

------------------------------------------------------------------------

# 30. Recommended Component Structure

Suggested frontend component structure:

``` text
app/
├── layout
├── chat/
│   ├── ChatPage
│   ├── ChatHeader
│   ├── MessageList
│   ├── UserMessage
│   ├── AssistantMessage
│   ├── Sources
│   ├── MessageActions
│   └── ChatComposer
│
├── sidebar/
│   ├── AppLogo
│   ├── NewChatButton
│   ├── ConversationList
│   ├── ConversationItem
│   ├── UserProfile
│   └── PlanCard
│
├── documents/
│   ├── DocumentsButton
│   ├── DocumentsDrawer
│   ├── DocumentSearch
│   ├── DocumentUpload
│   ├── DocumentList
│   ├── DocumentCard
│   ├── DocumentActions
│   ├── DocumentPreview
│   └── DeletedDocuments
│
└── retrieval/
    ├── RetrievalStatus
    ├── RetrievalDetails
    └── PipelineStatus
```

------------------------------------------------------------------------

# 31. Suggested Design Tokens

``` css
--background: #080b12;
--surface: #0d111a;
--surface-elevated: #121824;
--surface-hover: #171e2c;

--border: rgba(255, 255, 255, 0.08);

--text-primary: #f5f7fb;
--text-secondary: #9aa4b2;
--text-muted: #667085;

--primary: #6d5dfc;
--primary-hover: #7b6cff;

--success: #22c55e;
--warning: #f59e0b;
--danger: #ef4444;
```

These are starting values, not mandatory final colors.

------------------------------------------------------------------------

# 32. UI Implementation: shadcn/ui

Coretext should use **shadcn/ui** as the primary UI component foundation.

The goal is to avoid building common UI primitives from scratch while keeping the product visually custom and branded.

## 32.1 Component philosophy

Use shadcn/ui components wherever an existing primitive fits the requirement.

Customize:

- Colors
- Radius
- Borders
- Shadows
- Typography
- Spacing
- Icons
- Component composition

Do not make Coretext look like an untouched shadcn/ui starter template. shadcn/ui should provide the implementation foundation while Coretext maintains its own visual identity.

## 32.2 Recommended shadcn/ui components

Use the following components where appropriate:

| Coretext feature | shadcn/ui component |
|---|---|
| New Chat | Button |
| Conversation search | Input |
| Conversation list | Scroll Area |
| User profile menu | Dropdown Menu |
| Settings/profile actions | Dropdown Menu |
| Chat title actions | Dropdown Menu |
| Send button | Button |
| Composer | Textarea |
| Upload document | Button + Dialog |
| Document drawer | Sheet |
| Document preview | Dialog |
| Document actions | Dropdown Menu |
| Delete confirmation | Alert Dialog |
| Document processing | Progress |
| Sources | Badge |
| RAG status | Badge |
| Retrieval details | Collapsible |
| Upload tabs | Tabs |
| Document filters | Popover |
| Tooltips | Tooltip |
| Loading states | Skeleton |
| Notifications | Sonner |
| Mobile navigation | Sheet |
| Context menus | Context Menu |

## 32.3 Documents drawer

The Documents interface should use the shadcn/ui **Sheet** component.

Important behavior:

- Closed by default
- Opens from the right
- Does not permanently consume chat workspace space
- Can be closed using the close button
- Escape key should close it
- On mobile, it can become a full-screen sheet

Conceptually:

```text
Documents button
      ↓
shadcn/ui Sheet
      ↓
DocumentsDrawer
      ├── Header
      ├── Tabs
      ├── Search
      ├── Upload
      ├── DocumentList
      └── DeletedDocuments
```

## 32.4 Document cards

Document cards should be composed from standard shadcn/ui primitives rather than a custom UI system.

Suggested composition:

```text
Card
 ├── File icon
 ├── Filename
 ├── Metadata
 └── DropdownMenu
```

Metadata can use muted text and small Badge components.

## 32.5 Dialogs and destructive actions

Use **Alert Dialog** for destructive actions such as deleting a document.

Example:

```text
Delete document?

This will remove the document from your
knowledge base and it will no longer be
available for retrieval.

[ Cancel ] [ Delete ]
```

Use **Dialog** for:

- Document preview
- Retrieval details
- Advanced settings
- Other focused secondary workflows

## 32.6 Chat composer

Use shadcn/ui primitives to create a custom composer.

Recommended structure:

```text
Card / custom container
 ├── Textarea
 ├── Attachment Button
 ├── Document Button
 ├── Optional Tool Button
 ├── Settings Button
 └── Send Button
```

The composer should remain visually similar to the generated Coretext design rather than looking like a default shadcn form.

## 32.7 Sidebar

The left navigation can use shadcn/ui's **Sidebar** primitives.

Structure:

```text
Sidebar
 ├── SidebarHeader
 │    └── Coretext branding
 │
 ├── SidebarContent
 │    ├── New Chat
 │    ├── Conversation Search
 │    └── Conversation List
 │
 └── SidebarFooter
      ├── Profile
      ├── Plan Card
      ├── Settings
      ├── Help & Docs
      └── Sign Out
```

The sidebar should remain dark and visually lightweight.

## 32.8 Feedback and notifications

Use:

- Toast/Sonner for upload and document-management feedback
- Tooltip for icon-only controls
- Skeleton for loading conversations/documents
- Progress for file uploads and processing

Examples:

```text
✓ Document uploaded successfully
```

```text
Processing document...
██████████░░ 72%
```

```text
Document deleted
[ Undo ]
```

## 32.9 Accessibility

Prefer shadcn/ui/Radix primitives because they provide accessible interaction patterns for:

- Keyboard navigation
- Focus management
- Dialogs
- Menus
- Tooltips
- Tabs
- Drawers
- Alerts

Coretext should still verify accessibility for all custom compositions.

## 32.10 Implementation rule

**Build product-specific components by composing shadcn/ui primitives.**

For example:

```text
shadcn/ui primitives
        ↓
Coretext components
        ↓
Coretext application
```

Avoid creating custom replacements for standard primitives unless Coretext has a specific interaction that shadcn/ui does not cover.

# 32. Overall UX Goal

Coretext should feel like:

> **ChatGPT + a powerful document knowledge base + transparent
> Corrective RAG controls.**

The interface should not feel like an enterprise document-management
system.

The primary experience remains:

``` text
Open Coretext
      ↓
Start / select conversation
      ↓
Ask a question
      ↓
Coretext retrieves relevant knowledge
      ↓
Coretext evaluates/corrects retrieval
      ↓
Generate grounded response
      ↓
Show sources and lightweight retrieval status
```

Document management is available when needed through the **Documents
drawer**, rather than permanently occupying the chat workspace.

------------------------------------------------------------------------

# 33. MVP Priority

### P0 --- Must have

-   Dark mode
-   Left sidebar
-   New Chat
-   Conversation history
-   User profile
-   Chat interface
-   Message composer
-   Document upload
-   Documents drawer
-   Document list
-   Delete document
-   Source display
-   Basic retrieval status

### P1 --- Important

-   Document search
-   Document preview
-   Rename document
-   Restore deleted documents
-   Upload progress
-   Processing status
-   Retrieval details

### P2 --- Later

-   Advanced retrieval visualization
-   Reranking details
-   Evaluation metrics
-   Token/latency information
-   Multiple knowledge bases
-   Team/workspace support
-   Advanced document filters
-   Conversation sharing

------------------------------------------------------------------------

# 34. Design Direction Summary

**Coretext should be dark, minimal, modern, AI-native, and implemented using shadcn/ui primitives with a custom Coretext visual layer.**

The most important design decision is that the **chat remains the
primary workspace**.

Documents should be accessible through a dedicated button and slide-out
drawer rather than permanently taking up the right side of the
application.

The UI should communicate that Coretext is more than a basic chatbot
through subtle indicators for:

-   Retrieval
-   Relevance evaluation
-   Correction
-   Sources
-   Grounding

But these advanced capabilities should remain secondary to the simple
conversational experience.