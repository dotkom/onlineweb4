function Utils() {

  var that = this;
  this.apiQueue = [];

  /* adapted from djangoproject.com */
  /* Static method */
  function getCookie(name) {
    var cookieValue;
    if(document.cookie){
      var cookies = document.cookie.split(';');
      for(var i=0;i<cookies.length;i++){
        var cookie = $.trim(cookies[i]);
        if(cookie.substring(0, name.length+1) == name + '='){
          return decodeURIComponent(cookie.substring(name.length+1));
        }
      }
    }
  }

  /* Static method to make single API requests */
  Utils.prototype.makeApiRequest = function(request) {

    //console.log("doing request",request);
    $.ajax({
      url: request.url,
      type: request.type,
      data: request.data,
      headers: {'X-CSRFToken':getCookie('csrftoken')},
      error: (function(error){
        return function(e){
          //$('.saving-info').text('Saving failed! Best option for now is to do a refresh.');
        }
      })(request.error),
      success: (function(success){
        return function(data){
          success(data);
          //console.log("request complete!",request);
        }
      })(request.success)
    });
  }

  /* Object method to add a request to the API queue */
  Utils.prototype.makeApiQueueRequest = function(request){

    this.apiQueue.push(request);

    /* adapted from djangoproject.com */
    function getCookie(name){
      var cookieValue;
      if(document.cookie){
        var cookies = document.cookie.split(';');
        for(var i=0;i<cookies.length;i++){
          var cookie = $.trim(cookies[i]);
          if(cookie.substring(0, name.length+1) == name + '='){
            return decodeURIComponent(cookie.substring(name.length+1));
          }
        }
      }
    }

    if(this.apiQueue.length == 1){
      (function doApiRequest(){
        if(that.apiQueue.length == 0){
          //$('.saving-info').removeClass('saving');
          return;
        }
        //$('.saving-info').addClass('saving');
        var request = that.apiQueue.pop(0); //popleft? legit!
        console.log("doing request",request);
        $.ajax({
          url: request.url,
          type: request.type,
          data: request.data,
          headers: {'X-CSRFToken':getCookie('csrftoken')},
          error: (function(error){
            return function(e){
              //$('.saving-info').text('Saving failed! Best option for now is to do a refresh.');
            }
          })(request.error),
          success: (function(success){
            return function(data){
              success(data);
              console.log("request complete!",request);
              setTimeout(doApiRequest,0);
            }
          })(request.success)
        });
      })();
    }
  };

  /* Method to add status messages which mimic django's own. */
  Utils.prototype.setStatusMessage = function(message, tags) {
    if ($('div.messages').length === 0) {
      var prnt = $('nav.subnavbar');
      if (prnt.length === 0) {
        prnt = $('nav.navbar');
      }
      $('<div class="container messages"><div class"row"><div class="message-container col-md-12"></div></div></div>').insertAfter(prnt);
    }
    var msgWrapper = $('div.messages');
    var inner = msgWrapper.find('.message-container');
    var id = new Date().getTime();
    $('<div class="alert ' + tags + '" id="' + id +'"><button type="button" class="close" data-dismiss="alert">&times;</button>' + message + '</div>').appendTo(inner);

    //Fadeout and remove the alert
    setTimeout(function() {
      $('[id=' + id +']').fadeOut();
      setTimeout(function() {
        $('[id=' + id +']').remove();
      }, 5000);
    }, 5000);
  }

  /**
   * Render a template on the basis of the attributes of a data object
   * @param {object} tmpl A jQuery wrapper DOM object
   * @param {object} context An object containing the template payload
   * @return {object} Rendered DOM subtree containing provided context data
   */
  Utils.prototype.render = function (tmpl, context) {
    var node = window._.template(tmpl)
    return node(context)
  }
}

// Inject String format method if not defined
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] !== 'undefined' ? args[number] : match
    })
  }
}
