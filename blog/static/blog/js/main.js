// =================================================================== //
// ============================= MAIN.JS ============================= //
// =================================================================== //

$(document).ready(function(){

  // ============================================== //
  // --------------- COMMENT SYSTEM --------------- //
  // ============================================== //

  // dropdown menu
  $(document).on('click', '.options-btn', function(e){
    e.stopPropagation();
    var $dropdown = $(this).siblings('.options-dropdown');
    var $commentOptions = $(this).closest('.comment-options');

    // close all other dropdowns
    $('.comment-options').not($commentOptions).removeClass('active');
    $commentOptions.toggleClass('active');
  });

  // close dropdowns when clicking outside
  $(document).on('click', function(e){
    if(!$(e.target).closest('.comment-options').length){ $('.comment-options').removeClass('active');}
  });

  // main comment form submission - PREVENT DOUBLE POSTING
  $('#comment-form').off('submit').on('submit', function(e){
    e.preventDefault();
    var $form = $(this);
    var $submitBtn = $form.find('button[type="submit"]');
    var originalBtnText = $submitBtn.html();

    // check n prevent double submission
    if($submitBtn.prop('disabled')){ return false;}

    var content = getEditorContent($form);
    if(!content || content.trim() === ''){ alert('Please enter a comment'); return false;}
    $submitBtn.prop('disabled', true).html('<i class="spinner-border spinner-border-sm mr-2"></i> Submitting...');

    $.ajax({
      url: $form.attr('action'),
      type: 'POST',
      data: $form.serialize(),
      headers:{'X-Requested-With': 'XMLHttpRequest'},
      success: function(data){
        if(data.success){
          clearEditorContent($form);
          addCommentToPage(data);
          showMessage('Comment added successfully!', 'success');
        } else{ showMessage('Error submitting comment', 'danger');}
        $submitBtn.prop('disabled', false).html(originalBtnText);
      },
      error: function(xhr, status, error){
        console.error('Error submitting comment:', error);
        showMessage('Error submitting comment. Please try again.', 'danger');
        $submitBtn.prop('disabled', false).html(originalBtnText);
      }
    });
  });

  // --- REPLY FORM TOGGLE ---
  $(document).on('click', '.reply-btn', function(e){
    e.preventDefault();
    var cmtId = $(this).data('comment-id');
    var $replyForm = $('#reply-form-' + cmtId);
    $('.reply-form-container, .edit-form-container').hide();
    $('.delete-confirm').hide();
    $('.comment-options').removeClass('active');

    $replyForm.toggle();
    if($replyForm.is(':visible')){ setTimeout(function(){ $replyForm.find('textarea').focus();},100);}
  });

  // toggle -- edit form
  $(document).on('click', '.edit-btn', function(e){
    e.preventDefault();
    var cmtId = $(this).data('comment-id');
    var $editForm = $('#edit-form-' + cmtId);
    $('.reply-form-container, .edit-form-container').hide();
    $('.delete-confirm').hide();
    $('.comment-options').removeClass('active');

    $editForm.toggle();
    if($editForm.is(':visible')){ setTimeout(function(){$editForm.find('textarea').focus();},100);}
  });

  // cancel btns
  $(document).on('click', '.cancel-reply, .cancel-edit', function(e){
    e.preventDefault();
    var cmtId = $(this).data('comment-id');
    $('#reply-form-' + cmtId + ', #edit-form-' + cmtId).hide();
  });

  // toggle -- delete confirm
  $(document).on('click', '.delete-btn', function(e){
    e.preventDefault();
    var cmtId = $(this).data('comment-id');
    var $deleteConfirm = $('#delete-confirm-' + cmtId);
    $('.reply-form-container, .edit-form-container').hide();
    $('.comment-options').removeClass('active');

    $deleteConfirm.toggle();
  });

  $(document).on('click', '.cancel-delete', function(e){
    e.preventDefault();
    var cmtId = $(this).data('comment-id');
    $('#delete-confirm-' + cmtId).hide();
  });

  // === COMMENT VOTING ===
  $(document).on('click', '.comment-vote-btn', function(e){
    e.preventDefault();

    var $btn = $(this);
    var cmtId = $btn.data('comment-id');
    var voteType = $btn.data('vote-type');
    var $commentItem = $('#comment-' + cmtId);
    var $upvoteBtn = $commentItem.find('.upvote-btn');
    var $downvoteBtn = $commentItem.find('.downvote-btn');
    var $upvoteCount = $upvoteBtn.find('.upvote-count');
    var $downvoteCount = $downvoteBtn.find('.downvote-count');

    // disable voting btns during req
    $upvoteBtn.prop('disabled', true);
    $downvoteBtn.prop('disabled', true);

    $.ajax({
      url: `/comment/${cmtId}/vote/`,
      type: 'POST',
      data:{
        'vote_type': voteType,
        'csrfmiddlewaretoken': getCookie('csrftoken')
      },
      headers:{'X-Requested-With': 'XMLHttpRequest'},
      success: function(data){
        if(data.success){
          $upvoteCount.text(data.upvotes);
          $downvoteCount.text(data.downvotes);

          $upvoteBtn.removeClass('active');
          $downvoteBtn.removeClass('active');

          if(data.action !== 'removed'){
            if(voteType === 'up'){ $upvoteBtn.addClass('active');}
            else{ $downvoteBtn.addClass('active');}
          }
          showMessage('Vote Updated Successfully!', 'success');
        } else{ showMessage('Error voting on comment', 'danger');}
      },
      error: function(xhr, status, error){
        console.error('Error voting on comment:', error);
        showMessage('Error voting on comment. Please try again.', 'danger');
      },
      complete: function(){ // reactivate btns
        $upvoteBtn.prop('disabled', false);
        $downvoteBtn.prop('disabled', false);
      }
    });
  });

  // --- REPLY SUBMIT ---
  $(document).on('submit', '.reply-comment-form', function(e){
    e.preventDefault();
    var $form = $(this);
    var $submitBtn = $form.find('button[type="submit"]');
    var origBtnTxt = $submitBtn.html();
    var cmtId = $form.data('comment-id');

    if($submitBtn.prop('disabled')){ return false;}
    var content = $form.find('textarea[name="content"]').val().trim();
    if(!content){ showMessage('Please Enter a Reply', 'warning'); return false;}

    $submitBtn.prop('disabled', true).html('<i class="spinner-border spinner-border-sm mr-1"></i> posting...');
    $.ajax({
      url: $form.attr('action'),
      type: 'POST',
      data: $form.serialize(),
      headers:{'X-Requested-With': 'XMLHttpRequest'},
      success: function(data){
        if(data.success){
          $form.find('textarea[name="content"]').val('');
          $('#reply-form-' + cmtId).removeClass('active');
          location.reload();
        } else{ showMessage('Error Posting Reply', 'danger');}
      },
      error: function(){ showMessage('Error Posting Reply. Please Try Again.', 'danger');},
      complete: function(){ $submitBtn.prop('disabled', false).html(origBtnTxt);}
    });
  });

  // --- CONFIRM DELETE ---
  $(document).on('click', '.confirm-delete', function(e){
    e.preventDefault();
    var cmtId = $(this).data('comment-id');
    var $commentItem = $('#comment-' + cmtId);
    $commentItem.addClass('comment-loading');
    $.ajax({
      url: '/comment/' + cmtId + '/delete/',
      type: 'POST',
      data:{ 'csrfmiddlewaretoken': getCookie('csrftoken')},
      headers:{'X-Requested-With': 'XMLHttpRequest'},
      success: function(data){
        if(data.success){
          $commentItem.fadeOut(300, function(){
            $(this).remove();
            updateCommentCount(-1);
            checkNoComments();
            showMessage('Comment deleted successfully!', 'success');
          });
        } else{
          showMessage('Error deleting comment', 'danger');
          $commentItem.removeClass('comment-loading');
        }
      },
      error: function(xhr, status, error){
        console.error('Error deleting comment:', error);
        showMessage('Error deleting comment. Please try again.', 'danger');
        $commentItem.removeClass('comment-loading');
      }
    });
  });

  // === EDIT COMMENT FORM SUBMISSION ===
  $(document).on('submit', '.edit-comment-form', function(e){
    e.preventDefault();
    var $form = $(this);
    var cmtId = $form.data('comment-id');
    var $submitBtn = $form.find('button[type="submit"]');
    var origBtnTxt = $submitBtn.html();
    var $commentItem = $('#comment-' + cmtId);

    var content = $form.find('textarea[name="content"]').val().trim();
    if(!content){ showMessage('Comment cannot be empty', 'warning'); return;}

    $submitBtn.prop('disabled', true).html('<i class="spinner-border spinner-border-sm mr-1"></i> Saving...');
    $commentItem.addClass('comment-loading');

    $.ajax({
      url: $form.attr('action'),
      type: 'POST',
      data:{
        'content': content,
        'csrfmiddlewaretoken': getCookie('csrftoken')
      },
      headers:{'X-Requested-With': 'XMLHttpRequest'},
      success: function(data){
        if(data.success){
          $commentItem.find('.comment-content').first().html(data.content);
          if(!$commentItem.find('.comment-edited').length){
            $commentItem.find('.comment-timestamp').append(' <span class="comment-edited">(edited)</span>');
          }

          $('#edit-form-' + cmtId).removeClass('active');
          showMessage('Comment updated successfully!', 'success');
        } else{ showMessage(data.message || 'Error updating comment', 'danger');}
      },
      error: function(xhr, status, error){
        console.error('Error updating comment:', error);
        showMessage('Error updating comment. Please try again.', 'danger');
      },
      complete: function(){
        $submitBtn.prop('disabled', false).html(origBtnTxt);
        $commentItem.removeClass('comment-loading');
      }
    });
  });

  // ==================================================== //
  // ------------------- HELPER FUNCS ------------------- //
  // ==================================================== //

  function getCookie(name){
    let cookVal = null;
    if(document.cookie && document.cookie !== ''){
      const cookies = document.cookie.split(';');
      for(let i=0; i<cookies.length; i++){
        const cookie = cookies[i].trim();
        if(cookie.substring(0, name.length+1) ===(name+'=')){
          cookVal = decodeURIComponent(cookie.substring(name.length+1));
          break;
        }
      }
    }
    return cookVal;
  }

  function getEditorContent($form){
    var content = '';
    if(window.CKEDITOR5){
      var edtrInst = null;
      Object.keys(window.CKEDITOR5).forEach(function(key){
        if(key.startsWith('inst')){ edtrInst = window.CKEDITOR5[key];}
      });
      if(edtrInst){ content = edtrInst.getData();}
    } else{ content = $form.find('textarea[name="content"]').val();}
    return content;
  }

  function clearEditorContent($form){
    if(window.CKEDITOR5){
      Object.keys(window.CKEDITOR5).forEach(function(key){
        if(key.startsWith('inst')){ window.CKEDITOR5[key].setData('');}
      });
    } else{ $form.find('textarea[name="content"]').val('');}
  }

  function addCommentToPage(data){
    $('.no-comments').remove();

    var commentHtml = `
      <div class="comment-item" id="comment-${data.comment_id}">
        <div class="comment-header">
          <div class="comment-author-info">
            <img class="rounded-circle" src="${data.author_image}" width="32" height="32" alt="${data.comment_author}">
            <div>
              <a href="/user/${data.comment_author}/" class="comment-author-link">
                ${data.comment_author}
              </a>
              <div class="comment-timestamp">
                ${data.comment_date}
              </div>
            </div>
          </div>
          <div class="comment-options">
            <button class="options-btn" type="button" aria-label="comment options">
              <i class="bi bi-three-dots-vertical"></i>
            </button>
            <div class="options-dropdown">
              <button class="reply-btn" data-comment-id="${data.comment_id}">
                <i class="bi bi-reply"></i> Reply
              </button>
              <button class="report-btn" data-comment-id="${data.comment_id}">
                <i class="bi bi-flag"></i> Report
              </button>
            </div>
          </div>
        </div>
        <div class="comment-content">
          ${data.comment_content}
        </div>
        <div class="comment-vote-container">
          <button class="comment-vote-btn upvote-btn" data-comment-id="${data.comment_id}" data-vote-type="up" aria-label="upvote comment">
            <i class="bi bi-hand-thumbs-up"></i>
            <span class="upvote-count">0</span>
          </button>
          <button class="comment-vote-btn downvote-btn" data-comment-id="${data.comment_id}" data-vote-type="down" aria-label="downvote comment">
            <i class="bi bi-hand-thumbs-down"></i>
            <span class="downvote-count">0</span>
          </button>
        </div>
        <div class="comment-actions">
          <button class="comment-action-btn reply-btn" data-comment-id="${data.comment_id}">
            <i class="bi bi-reply"></i> Reply
          </button>
          <button class="comment-action-btn edit-btn" data-comment-id="${data.comment_id}">
            <i class="bi bi-pencil"></i> Edit
          </button>
          <button class="comment-action-btn delete-btn" data-comment-id="${data.comment_id}">
            <i class="bi bi-trash"></i> Delete
          </button>
        </div>
      </div>
    `;

    $('.comments-list').prepend(commentHtml);
    updateCommentCount(1);
  }

  function updateCommentCount(change){
    var $countElement = $('.content-section h4').first();
    var currCnt = parseInt($countElement.text().match(/\d+/)[0]) || 0;
    var nCnt = currCnt + change;
    $countElement.html('<i class="bi bi-chat-text"></i> Comments(' + nCnt + ')');
  }

  function checkNoComments(){
    if($('.comment-item').length === 0){
      $('.comments-list').html('<div class="no-comments"><i class="bi bi-chat-dots"></i><p class="text-muted">No comments yet. Be the first to Start the Conversation!</p></div>');
    }
  }

  function showMessage(message, type){
    var $messagesContainer = $('#messages-container');
    if($messagesContainer.length === 0){
      $('body').prepend('<div id="messages-container" class="fixed-top" style="margin-top: 60px; z-index: 1000; width: 300px; right: 20px;"></div>');
      $messagesContainer = $('#messages-container');
    }

    const alertHTML = `
      <div class="alert alert-${type} alert-dismissible fade show" role="alert">
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