@scenes @phase1b @requires_browser
Feature: Scene Reordering
  As an author
  I want to reorder scenes within a chapter
  So that I can restructure my story

  Background:
    Given I am logged in
    And I have a novel titled "My Novel"
    And the novel has a chapter titled "Chapter 1"
    And "Chapter 1" has scenes:
      | title   |
      | Scene A |
      | Scene B |
      | Scene C |

  @happy_path
  Scenario: Reorder scenes via API
    When I reorder the scenes in "Chapter 1" to:
      | title   |
      | Scene C |
      | Scene A |
      | Scene B |
    Then the scene order should be:
      | title   |
      | Scene C |
      | Scene A |
      | Scene B |

  @happy_path
  Scenario: Move a scene to the first position
    When I move "Scene C" to position 1 in "Chapter 1"
    Then "Scene C" should be first in the scene list
