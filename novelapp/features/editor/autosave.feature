@editor @critical @phase1b
Feature: Autosave
  As an author
  I want my work to be automatically saved
  So that I don't lose my writing

  Background:
    Given I am logged in
    And I am editing a scene

  @timer @slow
  Scenario: Autosave every 30 seconds
    When I type "This is new content"
    And I wait for 30 seconds
    Then the content should be automatically saved
    And I should see a "Saved" indicator

  @blur @fast
  Scenario: Autosave on blur
    When I type "This is new content"
    And I click outside the editor
    Then the content should be automatically saved
    And I should see a "Saved" indicator

  @indicator
  Scenario: Save status indicator updates
    Given I am viewing the save status indicator
    When I type content
    Then the indicator should show "Saving..."
    When the save completes
    Then the indicator should show "Saved"
    And the timestamp should be updated

  @persistence
  Scenario: Content persists after autosave
    When I type "Important content"
    And I wait for autosave to complete
    And I refresh the page
    Then the content should still be "Important content"

  @error_handling
  Scenario: Handle autosave failure
    Given the server is unavailable
    When I type content
    And autosave attempts to save
    Then I should see an error indicator
    And the content should remain in the editor
    And autosave should retry after a delay

  @multiple_changes
  Scenario: Autosave batches rapid changes
    When I type "First line"
    And I immediately type "Second line"
    And I immediately type "Third line"
    Then only one save request should be made
    And all changes should be included
