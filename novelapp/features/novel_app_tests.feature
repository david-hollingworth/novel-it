Feature: Novel Writing Application - Phase 1

# =============================================================================
# Phase 1A: Foundation
# =============================================================================

Feature: Django Project Setup
  As a developer
  I want to ensure the Django project is properly configured
  So that the application has a solid foundation

  Scenario: Django 5.x project is set up with proper structure
    Given the Django project exists
    When I check the Django version
    Then the version should be 5.x or higher
    And the project structure should include standard Django directories

  Scenario: Database models are created
    Given the Django project is set up
    When I inspect the database models
    Then I should see a Novel model
    And I should see a Chapter model
    And I should see a Scene model
    And I should see a Character model
    And I should see a Location model
    And I should see an Item model

  Scenario: Django apps structure is configured
    Given the Django project is set up
    When I check the installed apps
    Then I should see the "accounts" app
    And I should see the "novels" app
    And I should see the "planning" app
    And I should see the "core" app


Feature: User Authentication
  As a user
  I want to manage my account
  So that I can securely access my novels

  Scenario: User registration with username, email, and password
    Given I am on the registration page
    When I fill in "username" with "johndoe"
    And I fill in "email" with "john@example.com"
    And I fill in "password" with "SecurePass123!"
    And I fill in "confirm password" with "SecurePass123!"
    And I click the "Register" button
    Then I should see a success message
    And I should be redirected to the dashboard
    And a new user account should be created in the database

  Scenario: User registration with invalid email
    Given I am on the registration page
    When I fill in "username" with "johndoe"
    And I fill in "email" with "invalid-email"
    And I fill in "password" with "SecurePass123!"
    And I click the "Register" button
    Then I should see an error message "Please enter a valid email address"
    And no user account should be created

  Scenario: User registration with duplicate username
    Given a user exists with username "johndoe"
    And I am on the registration page
    When I fill in "username" with "johndoe"
    And I fill in "email" with "different@example.com"
    And I fill in "password" with "SecurePass123!"
    And I click the "Register" button
    Then I should see an error message "Username already exists"

  Scenario: User login with valid credentials
    Given I have a registered account with username "johndoe" and password "SecurePass123!"
    And I am on the login page
    When I fill in "username" with "johndoe"
    And I fill in "password" with "SecurePass123!"
    And I click the "Login" button
    Then I should be logged in
    And I should be redirected to the dashboard

  Scenario: User login with invalid credentials
    Given I have a registered account with username "johndoe" and password "SecurePass123!"
    And I am on the login page
    When I fill in "username" with "johndoe"
    And I fill in "password" with "WrongPassword"
    And I click the "Login" button
    Then I should see an error message "Invalid username or password"
    And I should remain on the login page

  Scenario: User logout
    Given I am logged in as "johndoe"
    And I am on the dashboard
    When I click the "Logout" button
    Then I should be logged out
    And I should be redirected to the login page

  Scenario: Password change for logged-in user
    Given I am logged in as "johndoe"
    And I am on the password change page
    When I fill in "current password" with "SecurePass123!"
    And I fill in "new password" with "NewSecurePass456!"
    And I fill in "confirm new password" with "NewSecurePass456!"
    And I click the "Change Password" button
    Then I should see a success message "Password changed successfully"
    And I should be able to login with the new password

  Scenario: All content is user-scoped
    Given user "alice" has created a novel titled "Alice's Adventure"
    And user "bob" has created a novel titled "Bob's Journey"
    When I log in as "alice"
    And I view my novels list
    Then I should see "Alice's Adventure"
    But I should not see "Bob's Journey"


Feature: Initial Views & Infrastructure
  As a developer
  I want basic CRUD views and infrastructure
  So that users can manage their content

  Scenario: Basic CRUD views using Django forms
    Given I am logged in
    When I navigate to any CRUD page
    Then the page should use Django forms
    And the forms should have proper validation
    And the forms should have CSRF protection

  Scenario: Git repository is initialized
    Given the project directory exists
    When I check for Git initialization
    Then a .git directory should exist
    And the repository should have commits
    And the remote should be set to Forgejo

  Scenario: .gitignore is configured for Python/Django
    Given the Git repository exists
    When I check the .gitignore file
    Then it should exclude "*.pyc" files
    And it should exclude "__pycache__" directories
    And it should exclude "db.sqlite3"
    And it should exclude ".env" files
    And it should exclude "media/" directory


# =============================================================================
# Phase 1B: Core Writing Features
# =============================================================================

