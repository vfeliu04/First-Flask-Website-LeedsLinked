$(document).ready(function() {

	// Set the token so that we are not rejected by server
	var csrf_token = $('meta[name=csrf-token]').attr('content');
	 // Configure ajaxSetup so that the CSRF token is added to the header of every request
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrf_token);
	        }
	    }
	});

	$("a.likes").on("click", function() {
        var clicked_obj = $(this);
        var post_id = clicked_obj.attr('id');
        var like_type = $(this).children()[0].id;
        var user_id = $(this).children()[2].id;
        

        $.ajax({
            url: '/likes',
            type: 'POST',
            data: JSON.stringify({ post_id: post_id, like_type: like_type, user_id: user_id}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                console.log(response);

                // Update the html rendered to reflect new count
                if (like_type == "like") {
                    clicked_obj.children('span').html(" " + response.like);
                    document.getElementById("sdislike").innerHTML = " " + response.dislike;
                    
                } 
                else {
                    clicked_obj.children('span').html(" " + response.dislike);
                    document.getElementById("slike").innerHTML = response.like;
                    
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});