$('document').ready(function() {
    var initialTitle = $('#modal .modal-header .title-holder').html();
    var initialContent = $('#modal .modal-body').html();

    $('#modal').on('shown.bs.modal', function (event) {
        let href = $(event.relatedTarget).attr('href');

        let titleDiv = $(this).find('.modal-header .title-holder');
        let contentDiv = $(this).find('.modal-body');

        titleDiv.html(initialTitle);
        contentDiv.html(initialContent);

        $.ajax({
            url: href
        })
            .done(response => {
                let data = $(response)

                let title = data.find('.title');
                let content = data.find('.content');

                let modal = $(this)

                titleDiv.html(title);
                contentDiv.html(content);
            })
            .fail(error => {
                console.error(error)
            })
    });
    $("#open-contact").click(function(event){
        event.stopImmediatePropagation();
        $("#modal-contact").css({"display" : "block"});
        $("#modal-contact").css({"opacity" : "2"});
        // let href = $(event.relatedTarget).attr('href');
        var href = $(this).attr("href");
        let titleDiv = $("#modal-contact").find('.modal-header .title-holder');
        let contentDiv = $("#modal-contact").find('.modal-body');

        titleDiv.html(initialTitle);
        contentDiv.html(initialContent);
        var contact = $(this).data("contact");
        var contactsmap = $(this).data("contactsmap");
        var type = $(this).data("type");
        $.ajax({
            type: 'GET',
            url: href,
            data: { contact : contact, contactsmap : contactsmap, type_contac : type},
            timeout: 10000
        })
            .done(response => {
                let data = $(response)

                let title = data.find('.title');
                let content = data.find('.content');

                let modal = $(this)

                titleDiv.html(title);
                contentDiv.html(content);
            })
            .fail(error => {
                console.error(error)
            })
    });

    var subinitialTitle = $('#sub-modal .modal-header .title-holder').html();
    var subinitialContent = $('#sub-modal .modal-body').html();

    $('#sub-modal').on('shown.bs.modal', function (event) {
        let href = $(event.relatedTarget).attr('href');

        let titleDiv = $(this).find('.modal-header .title-holder');
        let contentDiv = $(this).find('.modal-body');

        titleDiv.html(subinitialTitle);
        contentDiv.html(subinitialContent);

        $.ajax({
            url: href,
            timeout: 10000
        })
            .done(response => {
                let data = $(response)

                let title = data.find('.title');
                let content = data.find('.content-sub');

                let modal = $(this)

                titleDiv.html(title);
                contentDiv.html(content);
            })
            .fail(error => {
                console.error(error)
            })
    });
    $(".delete-mac").click(function(e){
        e.preventDefault();
        e.stopImmediatePropagation();
        var mac = $(this).data("mac");
        var service = $(this).data("service");
        var confirmed = confirm("Do you want to delete this MAC: " + mac +"?");
        var href = $(this).attr("href");
        if(confirmed){
            $.ajax({
                url: href,
                data: {'mac': mac, 'service': service },
                dataType: 'json',
                success: function(data) {
                    alert(data.result);
                    location.reload(true);
                },
                error: function(data) {
                    alert("erro");
                }
            });
        }
    });
    $(".delete_contact").click(function(e){
        e.preventDefault();
        e.stopImmediatePropagation();
        var contact = $(this).data("contact");
        var href = $(this).attr("href");
        var confirmar = confirm("Want to delete this contact: "+ contact + "?");
        if(confirmar){
            $.ajax({
                data: {'contact' : contact},
                url: href,
                success: function(data) {
                    alert(data.result);
                    location.reload(true);

                     },
                error: function(data) {
                    alert("erro");
                    }

            });
        }
    });
    $(".delete-phone").click(function(e){
        e.preventDefault();
        e.stopImmediatePropagation();
        var phone = $(this).data("phone");
        var href = $(this).attr("href");
        var confirmar = confirm("Want to delete this phone: "+ phone + "?");
        if(confirmar){
            $.ajax({
                data: {'phone' : phone},
                url: href,
                success: function(data) {
                    alert(data.result);
                    location.reload(true);
                     },
                error: function(data) {
                    alert("erro");
                    }
            });
        }
    });
    $(".delete-port").click(function(e){
        e.preventDefault();
        e.stopImmediatePropagation();
        var port = $(this).data("port");
        var channel = $(this).data("channel");
        var href = $(this).attr("href");
        var confirmar = confirm("Want to delete this port: "+ port + "?");
        if(confirmar){
            $.ajax({
                data: {'port' : port, 'channel' : channel},
                url: href,
                success: function(data) {
                    alert(data.result);
                    location.reload(true);
                     },

                error: function(data) {
                    alert("erro");
                    }
            });
        }
    });
});
$("body").on("click",".close",function(){
    location.reload(true);
});

