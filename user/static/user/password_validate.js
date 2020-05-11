jQuery.validator.addMethod("firstPassword", function (value, element) {
    return this.optional(element) || value.length >= 8;
}, "Heslo musí mať minimálne 8 znakov.");

jQuery.validator.addMethod("secondPassword", function (value, element) {
    return this.optional(element) || !value || value == $('#id_new_password1').val();
}, "Heslá sa nezhodujú.");

if (!validator) {
    var validator = $("form").validate();
}

$('#id_new_password1').rules("add", {
    required: true,
    firstPassword: true
});
$('#id_new_password2').rules("add", {
    required: true,
    secondPassword: true
});

$('#id_new_password1, #id_new_password2').change(function (element) {
    validator.element(element);
});

$('#id_new_password1').change(function (element) {
    // run validation on new_password2 again
    validator.element($("#id_new_password2"));
});