Feature: Novel Management
  As an author
  I want to manage my novels
  So that I can organize my writing projects

  Scenario: Create a new novel
    Given I am logged in
    And I am on the dashboard
    When I click the "Create New Novel" button
    And I fill in "title" with "My First Novel"
    And I fill in "description" with "A thrilling adventure story"
    And I click the "Save" button
    Then I should see a success message
    And I should see "My First Novel" in my novels list
    And the novel should be saved to the database

  Scenario: Edit novel details
    Given I am logged in
    And I have a novel titled "My First Novel"
    When I navigate to the novel's edit page
    And I change "title" to "My Amazing Novel"
    And I change "description" to "An updated description"
    And I click the "Save" button
    Then I should see a success message
    And the novel title should be updated to "My Amazing Novel"

  Scenario: Archive a novel
    Given I am logged in
    And I have a novel titled "My First Novel"
    When I navigate to the novel's page
    And I click the "Archive" button
    And I confirm the action
    Then the novel should be archived
    And the novel should not appear in my active novels list

  Scenario: List all archived novels
    Given I am logged in
    And I have an archived novel titled "Archived Novel"
    When I navigate to the "Archived Novels" page
    Then I should see "Archived Novel" in the list

  Scenario: Restore a novel from archive
    Given I am logged in
    And I have an archived novel titled "Archived Novel"
    When I navigate to the "Archived Novels" page
    And I click the "Restore" button next to "Archived Novel"
    Then the novel should be restored
    And "Archived Novel" should appear in my active novels list

  Scenario: Delete a novel
    Given I am logged in
    And I have a novel titled "Novel to Delete"
    When I navigate to the novel's page
    And I click the "Delete" button
    And I confirm the deletion
    Then the novel should be permanently deleted
    And "Novel to Delete" should not appear anywhere


Feature: Chapter Management
  As an author
  I want to manage chapters within my novels
  So that I can structure my story

  Scenario: Create a chapter
    Given I am logged in
    And I have a novel titled "My Novel"
    When I navigate to the novel's page
    And I click the "Add Chapter" button
    And I fill in "title" with "Chapter 1: The Beginning"
    And I fill in "summary" with "Our hero's journey starts"
    And I click the "Save" button
    Then I should see "Chapter 1: The Beginning" in the chapter list

  Scenario: Link a chapter to a novel
    Given I am logged in
    And I have a novel titled "My Novel"
    When I create a new chapter
    Then the chapter should be automatically linked to "My Novel"
    And the chapter should appear under "My Novel" in the chapter list

  Scenario: Edit a chapter's details
    Given I am logged in
    And I have a chapter titled "Chapter 1"
    When I navigate to the chapter's edit page
    And I change "title" to "Chapter 1: A New Dawn"
    And I click the "Save" button
    Then the chapter title should be updated

  Scenario: Archive a chapter
    Given I am logged in
    And I have a chapter titled "Chapter 1"
    When I click the "Archive" button on the chapter
    And I confirm the action
    Then the chapter should be archived
    And the chapter should not appear in the active chapter list

  Scenario: List all archived chapters
    Given I am logged in
    And I have an archived chapter titled "Old Chapter"
    When I navigate to the "Archived Chapters" page
    Then I should see "Old Chapter" in the list

  Scenario: Restore a chapter from archive
    Given I am logged in
    And I have an archived chapter titled "Old Chapter"
    When I navigate to the "Archived Chapters" page
    And I click the "Restore" button next to "Old Chapter"
    Then the chapter should be restored to active status

  Scenario: Reorder chapters within a novel
    Given I am logged in
    And I have a novel with chapters in this order:
      | Chapter 1 |
      | Chapter 2 |
      | Chapter 3 |
    When I drag "Chapter 3" to the first position
    Then the chapter order should be:
      | Chapter 3 |
      | Chapter 1 |
      | Chapter 2 |

  Scenario: Delete a chapter
    Given I am logged in
    And I have a chapter titled "Chapter to Delete"
    When I click the "Delete" button on the chapter
    And I confirm the deletion
    Then the chapter should be permanently deleted


