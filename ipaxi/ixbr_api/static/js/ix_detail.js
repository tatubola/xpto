$('document').ready(function() {
    var last_clicked = ''
    var pix_clicked = ''

    //Actions if click to see PIX information
    $(".pix-info").click(function(e){
        last_clicked = pix_clicked;
        pix_clicked = $(this).attr("id");

        /*****************************
        *** AJAX request PIX click ***
        *****************************/
        $.ajax({
            url: '/core/'+code+'/pix-detail/',
            data: {
              'pix': pix_clicked,
            },
            dataType: 'json',
            success: function (data) {
                if (data != {}) {
                    // Function to apply the jQuery logic
                    ShowPIXDataOnRequest(data);
                } else {
                    alert("This PIX doesn't have any info.");
                }
            }
        });
    });

    pix_clicked = '';

    /********************************
    *** Function to show PIX Data ***
    ********************************/
    function ShowPIXDataOnRequest(data){
        // If Last PIX clicked is different of actual click it
        // will append informations bhrought trhought request
        // and show off them witha new style
        if(last_clicked != pix_clicked){
            $(".mlpav4-info-" + pix_clicked).append(data.mlpav4_amount);
            $(".mlpav6-info-" + pix_clicked).append(data.mlpav6_amount);
            $(".bilateral-info-" + pix_clicked).append(data.bilateral_amount);
            $(".cix-info-" + pix_clicked).append(data.cix_amount);

            SwitchAppend(data.switch_set, pix_clicked);

            $(".info-" + pix_clicked).show();

            $("#" + pix_clicked + ", .info-" + pix_clicked).addClass("channel-list");
            $(".icon-" + pix_clicked + "> i").removeClass("fa-chevron-circle-right");
            $(".icon-" + pix_clicked + "> i").addClass("fa-chevron-circle-down");
            // Verify if it is not the first click of user,
            // to not apply this into nothing, because doens't exist last PIX clicked yet.
            if(last_clicked != '') {
                $(".info-" + last_clicked).hide();

                $(".asn-info-" + last_clicked).empty();
                $(".mlpav4-info-" + last_clicked).empty();
                $(".mlpav6-info-" + last_clicked).empty();
                $(".bilateral-info-" + last_clicked).empty();
                $(".switchs-info-" + last_clicked).empty();
                $(".cix-info-" + last_clicked).empty();

                $("#" + last_clicked + ", .info-" + last_clicked).removeClass("channel-list");
                $(".icon-" + last_clicked + "> i").removeClass("fa-chevron-circle-down");
                $(".icon-" + last_clicked + "> i").addClass("fa-chevron-circle-right");
            }
        // Else it is user has clicked in the same PIX,
        // not having been necessity of make a new AJAX request.
        // Just show again the informations.
        } else {
            $(".info-" + pix_clicked).toggle();

            //This if and else is just to fake toggle h6 style
            if(!$(".info-" + pix_clicked).is(':visible')){
                $("#" + last_clicked + ", .info-" + last_clicked).removeClass("channel-list");
                $(".icon-" + last_clicked + "> i").removeClass("fa-chevron-circle-down");
                $(".icon-" + last_clicked + "> i").addClass("fa-chevron-circle-right");

            } else {
                $("#" + pix_clicked + ", .info-" + pix_clicked).addClass("channel-list");
                $(".icon-" + pix_clicked + "> i").removeClass("fa-chevron-circle-right");
                $(".icon-" + pix_clicked + "> i").addClass("fa-chevron-circle-down");
            }
        }
    }

    var last_cix_clicked = ''
    var cix_clicked = ''

    $(".cix-info").click(function(e){
        last_cix_clicked = cix_clicked;
        cix_clicked = $(this).attr("id");

        /*****************************
        *** AJAX request PIX click ***
        *****************************/
        $.ajax({
            url: '/core/'+code+'/cix-detail/',
            data: {
              'uuid': cix_clicked,
            },
            dataType: 'json',
            success: function (data) {
                if (data != {}) {
                    // Function to apply the jQuery logic
                    ShowCIXDataOnRequest(data);
                } else {
                    alert("This PIX doesn't have any info.");
                }
            }
        });
    });

    // Click button search IP
    $("#search-button").click(function(e){
        e.preventDefault();
        var error_message = {'IP': 'Invalid IP', 'Tag': 'Invalid Tag', 'MAC': 'Invalid MAC Address'};

        var search_option = $("#search-options").val();
        var campo = $("#search-input").val();
        var resultado = false;
        switch (search_option) {
            case 'IP':
                $("#search-input").attr('name', 'ip');
                $("#search-form").attr('action', get_ip);
                if(campo.indexOf(".") != -1){
                    resultado = validateIPv4(campo)
                }else{
                    resultado = validateIPv6(campo)
                }
                break;

            case 'Tag':
                $("#search-input").attr('name', 'tag');
                $("#search-form").attr('action', get_tag);
                resultado = validateTag(campo);
                break;

            case 'MAC':
                $("#search-input").attr('name', 'mac');
                $("#search-form").attr('action', get_mac);
                resultado = validateMac(campo);
                break;

            default:
                break;
        }
        if(resultado){
            $(".invalid-feedback").html("");
            $("#search-input").removeClass("is-invalid");
            $("#search-form").submit();
        }else{
            $(".invalid-feedback").html(error_message[search_option]);
            $("#search_ip").addClass("was-validated");
            $("#search-input").addClass("is-invalid");
        }
        return false;
    });

    $("#consulta-mac-button").click(function(e){
        e.preventDefault();

        var field = $("#consulta-input").val();
        var result = false;

        result = validateMac(field)
        if(result){
            $(".invalid-feedback").html("Invalid Mac Address");
            $("#consulta-input").removeClass("is-invalid");
            $("#consulta-form").submit();
        }
        return false;
    });

    cix_clicked = '';

    /********************************
    *** Function to show PIX Data ***
    ********************************/
    function ShowCIXDataOnRequest(data){
        // If Last PIX clicked is different of actual click it
        // will append informations bhrought trhought request
        // and show off them witha new style
        if(last_cix_clicked != cix_clicked){
            var html = "";
            for(var i=0;i<data.asn_amount.length;i++){
                html += "<a href='/core/ix/"+code+"/"+data.asn_amount[i]+"/' style='color:white;'>"+data.asn_amount[i]+"</a>,";
            }
            $(".asn-cix-info-"+cix_clicked).append(html);
            $(".mlpav4-cix-info-" + cix_clicked).append(data.mlpav4_amount);
            $(".mlpav6-cix-info-" + cix_clicked).append(data.mlpav6_amount);
            $(".bilateral-cix-info-" + cix_clicked).append(data.bilateral_amount);
            $(".channel-cix-info-" + cix_clicked).append(data.port_master);

            // If Last CIX clicked has LAG, show LAG
            var lag = "";
            if(Object.keys(data.lag).length > 1){  // when MC-LAG
                lag += "<ul style='list-style:none;padding:0px;'>";
                for(index in data.lag){
                    lag += "<li>"+index+": "+data.lag[index]+"</li>";
                }
                lag += "</ul>";
            } else if(Object.keys(data.lag).length == 1){  // when LAG
                for(index in data.lag){
                    lag += data.lag[index];
                }
            }

            $(".channel-cix-info-lag-" + cix_clicked).html(lag);

            $(".info-" + cix_clicked).show();

            $("#" + cix_clicked + ", .info-" + cix_clicked).addClass("channel-list");
            $(".icon-" + cix_clicked + "> i").removeClass("fa-chevron-circle-right");
            $(".icon-" + cix_clicked + "> i").addClass("fa-chevron-circle-down");
            // Verify if it is not the first click of user,
            // to not apply this into nothing, because doens't exist last PIX clicked yet.
            if(last_cix_clicked != '') {
                $(".info-" + last_cix_clicked).hide();

                $(".asn-cix-info-" + last_cix_clicked).empty();
                $(".mlpav4-cix-info-" + last_cix_clicked).empty();
                $(".mlpav6-cix-info-" + last_cix_clicked).empty();
                $(".bilateral-cix-info-" + last_cix_clicked).empty();
                $(".channel-cix-info-" + last_cix_clicked).empty();
                $(".switch-cix-info-" + last_cix_clicked).empty();

                $("#" + last_cix_clicked + ", .info-" + last_cix_clicked).removeClass("channel-list");
                $(".icon-" + last_cix_clicked + "> i").removeClass("fa-chevron-circle-down");
                $(".icon-" + last_cix_clicked + "> i").addClass("fa-chevron-circle-right");
            }
        // Else it is user has clicked in the same PIX,
        // not having been necessity of make a new AJAX request.
        // Just show again the informations.
        } else {
            $(".info-" + cix_clicked).toggle();

            //This if and else is just to fake toggle h6 style
            if(!$(".info-" + cix_clicked).is(':visible')){
                $("#" + last_cix_clicked + ", .info-" + last_cix_clicked).removeClass("channel-list");
                $(".icon-" + last_cix_clicked + "> i").removeClass("fa-chevron-circle-down");
                $(".icon-" + last_cix_clicked + "> i").addClass("fa-chevron-circle-right");

            } else {
                $("#" + cix_clicked + ", .info-" + cix_clicked).addClass("channel-list");
                $(".icon-" + cix_clicked + "> i").removeClass("fa-chevron-circle-right");
                $(".icon-" + cix_clicked + "> i").addClass("fa-chevron-circle-down");
            }
        }
    }

    function validateTag(tag){
        return tag == parseInt(tag) && tag >= 0 && tag <= 4095;
    }

    function validateMac(mac){
        var regex = new RegExp('^(([a-fA-F0-9]{2}-){5}[a-fA-F0-9]{2}|([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}|([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4})?$');
        result = regex.test(mac);
        return result;
    }

    // Function validate IP
    function validateIPv4(campo){
        var regex = '[^0-9.]';
        var string = campo.split(".");

        var erro = 0;
        if(string.length === 4){
            if(string[0].length < 1 && string[0].length > 3){
                erro += 1;
            }
            if(string[1].length < 1 && string[0].length > 3){
                erro += 1;
            }
            if(string[2].length < 1 && string[0].length > 3){
                erro += 1;
            }
            if(string[3].length < 1 && string[0].length > 3){
                erro += 1;
            }
        }else{
            erro += 1;
        }
        if(campo.match(regex)) {

            return false;
        }
        else if(erro === 0) {
            return true;
        }
    }

    function validateIPv6(campo){
        var regex = '[^0-9a-f:]';
        var string = campo.split(":");

        var erroV = 0;
        if(string.length === 4){
           if(string[0].length < 1 && string[0].length > 4){

                erroV += 1;
            }
            if(string[1].length < 1 && string[0].length > 4){
                erroV += 1;
            }
            if(string[2] !== ""){
                erroV += 1;

            }
            if(string[3].length < 1 && string[0].length > 4){
                erroV += 1;
            }
        }else{

            erroV += 1;
        }
        if(campo.match(regex)) {
            return false;
        }
        else if(erroV === 0) {
            return true;
        }
    }

    // Function to do the main of the switchs after of to click the pix.
    function SwitchAppend(switch_set, obj_clicked){
        var html = "";
        for(index in switch_set){
          html += `
            <li>
                <a href='/core/ix/${code}/switch/${switch_set[index].uuid}' class='data-switch' style='text-decoration: underline;'>
                    ${switch_set[index].management_ip}
                </a>
                [${switch_set[index].model}] has ${switch_set[index].available_ports} (${switch_set[index].percent_available_ports}%) available ports
            </li>
        `;
        }
        $(".switchs-info-" + obj_clicked).html(html);

    }

    $("#search-options").change(function(e) {
        search_option = $("#search-options").val();

        $("#search-input").removeClass("is-invalid");
        $(".invalid-feedback").html("");

        switch (search_option) {
            case 'IP':
                $("#search-input").attr('placeholder', 'Search for IPs...');
                break;

            case 'Tag':
                $("#search-input").attr('placeholder', 'Search for Tag...');
                break;

            case 'MAC':
                $("#search-input").attr('placeholder', 'Search for MAC Address...');
                break;

            default:
                break;
        }
    });
});
