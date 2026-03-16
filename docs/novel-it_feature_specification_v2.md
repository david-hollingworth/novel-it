# Novel Writing Application - Feature Specification

Version. 2.0

17 November 2025

## 1\. Overview

A Django-based novel writing application with markdown block-based editor, character/plot management, and writing analytics.

* * *

## 2\. User Management

### 2.1 Authentication

*   User registration with email verification
*   Login/logout functionality
*   Password reset capability
*   Profile management (username, email, avatar)

### 2.2 User Preferences

*   Default project settings
*   Writing goals (daily word count target)
*   Editor preferences (theme, font size)
*   Export format preferences

* * *

## 3\. Project Management

### 3.1 Novel Projects

*   Create/edit/delete novels
*   Novel metadata:
    *   Title
    *   Subtitle (optional)
    *   Author name (optional)
    *   Genre
    *   Target word count (optional)
    *   Project status (planning, drafting, revising, complete)
    *   Synopsis/description (optional)
    *   Premise (optional)
    *   Pitch (optional)
    *   Cover image (optional)
    *   Created/modified timestamps

### 3.2 Project Organization

*   Archive/unarchive projects
*   Project templates (optional: genre-specific starting structures)
*   Duplicate project functionality
*   Export entire project (markdown, PDF, DOCX, ePub)

* * *

## 4\. Writing Interface

### 4.1 Document Structure

*   **Books** â†’ **Parts** â†’ **Chapters** â†’ **Scenes** hierarchy
*   Flexible structure (can skip Parts if not needed)
*   Drag-and-drop reordering of elements
*   Nested navigation sidebar
*   Corkboard View

### 4.2 Block-Based Content System

Each scene consists of ordered blocks:

#### Core Block Types

*   **Paragraph**: Standard markdown text
*   **Heading**: H1-H6 headings
*   **Note**: Author notes (not included in word count)
*   **Divider**: Scene/section breaks

#### Reference Blocks

*   **Character Reference**: Inline character card/mention
*   **Location Reference**: Quick location details
*   **Item Reference**: Reference to items/objects in the story
*   **Plot Point**: Marker for story structure points
*   **Research Note**: Link to research material

#### Media Blocks

*   **Image**: Embedded images with caption support
*   **Quote**: Formatted quotations/epigraphs

### 4.3 Block Properties

*   Unique ID
*   Block type
*   Content (markdown text)
*   Order/position
*   Metadata (timestamps, word count)
*   Parent scene relationship

### 4.4 Editor Features

*   Markdown syntax highlighting
*   Live preview toggle
*   Focus mode (distraction-free)
*   Word count (scene, chapter, total)
*   Character count
*   Reading time estimate
*   Readability assessment
*   Auto-save (every 30 seconds)
*   Manual save indicator
*   Undo/redo functionality

* * *

## 5\. Character Management

### 5.1 Character Profiles

*   Basic Information:
    *   Name (first, middle, last, nickname)
    *   Role (protagonist, antagonist, supporting, minor)
    *   Age/birthdate
    *   Gender/pronouns
    *   Physical description
*   Background:
    *   Biography (markdown)
    *   Personality traits
    *   Motivations
    *   Goals
    *   Fears/weaknesses
    *   Character arc notes
*   Visual:
    *   Profile image
    *   Gallery images

### 5.2 Character Relationships

*   Define relationships between characters
*   Relationship type (family, friend, enemy, romance, etc.)
*   Relationship description
*   Visual relationship graph (optional for v2)

### 5.3 Character Organization

*   Filter by role
*   Search characters
*   Character appearances (which scenes they appear in)
*   Character mention tracking

* * *

## 6\. Items/Objects Management

### 6.1 Item Database

*   Item name
*   Item type (weapon, artifact, vehicle, document, etc.)
*   Description (markdown)
*   Significance/importance
*   Current owner/location
*   History/provenance
*   Properties/abilities (for magical/special items)
*   Images

### 6.2 Item Tracking

*   Item appearances (which scenes)
*   Ownership timeline
*   Item relationships (parts of sets, etc.)

* * *

## 7\. Location/World Building

### 7.1 Location Database

*   Location name
*   Location type (city, building, room, region, etc.)
*   Parent location (hierarchical structure)
*   Description (markdown)
*   Images/maps
*   Notable features
*   History/background

### 7.2 World Building Notes

*   Magic systems
*   Technology levels
*   Cultural notes
*   Historical timeline
*   Rules and laws
*   Languages

* * *

## 8\. Plot & Structure

### 8.1 Plot Structure Templates

*   Three-Act Structure
*   Hero's Journey
*   Save the Cat
*   Custom structure
*   Structure visualization (timeline view)

### 8.2 Plot Points

*   Plot point name
*   Structure position (e.g., "Inciting Incident")
*   Associated scene(s)
*   Description
*   Status (planned, drafted, complete)

### 8.3 Scene Cards

*   Scene title
*   Scene goal/purpose
*   POV character
*   Location
*   Characters present
*   Items present
*   Plot points addressed
*   Conflicts/tension
*   Outcome
*   Scene status
*   Word count

### 8.4 Timeline

*   Event chronology
*   Date/time tracking for events
*   Timeline visualization (optional)

* * *

## 9\. Research & Notes

### 9.1 Research Database