Feature: Scene Management
  As an author
  I want to manage scenes within chapters
  So that I can break down my story into manageable pieces

  Scenario: Create a scene
    Given I am logged in
    And I have a chapter titled "Chapter 1"
    When I navigate to the chapter's page
    And I click the "Add Scene" button
    And I fill in "title" with "Opening Scene"
    And I fill in "description" with "The hero wakes up"
    And I click the "Save" button
    Then I should see "Opening Scene" in the scene list

  Scenario: Scene is child of a chapter
    Given I am logged in
    And I have a chapter titled "Chapter 1"
    When I create a scene within the chapter
    Then the scene should be linked to "Chapter 1"
    And the scene should only appear under "Chapter 1"

  Scenario: Change the parent chapter of a scene
    Given I am logged in
    And I have a scene titled "Scene 1" in "Chapter 1"
    And I have another chapter titled "Chapter 2"
    When I edit "Scene 1"
    And I change the parent chapter to "Chapter 2"
    And I save the changes
    Then "Scene 1" should appear under "Chapter 2"
    And "Scene 1" should not appear under "Chapter 1"

  Scenario: Edit a scene's details
    Given I am logged in
    And I have a scene titled "Opening Scene"
    When I navigate to the scene's edit page
    And I change "title" to "Dramatic Opening"
    And I change "description" to "A more exciting start"
    And I click the "Save" button
    Then the scene should be updated

  Scenario: Archive a scene
    Given I am logged in
    And I have a scene titled "Old Scene"
    When I click the "Archive" button on the scene
    And I confirm the action
    Then the scene should be archived

  Scenario: List all archived scenes
    Given I am logged in
    And I have an archived scene titled "Archived Scene"
    When I navigate to the "Archived Scenes" page
    Then I should see "Archived Scene" in the list

  Scenario: Restore a scene from archive
    Given I am logged in
    And I have an archived scene titled "Archived Scene"
    When I navigate to the "Archived Scenes" page
    And I click the "Restore" button next to "Archived Scene"
    Then the scene should be restored to active status

  Scenario: Delete a scene
    Given I am logged in
    And I have a scene titled "Scene to Delete"
    When I click the "Delete" button on the scene
    And I confirm the deletion
    Then the scene should be permanently deleted

  Scenario Outline: Set the status of a scene
    Given I am logged in
    And I have a scene titled "Test Scene"
    When I navigate to the scene's page
    And I change the status to "<status>"
    And I save the changes
    Then the scene status should be "<status>"

    Examples:
      | status        |
      | Not Started   |
      | In Progress   |
      | First Draft   |
      | Needs Review  |
      | Final Draft   |
      | Complete      |


Feature: Markdown Editor
  As an author
  I want to write in markdown
  So that I can format my text efficiently

  Scenario: CodeMirror 6 markdown editor is integrated
    Given I am logged in
    And I am viewing a scene
    Then I should see a CodeMirror editor
    And the editor should support markdown syntax highlighting

  Scenario: Autosave functionality every 30 seconds
    Given I am logged in
    And I am editing a scene
    When I type "This is new content"
    And I wait for 30 seconds
    Then the content should be automatically saved
    And I should see a "Saved" indicator

  Scenario: Autosave on blur
    Given I am logged in
    And I am editing a scene
    When I type "This is new content"
    And I click outside the editor
    Then the content should be automatically saved

  Scenario: Save status indicator
    Given I am logged in
    And I am editing a scene
    Then I should see a save status indicator
    When I type content
    Then the indicator should show "Saving..."
    When the save completes
    Then the indicator should show "Saved"

  Scenario: Markdown preview toggle
    Given I am logged in
    And I am editing a scene with markdown content
    When I click the "Preview" button
    Then I should see a rendered preview of the markdown
    When I click the "Edit" button
    Then I should see the markdown editor again

  Scenario: Keyboard shortcut Ctrl+S for save
    Given I am logged in
    And I am editing a scene
    When I type "New content"
    And I press "Ctrl+S"
    Then the content should be saved immediately

  Scenario: Keyboard shortcut Ctrl+P for preview
    Given I am logged in
    And I am editing a scene
    When I press "Ctrl+P"
    Then the preview mode should toggle

  Scenario: Keyboard shortcut Ctrl+B for bold
    Given I am logged in
    And I am editing a scene
    When I select text "important"
    And I press "Ctrl+B"
    Then the text should be wrapped in "**important**"

  Scenario: Keyboard shortcut Ctrl+I for italic
    Given I am logged in
    And I am editing a scene
    When I select text "emphasis"
    And I press "Ctrl+I"
    Then the text should be wrapped in "*emphasis*"

  Scenario: Keyboard shortcut Esc to exit full screen
    Given I am logged in
    And I am in distraction-free writing mode
    When I press "Esc"
    Then I should exit distraction-free mode


