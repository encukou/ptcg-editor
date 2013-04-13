/*global prettyPrintOne */

$.tcg_editor = function (context_name) {
    "use strict";
    var localStorage,
        storage_key = "edit_" + context_name,
        data,
        storage_listeners = [],
        display_container,
        display_pre,
        currently_displayed_menu;

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
            if (JSON.stringify(orig_value) === JSON.stringify(value)) {
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

    function hide_menu() {
        if (currently_displayed_menu) {
            currently_displayed_menu.remove();
            currently_displayed_menu = null;
        }
    }
    $(window.document).bind('click', hide_menu);

    function popup_menu(event, obj, get_items) {
        var items,
            search_items = [],
            menu,
            menu_in,
            searchbox,
            search,
            implicitly_selected_item = null;
        hide_menu();
        obj.addClass('dropdown open');
        menu = $('<div class="dropdown-menu"></div>');
        menu_in = $('<ul class="dropdown-menu-in" role="menu" aria-labelledby="dropdownMenu"></ul>');
        menu_in.css('max-height', '20em');
        menu.append(menu_in);
        items = get_items();
        foreach_array(items, function (item) {
            item = $(item);
            if (item.attr('data-search-key')) {
                menu_in.append(item);
                search_items.push(item);
            } else {
                menu.append(item);
            }
        });
        obj.append(menu);
        currently_displayed_menu = menu;
        event.stopPropagation();

        if (search_items.length > 10) {
            searchbox = $('<input type="search">');
            menu_in.before(searchbox);
            search = function(event) {
                var term = searchbox.val().toLowerCase(),
                    matching_items = [];
                foreach_array(search_items, function(item) {
                    item.removeClass('implicitly-selected');
                    if (item.attr('data-search-key').indexOf(term) !== -1) {
                        item.slideDown('fast');
                        matching_items.push(item)
                    } else {
                        item.slideUp('fast');
                    }
                });
                if (matching_items.length == 1) {
                    implicitly_selected_item = matching_items[0];
                    implicitly_selected_item.addClass('implicitly-selected');
                } else {
                    implicitly_selected_item = null;
                }
            };
            searchbox.on('click', function (event) {
                event.stopPropagation();
            }).on('edit', search).on('keydown', search).on('keyup', search).on('keydown', function (event) {
                if (event.which === 13 && implicitly_selected_item) {
                    implicitly_selected_item.trigger('click');
                };
            });
            searchbox.focus();
        }
    }
    function make_menu_item(text, onclick, search_key) {
        var item;
        item = $('<li><a></a></li>');
        item.find('a').text(text);
        item.click(function (event) {
            onclick();
            hide_menu();
            event.stopPropagation();
        });
        if (search_key) {
            item.attr('data-search-key', search_key);
        }
        return item;
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
            popup_menu(event, obj, function () {
                var result = [],
                    current = get(),
                    item;
                foreach_obj(options, function (value, text) {
                    if (current !== value && (current || value)) {
                        result.push(make_menu_item(text, function () {
                            set(value);
                            update();
                        }));
                    }
                });
                return result;
            });
        });
    });

    $('dd[data-type="tags"]').each(function () {
        var obj = $(this),
            update,
            attrs,
            options,
            values,
            sep,
            container = $('<span>'),
            appender = $('<span class="add">+</span>');
        sep = obj.attr('data-display-separator');
        options = JSON.parse(obj.attr('data-options'));
        values = foreach_array(obj.text().split(sep), null,
                               function (i) {return i.replace(/^\s+|\s+$/g, '')});
        obj.empty();
        obj.append(container);
        function get() {
            return values;
        }
        function set(new_values) {
            values = new_values.slice(0);
            container.empty();
            foreach_array(values, function (value, i) {
                var element = $('<span>'), separator=$('<span>');
                if (i) {
                    separator.text(sep)
                    container.append(separator);
                }
                element.text(value);
                container.append(element);
                element.on('click', function (event) {
                    popup_menu(event, obj, function () {
                        var result = [];
                        foreach_array(options, function (option) {
                            result.push(make_menu_item(option, function () {
                                values[i] = option;
                                set(values);
                                update();
                            }, option.toLowerCase()));
                        }, function (option) {
                            return option !== value;
                        });
                        result.push('<li class="divider"></li>');
                        result.push(make_menu_item('Remove ' + value, function () {
                            values.splice(i, 1);
                            set(values);
                            update();
                        }));
                        return result;
                    });
                });
            });
        }
        obj.addClass('editor-field');
        obj.append(appender);
        appender.on('click', function (event) {
            popup_menu(event, obj, function () {
                var result = [];
                foreach_array(options, function (option) {
                    result.push(make_menu_item(option, function () {
                        values.push(option);
                        set(values);
                        update();
                    }, option.toLowerCase()));
                });
                return result;
            });
        });
        update = prepare({
            get: get,
            set: set,
            mark_saved: function () { obj.removeClass('unsaved'); },
            mark_unsaved: function () { obj.addClass('unsaved'); },
            key: obj.attr('data-key')
        });
    });
};
