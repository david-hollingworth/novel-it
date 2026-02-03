@authentication @phase1a
Feature: Password Management
  As a registered user
  I want to manage my password
  So that I can keep my account secure

  Background:
    Given I am logged in as "johndoe"
    And my current password is "SecurePass123!"

  @happy_path
  Scenario: Successfully change password
    Given I am on the password change page
    When I fill in "current password" with "SecurePass123!"
    And I fill in "new password" with "NewSecurePass456!"
    And I fill in "confirm new password" with "NewSecurePass456!"
    And I click the "Change Password" button
    Then I should see a success message "Password changed successfully"
    And I should be able to login with the new password

  @validation @error_handling
  Scenario: Change password with incorrect current password
    Given I am on the password change page
    When I fill in "current password" with "WrongPassword"
    And I fill in "new password" with "NewSecurePass456!"
    And I fill in "confirm new password" with "NewSecurePass456!"
    And I click the "Change Password" button
    Then I should see an error message "Your old password was entered incorrectly"
    And my password should not be changed

  @validation @error_handling
  Scenario: Change password with mismatched new passwords
    Given I am on the password change page
    When I fill in "current password" with "SecurePass123!"
    And I fill in "new password" with "NewSecurePass456!"
    And I fill in "confirm new password" with "DifferentPass789!"
    And I click the "Change Password" button
    Then I should see an error message "The two password fields didn't match"
    And my password should not be changed

  @validation @error_handling
  Scenario: Change password to weak password
    Given I am on the password change page
    When I fill in "current password" with "SecurePass123!"
    And I fill in "new password" with "123"
    And I fill in "confirm new password" with "123"
    And I click the "Change Password" button
    Then I should see an error message about password strength
    And my password should not be changed
