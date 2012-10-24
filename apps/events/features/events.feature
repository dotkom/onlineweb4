Feature: First test
    Scenario: Hello Events
        Given I access the url "/events/"
        Then I see the header "Events"

    Scenario: Hello Event
        Given I access the url "/1/details"
        Then I see the header "Event 1"