Feature: Navigation
  As an author
  I want to navigate my novel easily
  So that I can move between scenes and chapters efficiently

  Scenario: Scene navigation - next within chapter
    Given I am logged in
    And I am viewing "Scene 1" of "Chapter 1"
    And "Scene 2" exists in "Chapter 1"
    When I click the "Next Scene" button
    Then I should be viewing "Scene 2"

  Scenario: Scene navigation - previous within chapter
    Given I am logged in
    And I am viewing "Scene 2" of "Chapter 1"
    And "Scene 1" exists in "Chapter 1"
    When I click the "Previous Scene" button
    Then I should be viewing "Scene 1"

  Scenario: Chapters displayed in left sidebar
    Given I am logged in
    And I have a novel with multiple chapters
    When I navigate to the novel page
    Then I should see a left sidebar
    And the sidebar should list all chapters

  Scenario: Chapter click displays scene cards dashboard
    Given I am logged in
    And I have a chapter with multiple scenes
    When I click on the chapter in the sidebar
    Then I should see a dashboard of scene cards

  Scenario: Scene card displays title
    Given I am logged in
    And I am viewing scene cards for a chapter
    Then each scene card should display its title

  Scenario: Scene card displays short description
    Given I am logged in
    And I am viewing scene cards for a chapter
    Then each scene card should display its short description

  Scenario: Scene card displays scene status
    Given I am logged in
    And I am viewing scene cards for a chapter
    And a scene has status "In Progress"
    Then the scene card should display "In Progress"

  Scenario: Reorder scenes within chapter using drag and drop
    Given I am logged in
    And I am viewing scene cards for a chapter with scenes:
      | Scene A |
      | Scene B |
      | Scene C |
    When I drag "Scene C" to the first position
    Then the scene order should be:
      | Scene C |
      | Scene A |
      | Scene B |

  Scenario: Breadcrumb trail navigation
    Given I am logged in
    And I am viewing a scene titled "Opening" in "Chapter 1" of "My Novel"
    Then I should see a breadcrumb trail "Dashboard / My Novel / Chapter 1 / Opening"
    When I click "Chapter 1" in the breadcrumb
    Then I should navigate to the Chapter 1 page

  Scenario: Scene cards in right sidebar
    Given I am logged in
    And I am editing a scene
    Then I should see a right sidebar with scene cards

  Scenario: Scroll scene cards in right sidebar
    Given I am logged in
    And I am editing a scene
    And there are many scenes in the chapter
    When I scroll in the right sidebar
    Then I should be able to see all scene cards

  Scenario: Click scene card to open scene
    Given I am logged in
    And I am viewing a chapter with multiple scenes
    When I click on a scene card for "Scene 2"
    Then I should navigate to "Scene 2" for editing


# =============================================================================
# Phase 1C: Planning Tools
# =============================================================================

Feature: Character Management
  As an author
  I want to manage characters
  So that I can keep track of my story's cast

  Scenario: Create a character
    Given I am logged in
    And I am on the characters page
    When I click the "Add Character" button
    And I fill in "name" with "John Smith"
    And I fill in "description" with "The protagonist"
    And I click the "Save" button
    Then I should see "John Smith" in the character list

  Scenario: Edit a character
    Given I am logged in
    And I have a character named "John Smith"
    When I navigate to the character's edit page
    And I change "name" to "Jonathan Smith"
    And I click the "Save" button
    Then the character should be updated

  Scenario: Archive a character
    Given I am logged in
    And I have a character named "John Smith"
    When I click the "Archive" button on the character
    And I confirm the action
    Then the character should be archived

  Scenario: List all archived characters
    Given I am logged in
    And I have an archived character named "Old Character"
    When I navigate to the "Archived Characters" page
    Then I should see "Old Character" in the list

  Scenario: Restore a character from archive
    Given I am logged in
    And I have an archived character named "Old Character"
    When I navigate to the "Archived Characters" page
    And I click the "Restore" button next to "Old Character"
    Then the character should be restored

  Scenario: Delete a character
    Given I am logged in
    And I have a character named "Character to Delete"
    When I click the "Delete" button on the character
    And I confirm the deletion
    Then the character should be permanently deleted


Feature: Location Management
  As an author
  I want to manage locations
  So that I can keep track of settings in my story

  Scenario: Create a location
    Given I am logged in
    And I am on the locations page
    When I click the "Add Location" button
    And I fill in "name" with "The Old Manor"
    And I fill in "description" with "A creepy abandoned house"
    And I click the "Save" button
    Then I should see "The Old Manor" in the location list

  Scenario: Edit a location
    Given I am logged in
    And I have a location named "The Old Manor"
    When I navigate to the location's edit page
    And I change "name" to "The Haunted Manor"
    And I click the "Save" button
    Then the location should be updated

  Scenario: Archive a location
    Given I am logged in
    And I have a location named "The Old Manor"
    When I click the "Archive" button on the location
    And I confirm the action
    Then the location should be archived

  Scenario: List all archived locations
    Given I am logged in
    And I have an archived location named "Old Place"
    When I navigate to the "Archived Locations" page
    Then I should see "Old Place" in the list

  Scenario: Restore a location from archive
    Given I am logged in
    And I have an archived location named "Old Place"
    When I navigate to the "Archived Locations" page
    And I click the "Restore" button next to "Old Place"
    Then the location should be restored

  Scenario: Delete a location
    Given I am logged in
    And I have a location named "Location to Delete"
    When I click the "Delete" button on the location
    And I confirm the deletion
    Then the location should be permanently deleted