function backPrevious() {
    window.history.back();
}

function getCookie(name) {
          var cookieValue = null;
          if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
               var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
             }
          }
      }
 return cookieValue;
}


function contactPopulate() {
    var csrfToken = $('[name=csrfmiddlewaretoken]').val();
    var ticket_typed = $('#id_ticket').val();
    jQuery.ajax({
        url: '/core/as/populate-as-contact/',
        type: "POST",
        dataType: "json",
        data: {
            ticket_id: ticket_typed,
            csrfmiddlewaretoken : csrfToken
        },
        success: function (data) {
            console.log("Populating Contact With Ticket: " + ticket_typed);

            if (data.asn != undefined) {
                if (data.asn != document.getElementById("id_asn").value){
                    alert("This ticket doesn't belogs to this ASN\n\nASN from ticket: "+data.asn);
                }
                else{
                    document.getElementById("id_asn").value = data.asn;
                    document.getElementById("id_ix").value = data.ix;
              
                    document.getElementById("id_org_name").value = data.org_name;
                    document.getElementById("id_org_shortname").value = data.org_shortname;
                    document.getElementById("id_org_cnpj").value = data.org_cnpj;
                    document.getElementById("id_org_url").value = data.org_url;
                    document.getElementById("id_org_addr").value = data.org_addr;

                    document.getElementById("id_contact_name_noc").value = data.contact_name_noc;
                    document.getElementById("id_contact_email_noc").value = data.contact_email_noc;
                    document.getElementById("id_contact_phone_noc").value = data.contact_phone_noc;

                    document.getElementById("id_contact_name_adm").value = data.contact_name_adm;
                    document.getElementById("id_contact_email_adm").value = data.contact_email_adm;
                    document.getElementById("id_contact_phone_adm").value = data.contact_phone_adm;

                    document.getElementById("id_contact_name_peer").value = data.contact_name_peer;
                    document.getElementById("id_contact_email_peer").value = data.contact_email_peer;
                    document.getElementById("id_contact_phone_peer").value = data.contact_phone_peer;

                    document.getElementById("id_contact_name_com").value = data.contact_name_com;
                    document.getElementById("id_contact_email_com").value = data.contact_email_com;
                    document.getElementById("id_contact_phone_com").value = data.contact_phone_com;

                    document.getElementById("id_contact_name_org").value = data.contact_name_org;
                    document.getElementById("id_contact_email_org").value = data.contact_email_org;
                    document.getElementById("id_contact_phone_org").value = data.contact_phone_org;
                }
            }
            else {
                alert("This ticket does not exist");
            }
        }
    });
}

function create_post(form, is_sub){
    var href = form.attr("action");
    $.ajax({
        data: form.serialize(),
        type: form.attr("method"),
        url: form.attr("action"),
        success: function(response) {
            if (is_sub){
                $(".content-sub").html($(response).find('.content-sub'));
            }else{
                $(".content").html($(response).find('.content'));
            }
        },
        error: function(data) {
            $(".content").html(data);
        }
    });
    return false;
};

// function to tag edit
function create_post_tag(form, is_sub){
    var href = form.attr("action")
    $("#tag-load").css({"display" : "block"});
    $("#form-display").css({"display" : "none"});
    $.ajax({
        data: form.serialize(),
        type: form.attr("method"),
        url: form.attr("action"),
        success: function(response) {
            $("#tag-load").css({"display" : "none"});
            if (is_sub){
                $(".content-sub").html($(response).find('.content-sub'));
            }else{
                $(".content").html($(response).find('.content'));
            }

        },
        error: function(data) {
            $(".content").html(data);
        },
        timeout: 360000  // 360 seconds
    });
    return false;
};


$(document).on('submit', '.django-form', function(e){
    e.preventDefault();
    e.stopImmediatePropagation();
    create_post($(this), false);
});
$(document).on('submit', '.django-form-sub', function(e){
    e.preventDefault();
    e.stopImmediatePropagation();
    create_post($(this), true);
});
$(document).on('submit', '.django-form-tag', function(e){
    e.preventDefault();
    e.stopImmediatePropagation();
    create_post_tag($(this), false);
});
