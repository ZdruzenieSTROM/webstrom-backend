jQuery.validator.addMethod("firstPassword", function (value, element) {
    return this.optional(element) || value.length >= 8;
}, "Heslo musí mať minimálne 8 znakov.");

jQuery.validator.addMethod("secondPassword", function (value, element) {
    return this.optional(element) || !value || value == $('#id_new_password1').val();
}, "Heslá sa nezhodujú.");

var password_validator = $("form").validate({
    rules: {
        new_password1: {
            required: true,
            firstPassword: true
        },
        new_password2: {
            required: true,
            secondPassword: true
        },
    }
});

$('#id_new_password1, #id_new_password2').change(function (element) {
    password_validator.element(element);
});

$('#id_new_password1').change(function (element) {
    // run validation on new_password2 again
    password_validator.element($("#id_new_password2"));
    $("#id_new_password2").valid();
});