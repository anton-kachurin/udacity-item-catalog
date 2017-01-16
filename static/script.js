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
