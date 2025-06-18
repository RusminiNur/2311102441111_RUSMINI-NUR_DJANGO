document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelector('nav .space-x-4');
    const hamburger = document.createElement('button');
    hamburger.innerHTML = '☰';
    hamburger.className = 'text-gray-600 hover:text-blue-700 md:hidden p-2';
    document.querySelector('nav .container').appendChild(hamburger);

    hamburger.addEventListener('click', function() {
        navLinks.style.display = navLinks.style.display === 'block' ? 'none' : 'block';
    });

    // Existing form submission confirmation (optional)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // if (!confirm('Are you sure you want to submit?')) {
            //     e.preventDefault();
            // }
        });
    });
});