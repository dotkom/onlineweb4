/* MODULES */

var events, tools, api;
var API_KEY = "5db1fee4b5703808c48078a76768b155b421b210c0761cd6a5d223f4d99f1eaa";

api = (function () {

    var doRequest = function (type, url, params, data) {
        $.ajax({
            type: type,
            dataType: "json",
            data: data,
            url: url + params,
            success: function (data) {
                console.log(data);
                events.events_callback(data);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                // tools.showerror(xhr);
                console.log("" + xhr.status + ":" + xhr.responseText);
                events.events_callback(null);
            }
        });
    }

    return {
        get_events: function () {
            return doRequest("GET", "/api/rfid/events/", "?event_end__gte=2013-11-30&api_key=" + API_KEY, {});
        },

        get_user_by_username: function (username) {
            return doRequest("GET", "/api/rfid/user/", "?username=" + username + "&api_key=" + API_KEY, {});
        }
    }
}());

events = (function () {

    var event_list = [];
    var active_event = {};
    var active_attendees = [];
    var active_user = {};

    var extract_events = function (data) {
        console.log(data);
        if (data.meta.total_count > 0) {
            event_list = data.events;
            console.log(event_list);
        }
        else {
            console.log("No events returned from query...");
            event_list = [];
        }
    }

    return {
        get_event_list: function () {
            api.get_events();
        },
        
        events_callback: function (data) {
            extract_events(data);
        }
    }
}());

tools = (function () {
    
    var active_user = {};

    return {
        get_user_by_uri: function (uri) {
            active_user = {};
        }
    }
}());

$(document).ready(function () {
    events.get_event_list();
});
