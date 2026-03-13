document.addEventListener('DOMContentLoaded', function() {
    const posts = document.querySelectorAll('[data-post-id]');
    posts.forEach(post => {
        const postId = post.getAttribute('data-post-id');
        if (!postId) return;
        fetch(`/post/${postId}/view`, {method: 'POST'})
            .then(res => res.json().then(data => ({status: res.status, body: data})))
            .then(({status, body}) => {
                if (status === 200 && body && body.views !== undefined) {
                    const el = document.getElementById(`views-${postId}`);
                    if (el) el.textContent = `${body.views} views`;
                }
            })
            .catch(err => console.error('Error recording view', err));
    });
});
