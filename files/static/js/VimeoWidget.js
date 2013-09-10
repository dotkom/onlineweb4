$('#uploadForm').submit(function() {
    var form = document.getElementById('uploadForm');
    var formData = new FormData(form);
    var action = form.getAttribute('action');
    sendXHRequest(formData, action);
    return false; 
});
            
function sendXHRequest(formData, uri) {
    var xhr = new XMLHttpRequest();
    xhr.upload.addEventListener('loadstart', onloadstartHandler, false);
    xhr.upload.addEventListener('progress', onprogressHandler, false);
    xhr.upload.addEventListener('load', uploadComplete, false);

    xhr.open('POST', uri, true);
    xhr.send(formData);
}

function onloadstartHandler(evt) {
    document.getElementById("progress").hidden = false;
}

function onprogressHandler(evt) {
    var percent = evt.loaded/evt.total*100;
    var progressBar = document.getElementById("progress");
    progressBar.value = percent;
}
