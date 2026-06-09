// Attach click handlers to like buttons and call the backend API to increment likes.
document.addEventListener('DOMContentLoaded', function () {
    function onLikeClick(e) {
        const btn = e.currentTarget;
        const postId = btn.getAttribute('data-post-id');
        if (!postId) return;

        // simple GET request to the like endpoint; update the count on success
        fetch(`/api/post/${postId}/like`)
            .then(res => res.json().then(data => ({status: res.status, body: data})))
            .then(({status, body}) => {
                if (status === 200 && body && body.likes !== undefined) {
                    const el = document.getElementById(`likes-${postId}`);
                    if (el) el.textContent = body.likes;
                    // give visual feedback
                    btn.classList.add('liked');
                    setTimeout(() => btn.classList.remove('liked'), 500);
                } else {
                    console.warn('Like failed', body);
                }
            }).catch(err => console.error('Error liking post', err));
    }

    const buttons = document.querySelectorAll('.like-button');
    buttons.forEach(b => b.addEventListener('click', onLikeClick));
});