Feature: Item Management
  As an author
  I want to manage items
  So that I can track important objects in my story

  Scenario: Create an item
    Given I am logged in
    And I am on the items page
    When I click the "Add Item" button
    And I fill in "name" with "Magic Sword"
    And I fill in "description" with "An ancient blade"
    And I click the "Save" button
    Then I should see "Magic Sword" in the item list

  Scenario: Edit an item
    Given I am logged in
    And I have an item named "Magic Sword"
    When I navigate to the item's edit page
    And I change "name" to "Excalibur"
    And I click the "Save" button
    Then the item should be updated

  Scenario: Archive an item
    Given I am logged in
    And I have an item named "Magic Sword"
    When I click the "Archive" button on the item
    And I confirm the action
    Then the item should be archived

  Scenario: List all archived items
    Given I am logged in
    And I have an archived item named "Old Artifact"
    When I navigate to the "Archived Items" page
    Then I should see "Old Artifact" in the list

  Scenario: Restore an item from archive
    Given I am logged in
    And I have an archived item named "Old Artifact"
    When I navigate to the "Archived Items" page
    And I click the "Restore" button next to "Old Artifact"
    Then the item should be restored

  Scenario: Delete an item
    Given I am logged in
    And I have an item named "Item to Delete"
    When I click the "Delete" button on the item
    And I confirm the deletion
    Then the item should be permanently deleted


Feature: Image Uploads
  As an author
  I want to upload images for characters, locations, and items
  So that I can visualize my story elements

  Scenario: Upload image for character
    Given I am logged in
    And I have a character named "John Smith"
    When I navigate to the character's edit page
    And I click the "Upload Image" button
    And I select a valid JPG file of 2MB
    And I click the "Save" button
    Then the image should be uploaded
    And I should see the image displayed on the character page

  Scenario: Upload image for location
    Given I am logged in
    And I have a location named "The Old Manor"
    When I navigate to the location's edit page
    And I click the "Upload Image" button
    And I select a valid PNG file of 3MB
    And I click the "Save" button
    Then the image should be uploaded
    And I should see the image displayed on the location page

  Scenario: Upload image for item
    Given I am logged in
    And I have an item named "Magic Sword"
    When I navigate to the item's edit page
    And I click the "Upload Image" button
    And I select a valid WEBP file of 1MB
    And I click the "Save" button
    Then the image should be uploaded
    And I should see the image displayed on the item page

  Scenario: Change image on character
    Given I am logged in
    And I have a character named "John Smith" with an existing image
    When I navigate to the character's edit page
    And I click the "Change Image" button
    And I select a new JPG file
    And I click the "Save" button
    Then the old image should be replaced
    And the new image should be displayed

  Scenario: Change image on location
    Given I am logged in
    And I have a location named "The Old Manor" with an existing image
    When I navigate to the location's edit page
    And I upload a new image
    Then the image should be replaced

  Scenario: Change image on item
    Given I am logged in
    And I have an item named "Magic Sword" with an existing image
    When I navigate to the item's edit page
    And I upload a new image
    Then the image should be replaced

  Scenario: Media directory is set up
    Given the Django project is configured
    When I check the settings
    Then a media directory should be configured
    And the media URL should be set

  Scenario: File size limit validation - reject oversized file
    Given I am logged in
    And I am uploading an image for a character
    When I select a file of 6MB
    And I click the "Save" button
    Then I should see an error message "File size must be under 5MB"
    And the file should not be uploaded

  Scenario: File type validation - accept JPG
    Given I am logged in
    And I am uploading an image for a character
    When I select a JPG file
    Then the file should be accepted

  Scenario: File type validation - accept PNG
    Given I am logged in
    And I am uploading an image for a character
    When I select a PNG file
    Then the file should be accepted

  Scenario: File type validation - accept GIF
    Given I am logged in
    And I am uploading an image for a character
    When I select a GIF file
    Then the file should be accepted

  Scenario: File type validation - accept WEBP
    Given I am logged in
    And I am uploading an image for a character
    When I select a WEBP file
    Then the file should be accepted

  Scenario: File type validation - reject invalid type
    Given I am logged in
    And I am uploading an image for a character
    When I select a PDF file
    Then I should see an error message "Only JPG, PNG, GIF, and WEBP files are allowed"
    And the file should not be uploaded


