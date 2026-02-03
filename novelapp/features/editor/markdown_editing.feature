@editor @critical @phase1b @requires_browser
Feature: Markdown Editing
  As an author
  I want to write in markdown
  So that I can format my text efficiently

  Background:
    Given I am logged in
    And I am viewing a scene

  @integration
  Scenario: CodeMirror 6 markdown editor is integrated
    Then I should see a CodeMirror editor
    And the editor should support markdown syntax highlighting

  @formatting
  Scenario: Apply bold formatting
    When I type "This is important text"
    And I select the word "important"
    And I press "Ctrl+B"
    Then the text should become "This is **important** text"

  @formatting
  Scenario: Apply italic formatting
    When I type "This needs emphasis"
    And I select the word "emphasis"
    And I press "Ctrl+I"
    Then the text should become "This needs *emphasis*"

  @formatting
  Scenario: Create headings
    When I type "# Main Title"
    Then the text should be highlighted as a heading
    When I type a new line and enter "## Subheading"
    Then both should be highlighted appropriately

  @formatting
  Scenario: Create lists
    When I type:
      """
      - First item
      - Second item
      - Third item
      """
    Then the editor should recognize it as a list
    And the formatting should be applied

  @code_blocks
  Scenario: Create code blocks
    When I type:
      """
      ```python
      def hello():
          print("Hello, world!")
      ```
      """
    Then the code block should be syntax highlighted

  @links
  Scenario: Insert links
    When I type "[Click here](https://example.com)"
    Then it should be recognized as a markdown link
    And the link syntax should be highlighted
