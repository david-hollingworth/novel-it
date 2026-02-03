@authentication @phase1a
Feature: User Logout
  As a logged-in user
  I want to log out of my account
  So that my work remains secure

  @happy_path
  Scenario: Successful logout
    Given I am logged in as "johndoe"
    And I am on the dashboard
    When I click the "Logout" button
    Then I should be logged out
    And I should be redirected to the login page
    And I should not be able to access protected pages
