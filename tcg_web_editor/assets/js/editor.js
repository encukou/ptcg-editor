/*global prettyPrintOne */

$.tcg_editor = function (context_name) {
    "use strict";
    var localStorage,
        storage_key = "edit_" + context_name,
        data,
        storage_listeners = [],
        display_container,
        display_pre;

    function foreach_array(array, func, filter) {
        var i,
            result = [];
        if (!func) {
            func = function (v) {
                return v;
            };
        }
        if (!filter) {
            filter = function (v) {
                return true;
            };
        }
        for (i = 0; i < array.length; i += 1) {
            if (filter(array[i])) {
                result.push(func(array[i], i));
            }
        }
        return result;
    }

    function foreach_obj(obj, func, filter) {
        var name;
        if (!func) {
            func = function (v) {
                return v;
            };
        }
        if (!filter) {
            filter = function (v) {
                return true;
            };
        }
        for (name in obj) {
            if (obj.hasOwnProperty(name) && filter(name, obj[name])) {
                func(name, obj[name]);
            }
        }
    }

    function log() {
        if (window.console) {
            foreach_array(arguments, function (thing) {
                window.console.log(thing);
            });
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

    display_container = $('<div class="container"></div>');
    display_container.append('<h2>Your unsaved edits</h2>');
    $('#edittabs-json').append(display_container);
    display_container.hide();
    display_pre = $('<pre></pre>');
    display_pre.appendTo(display_container);
    function show_edits() {
        display_pre.html(prettyPrintOne(JSON.stringify(data, null, 4), null, true));
        if (!is_empty(data)) {
            display_container.show();
        }
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
        foreach_array(storage_listeners, function (listener) {
            listener();
        });
        show_edits();
    }
    load_from_storage();
    $(window).bind('storage', load_from_storage);
    function data_save() {
        if (is_empty(data)) {
            localStorage.removeItem(storage_key);
        } else {
            localStorage.setItem(storage_key, JSON.stringify(data));
        }
        show_edits();
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
        function update() {
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

    function menu_handler(event, obj, get_items) {
        var items,
            menu = null,
            i;
        obj.addClass('dropdown open');
        function hide_menu() {
            if (menu) {
                menu.remove();
                $(window.document).unbind('click', hide_menu);
                menu = null;
            }
        }
        menu = $('<ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu"></ul>');
        items = get_items(hide_menu);
        foreach_array(items, function (item) {
            menu.append(item);
        });
        obj.append(menu);
        $(window.document).bind('click', hide_menu);
        event.stopPropagation();
    }

    function num_from_attr(attr, deflt) {
        if (attr === undefined) {
            return deflt;
        }
        return +attr;
    }

    function in_array(array, thing) {
        var i;
        for (i = 0; i < array.length; i += 1) {
            if (array[i] === thing) {
                return true;
            }
        }
        return false;
    }

    $('dd[data-type="enum"]').each(function () {
        var obj = $(this),
            update,
            attrs,
            val,
            options = {},
            rev_options = {};
        attrs = JSON.parse(obj.attr('data-options'));
        foreach_array(attrs, function (item) {
            var value = item[0],
                text = item[1];
            options[value] = text;
            rev_options[text] = value;
        });
        function get() {
            var rv = rev_options[obj.text()];
            if (!rv) {
                return null;
            }
            return rv;
        }
        function set(value) {
            if (!options[value]) {
                obj.text();
            } else {
                obj.text(options[value]);
            }
        }
        update = prepare({
            get: get,
            set: set,
            mark_saved: function () { obj.removeClass('unsaved'); },
            mark_unsaved: function () { obj.addClass('unsaved'); },
            key: obj.attr('data-key')
        });
        obj.addClass('editor-field');
        obj.on('click', function (event) {
            menu_handler(event, obj, function (hide_menu) {
                var result = [],
                    current = get(),
                    item;
                function add_item(dest, text, result_value) {
                    item = $('<li><a></a></li>');
                    item.find('a').text(text);
                    item.click(function (event) {
                        set(result_value);
                        update();
                        hide_menu();
                        event.stopPropagation();
                    });
                    dest.push(item);
                }
                foreach_obj(options, function (value, text) {
                    if (current !== value && (current || value)) {
                        add_item(result, text, value);
                    }
                });
                return result;
            });
        });
    });
};
