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
        if (!performSelfCheck()) return;

        $(".extras-choice").on('change', function() {
            var id = $(this).val();
            var text = $(this).text();
            Event.sendChoice(id, text);
        });

        if(all_extras.length >0 && selected_extra == "None"){
            message = "Vennligst velg et alternativ for extra bestilling. (Over avmeldingsknappen)";
            tools.showStatusMessage(message, 'alert-warning')
        }
        else if(all_extras.length >0 && jQuery.inArray(selected_extra, all_extras) == -1){
            message = "Ditt valg til ekstra bestilling er ikke lenger gyldig! Velg et nytt.";
            tools.showStatusMessage(message, 'alert-warning')
        }
    },

    sendChoice: function(id, text) {
        var url = window.location.href.toString()
        var data = {
            "extras_id": id,
            "action": "extras"
        }
        var success = function (data) {
            //var line = $('#' + attendee_id > i)
            tools.showStatusMessage(data.message, 'alert-success');
            
            var chosen_text = "Valgt ekstra: ";            
            var options = $(".extras-choice option");
            for (var i = options.length - 1; i >= 0; i--) {
                if(options[i].text.indexOf(chosen_text) >= 0){
                    options[i].text = all_extras[i];
                    break;
                }
            };

            var selected = $(".extras-choice option:selected");
            selected.text(chosen_text + selected.text())
        }
        var error = function (xhr, txt, error) {
            var message = "Det skjedde en feil! Refresh siden og prøv igjen, eller kontakt de ansvarlige hvis det fortsatt ikke går. "
            tools.showStatusMessage(message+error, 'alert-danger');
        }

        // Make an AJAX request using the Dashboard tools module
        tools.ajax('POST', url, data, success, error, null)
    }   
}


    
})(jQuery, Dashboard.tools)

$(document).ready(function () {
    Event.init()
})
