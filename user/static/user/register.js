function removeOptions(select) {
    while (select.length > 1) {
        select.remove(select.length-1);
    }
}

function setOptions(select, options) {
    var length = options.length;
    for (i = 0; i < length; i++){
        var option = document.createElement('option');
        option.value = options[i]['pk'];
        option.innerHTML = options[i]['name'];
        select.add(option);
    }
}

$('#id_county').change(function() {
    var select = $('#id_district')[0];
    removeOptions(select);
    if ($( this ).val()) {
        $.ajax({
            url: filter_district_url.replace('0', $( this ).val())
        }).done(function( data ) {
            setOptions(select, data);
        });
    }
});


$('#id_district').change(function() {
    var select = $('#id_school')[0];
    removeOptions(select);
    if ($( this ).val()) {
        $.ajax({
            url: filter_school_url.replace('0', $( this ).val())
        }).done(function( data ) {
            setOptions(select, data);
        });
    }
});