$('document').ready(function() {

    if($("#id_switch").val() != null){
        alert("aqui");
        switch_uuid = $("#id_switch").val()
        asn = $("#id_asn").val()
        $.ajax({
            url: '/core/get-ports-by-switch/',
            data: {
                'switch_uuid': switch_uuid,
                'asn': asn
            },
            dataType: 'json',
            success: function (data) {

                $("#id_ports").find('option').remove().end();
                for (port in data.ports){
                    document.getElementById("id_ports").options.add(new Option(port, data.ports[port]));
                }
                $.ajax({
                    url: '/core/get-ports-by-switch/',
                    data: {
                        'switch_uuid': switch_uuid,
                    },
                    dataType: 'json',
                    success: function (data) {
                        alert(data);
                        $("#id_ports").find('option').remove().end();
                        for (port in data.ports){
                            document.getElementById("id_ports").options.add(new Option(port, data.ports[port]));
                        }
                        $("#id_channel_name").val(data.name_prefix);

                                    }
                });
                e.stopPropagation();
            }
        });
    }
    /************************************
    *** AJAX request by search Swtich ***
    ************************************/
    $("body").on("change", "#id_switch", function(e) {
        if($("#id_ports").val() != null){
            switch_uuid = $("#id_switch").val()
            asn = $("#id_asn").val()
            $.ajax({
                url: '/core/get-ports-by-switch/',
                data: {
                  'switch_uuid': switch_uuid,
                  'asn': asn
                },
                dataType: 'json',
                success: function (data) {
                    $("#id_ports").find('option').remove().end();
                    for (port in data.ports){
                        document.getElementById("id_ports")
                            .options.add(new Option(port, data.ports[port]));
                    }
                    $("#id_channel_name").val(data.name_prefix);
                    $.ajax({
                        url: '/core/get-ports-by-switch/',
                        data: {
                            'switch_uuid': switch_uuid,
                        },
                        dataType: 'json',
                        success: function (data) {
                            $("#id_ports").find('option').remove().end();
                            for (port in data.ports){
                                document.getElementById("id_ports")
                                    .options.add(new Option(port, data.ports[port]));
                            }
                            $("#id_channel_name").val(data.name_prefix);
                        }
                    });
                    e.stopPropagation();
                }
            });
        }
    });
});

$('document').ready(function() {
    /*************************************
    ***** AJAX request by search PIX *****
    *************************************/
    $("body").on("change", "#id_pix", function(e) {
        if($("#id_ports").val() != null){
            var first_switch_uuid = '';
            pix_pk = $("#id_pix").val()
            asn = $("#id_asn").val()

            $.ajax({
                url: '/core/get-switchs-by-pix/',
                data: {
                    'pix_pk': pix_pk,
                    'asn': asn
                },
                dataType: 'json',
                success: function (data) {
                    $("#id_switch").find('option').remove().end();
                    for (sw in data.switchs){
                        document.getElementById("id_switch")
                            .options.add(new Option(data.switchs[sw], sw));
                    }

                    first_switch_uuid = document.getElementById("id_switch")[0].value;
                    $.ajax({
                        url: '/core/get-ports-by-switch/',
                        data: {
                            'switch_uuid': first_switch_uuid,
                        },
                        dataType: 'json',
                        success: function (data) {
                            $("#id_ports").find('option').remove().end();
                            for (port in data.ports){
                                document.getElementById("id_ports")
                                    .options.add(new Option(port, data.ports[port]));
                            }
                            $("#id_channel_name").val(data.name_prefix);
                        }
                    });
                }
            });
            e.stopPropagation();
        }
    });
});