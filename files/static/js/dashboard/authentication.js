/*
    The Authentication module exposes functionality directed towards user profiles, and the membership registry.
*/

var Authentication = (function ($, tools) {

    // Perform self check, display error if missing deps
    var performSelfCheck = function () {
        var errors = false
        if ($ == undefined) {
            console.error('jQuery missing!')
            errors = !errors
        }
        if (tools == undefined) {
            console.error('Dashboard tools missing!')
            errors = !errors
        }
        if (errors) return false
        return true
    }

    // Filter user list
    $("#search_input").keyup(function() {
        var terms = this.value.split()
        var jo = $("#userlist_body").find("tr")

        // If no filter term, show all
        if (terms == "") {
            jo.show()
            return
        }

        // Filter for query terms
        jo.hide()

        jo.filter(function (i, v) {
            var $t = $(this);
            for (var d = 0; d < terms.length; ++d) {
                if ($t.is(":contains('" + terms[d] + "')")) {
                    return true;
                }
            }
            return false;
        })
        //show the rows that match.
        .show();
        }).focus(function () {
            this.value = "";
            $(this).css({
                "color": "black"
            });
            $(this).unbind('focus');
        })

    return {

        // Bind them buttons and other initial functionality here
        init: function () {

            if (!performSelfCheck()) return
            
            $('#membership_list').tablesorter()

        }

    }

})(jQuery, Dashboard.tools)

$(document).ready(function () {
    Authentication.init()
})
