$('document').ready(function() {

    /******************************************************
	*** Function to display whois output for a given AS ***
	******************************************************/

    $.ajax({
        url: 'whois',
        timeout: 10000
    })
        .done(response => {
            content = $('#whoisContent');
            content.html($(response).html())
        })
        .fail(error => {
            content = $('#whoisContent');

            content.html($('#whoisFail'));
            $('#whoisFail').removeClass("hidden");

            content.append($('<div>' + error.statusText + '</div>'))
            console.error(error);
        })
})
