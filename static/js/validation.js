function validateFloat(event) {
    var input = event.target.value;
    if (isNaN(parseFloat(input))) {
       event.target.setCustomValidity("Please enter a valid float value.");
    } else {
       event.target.setCustomValidity("");
    }
 }