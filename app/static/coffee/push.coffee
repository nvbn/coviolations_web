$ ->
    class PushConnection
        ### Push connection ###

        constructor: (bind, @userId) ->
            _.extend @, Backbone.Events
            @sock = new SockJS bind
            @sock.onopen = $.proxy @onopen, @
            @sock.onmessage = $.proxy @onmessage, @

        onopen: ->
            @send
                method: 'subscribe'
                owner: @userId

        send: (msg) ->
            @sock.send JSON.stringify msg

        onmessage: (msg) ->
            msg = JSON.parse msg.data
            @trigger 'message', msg
            @trigger msg.type, msg


    window.push = new PushConnection window.pushBind, window.userId
