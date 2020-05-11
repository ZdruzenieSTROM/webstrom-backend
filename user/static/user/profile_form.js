////////// filling selects for school

var selectedDistrict = null;
var selectedSchool = null;
var selectedSchoolName = null;

$(document).ready(function () {
    $('#div_id_school_info').hide();
    $('#id_school_name').addClass("requiredField");

    selectedDistrict = $('#id_district').val();
    selectedSchool = $('#id_school').val();
    selectedSchoolName = $('#id_school_name').val();
    if ($('#id_school').val() === "1") {    // without school
        $('#id_school_not').prop('checked', true);
        $("#id_school_not").change();
        selectedSchool = null;
        selectedSchoolName = null;
    } else {
        $('#id_grade option[value="13"]').attr('disabled', true);

        if ($('#id_school').val() === "0") { // school not found
            $('#id_school_not_found').prop('checked', true);
            $("#id_school_not_found").change();
            selectedSchool = null;
            selectedSchoolName = null;
        } else {
            if (selectedDistrict) {
                $('#id_county').change();
            } else {
                $("#id_district").prop('disabled', true);
                $("#id_school_name").prop('disabled', true);
                $("#id_school_not_found").prop('disabled', true);
            }
        }
    }
});

$("#id_school_not").change(function () {
    if ($(this).is(":checked")) {
        $('#div_id_school_info').hide();

        $("#id_county").val(null);
        $("#id_county").prop('disabled', true);

        $("#id_district").val(0);
        $("#id_district").prop('disabled', true);

        $("#id_school").val(1);
        $("#id_school_name").val('Bez školy');
        $("#id_school_name").prop('disabled', true);
        $("#id_school_not_found").prop('disabled', true);

        $('#id_grade option[value="13"]').attr('disabled', false);
        $("#id_grade").val(13);
        $('#id_grade option:not(:selected)').attr('disabled', true);
    } else {
        $('#div_id_school_info').hide();

        $("#id_county").prop('disabled', false);

        $("#id_school").val(null);
        $("#id_school_name").val(null);
        $("#id_school_name").prop('disabled', true);

        $('#id_grade option:not(:selected)').attr('disabled', false);
        $('#id_grade option[value="13"]').attr('disabled', true);
        $("#id_grade").val(null);
    }
})

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

// update of possible districts values
$('#id_county').change(function () {
    // remove values of districts before refilling it
    removeOptions($('#id_district')[0]);
    var value = $(this).val();
    if (value) {    // if court is selected, refill districts
        $.ajax({
            url: filter_district_url.replace('0', $(this).val())
        }).done(function (data) {
            setOptions($('#id_district')[0], data);
            // if it is "zahraničie", set default district or enable district's select
            if (value === "9") {
                $('#id_district').val("901");
                $("#id_district").prop('disabled', true);
            } else {
                $("#id_district").prop('disabled', false);
            }
            if (selectedDistrict) {     // set initial data if reopened form
                $('#id_district').val(selectedDistrict);
                selectedDistrict = null;
            }
            $('#id_district').change();     // trigger change event
        });
    } else {       // if calue wasn't set, disable next select and also trigger change event
        $('#id_district').change();
        $("#id_district").prop('disabled', true);
    }
});

