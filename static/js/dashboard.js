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
    let filterSuggestions = [];

    // Fetch available genres for autocomplete
    fetchGenres();
    // Fetch filter extreme suggestions
    fetchFilterSuggestions();

    function fetchGenres() {
        console.log('Fetching genres from /api/genres');
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
            console.log('Genres fetched:', availableGenres);
            setupAutocomplete();
        })
        .catch(err => {
            console.error('Error fetching genres:', err);
            showError(`Failed to load genres from Spotify: ${err.message}. Using a comprehensive default list of genres for autocomplete.`);
            // Fallback to a comprehensive static list of genres
            availableGenres = [
                "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime", "black-metal", 
                "bluegrass", "blues", "bossanova", "brazil", "breakbeat", "british", "cantopop", 
                "chicago-house", "children", "chill", "classical", "club", "comedy", "country", 
                "dance", "dancehall", "death-metal", "deep-house", "detroit-techno", "disco", 
                "disney", "drum-and-bass", "dub", "dubstep", "edm", "electro", "electronic", 
                "emo", "folk", "forro", "french", "funk", "garage", "german", "gospel", "goth", 
                "grindcore", "groove", "grunge", "guitar", "happy", "hard-rock", "hardcore", 
                "hardstyle", "heavy-metal", "hip-hop", "holidays", "honky-tonk", "house", 
                "idm", "indian", "indie", "indie-pop", "industrial", "iranian", "j-dance", 
                "j-idol", "j-pop", "j-rock", "jazz", "k-pop", "kids", "latin", "latino", 
                "malay", "mandopop", "metal", "metal-misc", "metalcore", "minimal-techno", 
                "movies", "mpb", "new-age", "new-release", "opera", "pagode", "party", "philippines-opm", 
                "piano", "pop", "pop-film", "post-dubstep", "power-pop", "progressive-house", 
                "psych-rock", "punk", "punk-rock", "r-n-b", "rainy-day", "reggae", "reggaeton", 
                "road-trip", "rock", "rock-n-roll", "rockabilly", "romance", "sad", "salsa", 
                "samba", "sertanejo", "show-tunes", "singer-songwriter", "ska", "sleep", "soul", 
                "soundtracks", "spanish", "study", "summer", "swedish", "synth-pop", "tango", 
                "techno", "trance", "trip-hop", "turkish", "work-out", "world-music"
            ];
            console.log('Using fallback genres:', availableGenres);
            setupAutocomplete();
        });
    }

    function setupAutocomplete() {
        if (!genresInput) {
            console.error('Genres input field not found in DOM');
            showError('Genres input field not found. Autocomplete cannot be initialized.');
            return;
        }
        console.log('Setting up autocomplete for genres input');
        let selectedGenres = [];

        // Create a container for tags
        const tagContainer = document.createElement('div');
        tagContainer.className = 'flex flex-wrap gap-2 mb-2 min-h-[2rem] border border-gray-600 rounded-lg p-2 bg-gray-800';
        tagContainer.id = 'genre-tags';
        genresInput.parentNode.insertBefore(tagContainer, genresInput);
        genresInput.classList.add('flex-1');

        genresInput.addEventListener('input', function(e) {
            const value = e.target.value.trim();
            if (value.length >= 2) {
                const suggestions = availableGenres.filter(genre => 
                    genre.toLowerCase().startsWith(value.toLowerCase()) && !selectedGenres.includes(genre)
                );
                
                if (suggestions.length > 0) {
                    showSuggestions(suggestions);
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

        genresInput.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && genresInput.value === '' && selectedGenres.length > 0) {
                // Remove the last selected genre on backspace when input is empty
                selectedGenres.pop();
                updateGenreTags(selectedGenres, tagContainer, genresInput);
            }
        });
    }

    function showSuggestions(suggestions) {
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
                let selectedGenres = getSelectedGenres();
                selectedGenres.push(genre);
                updateGenreTags(selectedGenres, document.getElementById('genre-tags'), genresInput);
                genresInput.value = '';
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

    function updateGenreTags(genres, container, input) {
        container.innerHTML = '';
        genres.forEach(genre => {
            const tag = document.createElement('span');
            tag.className = 'bg-green-500 text-white px-2 py-1 rounded-full text-sm flex items-center gap-1';
            tag.innerHTML = `${genre} <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 cursor-pointer" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>`;
            container.appendChild(tag);
            tag.querySelector('svg').addEventListener('click', () => {
                let selectedGenres = getSelectedGenres().filter(g => g !== genre);
                updateGenreTags(selectedGenres, container, input);
                input.focus();
            });
        });
    }

    function getSelectedGenres() {
        const tags = document.querySelectorAll('#genre-tags span');
        return Array.from(tags).map(tag => tag.textContent.split(' ')[0]);
    }

    if (generateBtn) {
        generateBtn.addEventListener('click', function() {
            const count = parseInt(document.getElementById('count').value);
            const discoveryLevel = parseInt(document.getElementById('discovery-level').value);
            const minYear = parseInt(document.getElementById('min-year').value);
            const maxPopularity = parseInt(document.getElementById('max-popularity').value);
            const tempoSelect = document.getElementById('tempo');
            const energySelect = document.getElementById('energy');
            const targetTempo = tempoSelect ? tempoSelect.value : '';
            const targetEnergy = energySelect ? energySelect.value : '';
            const genres = getSelectedGenres();
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
                    tempo: targetTempo,
                    energy: targetEnergy,
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

            // Show modal for playlist options
            showPlaylistModal(selectedTracks);
        });
    }

    function showPlaylistModal(tracks) {
        // Create modal container
        let modal = document.getElementById('playlist-modal');
        if (modal) {
            modal.remove(); // Remove existing modal if it exists
        }
        
        modal = document.createElement('div');
        modal.id = 'playlist-modal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full">
                <h2 class="text-2xl font-bold mb-4 text-white">Save to Playlist</h2>
                <div id="playlist-options" class="mb-4">
                    <div class="flex items-center mb-2">
                        <input type="radio" id="new-playlist" name="playlist-option" value="new" checked class="text-green-500 focus:ring-green-500">
                        <label for="new-playlist" class="ml-2 text-white">Create New Playlist</label>
                    </div>
                    <div class="flex items-center">
                        <input type="radio" id="existing-playlist" name="playlist-option" value="existing" class="text-green-500 focus:ring-green-500">
                        <label for="existing-playlist" class="ml-2 text-white">Add to Existing Playlist</label>
                    </div>
                </div>
                <div id="new-playlist-name" class="mb-4">
                    <label for="playlist-name" class="block text-white mb-1">Playlist Name:</label>
                    <input type="text" id="playlist-name" value="AI Generated Playlist" class="w-full p-2 border border-gray-600 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500">
                </div>
                <div id="existing-playlist-select" class="mb-4 hidden">
                    <label for="playlist-select" class="block text-white mb-1">Select Playlist:</label>
                    <select id="playlist-select" class="w-full p-2 border border-gray-600 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500">
                        <option value="">Loading playlists...</option>
                    </select>
                </div>
                <div class="flex justify-end">
                    <button id="cancel-btn" class="px-4 py-2 bg-gray-600 text-white rounded mr-2 hover:bg-gray-500">Cancel</button>
                    <button id="save-btn" class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">Save</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Fetch playlists if selecting existing playlist
        const existingRadio = document.getElementById('existing-playlist');
        const existingSelectDiv = document.getElementById('existing-playlist-select');
        const newPlaylistDiv = document.getElementById('new-playlist-name');
        
        existingRadio.addEventListener('change', function() {
            existingSelectDiv.classList.remove('hidden');
            newPlaylistDiv.classList.add('hidden');
            fetchPlaylists();
        });
        
        document.getElementById('new-playlist').addEventListener('change', function() {
            existingSelectDiv.classList.add('hidden');
            newPlaylistDiv.classList.remove('hidden');
        });

        // Handle save and cancel actions
        document.getElementById('cancel-btn').addEventListener('click', function() {
            modal.remove();
        });

        document.getElementById('save-btn').addEventListener('click', function() {
            const option = document.querySelector('input[name="playlist-option"]:checked').value;
            if (option === 'new') {
                const playlistName = document.getElementById('playlist-name').value.trim();
                if (!playlistName) {
                    showError('Please enter a valid playlist name.');
                    return;
                }
                createNewPlaylist(playlistName, tracks);
            } else {
                const playlistId = document.getElementById('playlist-select').value;
                if (!playlistId) {
                    showError('Please select a playlist.');
                    return;
                }
                addToExistingPlaylist(playlistId, tracks);
            }
            modal.remove();
        });
    }

    function fetchPlaylists() {
        fetch('/api/user-playlists', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Failed to fetch playlists.');
                });
            }
            return response.json();
        })
        .then(data => {
            const select = document.getElementById('playlist-select');
            select.innerHTML = '';
            if (data.playlists && data.playlists.length > 0) {
                data.playlists.forEach(playlist => {
                    const option = document.createElement('option');
                    option.value = playlist.id;
                    option.textContent = `${playlist.name} (${playlist.track_count} tracks)`;
                    select.appendChild(option);
                });
            } else {
                select.innerHTML = '<option value="">No playlists found</option>';
            }
        })
        .catch(err => {
            showError(`Failed to load playlists: ${err.message}`);
            const select = document.getElementById('playlist-select');
            select.innerHTML = '<option value="">Error loading playlists</option>';
        });
    }

    function createNewPlaylist(name, tracks) {
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
                name: name,
                track_uris: tracks
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
            showError(`Playlist "${data.name}" created successfully with ${data.track_count} tracks!`);
            if (data.external_url) {
                window.open(data.external_url, '_blank');
            }
        })
        .catch(err => {
            showError(`Error creating playlist: ${err.message}`);
        });
    }

    function addToExistingPlaylist(playlistId, tracks) {
        // Show loading state
        createPlaylistBtn.disabled = true;
        createPlaylistBtn.textContent = 'Adding...';
        errorMessage.classList.add('hidden');

        fetch('/api/add-to-playlist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                playlist_id: playlistId,
                track_uris: tracks
            })
        })
        .then(response => {
            createPlaylistBtn.disabled = false;
            createPlaylistBtn.textContent = 'Create Playlist';
            
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Failed to add tracks to playlist. Please try again.');
                });
            }
            return response.json();
        })
        .then(data => {
            showError(`Successfully added ${data.track_count} tracks to the playlist!`);
        })
        .catch(err => {
            showError(`Error adding tracks to playlist: ${err.message}`);
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

    function fetchFilterSuggestions() {
        console.log('Fetching filter extreme suggestions from /api/filter-suggestions');
        fetch('/api/filter-suggestions', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Failed to fetch filter suggestions.');
                });
            }
            return response.json();
        })
        .then(data => {
            filterSuggestions = data.suggestions || [];
            console.log('Filter suggestions fetched:', filterSuggestions);
            renderFilterSuggestions(filterSuggestions);
        })
        .catch(err => {
            console.error('Error fetching filter suggestions:', err);
            showError(`Failed to load filter suggestions: ${err.message}`);
            document.getElementById('loading-suggestions').classList.add('hidden');
            document.getElementById('no-suggestions-message').classList.remove('hidden');
        });
    }

    function renderFilterSuggestions(suggestions) {
        const suggestionsContainer = document.getElementById('filter-suggestions');
        const loadingSuggestions = document.getElementById('loading-suggestions');
        const noSuggestionsMessage = document.getElementById('no-suggestions-message');
        
        loadingSuggestions.classList.add('hidden');
        
        if (!suggestions || suggestions.length === 0) {
            noSuggestionsMessage.classList.remove('hidden');
            suggestionsContainer.classList.add('hidden');
            return;
        }
        
        noSuggestionsMessage.classList.add('hidden');
        suggestionsContainer.classList.remove('hidden');
        suggestionsContainer.innerHTML = '';
        
        suggestions.forEach(category => {
            const categoryCard = document.createElement('div');
            categoryCard.className = 'category-card mb-4';
            categoryCard.innerHTML = `
                <h3 class="text-lg font-medium text-white mb-2">${category.filter} - ${category.extreme}</h3>
                <div class="tracks-grid grid grid-cols-1 gap-2"></div>
            `;
            const tracksGrid = categoryCard.querySelector('.tracks-grid');
            
            if (category.tracks && category.tracks.length > 0) {
                category.tracks.slice(0, 1).forEach(track => {
                    const trackCard = document.createElement('div');
                    trackCard.className = 'track-card p-2';
                    trackCard.innerHTML = `
                        <div class="track-info flex-1">
                            <div class="font-medium text-white">${track.title}</div>
                            <div class="text-sm text-gray-400">${track.artist}</div>
                            <div class="text-xs text-gray-500">
                                ${track.tempo !== 'N/A' ? 'Tempo: ' + track.tempo + ' | ' : ''}
                                ${track.energy !== 'N/A' ? 'Energy: ' + track.energy + ' | ' : ''}
                                ${track.mood !== 'N/A' ? 'Mood: ' + track.mood : ''}
                            </div>
                        </div>
                    `;
                    tracksGrid.appendChild(trackCard);
                });
            } else {
                tracksGrid.innerHTML = '<p class="text-gray-400 text-sm">No tracks available for this category.</p>';
            }
            
            suggestionsContainer.appendChild(categoryCard);
        });
    }
});
