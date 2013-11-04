/* MODULES */

var events, tools, api;
var API_KEY = "5db1fee4b5703808c48078a76768b155b421b210c0761cd6a5d223f4d99f1eaa";

// API module, has a private doRequest method, and public get and set methods
api = (function () {

    // Does a request based in input parameters
    var doRequest = function (type, dataType, url, params, send_data, callback) {
        $.ajax({
            type: type,
            dataType: dataType,
            contentType: "application/json",
            data: send_data,
            url: url + params,
            success: function (return_data) {
                console.log(return_data);
                callback(return_data);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                if (xhr.status === 202 || xhr.status === 204 || xhr.status === 304) {
                    callback(xhr);
                }
                else {
                    callback(null);
                }
            }
        });
    }

    return {
        // Gets event list
        get_events: function () {
            return doRequest("GET", "json", "/api/rfid/events/", "?api_key=" + API_KEY + "&event_end__gte=" + "2013-10-30" + "&limit=3", {}, events.events_callback);
        },

        // Gets user object by username
        get_user_by_username: function (username) {
            return doRequest("GET", "json", "/api/rfid/user/", "?username=" + username + "&api_key=" + API_KEY, {}, tools.user_callback);
        },

        // Gets user object by rfid
        get_user_by_rfid: function (rfid) {
            return doRequest("GET", "json", "/api/rfid/user/", "?rfid=" + rfid + "&api_key=" + API_KEY, {}, tools.user_callback);
        },

        // Sets an attendee as attended
        set_attended: function (attendee) {
            return doRequest("PATCH", "json", attendee.resource_uri, "?api_key=" + API_KEY, "{\"attended\": true}", events.attend_callback);
        },

        // Updates an event with new info
        update_event: function (event) {
            return doRequest("GET", "json", event.resource_uri, "?api_key=" + API_KEY, {}, events.update_event_callback(event));
        }
    }
}());

// The events module contains functions and containers for events, active event, active attendees and active user
events = (function () {

    var event_list = [];
    var active_event = null;
    var active_attendees = [];
    var active_user = null;

    // Private method that parses the returned events object and checks if there are any
    var extract_events = function (data) {
        console.log(data);
        if (data.meta.total_count > 0) {
            event_list = data.events;
            tools.populate_nav(event_list);
            events.set_active_event(0);
        }
        else {
            console.log("No events returned from query...");
            tools.showerror(404, "There are no upcoming events available...");
            event_list = [];
        }
    }

    return {
        // Gets the event list from the API
        get_event_list: function () {
            api.get_events();
        },
        
        // Public callback for event list
        events_callback: function (data) {
            if (data != null) {
                extract_events(data);
            }
            else {
                tools.showerror(404, "Det oppstod en uventet feil under henting av arrangementene.");
            }
        },

        // Returns the active event in view
        get_active_event: function () {
            return active_event;
        },

        // Sets the active event in view
        set_active_event: function (index) {
            active_event = event_list[index];
            $('#title').text(active_event.title);
            if (active_event.company_event.length > 0) {
                $('#event_image').attr('src', active_event.company_event[0].companies.image_companies_thumb);
            }
            tools.populate_attendance_list(active_event.attendance_event.users);
        },

        // Updates the active event with new data from the API
        update_active_event: function (event) {
            api.update_event(event);
        },

        // Public callback for the update event method
        update_event_callback: function (event) {
            if (data != null) {
                active_event = event;
            }
            else {
                tools.showerror(400, "Det oppstod en feil under oppdatering av arrangementsinformasjonen.");
            }
        },

        // Registers an attendant by the attendee URI
        register_attendant: function (attendee) {
            api.set_attended(attendee);
            console.log("Api trigger set_attended");
            console.log(attendee);
        },

        // Public callback for the register_attendant method
        attend_callback: function () {
            if (events.active_user != null) {
                tools.showsuccess(200, events.active_user.first_name + " " + events.active_user.last_name + " er registrert som deltaker!");
            }
            else {
                tools.showerror(400, "Det oppstod en uventet feil under registering av deltakeren.");
            }
        },

        // Gets the active user being processed
        get_active_user: function () {
            return active_user;
        },

        // Sets the active user being processed
        set_active_user: function (user) {
            active_user = user;
        },

        // Checks if user is in attendee list
        is_attendee: function (user) {
            for (var x = 0; x < active_event.attendance_event.users.length; x++) {
                if (active_event.attendance_event.users[x].user.id == user.id) return active_event.attendance_event.users[x];
            }
            return false;
        },
    }
}());

