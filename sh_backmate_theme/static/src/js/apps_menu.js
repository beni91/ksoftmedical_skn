//odoo.define('backmate_backend_theme.AppsMenu', function (require) {
//"use strict";
//
//var Widget = require('web.Widget');
//var AppsMenu = require('web.AppsMenu');
//var session = require('web.session');

//
//var AppsMenu = AppsMenu.include({
//
//    //--------------------------------------------------------------------------
//    // Handlers
//    //--------------------------------------------------------------------------
//
//    /**
//     * Called when clicking on an item in the apps menu.
//     *
//     * @private
//     * @param {MouseEvent} ev
//     */

//	    
//	  openFirstApp: function () {
//		
//	        if (!this._apps.length) {
//	            return
//	        }
//	        if(this.theme_style=='style7'){
//	        	$(".sh_backmate_theme_appmenu_div").addClass("show")
//	        	$("body").addClass("sh_sidebar_background_enterprise");
//	        //	$(".sh_search_container").css("display","block");
//	        	 $(".sh_backmate_theme_appmenu_div").css("opacity","1");
//	        	$(".o_action_manager").addClass("d-none");
//	        	$(".full").addClass("sidebar_arrow");
//	        	$(".o_menu_brand").css("display","none");
//	        	$(".o_menu_sections").css("display","none");
//	        }else{
//	        	   var firstApp = this._apps[0];
//	  	       this._openApp(firstApp);
//	        }
//	        
//	     
//	    },
//
//
//});
//
//return AppsMenu;
//
//
//});
