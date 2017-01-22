$('.logout-button').click(function(){
  var request = $.ajax('/logout', {method: 'POST'});
  request.done(function(){
    window.location.reload();
  });
  request.fail(function(){
    $.ajax('/force_logout', {method: 'POST'}).always(function(){
      window.location.reload();
    });
  });
});

$('.options-panel .options-button').on('click', function(event){
  var target = $(event.target).parents('.options-panel');
  $('.options-panel.visible').not(target).removeClass('visible');
  target.toggleClass('visible');
  $('.hover-layer').removeClass('visible');
});

$('.item .options-panel .delete-button').on('click', function(event){
  var target = $(event.target).parents('.item');
  target.find('.hover-layer').addClass('visible');
  $('.options-panel.visible').removeClass('visible');
});

$('.hover-layer .hover-layer-cancel').on('click', function(event){
  var target = $(event.target).parents('.hover-layer');
  target.removeClass('visible');
});

$('.hover-layer .hover-layer-confirm').on('click', function(event){
  var element = $(event.target);
  var url = element.data('delete-item');
  var request = $.ajax(url, {method: 'POST'});
  request.always(function(){
    window.location.reload();
  })
});

$(document).ready(function(){
  autosize($('textarea'));
});
