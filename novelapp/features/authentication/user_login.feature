@authentication @critical @phase1a
Feature: User Login
  As a registered user
  I want to log in to my account
  So that I can access my novels

  Background:
    Given I have a registered account with username "johndoe" and password "SecurePass123!"

  @happy_path
  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I fill in "username" with "johndoe"
    And I fill in "password" with "SecurePass123!"
    And I click the "Login" button
    Then I should be logged in
    And I should be redirected to the dashboard

  @error_handling
  Scenario: Login with invalid password
    Given I am on the login page
    When I fill in "username" with "johndoe"
    And I fill in "password" with "WrongPassword"
    And I click the "Login" button
    Then I should see an error message "Invalid username or password"
    And I should remain on the login page
    And I should not be logged in

  @error_handling
  Scenario: Login with non-existent username
    Given I am on the login page
    When I fill in "username" with "nonexistent"
    And I fill in "password" with "SomePassword123!"
    And I click the "Login" button
    Then I should see an error message "Invalid username or password"
    And I should remain on the login page

  @error_handling
  Scenario: Login with empty credentials
    Given I am on the login page
    When I click the "Login" button
    Then I should see validation errors
    And I should remain on the login page

  @security
  Scenario: Access protected page without login
    Given I am not logged in
    When I try to access the dashboard
    Then I should be redirected to the login page