Feature: Word Count System
  As an author
  I want accurate word counts
  So that I can track my writing progress

  Scenario: Calculate word count for scene excluding markdown
    Given I am logged in
    And I have a scene with content:
      """
      # This is a heading
      
      This is **bold** and this is *italic*.
      
      Here is a list:
      - Item 1
      - Item 2
      """
    When the word count is calculated
    Then the word count should be 14
    And markdown syntax should be excluded from the count

  Scenario: Word count rollup for chapters
    Given I am logged in
    And I have a chapter with scenes:
      | Scene 1 | 100 words |
      | Scene 2 | 150 words |
      | Scene 3 | 200 words |
    When I view the chapter
    Then the chapter word count should be 450

  Scenario: Word count rollup for novels
    Given I am logged in
    And I have a novel with chapters:
      | Chapter 1 | 450 words |
      | Chapter 2 | 600 words |
      | Chapter 3 | 350 words |
    When I view the novel
    Then the novel word count should be 1400

  Scenario: Display word count on scene page
    Given I am logged in
    And I am viewing a scene with 500 words
    Then I should see "500 words" displayed

  Scenario: Display word count on chapter page
    Given I am logged in
    And I am viewing a chapter with 1200 words
    Then I should see "1200 words" displayed

  Scenario: Display word count on novel page
    Given I am logged in
    And I am viewing a novel with 5000 words
    Then I should see "5000 words" displayed


# =============================================================================
# Phase 1D: Polish & UI
# =============================================================================

Feature: Frontend Enhancement
  As a user
  I want a modern, responsive interface
  So that I have a pleasant writing experience

  Scenario: HTMX integration for dynamic interactions
    Given I am on any page with dynamic content
    When I interact with HTMX-enabled elements
    Then the page should update without full reload
    And the interaction should feel smooth

  Scenario: Alpine.js for minimal interactivity
    Given I am on a page with interactive components
    When I interact with Alpine.js components
    Then they should respond immediately
    And state should be managed client-side

  Scenario: Tailwind CSS styling
    Given I am on any page
    Then the page should use Tailwind CSS classes
    And the design should be consistent throughout

  Scenario: Clean, uncluttered design system
    Given I am on any page
    Then the interface should be clean and minimal
    And there should be appropriate whitespace
    And colors should follow a consistent palette


Feature: Advanced Features
  As an author
  I want advanced UI features
  So that I can work more efficiently

  Scenario: Drag-and-drop for chapter reordering
    Given I am logged in
    And I am viewing a novel with chapters
    When I drag a chapter to a new position
    Then the chapter should move to that position
    And the order should be saved automatically

  Scenario: Drag-and-drop for scene reordering
    Given I am logged in
    And I am viewing a chapter with scenes
    When I drag a scene to a new position
    Then the scene should move to that position
    And the order should be saved automatically

  Scenario: Distraction-free writing mode
    Given I am logged in
    And I am editing a scene
    When I click the "Distraction-Free Mode" button
    Then all UI elements except the editor should be hidden
    And the editor should expand to full screen

  Scenario: Exit distraction-free mode
    Given I am in distraction-free writing mode
    When I press "Esc"
    Then I should return to normal editing mode
    And all UI elements should be restored

  Scenario: Confirmation prompt for deleting novel
    Given I am logged in
    And I have a novel
    When I click the "Delete" button
    Then I should see a confirmation dialog
    And the dialog should warn about permanent deletion

  Scenario: Confirmation prompt for deleting chapter
    Given I am logged in
    And I have a chapter
    When I click the "Delete" button
    Then I should see a confirmation dialog

  Scenario: Confirmation prompt for deleting scene
    Given I am logged in
    And I have a scene
    When I click the "Delete" button
    Then I should see a confirmation dialog


Feature: Performance & Responsiveness
  As a user
  I want a fast, responsive application
  So that I can work without frustration

  Scenario: Page load time under 1 second
    Given I am logged in
    When I navigate to any page
    Then the page should load in under 1 second
    And initial content should be visible immediately

  Scenario: Responsive design on tablet
    Given I am using a tablet device
    When I access the application
    Then the layout should adapt to tablet screen size
    And all features should remain accessible

  Scenario: Responsive design on desktop
    Given I am using a desktop device
    When I access the application
    Then the layout should use the full screen effectively
    And the sidebar should be visible

  Scenario: Test with real novel content
    Given I have imported a complete novel with 50,000 words
    And the novel has 20 chapters with 100 scenes
    When I navigate through the content
    Then all pages should load quickly
    And the editor should handle long scenes smoothly


# =============================================================================
# UI Pages
# =============================================================================

