function MessageError(mistakes) {
    $('#mistakes').html("");
    let error = "";
    for(let item in mistakes.responseJSON.error){
        error += '<div class = "alert alert-danger" <strong>' + mistakes.responseJSON.error[item] + '</strong></div';
    }
    $('#mistakes').append(error);
}
function NotificationError(message){
    Swal.fire({
        title: 'Error',
        text: 'Message',
        icon: 'error'
    })
}
function NotificationSuccess(message){
    Swal.fire({
        title: 'Exitoso!',
        text: 'Message',
        icon: 'success'
    })
}
/*Modal Notificacion*/
function Validation(){
    swal({
      title: "Pregunta?",
      text: "Mensaje aqui!",
      icon: "warning",
      buttons: true,
      dangerMode: true,
    })
    .then((willDelete) => {
      if (willDelete) {
        swal("Mensaje cuando presiona ok!", {
          icon: "success",
        });
      } else {
        swal("Mensaje cuando presiona cancel!");
      }
    });
}
function validInput(){
    swal({
      text: 'Search for a movie. e.g. "La La Land".',
      content: "input",
      button: {
        text: "Search!",
        closeModal: false,
      },
    })
    .then(name => {
      if (!name) throw null;

      return fetch(`https://itunes.apple.com/search?term=${name}&entity=movie`);
    })
    .then(results => {
      return results.json();
    })
    .then(json => {
      const movie = json.results[0];

      if (!movie) {
        return swal("No movie was found!");
      }

      const name = movie.trackName;
      const imageURL = movie.artworkUrl100;

      swal({
        title: "Top result:",
        text: name,
        icon: imageURL,
      });
    })
    .catch(err => {
      if (err) {
        swal("Oh noes!", "The AJAX request failed!", "error");
      } else {
        swal.stopLoading();
        swal.close();
      }
});
}