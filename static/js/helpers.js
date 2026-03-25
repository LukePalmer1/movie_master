function setUpWatchListButtons(afterFunc, userID){
    const watchlistButtons = document.getElementsByClassName('watchlistButton');
    
    if (watchlistButtons) {
        for (const button of watchlistButtons) {
            button.addEventListener('click', function() {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                button.disabled = true;
                fetch("/".concat(String(button.id).concat("/watchlist/")),{
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'profile=' + encodeURIComponent(userID),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        afterFunc(button);
                    }
                })
                .catch(() => {
                    alert("issue")
                })  
                .finally(() => {
                    button.disabled = false;
                })
            });
        };
    }
}