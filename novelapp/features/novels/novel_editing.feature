@novels @phase1b
Feature: Novel Editing
  As an author
  I want to edit my novel details
  So that I can update information as my story evolves

  Background:
    Given I am logged in
    And I have a novel titled "My First Novel" with description "Original description"

  @happy_path
  Scenario: Successfully edit novel details
    When I navigate to the novel's edit page
    And I change "title" to "My Amazing Novel"
    And I change "description" to "An updated description"
    And I click the "Save" button
    Then I should see a success message
    And the novel title should be updated to "My Amazing Novel"
    And the novel description should be updated to "An updated description"

  @validation @error_handling
  Scenario: Edit novel with empty title
    When I navigate to the novel's edit page
    And I clear the "title" field
    And I click the "Save" button
    Then I should see an error message "Title is required"
    And the novel should not be updated

  @security
  Scenario: Cannot edit another user's novel
    Given user "bob" has a novel titled "Bob's Novel"
    When I try to access the edit page for "Bob's Novel"
    Then I should receive a 403 Forbidden error
    And I should be redirected to my dashboard

  @cancel
  Scenario: Cancel editing novel
    When I navigate to the novel's edit page
    And I change "title" to "Changed Title"
    And I click the "Cancel" button
    Then the novel title should remain "My First Novel"
    And I should be returned to the novel page
