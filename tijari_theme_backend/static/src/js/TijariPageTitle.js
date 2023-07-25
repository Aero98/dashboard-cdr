odoo.define('tijari_theme_backend.tijariPageTitle', function (require) {
"use strict";

    var ajax = require('web.ajax');
    var { WebClient } = require("@web/webclient/webclient");
    var { patch } = require("web.utils");

    patch(WebClient.prototype, "tijari_theme_backend.tijariPageTitle", {
        setup() {
            this._super();
            var self = this
            ajax.rpc('/get/tab/title/').then(function(rec) {
                var new_title = rec
                self.title.setParts({ zopenerp: new_title })
            })
        },
    });
});