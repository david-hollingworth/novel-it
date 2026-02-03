@authentication @critical @phase1a
Feature: User Registration
  As a new user
  I want to register for an account
  So that I can start writing my novel

  Background:
    Given I am on the registration page

  @happy_path
  Scenario: Successful registration with valid details
    When I fill in "username" with "johndoe"
    And I fill in "email" with "john@example.com"
    And I fill in "password" with "SecurePass123!"
    And I fill in "confirm password" with "SecurePass123!"
    And I click the "Register" button
    Then I should see a success message
    And I should be redirected to the dashboard
    And a new user account should be created in the database

  @validation @error_handling
  Scenario: Registration with invalid email
    When I fill in "username" with "johndoe"
    And I fill in "email" with "invalid-email"
    And I fill in "password" with "SecurePass123!"
    And I click the "Register" button
    Then I should see an error message "Enter a valid email address"
    And no user account should be created

  @validation @error_handling
  Scenario: Registration with duplicate username
    Given a user exists with username "johndoe"
    When I fill in "username" with "johndoe"
    And I fill in "email" with "different@example.com"
    And I fill in "password" with "SecurePass123!"
    And I click the "Register" button
    Then I should see an error message "A user with that username already exists"
    And no new user account should be created

  @validation @error_handling
  Scenario: Registration with mismatched passwords
    When I fill in "username" with "johndoe"
    And I fill in "email" with "john@example.com"
    And I fill in "password" with "SecurePass123!"
    And I fill in "confirm password" with "DifferentPass456!"
    And I click the "Register" button
    Then I should see an error message "The two password fields didn't match"
    And no user account should be created

  @validation @error_handling
  Scenario: Registration with weak password
    When I fill in "username" with "johndoe"
    And I fill in "email" with "john@example.com"
    And I fill in "password" with "123"
    And I click the "Register" button
    Then I should see an error message about password strength
    And no user account should be created
