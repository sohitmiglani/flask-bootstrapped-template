function loading(){
        var user_521 = document.getElementById("user521").value
        var length_of_521 = user_521.length
        
        if (length_of_521>1){
            $("#loading").show(); 
        };
    };

function check_experiment() {
        server_url = "http://160.62.48.58:5001/api/check_folder_presence"

        user521= document.getElementById("user521").value
        gsm_id= document.getElementById("gsm_id").value

        // Format the input to json and use that as a param to the get call
        json_query = {'subdir': '/clscratch/miglaso1/' ,'user521': user521, 'gsm_id': gsm_id}
        // JQuery to call your nodejs. The second param. No sure that textStatus does, can use that for exception handling?
        $.getJSON(server_url, json_query, function(data, textStatus, jqXHR) {
            // Configurable. Use found element from data response in anyway you please
            if(data.found){
                message = 'The user- '.concat(user521,' - has run this experiment before. ',
                'If you continue, the previous results of ', gsm_id,' in Atlantis will be deleted.')
                alert(message);
            }
        });
    };