// The tools module contains different methods for manipulating the DOM and other fancy stuff
tools = (function () {

    return {
        // Temporarily show an error message on the top of the page...
        showerror: function (status, message) {
            tools.tempshow($('#topmessage').removeClass().addClass("alert alert-danger").text(message));
        },

        // Temporarily show a success message on the top of the page...
        showsuccess: function (status, message) {
            tools.tempshow($('#topmessage').removeClass().addClass("alert alert-success").text(message));
        },

        // Temporarily show a DOM object
        tempshow: function (object) {
            object.fadeIn(200);
            setTimeout(function () {
                object.fadeOut(200);
            }, 3000);
        },

        // Returns a date string representing today for filtering purposes
        today: function () {
            var d = new Date();
            y = d.getFullYear();
            m = d.getMonth() + 1;
            d = d.getDate();
            if (m < 10) m = "0" + m;
            if (d < 10) d = "0" + d;
            return y + "-" + m + "-" + d;
        },

        // This method populates the navbar dropdown with the events in the specified event_list
        populate_nav: function (event_list) {
            $(event_list).each(function (id) {
                $('#nav').append($('<li><a href="#" id="' + id + '">' + event_list[id].title + '</a></li>'));
            });
        },

        // This method takes in an array of attendees and lists those whose attended flag is set to true,
        // as well as keeping track of the total amount of attendees.
        populate_attendance_list: function (attendees) {
            var attended = 0;
            $('#attendees').empty();
            $('#attendees').append($('<tr><th>Nr</th><th>Fornavn</th><th>Etternavn</th></tr>'));
            $(attendees).each(function (id) {
                if (attendees[id].attended) {
                    attended++;
                    $('#attendees').append($('<tr><td>' + (id+1) + '</td><td>' + attendees[id].user.first_name + '</td><td>' + attendees[id].user.last_name + '</td></tr>'));
                }
            });
            $('#total_attendees').text('Antall oppmøtte: ' + attended + '/' + events.get_active_event().attendance_event.max_capacity);
        },

        // Get user by RFID
        get_user_by_rfid: function (rfid) {
            api.get_user_by_rfid(rfid);
        },

        // Get user by Username
        get_user_by_username: function (username) {
            api.get_user_by_username(username);  
        },

        // Public callback for User queries
        user_callback: function (user) {
            if (user != null && user.meta.total_count == 1) {
                events.set_active_user = user.objects[0];
                console.log("User object returned");
                console.log(user.objects[0]);
                var e = events.is_attendee(events.get_active_user);
                if (e) {
                    console.log("Attendee is in list and attendee object returned");
                    events.register_attendant(e);
                }
                else {
                    tools.showerror(401, "Brukeren er ikke oppført på listen, eller er på venteliste");
                }
            }
            else {
                tools.showerror(404, "Brukeren eksisterer ikke i databasen");
                events.set_active_user = null;
            }
        },

        // Parse text input for RFID or username
        parse_input: function (input) {
            console.log("Parsing input...");
            if (/^[0-9]{10}$/.test(input)) {
                console.log("Rfid valid");
                api.get_user_by_rfid(input);
            }
            else {
                console.log("Not RFID");
                api.get_user_by_username(input);
            }
        },
    }
}());

// On page load complete, do this stuff...
$(document).ready(function () {

    var last_rfid = null;

    // Get the event list from the API
    events.get_event_list();

    // Bind click listeners to the events menu links
    $('#nav').on('click', 'a', function (event) {
        event.preventDefault();
        events.set_active_event($(this).attr("id"));
    });

    $('#submit').on('click', function (event) {
        var input = $('#input').val();
        tools.parse_input(input);
    });
});
