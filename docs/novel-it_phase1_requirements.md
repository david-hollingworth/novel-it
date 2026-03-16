# Novel Writing Application - Phase 1 Requirements Specification

## Project Overview
Self-hosted web application for novel writing with focus on clean, uncluttered interface. Must support structured writing (novels/chapters/scenes) and planning databases for characters, locations, and items. Multi-user capable from the start.

---

## Technical Stack

**Backend:**
- Django 5.x
- PostgreSQL
- Django REST Framework (for API endpoints if needed)
- Python-Markdown (for rendering preview)

**Frontend:**
- HTMX (for dynamic interactions without complex JS)
- Alpine.js (minimal interactivity where needed)
- Tailwind CSS (clean, modern styling)
- CodeMirror 6 (markdown editor)

**Infrastructure:**
- Docker Compose
- PostgreSQL container
- Git repository in local Forgejo

---

## Phase 1 Core Features (MVP)

### 1. User Authentication
- Django's built-in authentication system
- User registration (username, email, password)
- Login/logout functionality
- Password change capability
- All novels and related content are user-scoped
- Users can only access their own content

**Phase 1 Exclusions:**
- Password reset via email
- Email verification
- Social authentication
- User profiles beyond basic info

### 2. Project Structure

**Novel** (belongs to User)
- Title
- Description/synopsis (markdown)
- Created/modified timestamps
- Word count (calculated, rolls up from all scenes)
- User can create multiple novels

**Chapter** (belongs to Novel)
- Title
- Order/sequence number
- Chapter summary/notes (markdown)
- Word count (calculated, rolls up from scenes)

**Scene** (belongs to Chapter)
- Title
- Order/sequence number
- Markdown content (the actual writing)
- Word count (auto-calculated from content)
- Scene notes/summary (markdown)

### 3. Writing Interface
- Clean markdown editor using CodeMirror 6
- Live word count display (scene level)
- Scene navigation (previous/next within chapter)
- Chapter navigation sidebar
- Autosave (every 30 seconds or on blur)
- Markdown preview toggle
- Distraction-free writing mode option
- Keyboard shortcuts for common actions:
  - Ctrl+S: Manual save
  - Ctrl+P: Toggle preview
  - Ctrl+B/I: Bold/Italic
  - Esc: Exit distraction-free mode

### 4. Planning Databases

All planning entities are scoped to a specific Novel (not shared across novels).

**Character**
- Name
- Role (protagonist/antagonist/supporting/other)
- Description (markdown)
- Notes (markdown)
- Optional image upload
- Belongs to Novel

**Location**
- Name
- Type (city/building/country/other - optional categorization)
- Description (markdown)
- Notes (markdown)
- Optional image upload
- Belongs to Novel

**Item**
- Name
- Type (object/weapon/artifact/other - optional categorization)
- Description (markdown)
- Notes (markdown)
- Optional image upload
- Belongs to Novel

### 5. Navigation & Organization

**Dashboard/Home Page:**
- List of user's novels
- Quick stats per novel (word count, chapter count, last modified)
- "Create New Novel" button
- Search/filter novels (by title)

**Novel Overview Page:**
- Novel title and description
- Total word count
- Chapter list with individual word counts
- Quick access tabs/sections for:
  - Chapters & Scenes
  - Characters
  - Locations
  - Items
- "Add Chapter" button
- Settings/edit novel details

**Chapter View:**
- Chapter title and summary
- Scene list with word counts
- Total chapter word count
- "Add Scene" button
- Reorder scenes (drag-and-drop)

**Writing View:**
- Full-screen capable
- Scene title (editable inline)
- Markdown editor
- Word count indicator
- Scene navigation
- Save status indicator

### 6. Data Management
- Full CRUD operations for all entities:
  - Novels
  - Chapters
  - Scenes
  - Characters
  - Locations
  - Items
- Drag-and-drop reordering for:
  - Chapters within a novel
  - Scenes within a chapter
- Soft delete (mark as archived, not hard delete)
- Restore from archive functionality
- Confirmation prompts for destructive actions

### 7. Word Count System
- **Scene level:** Direct count of markdown content (excluding markdown syntax)
- **Chapter level:** SUM of all scene word counts in that chapter
- **Novel level:** SUM of all scene word counts in entire novel
- Auto-calculated on save
- Stored in database for performance
- Displayed at all relevant levels

### 8. Image Handling
- Upload images for characters, locations, items
- Store in media directory
- Basic image display in detail views
- No image editing/cropping in Phase 1
- File size limits (e.g., 5MB per image)
- Supported formats: JPG, PNG, GIF, WEBP

---

