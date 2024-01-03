var recognition;
var recognizing = false;
var final_transcript = '';

// Initialize speech recognition
function initializeRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onstart = function() {
            recognizing = true;
            document.getElementById("speak-button").innerHTML = "<i class='fa fa-microphone-slash'></i>";
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
        };

        recognition.onend = function() {
            recognizing = false;
            document.getElementById("speak-button").innerHTML = "<i class='fa fa-microphone'></i>";
        };

        recognition.onresult = function(event) {
            var interim_transcript = '';
            for (var i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    final_transcript += event.results[i][0].transcript;
                } else {
                    interim_transcript += event.results[i][0].transcript;
                }
            }
            document.getElementById("message-input").value = final_transcript + interim_transcript;
        };
    } else {
        console.error('webkitSpeechRecognition not supported in this browser.');
    }
}

// Function to start and stop recording
function record() {
    if (recognizing) {
        recognition.stop();
        return;
    }
    final_transcript = '';
    recognition.lang = document.getElementById("language").value;
    recognition.start();
}

// Initialize the speech recognition when the document is ready
$(document).ready(function() {
    initializeRecognition();



    // Your existing autocomplete code
    $("#message-input").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "/suggestions",
                data: { term: request.term },
                dataType: "json",
                success: function(data) {
                    response(data);
                }
            });
        }
    });
});



$(document).ready(function() {
    // Select the text input with the id of "query"
    $("#message-input").autocomplete({
        // Specify a function for the source option
        source: function(request, response) {
            // Use the jQuery ajax method to request the suggestions from the Flask app
            $.ajax({
                url: "/suggestions",
                data: {
                    // Pass the term parameter with the value of the request
                    term: request.term
                },
                dataType: "json",
                success: function(data) {
                    // Pass the data to the response callback
                    response(data);
                }
            });
        }
    });
});

