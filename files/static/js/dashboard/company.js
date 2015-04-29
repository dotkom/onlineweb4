/*
    The Company module exposes functionality needed in the company section
    of the dashboard.
*/

var Company = (function ($, tools) {

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

    return {

        // Bind them buttons and other initial functionality here
        init: function () {

            if (!performSelfCheck()) return
            
            $('#company_list').tablesorter()

        }

    }

})(jQuery, Dashboard.tools)

$(document).ready(function () {
    Company.init()
})
