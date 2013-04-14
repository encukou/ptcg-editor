/*global prettyPrintOne, angular, */

$.tcg_editor = function (context_name, orig_data) {
    "use strict";
    var localStorage,
        storage_key = "edit_" + context_name,
        data,
        storage_listeners = [],
        display_container,
        display_pre,
        currently_displayed_menu;

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
            searchbox.on('click', function (event) {
                event.stopPropagation();
            }).on('edit keydown keyup', function (event) {
                var term = searchbox.val().toLowerCase(),
                    matching_items = [];
                foreach_array(search_items, function (item) {
                    item.removeClass('implicitly-selected');
                    if (item.attr('data-search-key').indexOf(term) !== -1) {
                        item.slideDown('fast');
                        matching_items.push(item);
                    } else {
                        item.slideUp('fast');
                    }
                });
                if (matching_items.length === 1) {
                    implicitly_selected_item = matching_items[0];
                    implicitly_selected_item.addClass('implicitly-selected');
                } else {
                    implicitly_selected_item = null;
                }
            }).on('keydown', function (event) {
                if (event.which === 13 && implicitly_selected_item) {
                    implicitly_selected_item.trigger('click');
                }
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

    angular.module('tcg', []);

    angular.module('tcg').controller('tcgCardCtrl', function ($scope) {
        var card = {},
            orig_card = {};
        $scope.card = card;
        $scope.orig_card = orig_card;
        foreach_obj(orig_data, function (key, value) {
            card[key] = value;
            orig_card[key] = JSON.parse(JSON.stringify(value));
        });
    });

    angular.module('tcg').directive('tcgStr', function () {
        return function (scope, element, attrs) {
            element = $(element);
            element.attr('contentEditable', true);
            scope.$watch(attrs.tcgStr, function (value) {
                if (element.text() !== value) {
                    element.text(value);
                }
            });
            element.on('focus blur keypress keyup click paste', function () {
                scope.$apply(attrs.tcgStr + '=' + JSON.stringify(element.text()));
            });
        };
    });

    angular.module('tcg').directive('tcgEnum', function () {
        return function (scope, element, attrs) {
            var sorted_options = JSON.parse(attrs.options),
                options = {};
            element = $(element);
            foreach_array(sorted_options, function (value) {
                options[value[0]] = value[1];
            });
            scope.$watch(attrs.tcgEnum, function (value) {
                if (value === null) {
                    value = '';
                }
                if (options.hasOwnProperty(value)) {
                    element.text(options[value]);
                } else {
                    element.text(value);
                }
            });
            element.on('click', function (event) {
                popup_menu(event, element, function () {
                    var result = [],
                        current = scope.$eval(attrs.tcgEnum);
                    foreach_array(sorted_options, function (value_text) {
                        var item,
                            value = value_text[0],
                            text = value_text[1];
                        if (!value) {
                            value = null;
                        }
                        item = make_menu_item(text, function () {
                            scope.$apply(attrs.tcgEnum + '=' + JSON.stringify(value));
                        }, text.toLowerCase());
                        result.push(item);
                        if (current === value || (!current && !value)) {
                            item.addClass('disabled');
                        }
                    });
                    if (attrs.tcgEnumRemove) {
                        result.push('<li class="divider"></li>');
                        result.push(make_menu_item('Remove ' + current, function () {
                            scope.$apply(attrs.tcgEnumRemove);
                        }));
                    }
                    return result;
                });
            });
        };
    });

    angular.module('tcg').directive('tcgTags', function ($compile) {
        return function (scope, element, attrs) {
            var sorted_options = JSON.parse(attrs.options),
                options = {};
            element = $(element);
            foreach_array(sorted_options, function (value) {
                options[value[0]] = value[1];
            });
            function reset() {
                var elem;
                element.empty();
                elem = $("<span>");
                elem.attr('ng-repeat', 'item in ' + attrs.tcgTags);
                elem.append($("<span data-ng-hide='$first'></span>").text(element.attr('data-display-separator')));
                elem.append($("<span data-ng-bind='item' data-tcg-enum-remove='1'></span>")
                    .attr('data-options', attrs.options)
                    .attr('data-tcg-enum', attrs.tcgTags + '[$index]')
                    .attr('data-tcg-enum-remove', attrs.tcgTags + '.splice($index, 1)')
                    );
                element.append($compile(elem)(scope));
                element.append($('<span class="action-button">+</span>').on('click', function (event) {
                    popup_menu(event, element, function () {
                        var result = [];
                        foreach_array(sorted_options, function (value_text) {
                            var value = value_text[0],
                                text = value_text[1];
                            result.push(make_menu_item(text, function () {
                                scope.$apply(function () {
                                    if (!scope.$eval(attrs.tcgTags)) {
                                        scope.$eval(attrs.tcgTags + '=[]');
                                    }
                                    scope.$eval(attrs.tcgTags + '.push(' + JSON.stringify(value) + ')');
                                });
                            }, text.toLowerCase()));
                        });
                        return result;
                    });
                }));
            }
            reset();
            scope.$watch(attrs.tcgTags, reset, true);
        };
    });

    angular.module('tcg').directive('tcgShowModified', function () {
        return function (scope, element, attrs) {
            element = $(element);
            element.addClass('editor-field');
            scope.$watch('card.' + attrs.tcgShowModified, function (value) {
                var now = scope.$eval('card.' + attrs.tcgShowModified),
                    orig = scope.$eval('orig_card.' + attrs.tcgShowModified);
                if (JSON.stringify(now) === JSON.stringify(orig)) {
                    element.removeClass('unsaved');
                } else {
                    element.addClass('unsaved');
                }
            }, true);
        };
    });

    angular.module('tcg').directive('tcgDiffHide', function () {
        return function (scope, element, attrs) {
            element = $(element);
            scope.$watch('card', function (value) {
                if (JSON.stringify(scope.card) === JSON.stringify(scope.orig_card)) {
                    element.css('display', 'none');
                } else {
                    element.css('display', 'block');
                }
            }, true);
        };
    });

    angular.module('tcg').directive('tcgDiff', function () {
        return function (scope, element, attrs) {
            element = $(element);
            scope.$watch('card', function (value) {
                var diff = {};
                function add_to_diff(key) {
                    var now, orig;
                    if (!diff.hasOwnProperty(key)) {
                        now = JSON.stringify(scope.card[key]);
                        orig = JSON.stringify(scope.orig_card[key]);
                        if (now !== orig) {
                            diff[key] = scope.card[key];
                        }
                    }
                }
                foreach_obj(scope.card, add_to_diff);
                foreach_obj(scope.orig_card, add_to_diff);
                $(element).html(prettyPrintOne(JSON.stringify(diff, null, 4), null, true));
            }, true);
        };
    });

/*****************************************************************************/


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
    }
    load_from_storage();
    $(window).bind('storage', load_from_storage);
    function data_save() {
        if (is_empty(data)) {
            localStorage.removeItem(storage_key);
        } else {
            localStorage.setItem(storage_key, JSON.stringify(data));
        }
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
            orig_value = orig_data[options.key];
        function update(value) {
            if (value === undefined) {
                value = options.get();
            } else {
                options.set(value);
            }
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

    $('dd[data-type="int"]').each(function () {
        var obj = $(this),
            container = $('<span class="the-value"></span>'),
            orig_value,
            update,
            start_y,
            start_value,
            moving = false,
            slider_container,
            step = parseInt(obj.attr('data-step'), 10) || 1;
        orig_value = parseInt(obj.text(), 10);
        obj.empty();
        obj.append(container);
        container.text(orig_value);
        function get() {
            var text = container.text(),
                value;
            value = parseInt(container.text(), 10);
            if (typeof value === 'number' && !isNaN(value)) {
                return Math.round(value / step, 10) * step;
            }
            return null;
        }
        function get_number() {
            var value = get();
            if (value === null) {
                return orig_value;
            }
            return value;
        }
        function set(value) {
            var target;
            if (value === null) {
                if (container.is(":focus")) {
                    target = '';
                } else {
                    target = 'N/A';
                }
            } else {
                target = String(value);
            }
            if (target !== container.text()) {
                container.text(target);
            }
        }
        obj.addClass('editor-field');
        update = prepare({
            get: get,
            set: set,
            mark_saved: function () { obj.removeClass('unsaved'); },
            mark_unsaved: function () { obj.addClass('unsaved'); },
            key: obj.attr('data-key')
        });

        container.attr('contentEditable', true);
        container.on('focus blur click paste', function () {
            update(get());
        });

        obj.append($('<span class="action-button">▾</span>').on('click', function () {
            update(get_number() - step);
        }));
        obj.append($('<span class="action-button slider">⇅</span>').draggable({
            axis: "y",
            start: function (event) {
                obj.addClass('shown');
                start_y = event.pageY;
                start_value = get_number();
                $(this).css('cursor', '-moz-grabbing');
            },
            drag: function (event) {
                update(parseInt(start_value / step + (start_y - event.pageY) / 10, 10) * step);
            },
            stop: function () {
                obj.removeClass('shown');
                $(this).css('cursor', '-moz-grab');
            },
            revert: true,
            revertDuration: 0,
            distance: 0,
            delay: 0
        }).css('cursor', '-moz-grab'));
        obj.append($('<span class="action-button">▴</span>').on('click', function () {
            update(get_number() + step);
        }));
        if (obj.attr('nullable')) {
            obj.append($('<span class="action-button">×</span>').on('click', function () {
                update(null);
            }));
        }
    });
};
