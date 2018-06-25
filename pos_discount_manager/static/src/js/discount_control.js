odoo.define('pos_discount_manage', function (require) {
    "use strict";

    var scr = require('point_of_sale.screens');
    scr.NumpadWidget.include({
        clickChangeMode:function(event){
            var newMode = event.currentTarget.attributes['data-mode'].nodeValue;
            console.log('in my app clicked')
            if(newMode == 'discount' && this.pos.config.disable_discount == 1){
                return 0;
            }
            else{
                return this.state.changeMode(newMode);
            }
        }
    })
});