Feature: Dashboard/Home Page
  As a user
  I want a comprehensive dashboard
  So that I can overview all my writing projects

  Scenario: Display list of user's novels
    Given I am logged in
    And I have created 3 novels
    When I navigate to the dashboard
    Then I should see all 3 novels listed

  Scenario: Show quick stats per novel
    Given I am logged in
    And I have a novel with 10,000 words in 5 chapters
    When I view the dashboard
    Then I should see "10,000 words" for that novel
    And I should see "5 chapters"

  Scenario: Show last modified date
    Given I am logged in
    And I last edited "My Novel" yesterday
    When I view the dashboard
    Then I should see "Last modified: yesterday"

  Scenario: Create New Novel button
    Given I am logged in
    And I am on the dashboard
    Then I should see a "Create New Novel" button
    When I click it
    Then I should navigate to the novel creation form

  Scenario: Search novels by title
    Given I am logged in
    And I have novels titled "Adventure Story" and "Mystery Novel"
    When I search for "Adventure"
    Then I should see "Adventure Story"
    But I should not see "Mystery Novel"

  Scenario: Filter novels by title
    Given I am logged in
    And I have multiple novels
    When I type in the filter field
    Then the novel list should filter in real-time


Feature: Novel Overview Page
  As a user
  I want a detailed novel overview
  So that I can manage a specific novel

  Scenario: Display novel title and description
    Given I am logged in
    And I have a novel titled "My Adventure" with description "A thrilling tale"
    When I navigate to the novel overview page
    Then I should see "My Adventure" as the title
    And I should see "A thrilling tale" as the description

  Scenario: Show total word count
    Given I am logged in
    And my novel has a total of 25,000 words
    When I view the novel overview
    Then I should see "25,000 words"

  Scenario: Display chapter list with individual word counts
    Given I am logged in
    And my novel has chapters:
      | Chapter 1 | 5,000 words  |
      | Chapter 2 | 7,500 words  |
      | Chapter 3 | 4,200 words  |
    When I view the novel overview
    Then I should see each chapter with its word count

  Scenario: Quick access tabs for different sections
    Given I am logged in
    And I am on the novel overview page
    Then I should see tabs for "Chapters", "Characters", "Locations", "Items"
    When I click the "Characters" tab
    Then I should see the characters section

  Scenario: Add Chapter button
    Given I am logged in
    And I am on the novel overview page
    Then I should see an "Add Chapter" button
    When I click it
    Then I should navigate to the chapter creation form

  Scenario: Settings/edit novel details interface
    Given I am logged in
    And I am on the novel overview page
    When I click the "Settings" button
    Then I should navigate to the novel edit page


Feature: Chapter View
  As a user
  I want a detailed chapter view
  So that I can manage scenes within a chapter

  Scenario: Display chapter title and summary
    Given I am logged in
    And I have a chapter titled "The Beginning" with summary "Our story starts"
    When I navigate to the chapter view
    Then I should see "The Beginning"
    And I should see "Our story starts"

  Scenario: Show scene corkboard with word counts
    Given I am logged in
    And I have a chapter with scenes:
      | Scene 1 | 800 words  |
      | Scene 2 | 1200 words |
      | Scene 3 | 600 words  |
    When I view the chapter
    Then I should see a corkboard layout of scenes
    And each scene card should show its word count

  Scenario: Display total chapter word count
    Given I am logged in
    And my chapter has 5,000 words total
    When I view the chapter
    Then I should see "5,000 words"

  Scenario: Add Scene button
    Given I am logged in
    And I am viewing a chapter
    Then I should see an "Add Scene" button
    When I click it
    Then I should navigate to the scene creation form

  Scenario: Scene reordering interface
    Given I am logged in
    And I am viewing a chapter with multiple scenes
    When I drag a scene to reorder it
    Then the scenes should reorder visually
    And the new order should be saved


Feature: Writing View
  As an author
  I want a focused writing interface
  So that I can write without distractions

  Scenario: Full-screen capable layout
    Given I am logged in
    And I am in the writing view
    When I click the "Full Screen" button
    Then the editor should expand to full screen
    And all other UI should be hidden

  Scenario: Inline editable scene title
    Given I am logged in
    And I am viewing a scene
    When I click on the scene title
    Then the title should become editable
    When I change the title and press Enter
    Then the title should be updated

  Scenario: Markdown editor integration
    Given I am logged in
    And I am in the writing view
    Then I should see a markdown editor
    And it should have syntax highlighting

  Scenario: Word count indicator
    Given I am logged in
    And I am writing a scene
    Then I should see a live word count indicator
    When I type more words
    Then the word count should update in real-time

  Scenario: Scene navigation controls
    Given I am logged in
    And I am viewing a scene in a chapter with multiple scenes
    Then I should see "Previous Scene" and "Next Scene" buttons
    When I click "Next Scene"
    Then I should navigate to the next scene

  Scenario: Save status indicator
    Given I am logged in
    And I am writing
    Then I should see a save status indicator
    When I type
    Then it should show "Saving..."
    When the save completes
    Then it should show "Saved"


# =============================================================================
# Security Implementation
# =============================================================================

