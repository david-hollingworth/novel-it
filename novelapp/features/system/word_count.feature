@system @critical @phase1c
Feature: Word Count System
  As an author
  I want accurate word counts
  So that I can track my writing progress

  Background:
    Given I am logged in

  @calculation @fast
  Scenario: Calculate word count for scene excluding markdown
    Given I have a scene with content:
      """
      # This is a heading
      
      This is **bold** and this is *italic*.
      
      Here is a list:
      - Item 1
      - Item 2
      """
    When the word count is calculated
    Then the word count should be 14
    And markdown syntax should be excluded from the count

  @calculation
  Scenario: Word count excludes only markdown syntax
    Given I have a scene with content:
      """
      The **hero** said, "I will go."
      """
    When the word count is calculated
    Then the word count should be 7
    And the bold markers should not be counted

  @rollup
  Scenario: Word count rollup for chapters
    Given I have a chapter with scenes:
      | Scene 1 | 100 words |
      | Scene 2 | 150 words |
      | Scene 3 | 200 words |
    When I view the chapter
    Then the chapter word count should be 450

  @rollup
  Scenario: Word count rollup for novels
    Given I have a novel with chapters:
      | Chapter 1 | 450 words |
      | Chapter 2 | 600 words |
      | Chapter 3 | 350 words |
    When I view the novel
    Then the novel word count should be 1400

  @display
  Scenario: Display word count on scene page
    Given I am viewing a scene with 500 words
    Then I should see "500 words" displayed

  @display
  Scenario: Display word count on chapter page
    Given I am viewing a chapter with 1200 words
    Then I should see "1200 words" displayed

  @display
  Scenario: Display word count on novel page
    Given I am viewing a novel with 5000 words
    Then I should see "5000 words" displayed

  @realtime
  Scenario: Word count updates in real-time while typing
    Given I am editing a scene
    When I type "Hello world this is a test"
    Then the word count should update to 6
    When I type more words
    Then the word count should update immediately

  @edge_cases
  Scenario: Handle empty content
    Given I have a scene with no content
    When the word count is calculated
    Then the word count should be 0

  @edge_cases
  Scenario: Handle content with only markdown
    Given I have a scene with content "**  **"
    When the word count is calculated
    Then the word count should be 0

  @accuracy
  Scenario: Count hyphenated words correctly
    Given I have a scene with content "mother-in-law self-evident"
    When the word count is calculated
    Then the word count should be 2

  @accuracy
  Scenario: Count contractions correctly
    Given I have a scene with content "don't can't won't"
    When the word count is calculated
    Then the word count should be 3