*   Title
*   Category/tags
*   Content (markdown)
*   Source URL/citation
*   Attachments (PDFs, images)
*   Related scenes/chapters

### 9.2 General Notes

*   Freeform notes section
*   Tagging system
*   Search functionality
*   Pin important notes

* * *

## 10\. Writing Statistics & Goals

### 10.1 Statistics Dashboard

*   Total word count (by project)
*   Words by chapter/scene
*   Writing streak (consecutive days)
*   Daily word count history (graph)
*   Average words per day
*   Estimated completion date
*   Writing pace analysis

### 10.2 Goal Setting

*   Daily word count goal
*   Project deadline
*   Chapter/scene targets
*   Progress visualization (progress bars)
*   Milestone notifications

### 10.3 Writing Sessions

*   Track writing sessions (start/end time)
*   Words written per session
*   Session notes
*   Session history

* * *

## 11\. Export & Backup

### 11.1 Export Formats

*   Markdown (single file or structure)
*   Plain text
*   PDF (formatted manuscript)
*   DOCX (Microsoft Word)
*   HTML
*   EPUB (optional for v2)

### 11.2 Export Options

*   Include/exclude author notes
*   Include/exclude front matter
*   Custom formatting options
*   Page size and margins (for PDF)

### 11.3 Backup

*   Automatic backups (daily)
*   Manual backup/download
*   Backup history (last 30 days)
*   Restore from backup

* * *

## 12\. Search & Navigation

### 12.1 Global Search

*   Search across all content (scenes, characters, locations, notes)
*   Filter by type
*   Recent searches
*   Search results preview

### 12.2 Navigation

*   Hierarchical sidebar navigation
*   Breadcrumb navigation
*   Quick jump (keyboard shortcut to search)
*   Recently viewed items
*   Bookmarks/favorites

* * *

## 13\. Collaboration (Future Phase)

### 13.1 Sharing

*   Share project with beta readers (read-only)
*   Share specific chapters
*   Comment functionality
*   Suggestion mode

### 13.2 Co-authoring (Optional)

*   Multiple authors per project
*   Permission levels
*   Conflict resolution
*   Activity log

* * *

## 14\. Technical Requirements

### 14.1 Technology Stack

*   **Backend**: Django 4.2+
*   **Database**: PostgreSQL
*   **Frontend**: HTML, CSS, JavaScript (Alpine.js recommended for lightweight reactivity)
*   **Markdown**: Python-Markdown with extensions
*   **Editor**: SimpleMDE (lightweight) or Toast UI Editor (feature-rich)
*   **Styling**: Tailwind CSS

### 14.2 Performance

*   Page load time < 2 seconds
*   Auto-save without UI lag
*   Efficient pagination for large projects
*   Lazy loading of content

### 14.3 Security

*   CSRF protection
*   SQL injection prevention
*   XSS protection
*   Secure password storage
*   Rate limiting for API endpoints

### 14.4 Data Management

*   Soft delete for content (recovery option)
*   Audit trail for major changes
*   Data validation
*   Database backups

* * *

## 15\. MVP (Minimum Viable Product) Scope

For initial development, focus on:

1.  User authentication
2.  Project CRUD operations
3.  Plot structure templates and scene cards
4.  Chapter/Scene structure (Books â†’ Parts â†’ Chapters â†’ Scenes)
5.  Block-based markdown editor (with image support)
6.  Basic character profiles
7.  Basic location database
8.  Basic items/objects database
9.  Word count tracking

**Defer to Phase 2:**

*   Advanced statistics/graphs
*   Timeline visualization
*   Relationship graphs
*   Collaboration features
*   Advanced export formats (PDF, DOCX, EPUB)
*   Writing sessions tracking
*   Character/location relationship visualization
*   Simple export (markdown, plain text)
*   Basic search

* * *

## 16\. User Interface Mockup Notes

### 16.1 Main Layout

*   Top navbar: Logo, project selector, user menu
*   Left sidebar: Document structure navigation
*   Main content area: Editor or content view
*   Right sidebar (contextual): Scene info, statistics, character/location/item quick-view

### 16.2 Key Views

*   Dashboard: Recent projects, writing stats, quick access
*   Editor: Full-width or sidebar mode
*   Project Settings: Metadata, structure, preferences
*   Character List: Grid or table view with filters
*   Location List: Hierarchical tree view
*   Items List: Grid or table view with filters
*   Plot Structure: Visual timeline with plot points
*   Statistics: Charts and metrics

### 16.3 Responsive Design

*   Mobile-friendly views
*   Touch-optimized for tablets
*   Progressive disclosure of features

* * *

## 17\. Future Enhancements

*   Mobile apps (iOS/Android)
*   Distraction-free writing app (desktop)
*   AI writing assistant integration
*   Thesaurus/dictionary integration
*   Grammar/style checking
*   Version control/branching (alternative storylines)
*   Storyboard visualization
*   Character image generation (AI)
*   Writing prompts/exercises
*   Community features (forums, writing groups)

* * *

## 18\. Revision History

- Version 1.0 - 13 Nov 2025
  - Initial Version
- Version 2.0 - 17 Nov 2025
  - Corrected section numbering after section 7
  - Section 3 - Changed 'project' to 'novel'
  - Added section 18 - Revision History and added version and date to the top of the document.
