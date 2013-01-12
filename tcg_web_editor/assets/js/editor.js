$.tcg_editor = function(context_name) {
    function log() {
        for (var i = 0; i < arguments.length; i++) {
            if(window.console) console.log(arguments[i]);
        }
    }

    function have_html5_storage() {
        try {
            return 'localStorage' in window && window['localStorage'] !== null;
        } catch (e) {
            return false;
        }
    }
    if (!have_html5_storage()) {
        return;
    }

    // http://stackoverflow.com/questions/4994201/is-object-empty
    var hasOwnProp = Object.prototype.hasOwnProperty;
    function is_empty(obj) {
        for (var key in obj) {
            if (hasOwnProp.call(obj, key))    return false;
        }
        return true;
    }

    var storage_key = "edit_" + context_name;
    var data;
    var storage_listeners = [];
    function load_from_storage() {
        try {
            data = JSON.parse(localStorage.getItem(storage_key));
            if (data === null) data = {};
        } catch (e) {
            data = {}
        }
        for (var i = 0; i < storage_listeners.length; i++) {
            storage_listeners[i]();
        }
    }
    load_from_storage();
    $(window).bind('storage', load_from_storage);
    function data_save() {
        if (is_empty(data)) {
            localStorage.removeItem(storage_key);
        }else{
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
        if (key in data) {
            delete data[key];
            data_save();
        }
    }

    function prepare_str() {
        var obj = $(this);
        data_key = obj.attr('data-key');
        obj.attr('contentEditable', true);
        obj.addClass('editor-field');
        var orig_value = obj.text();
        obj.attr('data-origvalue', obj.text());
        function update() {
            if(obj.attr('data-origvalue') == obj.text()) {
                data_remove(data_key);
                obj.removeClass('unsaved');
            }else{
                data_set(data_key, obj.text());
                obj.addClass('unsaved');
            }
        }
        function update_from_storage() {
            if (data_key in data) {
                obj.text(data[data_key]);
            }else{
                obj.text(orig_value);
            }
            update();
        }
        update_from_storage();
        storage_listeners.push(update_from_storage);
        obj.on('focus blur keypress keyup click paste', update);
    }

    $('dd[data-type="str"]').each(prepare_str);
}
