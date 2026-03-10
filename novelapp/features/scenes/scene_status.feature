@scenes @phase1b @workflow
Feature: Scene Status Management
  As an author
  I want to set the status of my scenes
  So that I can track my writing progress

  Background:
    Given I am logged in
    And I have a scene titled "Test Scene"

  @happy_path
  Scenario Outline: Set scene to different statuses
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

  @workflow
  Scenario: Track progress through writing workflow
    Given the scene status is "Not Started"
    When I navigate to the scene's page
    And I change the status to "In Progress"
    And I save the changes
    When I navigate to the scene's page
    And I write some content
    And I change the status to "First Draft"
    And I save the changes
    Then the status progression should be recorded

  @visual
  Scenario: Status is displayed on scene card
    Given the scene status is "In Progress"
    When I view the chapter's scene cards
    Then the scene card should display "In Progress"
    And the status should be visually distinct

  @filter
  Scenario: Filter scenes by status
    Given I have multiple scenes with different statuses:
      | title   | status      |
      | Scene 1 | In Progress |
      | Scene 2 | Complete    |
      | Scene 3 | Not Started |
    When I filter by status "In Progress"
    Then I should only see "Scene 1"
