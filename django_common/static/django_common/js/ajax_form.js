/*
* Helper class for forms, mostly helps with ajax form submits etc.
* 
* + Assumes there is an image with class 'ajax-indicator' on the page somewhere.
*/
function FormHelper(form_id) {
    if (form_id) {
        this.__form = $('#' + form_id);
    } else {
        this.__form = $('form');
    }
}

FormHelper.prototype.bind_for_ajax = function(success_handler, failure_handler) {
    var self=this;
    this.__form.submit(function() {
       self.ajax_submit(success_handler, failure_handler);
       return false;
    });
}

FormHelper.prototype.ajax_submit = function(success_handler, failure_handler) {
    this.__clear_errors();
    this.__form.find('img.ajax-indicator').show();
    
    var self=this;
    $.post(this.__form.attr('action'), this.__form.serialize(), 
        function(data) {
            if (data.success) {
                success_handler(data);
            } else if (failure_handler != undefined) {
                failure_handler(data);
            } else {
                self.__fill_errors(data);
            }
            self.__form.find('img.ajax-indicator').hide();
        },
    "json");
    
    this.__toggle_inputs_disable_state(true);
};

FormHelper.prototype.__fill_errors = function(data) {
    if (data.form != undefined) {
        for (var field in data.form.errors) {
            if (field != 'non_field_errors') {
                this.__form.find('#id_error_container_' + field).html(data.form.errors[field]);
                this.__form.find('#id_' + field + '_container').addClass('errorRow').addClass('errRow');
            } else {
                this.__form.prepend('<div id="id_non_field_errors" class="error">' +
                data.form.errors['non_field_errors'] + '</div>');
            }
        }
    }
    if (data.errors.length > 0) {
        this.__form.prepend('<div id="id_non_field_errors" class="error">' +
            data.errors + '</div>');
    }

    this.__toggle_inputs_disable_state(false);
};

FormHelper.prototype.__toggle_inputs_disable_state = function(disable) {
    this.__form.find('input, select').attr('disabled', disable);
}

FormHelper.prototype.__clear_errors = function() {
    this.__form.find('div.error_container').empty();
    this.__form.find('div.formRow').removeClass('errorRow').removeClass('errRow');
    $('#id_non_field_errors').remove();
};
