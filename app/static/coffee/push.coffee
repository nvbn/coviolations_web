window.coviolations ?=
    views: {}
    models: {}
    plotting: {}
    push: {}

$ ->
    app = window.coviolations

    class app.push.PushConnection
        ### Push connection ###

        constructor: (bind, @userId) ->
            ### Create sockjs client ###
            _.extend @, Backbone.Events
            @sock = new SockJS bind
            @sock.onopen = $.proxy @onopen, @
            @sock.onmessage = $.proxy @onmessage, @

        onopen: ->
            ### Send subscription message on open ###
            @send
                method: 'subscribe'
                owner: @userId

        send: (msg) ->
            ### Prepare message and send ###
            @sock.send JSON.stringify msg

        onmessage: (msg) ->
            ### Trigger event on message ###
            msg = JSON.parse msg.data
            @trigger 'message', msg
            @trigger msg.type, msg


    window.userId ?= 0
    app.push.push = new app.push.PushConnection window.pushBind, window.userId
