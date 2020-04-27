////////// filling selects for school

function removeOptions(select) {
    while (select.length > 1) {
        select.remove(select.length - 1);
    }
}

function setOptions(select, options) {
    var length = options.length;
    for (i = 0; i < length; i++) {
        var option = document.createElement('option');
        option.value = options[i]['pk'];
        option.innerHTML = options[i]['name'];
        select.add(option);
    }
}

$('#id_county').change(function () {
    var select = $('#id_district')[0];
    removeOptions(select);
    if ($(this).val()) {
        $.ajax({
            url: filter_district_url.replace('0', $(this).val())
        }).done(function (data) {
            setOptions(select, data);
        });
    }
});

$('#id_district').change(function () {
    var select = $('#id_school')[0];
    removeOptions(select);
    if ($(this).val()) {
        $.ajax({
            url: filter_school_url.replace('0', $(this).val())
        }).done(function (data) {
            setOptions(select, data);
        });
    }
});

////////// JS modifications of register form

$(document).ready(function(){ 
    $('#div_id_school_info').hide();
});

$('#id_school').change(function(){
    if ($( this ).val() == 0) {
        $('#div_id_school_info').show();
    } else {
        $('#div_id_school_info').hide();
    }
})

////////// JS validations of form during completion

// rewrite default email validation
jQuery.validator.addMethod("email", function (value, element) {
    return this.optional(element) || /^[a-zA-Z0-9.!#$%&*+\/=?^_`{|}~-]+@[a-zA-Z0-9.!#$%&*+\/=?^_`{|}~-]+\.[a-zA-Z]{2,63}$/.test(value);
}, "Zadajte platnú e-mailovú adresu.");

function myTrim(string) {
    return string.replace(/\s+/g, '');
}

jQuery.validator.addMethod("phone", function (value, element) {
    return this.optional(element) || /^(\+\d{1,3}\d{9})$/.test(myTrim(value));
}, "Zadaj telefónne číslo vo formáte validnom formáte +421 123 456 789 alebo +421123456789.");

jQuery.validator.addMethod("firstPassword", function (value, element) {
    // run validation on password2 again
    $("#id_password2").valid();
    //TODO: check the strength of pasword
    return true;
}, "Heslá sa nezhodujú.");

jQuery.validator.addMethod("secondPassword", function (value, element) {
    return this.optional(element) || !value || value == $('#id_password1').val();
}, "Heslá sa nezhodujú.");

var validator = $("form").validate({
    rules: {
        email: {
            required: true,
            email: true
        },
        password1: {
            required: true,
            firstPassword: true
        },
        password2: {
            required: true,
            secondPassword: true
        },
        phone: {
            required: false,
            phone: true
        },
        parent_phone: {
            required: false,
            phone: true
        },
    }
});

$('#id_email, #id_password1, #id_password2, #id_phone, #id_parent_phone').change(function (element) {
    validator.element( element );
});

$('form').on( "submit", function() {
    if ($('#phone').val()) $('#phone').val(myTrim($('#phone').val()));
    if ($('#parent_phone').val()) $('#parent_phone').val(myTrim($('#parent_phone').val()));
} )