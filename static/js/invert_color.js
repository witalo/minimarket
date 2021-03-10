if (sessionStorage.getItem('mode') === 'dark') {
    $('body').css({'filter': 'invert(1)'});
    $('input[id=switch-label]').prop('checked', true);
} else {
    $('input[id=switch-label]').prop('checked', false);
}

$('input[id=switch-label]').change(function () {
    if (this.checked) {

        $('body').css({'filter': 'invert(1)'})
        sessionStorage.setItem('mode', 'dark');
    } else {
        $('body').css({'filter': 'invert(0)'})
        sessionStorage.setItem('mode', 'white');
    }
});
