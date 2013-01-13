$.tcg_editor = function (context_name) {
    "use strict";
    var localStorage,
        storage_key = "edit_" + context_name,
        data,
        storage_listeners = [];

    function log() {
        var i;
        if (window.console) {
            for (i = 0; i < arguments.length; i += 1) {
                window.console.log(arguments[i]);
            }
        }
    }

    function have_html5_storage() {
        try {
            return window.localStorage !== undefined  && window.localStorage !== null;
        } catch (e) {
            return false;
        }
    }
    if (!have_html5_storage()) {
        return;
    }
    localStorage = window.localStorage;

    // http://stackoverflow.com/questions/4994201/is-object-empty
    function is_empty(obj) {
        var key;
        for (key in obj) {
            if (obj.hasOwnProperty(key)) {
                return false;
            }
        }
        return true;
    }

    function load_from_storage() {
        var i;
        try {
            data = JSON.parse(localStorage.getItem(storage_key));
            if (data === null) {
                data = {};
            }
        } catch (e) {
            data = {};
        }
        for (i = 0; i < storage_listeners.length; i += 1) {
            storage_listeners[i]();
        }
    }
    load_from_storage();
    $(window).bind('storage', load_from_storage);
    function data_save() {
        if (is_empty(data)) {
            localStorage.removeItem(storage_key);
        } else {
            localStorage.setItem(storage_key, JSON.stringify(data));
        }
        log(storage_key, localStorage.getItem(storage_key));
    }
    function data_set(key, value) {
        if (data[key] !== value) {
            data[key] = value;
            data_save();
        }
    }
    function data_remove(key) {
        if (data.hasOwnProperty(key)) {
            delete data[key];
            data_save();
        }
    }

    function prepare(options) {
        var data_key = options.key,
            orig_value = options.get();
        function update(value) {
            var value = options.get();
            if (orig_value === value) {
                data_remove(data_key);
                options.mark_saved();
            } else {
                data_set(data_key, value);
                options.mark_unsaved();
            }
        }
        function update_from_storage() {
            if (data.hasOwnProperty(data_key)) {
                options.set(data[data_key]);
            } else {
                options.set(orig_value);
            }
            update();
        }
        update_from_storage();
        storage_listeners.push(update_from_storage);
        return update;
    }

    $('dd[data-type="str"]').each(function () {
        var obj = $(this),
            update;
        update = prepare({
            get: function () { return obj.text(); },
            set: function (value) { return obj.text(value); },
            mark_saved: function () { obj.removeClass('unsaved'); },
            mark_unsaved: function () { obj.addClass('unsaved'); },
            key: obj.attr('data-key')
        });
        obj.addClass('editor-field');
        obj.attr('contentEditable', true);
        obj.on('focus blur keypress keyup click paste', update);
    });

    $('dd[data-type="select-one"]').each(function () {
        var obj = $(this),
            update,
            attrs,
            val,
            i,
            options = {},
            rev_options = {},
            hide_menu = null;
        attrs = obj.attr('data-options').split(';');
        for(i = 0; i < attrs.length; i += 1) {
            val = attrs[i].split('=');
            options[val[0]] = val[1];
            rev_options[val[1]] = val[0];
        }
        update = prepare({
            get: function () { return rev_options[obj.text()]; },
            set: function (value) { return obj.text(options[value]); },
            mark_saved: function () { obj.removeClass('unsaved'); },
            mark_unsaved: function () { obj.addClass('unsaved'); },
            key: obj.attr('data-key')
        });
        obj.addClass('editor-field');
        obj.on('click', function (event) {
            var menu,
                item;
            obj.addClass('dropdown open');
            if (hide_menu) {
                hide_menu();
            } else {
                menu = $('<ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu"></ul>').appendTo( "body" );
                for(i = 0; i < attrs.length; i += 1) {
                    (function (value, text) {
                        if (text != obj.text()) {
                            item = $('<li><a></a></li>');
                            item.find('a').text(text);
                            item.click(function (event) {
                                obj.text(text);
                                update();
                                hide_menu();
                                event.stopPropagation();
                            });
                            menu.append(item);
                        }
                    }).apply(this, attrs[i].split('='));
                }
                obj.append(menu);
                hide_menu = function () {
                    menu.remove()
                    $(document).unbind('click', hide_menu);
                    hide_menu = null;
                };
                $(document).bind('click', hide_menu);
                event.stopPropagation();
            }
        });
    });
};
