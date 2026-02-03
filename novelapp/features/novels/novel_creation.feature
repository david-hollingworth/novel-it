@novels @critical @phase1b
Feature: Novel Creation
  As an author
  I want to create a new novel
  So that I can start writing my story

  Background:
    Given I am logged in
    And I am on the dashboard

  @happy_path
  Scenario: Successfully create a novel
    When I click the "Create New Novel" button
    And I fill in "title" with "My First Novel"
    And I fill in "description" with "A thrilling adventure story"
    And I click the "Save" button
    Then I should see a success message
    And I should see "My First Novel" in my novels list
    And the novel should be saved to the database
    And the novel should belong to the current user

  @validation @error_handling
  Scenario: Create novel with empty title
    When I click the "Create New Novel" button
    And I fill in "description" with "A story without a title"
    And I click the "Save" button
    Then I should see an error message "Title is required"
    And no novel should be created

  @validation
  Scenario: Create novel with only title (description optional)
    When I click the "Create New Novel" button
    And I fill in "title" with "Minimalist Novel"
    And I click the "Save" button
    Then I should see a success message
    And "Minimalist Novel" should be created successfully

  @multiple_users @security
  Scenario: Novel is only visible to creator
    Given user "alice" has created a novel titled "Alice's Adventure"
    When I view my novels list
    Then I should not see "Alice's Adventure"
    And I should only see my own novels
