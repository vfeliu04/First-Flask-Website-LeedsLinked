
function removeFlashMessage(element) {
    element.remove();
}

function goBack() {
    window.history.back();
    
}

// Listen for the popstate event
window.addEventListener('popstate', function(event) {
    // Check if the event was triggered by a back navigation
    if (event.state && event.state.pageReload) {
        console.log('Reloading the page...');
        // Reload the page
        window.location.reload();
    }
});

document.addEventListener("DOMContentLoaded", function() {
    var flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(element) {
        setTimeout(function() {
            if (!element.classList.contains('closed')) {
                removeFlashMessage(element);
            }
        }, 10000);
    });
});