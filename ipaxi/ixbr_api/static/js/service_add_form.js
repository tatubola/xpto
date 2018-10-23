/*
    Render fields according to selected option on "#id_service_option"
    field and the cix type of the given channel.

    Args: customer_channel : bool -> true if channel field 
                        "id_customer_channel" should be considered.
                        false other else.
*/
function update_mlpa_form_by_service_option(customer_channel){
    var option = $("#id_service_option").val()
    $("#message-tags").css({"display" : "none"});
    if(!channel){
        channel = $("#id_channel").val();
    }
    if(customer_channel){
        channel = $("#id_customer_channel").val();
    }
    $("#ip-load").css({"display" : "block"});
    $("#form-ipv4").css({"display" : "none"});
    $("#form-ipv6").css({"display" : "none"});
    if (channel){
        $.ajax({
            url: '/core/get-ips-and-tags-by-ix/',
            data: {
                'option': option,
                'ix': code,
                'channel': channel
            },
            dataType: 'json',
            success: function (data) {
                $("#ip-load").css({"display" : "none"});

                if(option === 'only_v4'){
                    $("#id_mlpav4_address").val(data['ipv4']);
                    $("#id_tag_v4").val(data['tag'][0]);
                    $("#id_tag_v4").attr("required",true);
                    $("#id_tag_v6").attr("required",false);
                    $("#form-ipv4").css({"display" : "block"});
                    $("#form-ipv6").css({"display" : "none"});
                }
                else if(option === 'only_v6'){
                    $("#id_mlpav6_address").val(data['ipv6']);
                    $("#id_tag_v6").val(data['tag'][0]);
                    $("#id_tag_v6").attr("required",true);
                    $("#id_tag_v4").attr("required",false);
                    $("#form-ipv6").css({"display" : "block"});
                    $("#form-ipv4").css({"display" : "none"});
                }
                else if(option === 'v4_and_v6'){
                    if(data['cix_type'] === 3){
                        $("#id_tag_v4").val(data['tag'][0]);
                        $("#id_tag_v6").val(data['tag'][0]);
                    }else{
                        $("#id_tag_v4").val(data['tag'][0]);
                        $("#id_tag_v6").val(data['tag'][1]);
                    }
                    $("#id_mlpav4_address").val(data['ipv4']);
                    $("#id_tag_v4").attr("required",true);
                    $("#id_tag_v6").attr("required",true);
                    $("#id_mlpav6_address").val(data['ipv6']);
                    $("#form-ipv6").css({"display" : "block"});
                    $("#form-ipv4").css({"display" : "block"});
                }
            }
        });
        $.ajax({
             url: '/core/get-cix-type-by-customer-channel/',
             data: {
                 'channel': channel,
            },
            dataType: 'json',
            success: function (data) {
             if(data.cix_type === 3){
                 $(".form-inner").css({"display":"block"});
             }
              }
         }); 
    }else{
        alert("Please select some channel");
    }
}

/*
    Update switch list according to "#id_pix" field

    Args: form_type : String -> bilateral if bilateralform.
                                mlpa other else.
*/
function update_switch_by_pix_bilateral_form(form_type, pix, idswitch){

    var first_switch_uuid = '';
    var pix_pk = $(pix).val()
    if (pix_pk){
        $.ajax({
            url: '/core/get-switchs-by-pix/',
            data: {
                'pix_pk': pix_pk,
            },
            dataType: 'json',
            success: function (data) {
                $(idswitch).find('option').remove().end();
                for (sw in data.switchs){
                    document.getElementById(idswitch.split("#")[1])
                        .options.add(new Option(data.switchs[sw], sw));
                } 
                if(form_type == "bilateral"){
                    if(pix == '#id_pix'){
                        update_channels_by_switch_asn_bilateral_form(false);
                    }
                    else{
                        update_channels_by_switch_asn_bilateral_form(true);
                    }
                } else{
                    update_channels_by_switch_asn_mpla_form();
                }          

            }
        });
    }else{
        $(idswitch).empty();
        if(form_type == 'bilateral'){
            if(pix == '#id_pix'){
                update_channels_by_switch_asn_bilateral_form(false);
            }
            else{
                update_channels_by_switch_asn_bilateral_form(true);
            }
        } else{
            update_channels_by_switch_asn_mpla_form();
        }
    }     
};

/*
    Update channles list according to "#id_switch" 
    and "id_asn" fields using rules for bilateral.

*/

