$('document').ready(function() {
    $("#search-button").click(function(e){
        e.preventDefault();
        var error_message = {'asn-option': 'Invalid ASN'};

        search_option = $( "input[name=input-type]:checked" ).attr('id');
        var value = $("#search-input").val();
        var result = false;

        switch (search_option) {
            case 'asn-option':
                result = validateASN(value);
                break;
            case 'name-option':
                if(value.length <= 255){
                    result = true;
                }
            case 'uuid-option':
                if(value.length <= 255){
                    result = true;
                }
            default:
                break;

        }
        if(result){
            $(".invalid-feedback").html("");
            $("#search-input").removeClass("is-invalid");
            $("#search-form").submit();
        }else{
            $(".invalid-feedback").html(error_message[search_option]);
            $("#search_ip").addClass("was-validated");
            $("#search-input").addClass("is-invalid");
        }

    });

    $( "input" ).click(function(e) {
        search_option = $( "input[name=input-type]:checked" ).attr('id');

        $("#search-input").removeClass("is-invalid");
        $(".invalid-feedback").html("");

        switch (search_option) {
            case 'asn-option':
                $("#search-form").attr('action', get_asn);
                $("#search-input").attr('name', 'asn');
                $("#search-input").attr('placeholder', 'Search for ASN...');
                $("#search-input").attr('type', 'number');
                break;

            case 'name-option':
                $("#search-form").attr('action', get_name);
                $("#search-input").attr('name', 'name');
                $("#search-input").attr('placeholder', 'Search ASN by Name...');
                $("#search-input").attr('type', 'text');
                break;

            case 'uuid-option':
                $("#search-form").attr('action', get_uuid);
                $("#search-input").attr('name', 'uuid');
                $("#search-input").attr('placeholder', 'Search Service UUID...');
                $("#search-input").attr('type', 'text');
                break;

            default:
                break;
        }
    });

    function validateASN(number){
        let regex = '[^0-9:]';
        let error = 0;
        if(number.length < 1){
            error += 1;
        }
        if(number.match(regex)){
            return false;
        }
        else if(error === 0){
            return true;
        }
        else if(error !== 0){
            return false;
        }
    }
});
