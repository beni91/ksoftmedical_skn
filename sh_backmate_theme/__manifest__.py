# -*- coding: utf-8 -*-
{
    "name": "Backmate Backend Theme Basics [For Community Edition]",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Themes/Backend",
    "summary": "Material Backend, Responsive, Backmate Backend Theme, fully functional Backend Theme, flexible Backend Theme, fast Backend Theme, lightweight Backend Theme, animated Backend Theme, modern multipurpose theme Odoo",
    "description": """Are you bored with your standard odoo backend theme? Are You are looking for modern, creative, clean, clear, materialize Odoo theme for your backend? So you are at right place, We have made sure that this theme is highly customizable and it comes with a premium look and feel. Our theme is not only beautifully designed but also fully functional, flexible, fast, lightweight, animated and modern multipurpose theme. Our backend theme is suitable for almost every purpose.""",
    "version": "15.0.9",
    "depends":
    [
        "web",
        "sh_back_theme_config",
        "mail"
    ],

    "data":
    [
        "security/backmate_security.xml",
        "security/ir.model.access.csv",
        "data/pwa_configuraion_data.xml",
        "views/assets.xml",
        "views/login_layout.xml",
        "views/pwa_configuration_view.xml",
        "views/views.xml",
        "views/notifications_view.xml",
        "views/send_notifications.xml",
        "views/web_push_notification.xml",
    ],

    'images': [
        'static/description/splash-screen.png',
        'static/description/splash-screen_screenshot.gif'
    ],
    
     'assets': {
       
        'web.assets_backend': [
            'sh_backmate_theme/static/src/scss/theme.scss',
            'sh_backmate_theme/static/src/scss/font.scss',
            'sh_backmate_theme/static/src/scss/buttons.scss',
            'sh_backmate_theme/static/src/scss/background-img.scss',
            'sh_backmate_theme/static/src/scss/saidbar.scss',
            'sh_backmate_theme/static/src/scss/separtor.scss',
            'sh_backmate_theme/static/src/scss/navbar.scss',
            'sh_backmate_theme/static/src/scss/form_view.scss',
            'sh_backmate_theme/static/src/scss/button_icon.scss',
            'sh_backmate_theme/static/src/scss/sidebar_bg.scss',
            'sh_backmate_theme/static/src/scss/theme_style_4.scss',
            'sh_backmate_theme/static/src/scss/popup_style.scss',
            'sh_backmate_theme/static/src/scss/menu_mobile.scss',
            'sh_backmate_theme/static/src/scss/sticky_chatter.scss',
            'sh_backmate_theme/static/src/scss/sticky_form.scss',
            'sh_backmate_theme/static/src/scss/sticky_list_inside_form.scss',
            'sh_backmate_theme/static/src/scss/sticky_list.scss',
            'sh_backmate_theme/static/src/js/menu.js',
            'sh_backmate_theme/static/src/js/global_search.js',
            'sh_backmate_theme/static/src/scss/global_search.scss',
            'sh_backmate_theme/static/src/js/apps_menu.js',
            'sh_backmate_theme/static/src/js/status_bar.js',
            # 'sh_backmate_theme/static/src/js/customize_user.js',
            'sh_backmate_theme/static/src/js/night_mode.js',
            'sh_backmate_theme/static/src/js/control_panel.js',
            'sh_backmate_theme/static/src/scss/quick_menu.scss',
            'sh_backmate_theme/static/src/js/quick_menu.js',
            'sh_backmate_theme/static/src/js/vertical_pen.js',
            'sh_backmate_theme/static/src/js/calculator.js',
            'sh_backmate_theme/static/src/scss/tab.scss',
            'sh_backmate_theme/static/src/scss/form_element_style.scss',
            'sh_backmate_theme/static/src/scss/chatter_position.scss',
            'sh_backmate_theme/static/src/scss/calculator.scss',
            'sh_backmate_theme/static/src/scss/notification.scss',
            'sh_backmate_theme/static/src/scss/breadcrumb.scss',
            'sh_backmate_theme/static/src/scss/form_full_width.scss',
            'sh_backmate_theme/static/src/scss/loader.scss',
            # 'sh_backmate_theme/static/src/js/sh_bus_notification.js',
            # 'sh_backmate_theme/static/src/js/web_notification.js',
            'sh_backmate_theme/static/src/scss/nprogress.scss',
            'sh_backmate_theme/static/src/js/nprogress.js',
            'sh_backmate_theme/static/src/js/progressbar.js',
            'sh_backmate_theme/static/src/scss/background-color.scss',
            'sh_backmate_theme/static/index.js',
            'https://www.gstatic.com/firebasejs/8.4.3/firebase-app.js',
            'https://www.gstatic.com/firebasejs/8.4.3/firebase-messaging.js',
            'sh_backmate_theme/static/src/js/firebase.js',

            'sh_backmate_theme/static/src/js/action_service.js',
           'sh_backmate_theme/static/src/js/action_container.js',
          
            'sh_backmate_theme/static/src/js/dropdown.js',
            # 'sh_backmate_theme/static/src/js/profilesection.js',
            # 'sh_backmate_theme/static/src/js/control_panel_lagecy.js',
            
             'sh_backmate_theme/static/src/js/navbar.js',
            # ('replace', 'web/static/src/webclient/actions/action_container.js', 
            # 'sh_backmate_theme/static/src/js/action_container.js'),        
            'sh_backmate_theme/static/src/js/bus_notification.js',
            'sh_backmate_theme/static/src/scss/night_mode_user.scss',
            'sh_backmate_theme/static/src/js/language_selector.js',
            'sh_backmate_theme/static/src/js/route_service.js',
        ],
        'web.assets_qweb': [
                "sh_backmate_theme/static/src/xml/sh_thread.xml",
                "sh_backmate_theme/static/src/xml/menu.xml",
                "sh_backmate_theme/static/src/xml/navbar.xml",
                "sh_backmate_theme/static/src/xml/form_view.xml",
                "sh_backmate_theme/static/src/xml/widget.xml",
                "sh_backmate_theme/static/src/xml/global_search.xml",
                "sh_backmate_theme/static/src/xml/base.xml",
                "sh_backmate_theme/static/src/xml/web_quick_menu.xml",
        ],
         'web.assets_frontend': [
            'sh_backmate_theme/static/src/scss/login_style_1.scss'
           
        ],
        
      
       
    },
     
     
    "live_test_url": "https://softhealer.com/contact_us",
    "installable": True,
    "application": True,
    "price": 95,
    "currency": "EUR",
    "bootstrap": True
}
