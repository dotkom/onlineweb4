/*
    The event module provides dynamic functions to event objects
    such as saving user selection on event extras
*/

var Event = (function ($, tools) {

    // Perform self check, display error if missing deps
    var performSelfCheck = function () {
        var errors = false
        if ($ == undefined) console.error('jQuery missing!')
        if (tools == undefined) console.error('Dashboard tools missing!')
        if (errors) return false
        return true
    }

return {
    init: function () {
            if (!performSelfCheck()) return
    },

    sendChoice: function(id, text) {
        var url = window.location.href.toString()
        var data = {
            "extras_id": id,
            "action": "extras"
        }
        var success = function (data) {
            //var line = $('#' + attendee_id > i)
            tools.showStatusMessage(data.message, 'alert-success')
            var message = "Valgt ekstra: ";
            $("#choose-extras > .text").text(message + text);
        }
        var error = function (xhr, txt, error) {
            tools.showStatusMessage(error, 'alert-danger')
        }

        // Make an AJAX request using the Dashboard tools module
        tools.ajax('POST', url, data, success, error, null)
    }   
}


    
})(jQuery, Dashboard.tools)

$(document).ready(function () {
    Event.init()
    $(".extras-choice").click(function() {
        var id = $(this).attr("data");
        var text = $(this).text();
        Event.sendChoice(id, text);
    });
})
