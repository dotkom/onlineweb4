import $ from "jquery";
import Cookies from "js-cookie";
import { makeApiRequest, showFlashMessage } from "common/utils/";

/*
    The event module provides dynamic functions to event objects
    such as saving user selection on event extras
*/

// Global variables defined in details template
const allExtras = window.all_extras;
const selectedExtra = window.selected_extra;

const sendChoice = id => {
    const url = window.location.href.toString();
    const data = {
        extras_id: id,
        action: "extras"
    };
    const success = jsonData => {
        // var line = $('#' + attendee_id > i)
        showFlashMessage(jsonData.message, "alert-success");

        const chosenText = "Valgt ekstra: ";
        const options = $(".extras-choice option");
        for (let i = options.length - 1; i >= 0; i -= 1) {
            if (options[i].text.indexOf(chosenText) >= 0) {
                options[i].text = allExtras[i];
                break;
            }
        }

        const selected = $(".extras-choice option:selected");
        selected.text(chosenText + selected.text());
    };
    const error = (xhr, txt, errorMessage) => {
        const message =
            "Det skjedde en feil! Refresh siden og prøv igjen, eller kontakt de ansvarlige hvis det fortsatt ikke går. ";
        showFlashMessage(message + errorMessage, "alert-danger");
    };

    // Make an AJAX request
    makeApiRequest({ type: "POST", url, data, success, error });
};

const init = () => {
    $(".extras-choice").on("change", function changeExtraChoice() {
        const id = $(this).val();
        const text = $(this).text();
        sendChoice(id, text);
    });

    if (allExtras.length > 0 && selectedExtra === "None") {
        const message =
            "Vennligst velg et alternativ for extra bestilling. (Over avmeldingsknappen)";
        showFlashMessage(message, "alert-warning");
    } else if (
        allExtras.length > 0 &&
        selectedExtra !== "" &&
        $.inArray(selectedExtra, allExtras) === -1
    ) {
        const message =
            "Ditt valg til ekstra bestilling er ikke lenger gyldig! Velg et nytt.";
        showFlashMessage(message, "alert-warning");
    }
};

const refundPayment = async relationId => {
    const refundUrl = `/api/v1/payment/relations/${relationId}/`;
    const response = await fetch(refundUrl, {
        method: "DELETE",
        credentials: "include",
        headers: { "X-CSRFToken": Cookies.get("csrftoken") }
    });
    const responseData = await response.json();
    if (responseData.message) {
        const status = response.ok ? "alert-success" : "alert-warning";
        showFlashMessage(responseData.message, status);
    }
};

window.addEventListener("load", () => {
    const refundButton = document.getElementById("refund-payment-button");
    console.log(refundButton);
    if (refundButton) {
        const relationId = refundButton.dataset.paymentrelationid;
        console.log(relationId);
        refundButton.addEventListener("click", async () => {
            await refundPayment(relationId);
        });
    }
});

export default init;
