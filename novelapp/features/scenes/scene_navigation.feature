@scenes @phase1b
Feature: Scene Navigation
  As an author
  I want to navigate between scenes
  So that I can move through my chapter while writing

  Background:
    Given I am logged in
    And I have a novel titled "My Novel"
    And the novel has a chapter titled "Chapter 1"
    And "Chapter 1" has scenes:
      | title   |
      | Scene 1 |
      | Scene 2 |
      | Scene 3 |

  @happy_path
  Scenario: Navigate to the next scene
    Given I am on the editor for "Scene 1"
    When I click the "Next Scene" button
    Then I should be on the editor for "Scene 2"

  @happy_path
  Scenario: Navigate to the previous scene
    Given I am on the editor for "Scene 2"
    When I click the "Previous Scene" button
    Then I should be on the editor for "Scene 1"

  @edge_case
  Scenario: No previous scene button on first scene
    Given I am on the editor for "Scene 1"
    Then I should not see a "Previous Scene" button

  @edge_case
  Scenario: No next scene button on last scene
    Given I am on the editor for "Scene 3"
    Then I should not see a "Next Scene" button
