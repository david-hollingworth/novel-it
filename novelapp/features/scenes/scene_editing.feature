@scenes @phase1b
Feature: Scene Editing
  As an author
  I want to edit my scenes
  So that I can update their titles, notes, and status

  Background:
    Given I am logged in
    And I have a novel titled "My Novel"
    And the novel has a chapter titled "Chapter 1"
    And "Chapter 1" has a scene titled "Opening Scene"

  @happy_path
  Scenario: Successfully edit a scene title
    Given I am viewing the scene "Opening Scene"
    When I click the "Edit Scene" button
    And I change "title" to "Revised Opening"
    And I click the "Save Changes" button
    Then I should see a success message
    And I should see "Revised Opening" in the scene list

  @validation @error_handling
  Scenario: Cannot save a scene with an empty title
    Given I am viewing the scene "Opening Scene"
    When I click the "Edit Scene" button
    And I clear the "title" field
    And I click the "Save Changes" button
    Then I should see an error message "Title is required"

  @happy_path
  Scenario: Archive a scene
    Given I am viewing the scene "Opening Scene"
    When I click the "Archive" button on the scene
    And I confirm the action
    Then the scene should be archived
    And "Opening Scene" should not appear in the chapter's scene list

  @happy_path
  Scenario: Restore an archived scene
    Given "Opening Scene" is archived
    When I navigate to the "Archived Scenes" page for "Chapter 1"
    And I click the "Restore" button next to "Opening Scene"
    And I confirm the action
    Then "Opening Scene" should appear in the chapter's scene list

  @happy_path
  Scenario: Permanently delete a scene
    Given I am viewing the scene "Opening Scene"
    When I click the "Delete" button on the scene
    And I confirm the deletion
    Then "Opening Scene" should be permanently deleted
