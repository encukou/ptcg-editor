$.tcg_editor = function (context_name) {
    "use strict";
    var localStorage,
        storage_key = "edit_" + context_name,
        data,
        storage_listeners = [];

    function log() {
        if (window.console) {
            foreach_array(arguments, function (thing) {
                window.console.log(thing);
            });
        }
    }

    function foreach_array(array, func, filter) {
        var i,
            result = [];
        if (!func) {
            func = function (v) {
                return v;
            }
        }
        if (!filter) {
            filter = function (v) {
                return true;
            }
        }
        for (i = 0; i < array.length; i += 1) {
            if (filter(array[i])) {
                result.push(func(array[i], i));
            }
        }
        return result;
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

    var display_container = $('<div class="container"></div>');
    display_container.append('<h2>Your unsaved edits</h2>');
    $('#edittabs-json').append(display_container);
    display_container.hide();
    var display_pre = $('<pre></pre>');
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
        } else {
            return +attr;
        }
    }

    function in_array(array, thing) {
        var i;
        for (i = 0; i < array.length; i += 1) {
            if (array[i] == thing) {
                return true;
            }
        }
        return false;
    }

    $('dd[data-type="select"]').each(function () {
        var obj = $(this),
            update,
            attrs,
            val,
            i,
            options = {},
            rev_options = {},
            min,
            max,
            sep;
        min = num_from_attr(obj.attr('data-min'), 0);
        max = num_from_attr(obj.attr('data-max'), 0);
        sep = obj.attr('data-separator') || "`$dummy$`";
        attrs = obj.attr('data-options').split(';');
        foreach_array(attrs, function (pair) {
            val = pair.split('=');
            options[val[0]] = val[1];
            rev_options[val[1]] = val[0];
        });
        function get() {
            var text = obj.text();
            if (text === "&nbsp;") {
                return [];
            }
            return foreach_array(obj.text().split(sep), function (word) {
                return rev_options[word];
            }).join('');
        }
        function set(value) {
            if (value.length == 0) {
                return "&nbsp;";
            }
            obj.text(foreach_array(value, function(letter) {
                return options[letter];
            }).join(sep));
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
            var item;
            menu_handler(event, obj, function (hide_menu) {
                var result_a = [],
                    result_b = [],
                    current = get();
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
                foreach_array(attrs, function (attr) {
                    var value = attr.split('=')[0],
                        text = attr.split('=')[1];
                    if (current != value && min) {
                        add_item(result_a, "= " + text, value);
                    }
                    if (in_array(current, value)) {
                        if (current.length > min) {
                            add_item(
                                result_b,
                                "− " + text,
                                foreach_array(
                                    current, null, function(v) {
                                        return v != value;
                                    }
                                ).join('')
                            );
                        }
                    } else {
                        if (!max || current.length < max) {
                            add_item(result_b, "+ " + text, current + value);
                        }
                    }
                });
                if (result_a.length && result_b.length) {
                    result_a.push($('<li class="divider"></li>'));
                    foreach_array(result_b, function (item) {
                        result_a.push(item);
                    });
                    return result_a;
                } else if (result_a.length) {
                    return result_a;
                } else {
                    return result_b;
                }
            });
        });
    });
};
