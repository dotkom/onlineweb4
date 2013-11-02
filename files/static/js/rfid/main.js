/* MODULES */

var events, tools, api;
var API_KEY = "5db1fee4b5703808c48078a76768b155b421b210c0761cd6a5d223f4d99f1eaa";

// API module, has a private doRequest method, and public get and set methods
api = (function () {

    // Does a request based in input parameters
    var doRequest = function (type, url, params, data, callback) {
        $.ajax({
            type: type,
            dataType: "json",
            data: data,
                url: url + params,
            success: function (data) {
                console.log(data);
                callback(data);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                // tools.showerror(xhr);
                console.log("" + xhr.status + ":" + xhr.responseText);
                callback(null);
            }
        });
    }

    return {
        // Gets event list
        get_events: function () {
            return doRequest("GET", "/api/rfid/events/", "?api_key=" + API_KEY, {}, events.events_callback);
        },

        // Gets user object by username
        get_user_by_username: function (username) {
            return doRequest("GET", "/api/rfid/user/", "?username=" + username + "&api_key=" + API_KEY, {}, tools.user_callback);
        },

        set_attended: function (uri, user) {
            return doRequest("PATCH", uri, "?api_key=" + API_KEY, {"attended": true}, events.attend_callback(user));
        }

    }
}());

// The events module contains functions and containers for events, active event, active attendees and active user
events = (function () {

    var event_list = [];
    var active_event = {};
    var active_attendees = [];
    var active_user = {};

    // Private method that parses the returned events object and checks if there are any
    var extract_events = function (data) {
        console.log(data);
        if (data.meta.total_count > 0) {
            event_list = data.events;
            tools.populate_nav(event_list);
            active_event = event_list[0];
            $('#title').text(active_event.title);
            $('#1').parent().addClass('active');
            tools.populate_attendance_list(active_event.attendance_event.users);
            console.log(event_list);
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
            extract_events(data);
        },

        // Returns the active event in view
        get_active_event: function () {
            return active_event;
        },

        // Sets the active event in view
        set_active_event: function (index) {
            active_event = event_list[index];
            $('#title').text(active_event.title);
        },

        // Registers an attendant by the attendee URI
        register_attendant: function (uri, user) {
            api.set_attended(uri, user);
        },

        // Public callback for the register_attendant method
        attended_callback: function (user) {
            if (user) {
                tools.showsuccess(200, "Tihi");
            }
            else {

            }
        }
    }
}());

// The tools module contains different methods for manipulating the DOM and other fancy stuff
tools = (function () {
    
    var active_user = {};

    return {

        get_user_by_uri: function (uri) {
            active_user = {};
        },

        showerror: function (status, message) {
            tools.tempshow($('#topmessage').removeClass().addClass("alert alert-danger").text(message));
        },

        showsuccess: function (status, message) {
            tools.tempshow($('#topmessage').removeClass().addClass("alert alert-success").text(message));
        },

        tempshow: function (object) {
            object.fadeIn(200);
            setTimeout(function () {
                object.fadeOut(200);
            }, 3000);
        },

        populate_nav: function (event_list) {
            $(event_list).each(function (id) {
                $('#nav').append($('<li><a href="#" id="' + event_list[id].id + '">' + event_list[id].title + '</a></li>'));
            });
        },

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
        }

    }
}());

// On page load complete, do this stuff...
$(document).ready(function () {
    events.get_event_list();
    $('#nav').on('click', 'a', function (event) {
        console.log($(this));
        $(this).parent().addClass('active');
    });
});
