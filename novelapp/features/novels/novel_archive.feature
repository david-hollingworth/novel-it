@novels @critical @phase1b
Feature: Novel Archiving
  As an author
  I want to archive a novel
  So that I can hide it from my collection
  And I can retrieve it later

  Background:
    Given I am logged in
    And I am on the dashboard
    And I have a novel titled "My Novel"

  @happy_path
  Scenario: Archive a novel
    When I click the "Archive" button on "My Novel"
    And I confirm the archiving
    Then I should not see "My Novel" in the novel list
    And I should see "My Novel" in the archived novel list

  @sad_path
  Scenario: Cancel archiving of a novel
    When I click the "Archive" button on "My Novel"
    And I cancel the archiving
    Then I should see "My Novel" in the novel list
    And I should not see "My Novel" in the archived novel list

  @edge_case
  Scenario: Archive a novel with chapters
    Given I have a chapter titled "Chapter 1" in "My Novel"
    When I click the "Archive" button on "My Novel"
    And I confirm the archiving
    Then I should not see "My Novel" in the novel list
    And I should see "My Novel" in the archived novel list

  @edge_case
  Scenario: Archive a novel with chapters and scenes
    Given I have a chapter titled "Chapter 1" in "My Novel"
    And I have a scene titled "Scene 1" in "Chapter 1"
    When I click the "Archive" button on "My Novel"
    And I confirm the archiving
    Then I should not see "My Novel" in the novel list
    And I should see "My Novel" in the archived novel list

  @happy_path
  Scenario: Unarchive a novel
    Given I have a novel titled "My Novel" in the archived novel list
    When I click the "Unarchive" button on "My Novel"
    And I confirm the unarchiving
    Then I should see "My Novel" in the novel list
    And I should not see "My Novel" in the archived novel list

  @sad_path
  Scenario: Cancel unarchiving of a novel
    Given I have a novel titled "My Novel" in the archived novel list
    When I click the "Unarchive" button on "My Novel"
    And I cancel the unarchiving
    Then I should see "My Novel" in the archived novel list
    And I should not see "My Novel" in the novel list

  @edge_case
  Scenario: Unarchive a novel with chapters
    Given I have a novel titled "My Novel" in the archived novel list
    And I have a chapter titled "Chapter 1" in "My Novel"
    When I click the "Unarchive" button on "My Novel"
    And I confirm the unarchiving
    Then I should see "My Novel" in the novel list
    And I should not see "My Novel" in the archived novel list
    And I should see "Chapter 1" in the chapter list

  @edge_case
  Scenario: Unarchive a novel with chapters and scenes
    Given I have a novel titled "My Novel" in the archived novel list
    And I have a chapter titled "Chapter 1" in "My Novel"
    And I have a scene titled "Scene 1" in "Chapter 1"
    When I click the "Unarchive" button on "My Novel"
    And I confirm the unarchiving
    Then I should see "My Novel" in the novel list
    And I should not see "My Novel" in the archived novel list
    And I should see "Chapter 1" in the chapter list
    And I should see "Scene 1" in the scene list
