$(document).ready(function(){
    $("#messageform").on("submit", function(){
        sendMessage($(this))
        return false
    })

    $("#messageform").on("keypress", function(evt){
        if (evt.keyCode == 13) {
            sendMessage($(this))
            return false
        }
        return true
    })

    $("#message").select()
    updater.start()
})

function sendMessage(form) {
    var message = form.formToDict()
    updater.socket.send(JSON.stringify(message))
    form.find("input[type=text]").val("").select()
}

jQuery.fn.formToDict = function() {
    let json = {}
    var fields = this.serializeArray()
    for (let field of fields) {
        json[field.name] = field.value
    }

    if (json.next) delete json.next
    return json
}

var updater = {
    socket: null,

    start: function() {
        var url = "ws://"+location.host+"/chatsocket"
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            updater.showMessage(JSON.parse(event.data))
        }
    },

    showMessage: function(message) {
        let existing = $("#m"+message.id)
        if (existing.length>0) return
        var node = $(message.html)
        node.hide()
        $("#inbox").append(node)
        node.slideDown()
    }
}