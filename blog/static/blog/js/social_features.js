/* ======= SOCIAL_FEATURES.JS ======= */

document.addEventListener('DOMContentLoaded', function(){
    // -- CSRF TOKEN HANDLING FOR AJAX REQS
    function getCookie(name){
        let cookieValue = null;
        if(document.cookie && document.cookie !== ''){
            const cookies = document.cookie.split(';');
            for(let i=0; i<cookies.length; i++){
                const cookie = cookies[i].trim();
                if(cookie.substring(0, name.length+1) === (name + '=')){
                    cookieValue = decodeURIComponent(cookie.substring(name.length+1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // -- SETUP AJAX CSRF TOKEN --
    function csrfSafeMethod(method){ return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));}

    // ADDING CSRF TOKEN TO AJAX REQS
    $.ajaxSetup({
        beforeSend: function(xhr, settings){
            if(!csrfSafeMethod(settings.type) && !this.crossDomain){ xhr.setRequestHeader("X-CSRFToken", csrftoken);}
        }
    });

    // -- VOTE BUTTONS w AJAX --
    $('.vote-btn').click(function(e){
        e.preventDefault();
        const voteUrl = $(this).attr('href');
        const postId = $(this).data('post-id');
        const voteType = $(this).data('vote-type');
        const voteCont = $(this).closest('.vote-container');

        $.ajax({
            url: voteUrl,
            type: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            success: function(data){
                // -- UPD VOTE DISPLAY --
                voteCont.find('.upvote-count').text(data.upvotes);
                voteCont.find('.downvote-count').text(data.downvotes);
                voteCont.find('.vote-score').text(data.score);

                // -- UPD BTN ACTIVE STATES --
                if(voteType === 'upvote'){
                    if(data.message.includes('removed')){
                        voteCont.find('.upvote-btn').removeClass('btn-orange').addClass('btn-outline-orange');
                    }
                    else{
                        voteCont.find('.upvote-btn').removeClass('btn-outline-orange').addClass('btn-orange');
                        voteCont.find('.downvote-btn').removeClass('btn-dark-orange').addClass('btn-outline-dark-orange');
                    }
                } else{
                    if(data.message.includes('removed')){
                        voteCont.find('.downvote-btn').removeClass('btn-dark-orange').addClass('btn-outline-dark-orange');
                    } else{
                        voteCont.find('.downvote-btn').removeClass('btn-outline-dark-orange').addClass('btn-dark-orange');
                        voteCont.find('.upvote-btn').removeClass('btn-orange').addClass('btn-outline-orange');
                    }
                }

                showFlashMessage(data.message, 'success');
            },
            error: function(xhr, status, error){ showFlashMessage('Error: ' + error, 'danger');}
        });
    });

    // COMMENT SUBMISSION w AJAX
    $('#comment-form').submit(function(e){
        e.preventDefault();

        const form = $(this);
        const formData = form.serialize();
        const submitBtn = form.find('button[type="submit"]');
        const textArea = form.find('textarea');

        submitBtn.prop('disabled', true).text('Submitting...');

        $.ajax({
            url: form.attr('action'),
            type: 'POST',
            data: formData,
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            success: function(data){
                if(data.success){
                    textArea.val(''); // cleaering the form

                    // new comment prepended to the list
                    const newComment = createCommentHTML(data);
                    $('.comments-list').prepend(newComment);

                    const count = parseInt($('.comment-count').text()) + 1;
                    $('.comment-count').text(count);

                    showFlashMessage('Comment added successfully!', 'success');
                }
                submitBtn.prop('disabled', false).text('Submit Comment');
            },
            error: function(xhr, status, error){
                showFlashMessage('Error: '+error, 'danger');
                submitBtn.prop('disabled', false).text('Submit Comment');
            }
        });
    });

    // -- HELPER FUNC TO CREATE HTML FOR NEW COMMENT --
    function createCommentHTML(data){
        return `
            <div class="media comment-item mb-3">
                <img class="rounded-circle comment-img mr-3" src="${data.author_image}" width="40" height="40">
                <div class="media-body">
                    <div class="comment-metadata">
                        <a href="/user/${data.comment_author}" class="comment-author">${data.comment_author}</a>
                        <small class="text-muted ml-2">${data.comment_date}</small>
                    </div>
                    <div class="comment-content mt-1">
                        ${data.comment_content}
                    </div>
                    <button class="btn btn-sm btn-link reply-toggle mt-1" data-comment-id="${data.comment_id}">
                        <i class="bi bi-reply"></i> Reply
                    </button>
                    <div class="reply-form mt-2 d-none" id="reply-form-${data.comment_id}">
                        <form method="POST" action="/post/${data.post_id}/comment/">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                            <input type="hidden" name="parent_id" value="${data.comment_id}">
                            <div class="form-group">
                                <textarea name="content" class="form-control" rows="2" placeholder="Write a reply..."></textarea>
                            </div>
                            <button type="submit" class="btn btn-sm btn-orange">Submit Reply</button>
                            <button type="button" class="btn btn-sm btn-secondary cancel-reply" data-comment-id="${data.comment_id}">Cancel</button>
                        </form>
                    </div>
                </div>
            </div>
        `;
    }

    // HLPR FNC -- SHOW FLASH MESSAGE --
    function showFlashMessage(message, type){
        const alertHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        `;

        $('#messages-container').append(alertHTML);

        setTimeout(function(){ $('.alert').alert('close');}, 3000);
    }

    // -- TOOLTIPS INIT --
    $(function (){ $('[data-toggle="tooltip"]').tooltip();});
});