## Database Schema Summary

```
User (Django built-in)
  └─ Novel
      ├─ word_count (calculated)
      ├─ Chapter
      │   ├─ word_count (calculated)
      │   └─ Scene
      │       └─ word_count (calculated)
      ├─ Character
      │   └─ image (optional)
      ├─ Location
      │   └─ image (optional)
      └─ Item
          └─ image (optional)
```

**Key Relationships:**
- User → Novel (One-to-Many)
- Novel → Chapter (One-to-Many)
- Chapter → Scene (One-to-Many)
- Novel → Character/Location/Item (One-to-Many each)

---

## Phase 1 Exclusions (Future Features)

The following are explicitly OUT OF SCOPE for Phase 1:

- Linking characters/locations/items to scenes (references/tagging)
- Plotting/outlining tools (Kanban board, corkboard view)
- Story structure templates
- Export functionality (PDF, DOCX, etc.)
- Import from other formats
- Version control/revision history
- Comments/annotations on scenes
- Goals/targets (daily word count goals, etc.)
- Statistics/analytics beyond word count
- Multi-user collaboration (sharing novels)
- Search functionality across content
- Tags/categories for scenes
- Full-text search
- Mobile app
- Offline mode
- AI writing assistance
- Spell check/grammar (rely on browser)
- Custom themes/appearance settings

---

## UI/UX Requirements

### Design Principles
- Clean, minimal interface
- Uncluttered workspace
- Fast and responsive
- Keyboard-friendly
- Mobile-responsive (tablet and desktop focus)

### Performance Requirements
- Page loads < 1 second
- Autosave without interrupting typing
- No full page refreshes during editing
- Smooth transitions

### Accessibility
- Semantic HTML
- Keyboard navigation support
- Proper focus management
- Readable contrast ratios

---

## Security Considerations

- User authentication required for all content
- CSRF protection (Django default)
- SQL injection prevention (Django ORM)
- XSS prevention (Django templating)
- Secure password storage (Django default hashing)
- File upload validation
- Rate limiting on authentication endpoints (future consideration)

---

## Development Phases

### Phase 1A: Foundation (First Session)
- Django project setup
- Docker Compose configuration
- Database models
- User authentication
- Basic CRUD views (using Django forms initially)

### Phase 1B: Core Writing (Second Session)
- Novel/Chapter/Scene management
- Basic navigation
- Markdown editor integration (CodeMirror)
- Autosave functionality

### Phase 1C: Planning Tools (Third Session)
- Character/Location/Item management
- Image uploads
- Word count calculation and display

### Phase 1D: Polish (Fourth Session)
- HTMX integration for smooth interactions
- Tailwind CSS styling
- Drag-and-drop reordering
- Distraction-free mode
- Testing with real content

---

## Success Criteria

Phase 1 is considered complete when:

1. User can register, login, and manage their account
2. User can create multiple novels
3. User can create chapters and scenes within a novel
4. User can write and edit content in markdown with a clean editor
5. Word counts roll up correctly (scene → chapter → novel)
6. User can create and manage character/location/item databases
7. User can upload images for planning entities
8. Interface feels clean, uncluttered, and pleasant to use
9. Application is stable enough to use for actual novel writing
10. **Primary success metric:** Developer actually uses it to work on their novel and fix Act 1 plot issues

---

## Future Phases (Post Phase 1)

### Phase 2: Enhanced Planning
- Link characters/locations/items to scenes
- Scene cards/corkboard view
- Kanban board for plotting
- Story structure templates

### Phase 3: Export & Sharing
- Export to DOCX, PDF, EPUB
- Print-ready formatting
- Backup/restore functionality

### Phase 4: Advanced Features
- Version control/revision history
- Full-text search
- Goals and statistics
- Timeline view
- Advanced analytics

---

## Technical Notes

### Docker Compose Structure
```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: novelapp
      POSTGRES_USER: novelapp
      POSTGRES_PASSWORD: [secure password]
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
      - media_files:/code/media
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgres://novelapp:[password]@db:5432/novelapp
```

### Django Apps Structure
```
novelapp/
  ├── accounts/        # User authentication
  ├── novels/          # Novel, Chapter, Scene models
  ├── planning/        # Character, Location, Item models
  ├── core/            # Shared utilities, base templates
  └── static/          # CSS, JS, images
```

---

## Deployment Notes

- Running locally via Docker Compose
- No external hosting in Phase 1
- Access via localhost:8000
- PostgreSQL data persisted in Docker volume
- Media files (uploads) persisted in Docker volume
- Code tracked in Forgejo repository

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-29  
**Status:** Approved for Development
