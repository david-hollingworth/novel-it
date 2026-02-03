Feature: Chapter Management
  As an author
  I want to manage chapters within my novels
  So that I can structure my story

  Scenario: Create a chapter
    Given I am logged in
    And I have a novel titled "My Novel"
    When I navigate to the novel's page
    And I click the "Add Chapter" button
    And I fill in "title" with "Chapter 1: The Beginning"
    And I fill in "summary" with "Our hero's journey starts"
    And I click the "Save" button
    Then I should see "Chapter 1: The Beginning" in the chapter list

  Scenario: Link a chapter to a novel
    Given I am logged in
    And I have a novel titled "My Novel"
    When I create a new chapter
    Then the chapter should be automatically linked to "My Novel"
    And the chapter should appear under "My Novel" in the chapter list

  Scenario: Edit a chapter's details
    Given I am logged in
    And I have a chapter titled "Chapter 1"
    When I navigate to the chapter's edit page
    And I change "title" to "Chapter 1: A New Dawn"
    And I click the "Save" button
    Then the chapter title should be updated

  Scenario: Archive a chapter
    Given I am logged in
    And I have a chapter titled "Chapter 1"
    When I click the "Archive" button on the chapter
    And I confirm the action
    Then the chapter should be archived
    And the chapter should not appear in the active chapter list

  Scenario: List all archived chapters
    Given I am logged in
    And I have an archived chapter titled "Old Chapter"
    When I navigate to the "Archived Chapters" page
    Then I should see "Old Chapter" in the list

  Scenario: Restore a chapter from archive
    Given I am logged in
    And I have an archived chapter titled "Old Chapter"
    When I navigate to the "Archived Chapters" page
    And I click the "Restore" button next to "Old Chapter"
    Then the chapter should be restored to active status

  Scenario: Reorder chapters within a novel
    Given I am logged in
    And I have a novel with chapters in this order:
      | Chapter 1 |
      | Chapter 2 |
      | Chapter 3 |
    When I drag "Chapter 3" to the first position
    Then the chapter order should be:
      | Chapter 3 |
      | Chapter 1 |
      | Chapter 2 |

  Scenario: Delete a chapter
    Given I am logged in
    And I have a chapter titled "Chapter to Delete"
    When I click the "Delete" button on the chapter
    And I confirm the deletion
    Then the chapter should be permanently deleted