Feature: Security
  As a developer
  I want robust security measures
  So that user data is protected

  Scenario: CSRF protection is enabled
    Given the Django application is running
    When I submit any form
    Then the form should include a CSRF token
    And submissions without CSRF token should be rejected

  Scenario: User content scoping - users see only their content
    Given user "alice" has a novel
    And user "bob" has a novel
    When "alice" logs in
    Then "alice" should only see her own novels
    And "alice" should not be able to access "bob's" novels

  Scenario: Attempt to access another user's content via URL
    Given user "alice" has a novel with ID 123
    And user "bob" is logged in
    When "bob" tries to access novel ID 123 directly via URL
    Then "bob" should receive a 403 Forbidden error
    Or "bob" should be redirected to their dashboard

  Scenario: File upload validation for size
    Given I am uploading an image
    When the file is over 5MB
    Then the upload should be rejected
    And I should see an error message

  Scenario: File upload validation for type
    Given I am uploading a file
    When the file is not JPG, PNG, GIF, or WEBP
    Then the upload should be rejected
    And I should see an error message

  Scenario: XSS prevention in templates
    Given I am logged in
    And I create content with HTML: "<script>alert('XSS')</script>"
    When I view the content
    Then the HTML should be escaped
    And the script should not execute

  Scenario: Secure password storage
    Given I register with password "SecurePass123!"
    When I check the database
    Then the password should be hashed
    And the plaintext password should not be stored


# =============================================================================
# Accessibility
# =============================================================================

Feature: Accessibility
  As a user with accessibility needs
  I want the application to be accessible
  So that I can use it effectively

  Scenario: Semantic HTML throughout
    Given I am on any page
    When I inspect the HTML
    Then it should use semantic elements like <nav>, <main>, <article>
    And headings should follow a logical hierarchy

  Scenario: Keyboard navigation support
    Given I am on any page
    When I use only the keyboard
    Then I should be able to navigate to all interactive elements
    And I should be able to activate buttons and links with Enter

  Scenario: Proper focus management
    Given I am navigating with keyboard
    When I tab through the page
    Then focus should move in a logical order
    And focused elements should have visible focus indicators

  Scenario: Readable contrast ratios
    Given I am on any page
    When I check the color contrast
    Then text should have a minimum contrast ratio of 4.5:1
    And large text should have a minimum contrast ratio of 3:1


# =============================================================================
# Final Testing & Success Criteria
# =============================================================================

Feature: Integration Testing
  As a QA tester
  I want to verify all features work together
  So that the application is ready for use

  Scenario: User registration, login, and account management workflow
    Given I am a new user
    When I register an account
    And I log in
    And I change my password
    And I log out
    And I log in with the new password
    Then all steps should complete successfully

  Scenario: Creating multiple novels
    Given I am logged in
    When I create 5 different novels
    Then all 5 should appear in my dashboard
    And each should be independently manageable

  Scenario: Creating chapters and scenes within novels
    Given I am logged in
    And I have a novel
    When I create 3 chapters
    And I create 5 scenes in each chapter
    Then all chapters and scenes should be properly structured

  Scenario: Writing and editing markdown content
    Given I am logged in
    And I have a scene
    When I write markdown content with headings, lists, and formatting
    And I save the content
    And I reload the page
    Then the content should be preserved exactly

  Scenario: Word counts roll up correctly
    Given I am logged in
    And I have a novel with:
      | Chapter 1 | Scene 1 | 500 words  |
      | Chapter 1 | Scene 2 | 300 words  |
      | Chapter 2 | Scene 1 | 700 words  |
    Then Chapter 1 should show 800 words
    And Chapter 2 should show 700 words
    And the novel should show 1500 words

  Scenario: Character/location/item database management
    Given I am logged in
    When I create characters, locations, and items
    And I edit them
    And I archive some
    And I restore archived ones
    And I delete some
    Then all operations should work correctly

  Scenario: Image uploads for planning entities
    Given I am logged in
    When I upload images for characters
    And I upload images for locations
    And I upload images for items
    Then all images should be stored and displayed correctly

  Scenario: Interface is clean and uncluttered
    Given I am using the application
    When I navigate through different pages
    Then the interface should feel minimal and focused
    And there should be no unnecessary visual clutter

  Scenario: Application stability with real content
    Given I have imported a novel with 50,000 words
    And the novel has 20 chapters
    And each chapter has 10 scenes
    When I navigate, edit, and manage the content
    Then the application should remain responsive and stable
    And no errors should occur

  Scenario: PRIMARY SUCCESS - Use app to work on novel
    Given I am an author working on my novel
    When I use the app to write and edit Act 1
    And I identify and fix plot issues
    Then the app should support my creative process effectively
    And I should be able to complete my writing goals