function update_channels_by_switch_asn_bilateral_form(origin){

    if(origin){
        switch_item = $("#id_origin_switch").val();
        asn_value = $("#id_origin_asn").val();
        channel = "#id_origin_channel";
    }else{
     switch_item = $("#id_switch").val();
     asn_value = $("#id_asn").val();
     channel = "#id_customer_channel";       
    }
    if(!asn_value){
        alert("Please inform the ASN Connection")
    }else if(switch_item){

        $.ajax({
            url: '/core/get-customer-channels-by-switch-and-asn/',
            data: {
              'switch': switch_item,
              'asn' : asn_value,
            },
            dataType: 'json',
            success: function (data) {
                $(channel).find('option').remove().end();
                for (item in data.channels_list){
                    document.getElementById(channel.split("#")[1])
                        .options.add(new Option(data.channels_list[item], item));
                }
                update_tags_by_bilateral_type();
            }
        });

    }else{
        $(channel).empty();
    }

};

/*
    Update channles list according to "#id_switch" 
    and "id_asn" fields using rules for mlpa.

*/

function update_channels_by_switch_asn_mpla_form(){

    switch_item = $("#id_switch").val();
    asn_value = $("#id_asn").val();
    if(!asn_value){
        alert("Please inform the ASN Connection")
    }else if(switch_item){

        $.ajax({
            url: '/core/get-customer-channels-by-switch/',
            data: {
              'switch': switch_item,
              'asn' : asn_value,
            },
            dataType: 'json',
            success: function (data) {
                $("#id_customer_channel").find('option').remove().end();
                for (item in data.channels_list){
                    document.getElementById("id_customer_channel")
                        .options.add(new Option(data.channels_list[item], item));
                }
                update_mlpa_form_by_service_option(true);
            }
        });

    }else{
        $("#id_customer_channel").empty();
        update_mlpa_form_by_service_option(true);

    }

}

/*
    Update tag fields suggestion by
    channel bilateral type

*/

function update_tags_by_bilateral_type(){

    channel_b = $("#id_customer_channel").val();
    channel_a = $("#id_origin_channel").val();
    ix = $("#id_ix").val();
    asn = $("#id_asn").val();
    if (channel_a && channel_b){
        $.ajax({
            url: '/core/get-bilateral-type/',
            data: {
                'channel_a': channel_a,
                'channel_b': channel_b,
                'ix': ix,
            },
            dataType: 'json',
            success: function (data) {
                switch(data.bilateral_type){

                    case 0:

                        $("#id_tag_b").val(data.tag_a);
                        $("#id_tag_a").val(data.tag_b);
                        $("#id_inner_b").val("");
                        $("#id_inner_a").val("");
                        break;

                    case 1:

                        $("#id_tag_a").val(data.tag_a);
                        $("#id_inner_a").val(data.tag_b);
                        $("#id_tag_b").val(data.tag_b);
                        break;

                    case 2:

                        $("#id_tag_b").val(data.tag_b);
                        $("#id_inner_b").val(data.tag_a);
                        $("#id_tag_a").val(data.tag_a);
                        break;

                    case 3:

                        $("#id_tag_a").val(data.tag_a);
                        $("#id_tag_b").val(data.tag_b);
                        $("#id_inner_a").val(data.inner_a);
                        $("#id_inner_b").val(data.inner_b);
                        break;

                    default:
                        console.log("default");
                        $("#id_tag_b").val(data.tag_a);
                        $("#id_tag_a").val(data.tag_b);
                        $("#id_inner_b").val("");
                        $("#id_inner_a").val("");
                        break;
                }

            }
        });
    }
}
function search_channel_by_mac(){

    mac_value = $("#id_mac_search").val();
    if(mac_value){

        $.ajax({
            url: '/core/search-customer-channel-by-mac/',
            data: {
              'mac': mac_value,
            },
            dataType: 'json',
            success: function (data) {
                channel = "#id_customer_channel";
                $(channel).find('option').remove().end();
                for (item in data.channels_list){
                    document.getElementById(channel.split("#")[1])
                        .options.add(new Option(data.channels_list[item], item));
                }
                $("#id_pix").hide();
                $("#id_switch").hide();
                $('label[for="id_pix"]').hide();
                $('label[for="id_switch"]').hide();
                update_tags_by_bilateral_type();
            }
        });

    }else{
        $(channel).empty();
    }

};