// update of possible school values
var schools = [];
var accentMap = {
    "á": "a",
    "ä": "a",
    "č": "c",
    "ď": "d",
    "é": "e",
    "í": "i",
    "ĺ": "l",
    "ľ": "l",
    "ň": "n",
    "ó": "o",
    "ô": "o",
    "ŕ": "r",
    "š": "s",
    "ť": "t",
    "ú": "u",
    "ý": "y",
    "ž": "z",
    "Ǎ": "a",
    "Ä": "a",
    "Č": "c",
    "Ď": "d",
    "É": "e",
    "Í": "i",
    "Ĺ": "l",
    "Ľ": "l",
    "Ň": "n",
    "Ó": "o",
    "Ô": "o",
    "Ŕ": "r",
    "Š": "s",
    "Ť": "t",
    "Ú": "u",
    "Ý": "y",
    "Ž": "z"
};
function normalize(term) {
    var ret = "";
    for (var i = 0; i < term.length; i++) {
        ret += accentMap[term.charAt(i)] || term.charAt(i);
    }
    return ret;
};
$('#id_district').change(function () {
    // remove old values because of new district
    $('#id_school').val(null);
    $('#id_school_name').val(null);
    $("#id_school_not_found").prop("checked", false);
    if ($(this).val()) {    // if district is selected, refill schools
        $.ajax({
            url: filter_school_url.replace('0', $(this).val())
        }).done(function (data) {
            schools = data;
            $("#id_school_name").prop('disabled', false);
            $("#id_school_not_found").prop('disabled', false);
            $("#id_school_name").autocomplete({
                minLength: 0,
                source: function (request, response) {
                    var matcher = new RegExp($.ui.autocomplete.escapeRegex(request.term), "i");
                    response($.grep(schools, function (value) {
                        value = value.label || value.value || value;
                        return matcher.test(value) || matcher.test(normalize(value));
                    }));
                },
                focus: function (event, ui) {
                    return false;
                },
                select: function (event, ui) {
                    $("#id_school").val(ui.item.value);
                    $("#id_school_name").val(ui.item.label);
                    return false;
                }
            })
                .autocomplete("instance")._renderItem = function (ul, item) {
                    return $("<li>")
                        .append("<div>" + item.label + "</div>")
                        .appendTo(ul);
                };
            if (selectedSchoolName) {     // set initial data if reopened form
                $('#id_school').val(selectedSchool);
                $('#id_school_name').val(selectedSchoolName);
                selectedSchool = null;
                selectedSchoolName = null;
            } else if (selectedSchool === "0") {
                $("#id_school_not_found").prop('checked', true);
                $("#id_school_not_found").change();
            }
        });
    } else {
        $("#id_school_name").prop('disabled', true);
        $("#id_school_not_found").prop('disabled', true);
    }
});

function chechAvailableSchools(school) {
    const result = schools.find(({ label }) => label === school);
    if (!result) {
        $("#id_school").val(null);
        $("#id_school_name").val(null);
    }
}

$('#id_school_name').change(function () {
    chechAvailableSchools($("#id_school_name").val());
    $('#div_id_school_info').hide();
})

$("#id_school_not_found").change(function () {
    if ($(this).is(":checked")) {
        $('#div_id_school_info').show();
        $("#id_school").val(0);
        $("#id_school_name").val('Iná škola');
        $("#id_school_name").prop('disabled', true);
        $("#id_school_not").prop('disabled', true);
    } else {
        $('#div_id_school_info').hide();
        $("#id_school").val(null);
        $("#id_school_name").val(null);
        $("#id_school_name").prop('disabled', false);
        $("#id_school_not").prop('disabled', false);
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
    return this.optional(element) || value.length >= 8;
}, "Heslo musí mať minimálne 8 znakov.");

jQuery.validator.addMethod("secondPassword", function (value, element) {
    return this.optional(element) || !value || value == $('#id_password1').val();
}, "Heslá sa nezhodujú.");

var validator = $("form").validate({
    rules: {
        email: {
            required: true,
            email: true
        },
        phone: {
            required: false,
            phone: true
        },
        parent_phone: {
            required: false,
            phone: true
        },
        school_name: {
            required: true
        },
    }
});

$('#id_email, #id_phone, #id_parent_phone').change(function (element) {
    validator.element(element);
});

$('form').on("submit", function () {
    if ($('#phone').val()) $('#phone').val(myTrim($('#phone').val()));
    if ($('#parent_phone').val()) $('#parent_phone').val(myTrim($('#parent_phone').val()));
})