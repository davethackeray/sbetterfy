document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const selectAllBtn = document.getElementById('select-all-btn');
    const createPlaylistBtn = document.getElementById('create-playlist-btn');
    const tracksContainer = document.getElementById('tracks-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');
    const recommendationsResults = document.getElementById('recommendations-results');
    const noTracksMessage = document.getElementById('no-tracks-message');
    const feedbackForm = document.getElementById('feedback-form');
    const feedbackError = document.getElementById('feedback-error');
    const feedbackSuccess = document.getElementById('feedback-success');
    const submitFeedbackBtn = document.getElementById('submit-feedback-btn');
    const genresInput = document.getElementById('genres');

    let recommendedTracks = [];
    let selectedTracks = [];
    let availableGenres = [];

    // Fetch available genres for autocomplete
    fetchGenres();

    function fetchGenres() {
        fetch('/api/genres', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Failed to fetch genres.');
                });
            }
            return response.json();
        })
        .then(data => {
            availableGenres = data.genres || [];
            setupAutocomplete();
        })
        .catch(err => {
            console.error('Error fetching genres:', err);
        });
    }

    function setupAutocomplete() {
        if (!genresInput) return;

        genresInput.addEventListener('input', function(e) {
            const value = e.target.value;
            const lastCommaIndex = value.lastIndexOf(',');
            const currentWord = lastCommaIndex === -1 ? value : value.substring(lastCommaIndex + 1).trim();
            
            if (currentWord.length >= 2) {
                const suggestions = availableGenres.filter(genre => 
                    genre.toLowerCase().startsWith(currentWord.toLowerCase())
                );
                
                if (suggestions.length > 0) {
                    showSuggestions(suggestions, lastCommaIndex);
                } else {
                    hideSuggestions();
                }
            } else {
                hideSuggestions();
            }
        });

        genresInput.addEventListener('blur', function() {
            setTimeout(hideSuggestions, 200); // Delay to allow click on suggestion
        });
    }

    function showSuggestions(suggestions, lastCommaIndex) {
        let suggestionBox = document.getElementById('genre-suggestions');
        if (!suggestionBox) {
            suggestionBox = document.createElement('div');
            suggestionBox.id = 'genre-suggestions';
            suggestionBox.className = 'bg-gray-800 border border-gray-600 rounded-lg shadow-lg p-2 absolute z-10 max-h-40 overflow-y-auto';
            suggestionBox.style.width = genresInput.offsetWidth + 'px';
            suggestionBox.style.top = (genresInput.offsetTop + genresInput.offsetHeight + 5) + 'px';
            suggestionBox.style.left = genresInput.offsetLeft + 'px';
            genresInput.parentNode.appendChild(suggestionBox);
        }
        
        suggestionBox.innerHTML = '';
        suggestions.slice(0, 5).forEach(genre => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'p-2 hover:bg-gray-700 cursor-pointer text-white';
            suggestionItem.textContent = genre;
            suggestionItem.addEventListener('click', function() {
                const currentValue = genresInput.value;
                const newValue = lastCommaIndex === -1 ? genre : currentValue.substring(0, lastCommaIndex + 1) + ' ' + genre;
                genresInput.value = newValue;
                hideSuggestions();
                genresInput.focus();
            });
            suggestionBox.appendChild(suggestionItem);
        });
    }

    function hideSuggestions() {
        const suggestionBox = document.getElementById('genre-suggestions');
        if (suggestionBox) {
            suggestionBox.remove();
        }
    }

    if (generateBtn) {
        generateBtn.addEventListener('click', function() {
            const count = parseInt(document.getElementById('count').value);
            const discoveryLevel = parseInt(document.getElementById('discovery-level').value);
            const minYear = parseInt(document.getElementById('min-year').value);
            const maxPopularity = parseInt(document.getElementById('max-popularity').value);
            const targetTempo = parseInt(document.getElementById('target-tempo').value);
            const targetEnergy = parseInt(document.getElementById('target-energy').value);
            const genres = document.getElementById('genres').value.split(',').map(g => g.trim()).filter(g => g);
            const moods = document.getElementById('moods').value.split(',').map(m => m.trim()).filter(m => m);

            // Input validation
            if (isNaN(count) || count < 1 || count > 50) {
                showError('Please enter a valid number of tracks (1-50).');
                return;
            }
            if (isNaN(discoveryLevel) || discoveryLevel < 0 || discoveryLevel > 100) {
                showError('Please enter a valid discovery level (0-100).');
                return;
            }
            if (isNaN(minYear) || minYear < 1900 || minYear > 2025) {
                showError('Please enter a valid minimum year (1900-2025).');
                return;
            }
            if (isNaN(maxPopularity) || maxPopularity < 0 || maxPopularity > 100) {
                showError('Please enter a valid maximum popularity (0-100).');
                return;
            }
            if (isNaN(targetTempo) || targetTempo < 40 || targetTempo > 200) {
                showError('Please enter a valid target tempo (40-200 BPM).');
                return;
            }
            if (isNaN(targetEnergy) || targetEnergy < 0 || targetEnergy > 100) {
                showError('Please enter a valid target energy (0-100).');
                return;
            }

            // Show loading indicator
            loadingIndicator.classList.remove('hidden');
            errorMessage.classList.add('hidden');
            recommendationsResults.classList.add('hidden');
            noTracksMessage.classList.add('hidden');

            // Make API request
            fetch('/api/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    count: count,
                    discovery_level: discoveryLevel,
                    min_year: minYear,
                    max_popularity: maxPopularity,
                    target_tempo: targetTempo,
                    target_energy: targetEnergy,
                    genres: genres,
                    moods: moods
                })
            })
            .then(response => {
                loadingIndicator.classList.add('hidden');
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(errorData.error || 'Failed to fetch recommendations. Please try again.');
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Raw API response:', data);
                recommendedTracks = data.tracks || (Array.isArray(data) ? data : []);
                console.log('Processed recommendedTracks:', recommendedTracks);
                selectedTracks = [];
                renderTracks(recommendedTracks);
                
                if (recommendedTracks.length === 0) {
                    noTracksMessage.textContent = "No recommendations could be verified with Spotify. Please try different parameters or generate again.";
                    noTracksMessage.classList.remove('hidden');
                    recommendationsResults.classList.add('hidden');
                } else {
                    recommendationsResults.classList.remove('hidden');
                    noTracksMessage.classList.add('hidden');
                }
            })
            .catch(err => {
                showError(`Error: ${err.message}`);
            });
        });
    }

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            const checkboxes = tracksContainer.querySelectorAll('input[type="checkbox"]');
            const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = !allChecked;
                const trackId = checkbox.getAttribute('data-track-id');
                if (!allChecked) {
                    if (!selectedTracks.includes(trackId)) {
                        selectedTracks.push(trackId);
                    }
                } else {
                    selectedTracks = selectedTracks.filter(id => id !== trackId);
                }
            });
            
            selectAllBtn.textContent = allChecked ? 'Select All' : 'Deselect All';
        });
    }

    if (createPlaylistBtn) {
        createPlaylistBtn.addEventListener('click', function() {
            if (selectedTracks.length === 0) {
                showError('Please select at least one track to create a playlist.');
                return;
            }

            const playlistName = prompt('Enter a name for your playlist:', 'AI Generated Playlist');
            if (!playlistName) {
                showError('Playlist creation cancelled or invalid name provided.');
                return;
            }

            // Show loading state
            createPlaylistBtn.disabled = true;
            createPlaylistBtn.textContent = 'Creating...';
            errorMessage.classList.add('hidden');

            fetch('/api/create-playlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: playlistName,
                    track_uris: selectedTracks
                })
            })
            .then(response => {
                createPlaylistBtn.disabled = false;
                createPlaylistBtn.textContent = 'Create Playlist';
                
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(errorData.error || 'Failed to create playlist. Please try again.');
                    });
                }
                return response.json();
            })
            .then(data => {
                alert(`Playlist "${data.name}" created successfully with ${data.track_count} tracks!`);
                // Optionally, redirect to Spotify or show a link
                if (data.external_url) {
                    window.open(data.external_url, '_blank');
                }
            })
            .catch(err => {
                showError(`Error creating playlist: ${err.message}`);
            });
        });
    }

    function renderTracks(tracks) {
        console.log('Rendering tracks:', tracks);
        tracksContainer.innerHTML = '';
        if (!tracks || tracks.length === 0) {
            console.log('No tracks to render.');
            return;
        }

        tracks.forEach(track => {
            const trackCard = document.createElement('div');
            trackCard.className = 'track-card';
            trackCard.innerHTML = `
                <div class="track-info flex-1">
                    <div class="font-medium text-white">${track.title}</div>
                    <div class="text-sm text-gray-400">${track.artist}</div>
                </div>
                <input type="checkbox" data-track-id="${track.uri}" class="ml-4 w-5 h-5 text-green-500 focus:ring-green-500 border-gray-600 bg-gray-700 rounded">
            `;
            tracksContainer.appendChild(trackCard);

            const checkbox = trackCard.querySelector('input[type="checkbox"]');
            checkbox.addEventListener('change', function() {
                if (this.checked) {
                    if (!selectedTracks.includes(track.uri)) {
                        selectedTracks.push(track.uri);
                    }
                } else {
                    selectedTracks = selectedTracks.filter(uri => uri !== track.uri);
                }
            });
        });
    }

    function showError(message) {
        // Create a flash message element similar to Flask flash messages
        const flashContainer = document.createElement('div');
        flashContainer.className = 'flash-message bg-red-500 text-white p-4 rounded-lg shadow-lg mb-2';
        flashContainer.textContent = message;
        
        // Add to the flash messages container or create one if it doesn't exist
        let flashMessages = document.getElementById('flash-messages');
        if (!flashMessages) {
            flashMessages = document.createElement('div');
            flashMessages.id = 'flash-messages';
            flashMessages.className = 'fixed top-4 right-4 z-50';
            document.body.appendChild(flashMessages);
        }
        
        flashMessages.appendChild(flashContainer);
        setTimeout(() => {
            flashContainer.remove();
        }, 5000);
    }

    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const rating = document.getElementById('ui-rating').value;
            const comments = document.getElementById('feedback-comments').value.trim();

            if (!rating || rating < 1 || rating > 5) {
                showFeedbackError('Please select a valid rating.');
                return;
            }

            if (comments.length > 1000) {
                showFeedbackError('Comments should not exceed 1000 characters.');
                return;
            }

            // Simulate API call or store feedback locally for now
            submitFeedbackBtn.disabled = true;
            submitFeedbackBtn.textContent = 'Submitting...';
            feedbackError.classList.add('hidden');
            feedbackSuccess.classList.add('hidden');

            setTimeout(() => {
                submitFeedbackBtn.disabled = false;
                submitFeedbackBtn.textContent = 'Submit Feedback';
                feedbackSuccess.classList.remove('hidden');
                document.getElementById('feedback-comments').value = '';
                setTimeout(() => {
                    feedbackSuccess.classList.add('hidden');
                }, 3000);
            }, 1000);
        });
    }

    function showFeedbackError(message) {
        showError(message);
    }
});
