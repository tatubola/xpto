$('document').ready(function() {
        var current = ''
    $('.right-down-icon').click(function(e){
                icon = $(this).find(".fa");
        var id = e.target.id;
        var clean_id = "."+id;

        if (current === clean_id)
        {
                $(icon).removeClass("fa-chevron-circle-down");
                        $(icon).addClass("fa-chevron-circle-right");
                $(clean_id).hide();
                current = ''
        }else{
                $(icon).removeClass("fa-chevron-circle-right");
                        $(icon).addClass("fa-chevron-circle-down");
                $(clean_id).show();
                current = clean_id;
        }
     })
});

$(document).on('keyup', '.keyup-tag', function(e){
    e.preventDefault();
    var tag_v6 = $("#id_tag_v6").val();
    var tag_v4 = $("#id_tag_v4").val();
    var option = $('#id_service_option').find('option:selected').val();

        if(option === "v4_and_v6"){
            if(tag_v4 === tag_v6){
                $(".message-tags").css({"display" : "block"});
            }else{
                $(".message-tags").css({"display" : "none"});
            }
        }else{
            $(".message-tags").css({"display" : "none"});
        }
});

$(document).on('change', '#id_service_option', function(e){
    e.preventDefault();
    
    var choice_value = $('#id_service_option').find('option:selected').text();
    if (choice_value === 'Only IPv4'){
        $('.v6-form').hide();
        $('.v4-form').show();
    }else if(choice_value === 'Only IPv6'){
        $('.v4-form').hide();
        $('.v6-form').show();
    }else{
        $('.v4-form').show();
        $('.v6-form').show();
    }
});

/*
  Function to delete service, called by as_ix_detail.html
  args: service_type -> servicy type
        service_pk -> service primary key
*/
function delete_service(service_type, service_pk){
    var confirmed = confirm("Do you want to remove this "+ service_type +" service?");
    if(confirmed){
        $.ajax({
            url: '/core/service/delete/'+service_pk+"/",
            type: 'POST',
            dataType: 'json',
            data: {
                'service_pk': service_pk,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(data){
                alert("Service" + service_type + " removed");
                location.reload(true);
            },
            error: function(error){
                if (error.status == 400){
                    alert(error.responseJSON.message);
                }
                else {
                    alert("Couldn't delete");
                }
            }
        });
    }
}
