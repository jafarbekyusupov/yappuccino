/* ========= COMMENT_VOTING.JS ========= */

$(document).ready(function(){
  $(document).on('click', '.comment-vote-btn', function(e){
    e.preventDefault();

    const commentId = $(this).data('comment-id');
    const voteType = $(this).data('vote-type');
    const $voteContainer = $(this).closest('.comment-vote-container');

    // -- GETTING CSRF TOKEN FROM COOKIE --
    function getCookie(name){
      let cookieValue = null;
      if(document.cookie && document.cookie !== ''){
        const cookies = document.cookie.split(';');
        for(let i=0; i<cookies.length; i++){
          const cookie = cookies[i].trim();
          if(cookie.substring(0, name.length+1) === (name + '=')){
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // -- SENDING AJAX REQUEST
    $.ajax({
      url: `/comment/${commentId}/vote/`,
      type: 'POST',
      data:{
        'vote_type': voteType,
        'csrfmiddlewaretoken': csrftoken
      },
      headers:{
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      success: function(data){
        if(data.success){
          $voteContainer.find('.upvote-count').text(data.upvotes);
          $voteContainer.find('.downvote-count').text(data.downvotes);

          const $upvoteBtn = $voteContainer.find('.upvote-btn');
          const $downvoteBtn = $voteContainer.find('.downvote-btn');

          // upd acitev state of btns
          if(data.action === 'added' || data.action === 'changed'){
            voteType === 'up' ?
              ($upvoteBtn.addClass('active'), $downvoteBtn.removeClass('active'))
              : ($downvoteBtn.addClass('active'), $upvoteBtn.removeClass('active'));
          }
            showMessage(`Vote ${data.action} successfully!`, 'success');
          } else if(data.action === 'removed'){
            voteType === 'up' ? $upvoteBtn.removeClass('active') : $downvoteBtn.removeClass('active');
            showMessage('Vote removed successfully!', 'success');
          } else{
              showMessage(data.message || 'Error voting on comment. Please try again.', 'danger');
          }
      },
      error: function(xhr, status, error){
        console.error('Error voting on comment:', error);
        console.error('Status:', status);
        console.error('Response:', xhr.responseText);
        showMessage('Error voting on comment. Please try again.', 'danger');
      }
    });
  });

  // -- HELPER FUNC TO SHOW MSGS --
  function showMessage(message, type){
    const $messagesContainer = $('#messages-container');

    const alertHTML = `
      <div class="alert alert-${type} alert-dismissible fade show text-center" role="alert">
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
    `;

    $messagesContainer.append(alertHTML);

    setTimeout(function(){ $('.alert').alert('close');}, 3000);
  }
});