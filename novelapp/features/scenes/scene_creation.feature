@scenes @critical @phase1b
Feature: Scene Creation
  As an author
  I want to create scenes within chapters
  So that I can break down my story into manageable pieces

  Background:
    Given I am logged in
    And I have a novel titled "My Novel"
    And the novel has a chapter titled "Chapter 1"

  @happy_path
  Scenario: Successfully create a scene
    Given I am viewing "Chapter 1"
    When I click the "Add Scene" button
    And I fill in "title" with "Opening Scene"
    And I fill in "description" with "The hero wakes up"
    And I click the "Save" button
    Then I should see a success message
    And I should see "Opening Scene" in the scene list
    And the scene should be linked to "Chapter 1"

  @validation @error_handling
  Scenario: Create scene with empty title
    Given I am viewing "Chapter 1"
    When I click the "Add Scene" button
    And I fill in "description" with "A scene without a title"
    And I click the "Save" button
    Then I should see an error message "Title is required"
    And no scene should be created

  @relationship
  Scenario: Scene is correctly associated with parent chapter
    Given I am viewing "Chapter 1"
    When I create a scene titled "Test Scene"
    Then the scene should be a child of "Chapter 1"
    And the scene should only appear under "Chapter 1"

  @ordering
  Scenario: New scenes are added at the end
    Given "Chapter 1" has scenes:
      | Scene 1 |
      | Scene 2 |
    When I create a new scene titled "Scene 3"
    Then the scene order should be:
      | Scene 1 |
      | Scene 2 |
      | Scene 3 |

  @fast
  Scenario: Create multiple scenes quickly
    Given I am viewing "Chapter 1"
    When I create scenes with titles:
      | Opening     |
      | Rising      |
      | Climax      |
      | Resolution  |
    Then all 4 scenes should be created
    And they should appear in the correct order
