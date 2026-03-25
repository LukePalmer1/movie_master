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

function setUpEditReviews() {
    const updateStarVisuals = setUpStarRating();

    const ratingInput = document.getElementById('rating-input');
    const ratingDisplay = document.getElementById('rating-display');
    const editReviewForm = document.getElementById('editReviewForm');
    const editReviewUrl = document.getElementById('editReviewUrl');
    const editReviewText = document.getElementById('editReviewText');
    const editReviewMovieTitle = document.getElementById('editReviewMovieTitle');
    const saveReviewBtn = document.getElementById('saveReviewBtn');
    const editReviewFeedback = document.getElementById('editReviewFeedback');
    const modalElement = document.getElementById('editReviewModal');
    const editReviewModal = modalElement ? bootstrap.Modal.getOrCreateInstance(modalElement) : null;

    if (!editReviewForm) return;
    document.querySelectorAll('.edit-review-btn').forEach((button) => {
        button.addEventListener('click', function() {
            editReviewUrl.value = this.dataset.editUrl;
            editReviewMovieTitle.textContent = this.dataset.movieTitle;
            editReviewText.value = this.dataset.review || '';
            ratingInput.value = this.dataset.rating || 0;
            ratingDisplay.innerText = (this.dataset.rating || 0) + ' / 5';

            if (updateStarVisuals) {
                updateStarVisuals(parseFloat(this.dataset.rating || 0));
            }
            editReviewFeedback.style.display = 'none';
            editReviewFeedback.textContent = '';
        });
    });

    editReviewForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const csrfToken = editReviewForm.querySelector('[name=csrfmiddlewaretoken]').value;
        const url = editReviewUrl.value;

        saveReviewBtn.disabled = true;
        saveReviewBtn.textContent = 'Saving..';
        editReviewFeedback.style.display = 'none';
        editReviewFeedback.textContent = '';

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                rating: ratingInput.value,
                review: editReviewText.value
            }),
        })
        .then(async (response) => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Something went wrong!');
            } return data;
        })
        .then((data) => {
            const reviewText = document.getElementById(`review-text-${data.rating_id}`);
            const ratingValue = document.getElementById(`rating-value-${data.rating_id}`);
            const editButton = document.querySelector(`.edit-review-btn[data-rating-id="${data.rating_id}"]`);
            if (reviewText) reviewText.textContent = `"${data.review}"`;
            if (ratingValue) ratingValue.textContent = `${data.rating} / 5`;
            if (editButton) {
                editButton.dataset.review = data.review;
                editButton.dataset.rating = data.rating;
            }
            editReviewFeedback.style.display = 'block';
            editReviewFeedback.style.color = 'green';
            editReviewFeedback.textContent = 'Review updated!';

            setTimeout(() => {
                if (editReviewModal) editReviewModal.hide();
            }, 500);
        })
        .catch((error) => {
            editReviewFeedback.style.display = 'block';
            editReviewFeedback.style.color = 'red';
            editReviewFeedback.textContent = error.message || 'Network error. Please try again.';
        })
        .finally(() => {
            saveReviewBtn.disabled = false;
            saveReviewBtn.textContent = 'Save Rating';
        });
    });
}

function setUpStarRating() {
    const ratingContainer = document.getElementById('interactive-rating');
    if (!ratingContainer) return null;

    const stars = ratingContainer.querySelectorAll('i');
    const ratingInput = document.getElementById('rating-input');
    const ratingDisplay = document.getElementById('rating-display');

    function updateStarVisuals(value) {
        stars.forEach((star, index) => {
            star.className = 'bi text-warning ';
            if (value >= index + 1) star.className += 'bi-star-fill';
            else if (value >= index + 0.5) star.className += 'bi-star-half';
            else star.className += 'bi-star';
        });
    }

    stars.forEach((star, index) => {
        star.addEventListener('mousemove', function(e) {
            const rect = star.getBoundingClientRect();
            const isHalf = (e.clientX - rect.left) < (rect.width / 2);
            updateStarVisuals(index + (isHalf ? 0.5 : 1));
        });

        star.addEventListener('click', function(e) {
            const rect = star.getBoundingClientRect();
            const isHalf = (e.clientX - rect.left) < (rect.width / 2);
            const finalValue = index + (isHalf ? 0.5 : 1);

            ratingInput.value = finalValue;
            ratingDisplay.innerText = finalValue + ' / 5';
        });
    });

    ratingContainer.addEventListener('mouseleave', function() {
        updateStarVisuals(parseFloat(ratingInput.value || 0));
    });
    return updateStarVisuals;
}

function setUpFollowButtons(afterFunc, userID){
    const followBtns = document.getElementsByClassName('follow-btn');
    for(const button of followBtns) {
        button.addEventListener('click', function() {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            button.disabled = true;
            fetch("/".concat(String(button.id).concat("/toggle-follow/")),{
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