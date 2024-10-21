// script.js

// Example: Confirmation before form submission
document.addEventListener('DOMContentLoaded', function() {
    const deleteLinks = document.querySelectorAll('a[href^="/delete/"]');
    deleteLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            const confirmation = confirm('Are you sure you want to delete this complaint?');
            if (!confirmation) {
                event.preventDefault();
            }
        });
    });
});
