
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
}
