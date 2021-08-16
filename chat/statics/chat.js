let ENTER_KEY_CODE = 13

$(document).ready(function(){
    $("#messageform").on("submit", function(){
        sendMessage($(this))
        return false //prevent default form action
    })

    $("#messageform").on("keypress", function(e){
        if(e.keyCode == ENTER_KEY_CODE){
          sendMessage($(this))
          return false  
        }
        return true
    })

    $("#message").select()
    messageBox.loadMessages()
})


function sendMessage(form){
    var message = form.formToDict()
    var submitBtn = form.find("input[type=submit]")
    submitBtn.disabled()

    $.postJSON("/a/message/new", message, function(response){
        messageBox.showMessage(response);
        if(message.id){
            form.parent.remove()
        }else{
            form.find("input[type=text]").val("").select()
            submitBtn.enable()
        }
    })
}

function getCookie(name){
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b")
    return r ? r[1] : undefined
}


jQuery.postJSON = function (url , args, callback){
    args.xsrf = getCookie("_xsrf")
    $.ajax({
        url: url, data: $.param(args), dataType: "text", type: "POST", 
        success: function(response){
            if (callback) callback(eval("(" + response + ")"))
        },
        error: function(response){
            console.log("ERROR:", response)
        }
    })
}


jQuery.fn.formToDict = function(){
    var fields = this.serializeArray()
    var json = {}
    for (let field of fields){
        json[field.name] = field.value
    }

    if (json.next) delete json.next
    return json
}

jQuery.fn.disabled = function(){
    this.enable(false)
    return this
}

jQuery.fn.enable = function(optEnable){
    if (arguments.length && !optEnable){
        this.attr("disabled", "disabled")
    }else{
        this.removeAttr("disabled")
    }
    return this
}

var messageBox = {
    errorSleepTime: 500,
    cursor: null,
    loadMessages: function(){
        var args = {"_xsrf": getCookie("_xsrf")};
        if (messageBox.cursor) {
            args.cursor = messageBox.cursor
        }

        $.ajax({
            url: "/a/message/updates", type: "POST", dataType: "text",
            data: $.param(args),
            success: messageBox.onSuccess,
            erorr: messageBox.onError
        })
    },

    onSuccess: function(response){
        try{
            messageBox.showMultiMessages(eval("(" + response + ")"))
        } catch (e) {
            messageBox.onError(e)
            return
        }
        messageBox.errorSleepTime = 500
        window.setTimeout(messageBox.loadMessages, messageBox.errorSleepTime)
    }, 

    onError: function(error) {
        messageBox.errorSleepTime *= 2
        console.log("Poll error; sleeping for", messageBox.errorSleepTime, "ms")
        setTimeout(messageBox.loadMessages, messageBox.errorSleepTime)
    },

    showMultiMessages: function(response) {
        if (!response.messages) return;
        var messages = response.messages;
        messageBox.cursor = messages[messages.length-1].id
        console.log(messages.length, "new messages, cursor: ", messageBox.cursor)
        for (let message of messages) {
            messageBox.showMessage(message)
        }
    }, 

    showMessage: function(message) {
        var existing = $("#"+message.id)
        if (existing.length>0) return
        var node = $(message.html)
        node.hide()
        $("#inbox").append(node)
        node.slideDown()
    }
}