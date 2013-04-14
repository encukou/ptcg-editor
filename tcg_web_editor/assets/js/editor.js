/*global prettyPrintOne, angular, */

$.tcg_editor = function (context_name, orig_data) {
    "use strict";
    var localStorage,
        storage_key = "edit_" + context_name,
        storage_listeners = [],
        display_container,
        display_pre,
        currently_displayed_menu,
        tcg;

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

    function action_button(text, onclick) {
        var elem = $('<span class="action-button"></span>');
        elem.text(text);
        if (onclick) {
            elem.on('click', onclick);
        }
        return elem;
    }

    tcg = angular.module('tcg', []);

    tcg.controller('tcgCardCtrl', function ($scope, tcgLocalStorage) {
        $scope.card = {};
        $scope.orig_card = {};
        $.extend(true, $scope.card, orig_data);
        $.extend(true, $scope.orig_card, orig_data);
        tcgLocalStorage.watch($scope);
    }).$inject = ['tcgLocalStorage'];

    tcg.directive('tcgStr', function () {
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

    tcg.directive('tcgEnum', function () {
        return function (scope, element, attrs) {
            var sorted_options = JSON.parse(attrs.options || '[]'),
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
                            if (attrs.tcgEnumNull && scope.$eval(attrs.tcgEnumNull).length === 0) {
                                scope.$apply(attrs.tcgEnumNull + '=null');
                            }
                        }));
                    }
                    return result;
                });
            });
        };
    });

    tcg.directive('tcgTags', function ($compile) {
        return function (scope, element, attrs) {
            var sorted_options = JSON.parse(attrs.options),
                options = {};
            element = $(element);
            foreach_array(sorted_options, function (value) {
                options[value[0]] = value[1];
            });
            scope.$watch(attrs.tcgTags, function () {
                var elem;
                element.empty();
                elem = $("<span>");
                elem.attr('ng-repeat', 'item in ' + attrs.tcgTags);
                elem.append($("<span data-ng-hide='$first'></span>").text(element.attr('data-display-separator')));
                elem.append($("<span data-ng-bind='item' data-tcg-enum-remove='1'></span>")
                    .attr('data-options', attrs.options)
                    .attr('data-tcg-enum', attrs.tcgTags + '[$index]')
                    .attr('data-tcg-enum-remove', attrs.tcgTags + '.splice($index, 1)')
                    .attr('data-tcg-enum-null', attrs.tcgTags)
                    );
                element.append($compile(elem)(scope));
                element.append(action_button('+', function (event) {
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
            }, true);
        };
    });

    tcg.directive('tcgInt', function () {
        return function (scope, element, attrs) {
            var container = $('<span class="the-value"></span>'),
                start_y,
                start_value,
                step = parseInt(attrs.step, 10) || 1;
            function get_number() {
                var value = scope.$eval(attrs.tcgInt);
                if (typeof value === 'number') {
                    return value;
                }
                return 0;
            }
            element = $(element);
            element.empty();
            element.append(container);
            element.append(action_button('▾', function (event) {
                scope.$apply(function () {
                    scope.$eval(attrs.tcgInt + '=' + JSON.stringify(get_number()) + '-1');
                });
            }));
            element.append(action_button('⇅').addClass('slider').draggable({
                axis: "y",
                start: function (event) {
                    element.parents("*[data-tcg-show-modified]").add(element).addClass('shown');
                    start_y = event.pageY;
                    start_value = get_number();
                    $(this).css('cursor', '-moz-grabbing');
                },
                drag: function (event) {
                    var value = parseInt(start_value / step + (start_y - event.pageY) / 10, 10) * step;
                    scope.$apply(attrs.tcgInt + '=' + value);
                },
                stop: function () {
                    element.parents("*[data-tcg-show-modified]").add(element).removeClass('shown');
                    $(this).css('cursor', '-moz-grab');
                },
                revert: true,
                revertDuration: 0,
                distance: 0,
                delay: 0
            }).css('cursor', '-moz-grab'));
            element.append(action_button('▴', function (event) {
                scope.$apply(function () {
                    scope.$eval(attrs.tcgInt + '=' + JSON.stringify(get_number()) + '+1');
                });
            }));
            if (attrs.nullable) {
                element.append(action_button('×', function (event) {
                    scope.$apply(attrs.tcgInt + '=' + JSON.stringify(null));
                }));
            }
            scope.$watch(attrs.tcgInt, function () {
                var value = scope.$eval(attrs.tcgInt);
                if (typeof value === 'number') {
                    container.text(value);
                } else {
                    container.text('N/A');
                }
            });
        };
    });

    tcg.directive('tcgDamageMods', function ($compile) {
        return function (scope, element, attrs) {
            var replacement;
            element = $(element);
            element.empty();
            replacement = $('<div data-ng-repeat="mod in ' + attrs.tcgDamageMods + '"></div>');
            replacement.append($('<dl class="row-fluid"></dl>')
                .append($('<dt class="span2"></dt>')
                    .attr('data-ng-bind', "(mod.operation == '-') && 'Resistance' || 'Weakness'")
                    .attr('data-tcg-remove-from', attrs.tcgDamageMods))
                .append($('<dd class="span4" data-tcg-show-modified="' + attrs.tcgDamageMods + '[$index]"></dd>')
                    .append($('<span data-tcg-enum="mod.type"></span>')
                        .attr('data-options', $('*[data-tcg-show-modified=types]').attr('data-options')))
                    .append(': ')
                    .append($('<span data-tcg-enum="mod.operation"></span>')
                        .attr('data-options', JSON.stringify([["-", "-"], ["+", "+"], ["×", "×"]])))
                    .append($('<span data-tcg-int="mod.amount"></span>'))
                    ));
            element.append($compile(replacement)(scope));
        };
    });

    tcg.directive('tcgRemoveFrom', function ($compile) {
        return function (scope, element, attrs) {
            element = $(element);
            element.on('click', function (event) {
                popup_menu(event, element.parent(), function () {
                    return [
                        make_menu_item('Remove this ' + element.text(), function () {
                            console.log(attrs.tcgRemoveFrom + '.splice($index, 1)',  scope.$eval('$index'));
                            scope.$apply(attrs.tcgRemoveFrom + '.splice($index, 1)');
                        })
                    ];
                });
            });
        };
    });

    tcg.directive('tcgAdder', function () {
        return function (scope, element, attrs) {
            element = $(element);
            element.attr('data-tcg-show-modified', '1');
            element.css('cursor', 'default');
            element.append(action_button('+', function (event) {
                popup_menu(event, element, function () {
                    return [
                        make_menu_item('Add Weakness', function () {
                            scope.$apply(function () {
                                scope.card['damage modifiers'].push({
                                    amount: 2,
                                    operation: '×',
                                    type: 'Fire'
                                });
                            });
                        }),
                        make_menu_item('Add Resistance', function () {
                            scope.$apply(function () {
                                scope.card['damage modifiers'].push({
                                    amount: 20,
                                    operation: '-',
                                    type: 'Fire'
                                });
                            });
                        })
                    ];
                });
            }));
        };
    });

    tcg.directive('tcgShowModified', function () {
        return function (scope, element, attrs) {
            var exp = attrs.tcgShowModified.replace(/^card[.]?/, '');
            if (exp.indexOf('[') !== 0) {
                exp = '.' + exp;
            }
            element = $(element);
            element.addClass('editor-field');
            scope.$watch('card' + exp, function (value) {
                var now,
                    orig;
                now = scope.$eval('card' + exp);
                orig = scope.$eval('orig_card' + exp);
                if (angular.toJson(now) === angular.toJson(orig) || (now === null && orig === undefined)) {
                    element.removeClass('unsaved');
                } else {
                    element.addClass('unsaved');
                }
            }, true);
        };
    });

    tcg.directive('tcgDiffHide', function () {
        return function (scope, element, attrs) {
            element = $(element);
            scope.$watch('card', function (value) {
                if (angular.toJson(scope.card) === angular.toJson(scope.orig_card)) {
                    element.css('display', 'none');
                } else {
                    element.css('display', 'block');
                }
            }, true);
        };
    });

    function make_diff(now, orig) {
        var diff = {};
        now = angular.copy(now);
        function add_to_diff(key) {
            var val_now, val_orig;
            if (key.indexOf('$') !== 0 && !diff.hasOwnProperty(key)) {
                val_now = angular.toJson(now[key]);
                val_orig = angular.toJson(orig[key]);
                if (val_now !== val_orig) {
                    if (now[key] !== null || orig[key] !== undefined) {
                        if (val_now === undefined) {
                            diff[key] = null;
                        } else {
                            diff[key] = now[key];
                        }
                    }
                }
            }
        }
        foreach_obj(now, add_to_diff);
        foreach_obj(orig, add_to_diff);
        return diff;
    }

    function apply_diff(obj, diff) {
        foreach_obj(diff, function (key, value) {
            if (value === null) {
                delete obj[key];
            } else {
                obj[key] = value;
            }
        });
    }

    tcg.directive('tcgDiff', function () {
        return function (scope, element, attrs) {
            element = $(element);
            scope.$watch('card', function (value) {
                var diff = angular.toJson(make_diff(scope.card, scope.orig_card), true);
                $(element).html(prettyPrintOne(diff, null, true));
            }, true);
        };
    });

    function load_from_storage(key) {
        var data;
        try {
            data = JSON.parse(localStorage.getItem(key));
            if (data === null) {
                data = {};
            }
        } catch (e) {
            data = {};
        }
        return data;
    }

    tcg.factory('tcgLocalStorage', function () {
        var tcgLocalStorage = {
            watch: function (scope) {
                var last = scope;

                apply_diff(scope.card, load_from_storage(storage_key));

                $(window).bind('storage', function (event) {
                    scope.$apply(function () {
                        scope.card = $.extend(true, {}, scope.orig_card);
                        apply_diff(scope.card, load_from_storage(storage_key));
                    });
                });

                scope.$watch('card', function (value) {
                    var diff = make_diff(scope.card, scope.orig_card);
                    if (is_empty(diff)) {
                        localStorage.removeItem(storage_key);
                    } else {
                        localStorage.setItem(storage_key, JSON.stringify(diff));
                    }
                }, true);
            }
        };
        return tcgLocalStorage;
    });
};
