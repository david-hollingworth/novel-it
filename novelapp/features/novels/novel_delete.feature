@novels @critical @phase1b
Feature: Novel Deletion
  As an author
  I want to delete a novel
  So that I can remove it from my collection

  Background:
    Given I am logged in
    And I am on the dashboard
    And I have a novel titled "My Novel"

  @happy_path
  Scenario: Delete a novel
    When I click the "Delete" button on "My Novel"
    And I confirm the deletion
    Then I should not see "My Novel" in the novel list

  @sad_path
  Scenario: Cancel deletion of a novel
    When I click the "Delete" button on "My Novel"
    And I cancel the deletion
    Then I should see "My Novel" in the novel list

  @edge_case
  Scenario: Delete a novel with chapters
    Given I have a chapter titled "Chapter 1" in "My Novel"
    When I click the "Delete" button on "My Novel"
    And I confirm the deletion
    Then I should not see "My Novel" in the novel list
    And I should not see "Chapter 1" in the chapter list

  @edge_case
  Scenario: Delete a novel with chapters and scenes
    Given I have a chapter titled "Chapter 1" in "My Novel"
    And I have a scene titled "Scene 1" in "Chapter 1"
    When I click the "Delete" button on "My Novel"
    And I confirm the deletion
    Then I should not see "My Novel" in the novel list
    And I should not see "Chapter 1" in the chapter list
    And I should not see "Scene 1" in the scene list
