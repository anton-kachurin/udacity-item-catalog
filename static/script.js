$('.logout-button').click(function(){
  var request = $.ajax('/logout',{method: 'POST'});
  request.done(function(){
    window.location.reload();
  })
});
