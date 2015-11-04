/*
    The event module provides dynamic functions to event objects
    such as saving user selection on event extras
*/

var Event = (function ($) {

    // Perform self check, display error if missing deps
    var performSelfCheck = function () {
        var errors = false
        if ($ == undefined) console.error('jQuery missing!')
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
            Event.showFlashMessage(message, 'alert-warning')
        }
        else if(all_extras.length >0 && selected_extra !== "" && jQuery.inArray(selected_extra, all_extras) == -1){
            message = "Ditt valg til ekstra bestilling er ikke lenger gyldig! Velg et nytt.";
            Event.showFlashMessage(message, 'alert-warning')
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
            Event.showFlashMessage(data.message, 'alert-success');
            
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
            Event.showFlashMessage(message+error, 'alert-danger');
        }

        // Make an AJAX request
        Event.ajaxRequest({'method': 'POST', 'url': url, 'data': data, success: success, error: error});
    },

    ajaxRequest: function(request) {
        $.ajax({
            url: request.url,
            type: "POST",
            data: request.data,
            headers: {'X-CSRFToken':$.cookie('csrftoken')},
            error: (function(error){
                return function(e){
                    error(e);
                }
            })(request.error),
            success: (function(success){
                return function(data){
                    success(data);
                }
            })(request.success)
        });
    },

    showFlashMessage: function (message, tags) {
        var id = new Date().getTime();
        var wrapper = $('.messages')
        var message = $('<div class="row" id="'+ id +'"><div class="col-md-12">' + 
                        '<div class="alert ' + tags + '">' + 
                        message + '</div></div></div>')

        if(wrapper.length == 0){
            wrapper = $('section:first > .container:first')
        }
        message.prependTo(wrapper)

        // Fadeout and remove the alert
        setTimeout(function() {
            $('[id=' + id +']').fadeOut();
            setTimeout(function() {
                $('[id=' + id +']').remove();
            }, 5000);
        }, 5000);
    }
}


    
})(jQuery)

$(document).ready(function () {
    Event.init()
})

