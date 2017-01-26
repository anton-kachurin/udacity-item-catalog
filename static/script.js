$('.logout-button').click(function(){
  // send a logout request to the server
  var request = $.ajax('/logout', {method: 'POST'});
  request.done(function(){
    // if performed sucessfully, reload the page to reflect changes
    window.location.reload();
  });
  request.fail(function(){
    // if failed, force logout by sending another request
    $.ajax('/force_logout', {method: 'POST'}).always(function(){
      // when done, reload the page
      window.location.reload();
    });
  });
});

// 'options' button clicked
$('.options-panel .options-button').on('click', function(event){
  // find a corresponding options panel element
  var target = $(event.target).parents('.options-panel');
  // toggle a corresponding options panel
  target.toggleClass('visible');

  // close all other option panels
  $('.options-panel.visible').not(target).removeClass('visible');
  // hide any 'delete confirmation' layers
  $('.hover-layer').removeClass('visible');
});

// 'delete' button is clicked
$('.item .options-panel .delete-button').on('click', function(event){
  // find a corresponding '.item' element
  var target = $(event.target).parents('.item');
  // show 'delete confirmation' layer on top of it
  target.find('.hover-layer').addClass('visible');
  // close all option panels
  $('.options-panel.visible').removeClass('visible');
});

// 'cancel' button on the 'delete confirmation' hover layer clicked
$('.hover-layer.visible .hover-layer-cancel').on('click', function(event){
  var target = $(event.target).parents('.hover-layer');
  // hide the hover layer
  target.removeClass('visible');
});

// 'confirm' button on the 'delete confirmation' hover layer clicked
$('.hover-layer.visible .hover-layer-confirm').on('click', function(event){
  var element = $(event.target);
  // retrieve a 'delete' URL from 'delete-data' attribute
  var url = element.data('delete-item');
  // send a delete request to the server
  var request = $.ajax(url, {method: 'POST'});
  request.always(function(){
    // when done, reload the page to reflect the changes
    window.location.reload();
  })
});

$(document).ready(function(){
  // make textareas expand to the height of the text entered in it
  autosize($('textarea'));
});
