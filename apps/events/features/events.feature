Feature: Shows events
    Scenario: Hello Events
        Given I access the url "/events/"
        Then I see the header "Events"

    Scenario: Hello Event
        Given I access the url "/events/1"
        Then I see the header "Event"
