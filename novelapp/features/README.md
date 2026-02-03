# Novel App BDD Feature Files

## Directory Structure

```
features/
├── authentication/
│   ├── user_registration.feature      (@authentication @critical @phase1a)
│   ├── user_login.feature             (@authentication @critical @phase1a)
│   ├── user_logout.feature            (@authentication @phase1a)
│   └── password_management.feature    (@authentication @phase1a)
│
├── novels/
│   ├── novel_creation.feature         (@novels @critical @phase1b)
│   ├── novel_editing.feature          (@novels @phase1b)
│   ├── novel_archiving.feature        (@novels @phase1b)
│   └── novel_deletion.feature         (@novels @phase1b)
│
├── chapters/
│   ├── chapter_creation.feature       (@chapters @phase1b)
│   ├── chapter_editing.feature        (@chapters @phase1b)
│   ├── chapter_reordering.feature     (@chapters @phase1b @requires_browser)
│   └── chapter_archiving.feature      (@chapters @phase1b)
│
├── scenes/
│   ├── scene_creation.feature         (@scenes @critical @phase1b)
│   ├── scene_editing.feature          (@scenes @phase1b)
│   ├── scene_status.feature           (@scenes @phase1b @workflow)
│   ├── scene_reordering.feature       (@scenes @phase1b @requires_browser)
│   └── scene_navigation.feature       (@scenes @phase1b)
│
├── editor/
│   ├── markdown_editing.feature       (@editor @critical @phase1b @requires_browser)
│   ├── autosave.feature              (@editor @critical @phase1b)
│   ├── keyboard_shortcuts.feature     (@editor @phase1b @requires_browser)
│   └── preview.feature               (@editor @phase1b @requires_browser)
│
├── planning/
│   ├── character_management.feature   (@planning @phase1c)
│   ├── location_management.feature    (@planning @phase1c)
│   ├── item_management.feature        (@planning @phase1c)
│   └── image_uploads.feature          (@planning @phase1c)
│
├── ui/
│   ├── dashboard.feature             (@ui @phase1d)
│   ├── novel_overview.feature        (@ui @phase1d)
│   ├── chapter_view.feature          (@ui @phase1d)
│   └── writing_view.feature          (@ui @phase1d @requires_browser)
│
└── system/
    ├── word_count.feature            (@system @critical @phase1c)
    ├── navigation.feature            (@system @phase1b)
    ├── security.feature              (@system @critical)
    └── accessibility.feature         (@system)
```

## Running Tests

### Run All Tests
```bash
python manage.py behave
```

### Run by Directory (Feature Area)
```bash
# Run all authentication tests
python manage.py behave features/authentication/

# Run all novel management tests
python manage.py behave features/novels/

# Run all editor tests
python manage.py behave features/editor/
```

### Run Specific Feature File
```bash
python manage.py behave features/authentication/user_registration.feature
python manage.py behave features/scenes/scene_creation.feature
```

### Run by Tags

```bash
# Critical tests only
python manage.py behave --tags=critical

# Phase 1A tests
python manage.py behave --tags=phase1a

# Phase 1B tests
python manage.py behave --tags=phase1b

# All authentication and novel tests
python manage.py behave --tags=authentication,novels

# Fast tests only (exclude slow/browser tests)
python manage.py behave --tags=fast

# Exclude browser tests
python manage.py behave --tags=~requires_browser

# Run critical tests but not browser tests
python manage.py behave --tags=critical --tags=~requires_browser

# Tests that are work in progress
python manage.py behave --tags=wip
```

### Run Multiple Specific Features
```bash
python manage.py behave \
  features/authentication/ \
  features/novels/novel_creation.feature \
  features/scenes/scene_creation.feature
```

## Tag Reference

### By Priority
- `@critical` - Must-have functionality
- `@important` - High priority
- `@nice_to_have` - Lower priority

### By Development Phase
- `@phase1a` - Foundation
- `@phase1b` - Core Writing Features
- `@phase1c` - Planning Tools
- `@phase1d` - Polish & UI

### By Test Type
- `@fast` - Quick tests (< 1 second)
- `@slow` - Slower tests (> 5 seconds)
- `@requires_browser` - Needs Selenium
- `@integration` - Integration tests
- `@unit` - Unit-level tests

### By Feature Area
- `@authentication`
- `@novels`
- `@chapters`
- `@scenes`
- `@editor`
- `@planning`
- `@ui`
- `@system`

### By Scenario Type
- `@happy_path` - Success scenarios
- `@error_handling` - Error cases
- `@validation` - Form/input validation
- `@security` - Security tests
- `@workflow` - Multi-step workflows

### By Status
- `@wip` - Work in progress
- `@broken` - Known broken tests
- `@skip` - Skip this test

## Test Execution Strategy

### Development Workflow
```bash
# 1. While developing a feature, run just that feature
python manage.py behave features/novels/novel_creation.feature

# 2. Before committing, run all fast tests
python manage.py behave --tags=fast

# 3. Before pushing, run all critical tests
python manage.py behave --tags=critical
```

### CI/CD Pipeline
```bash
# Stage 1: Fast tests (every push)
python manage.py behave --tags=fast,critical --tags=~requires_browser

# Stage 2: Full test suite (before merge)
python manage.py behave

# Stage 3: Browser tests (nightly or on-demand)
python manage.py behave --tags=requires_browser
```

## Tips for Implementation

1. **Start Small**: Implement one feature file at a time
2. **Reuse Steps**: Common steps go in `steps/common_steps.py`
3. **Tag Early**: Add tags as you create scenarios
4. **Run Often**: Run tests during development
5. **Keep Organized**: One feature area per directory

## Example Implementation Order

1. **Week 1**: Authentication features
   - Implement all authentication step definitions
   - Get all auth tests passing

2. **Week 2**: Novel management
   - Novel CRUD operations
   - User scoping/security

3. **Week 3**: Chapters and Scenes
   - Basic CRUD
   - Parent-child relationships

4. **Week 4**: Editor features
   - Start with autosave (no browser)
   - Add markdown editing (with browser)

5. **Week 5**: Planning tools
   - Characters, locations, items
   - Image uploads

6. **Week 6**: Polish
   - UI tests
   - Word count
   - Navigation

## Benefits of This Structure

✅ **Easy to navigate** - Find tests by feature area
✅ **Parallel execution** - Run multiple features simultaneously
✅ **Selective testing** - Test only what you're working on
✅ **Clear ownership** - Team members can own feature areas
✅ **Better git history** - Changes isolated to specific files
✅ **Flexible CI/CD** - Run subsets of tests at different stages
✅ **Maintainable** - Easier to update and refactor

## Total Test Count by Area

- Authentication: ~15 scenarios
- Novels: ~12 scenarios
- Chapters: ~15 scenarios
- Scenes: ~20 scenarios
- Editor: ~15 scenarios
- Planning: ~18 scenarios
- UI: ~12 scenarios
- System: ~15 scenarios

**Total: ~122 scenarios**

This provides comprehensive coverage of all Phase 1 requirements while remaining organized and maintainable.
