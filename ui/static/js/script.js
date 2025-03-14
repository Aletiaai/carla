document.addEventListener('DOMContentLoaded', function() {
    const blogForm = document.getElementById('blogForm');
    const generateBtn = document.getElementById('generateBtn');
    const blogPreview = document.getElementById('blogPreview');
    const blogContent = document.getElementById('blogContent');
    const copyBtn = document.getElementById('copyBtn');
    const saveBtn = document.getElementById('saveBtn');
    const loading = document.getElementById('loading');
    const emailBtn = document.createElement('button');

    emailBtn.id = 'createEmailBtn';
    emailBtn.className = 'btn btn-secondary';
    emailBtn.textContent = 'Create Email Campaign';
    blogPreview.appendChild(emailBtn);
    
    let currentBlogData = null;
    
    // Generate blog
    blogForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const topic = document.getElementById('topic').value;
        const audience = document.getElementById('audience').value;
        const length = document.getElementById('length').value;
        
        // Show loading spinner
        loading.style.display = 'block';
        blogPreview.style.display = 'none';
        
        try {
            const response = await fetch('/api/blogs/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    topic: topic,
                    audience: audience,
                    length: parseInt(length),
                    user_id: 'default_user' // In a real app, get from auth
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                currentBlogData = result.data;
                
                // Display the blog content with markdown rendering
                const markdownContent = result.data.raw_content;
                
                // Simple markdown rendering (you can use a library like marked.js for better rendering)
                const htmlContent = markdownContent
                    .replace(/# (.*)/g, '<h1>$1</h1>')
                    .replace(/## (.*)/g, '<h2>$1</h2>')
                    .replace(/\n\n/g, '<br><br>');
                
                blogContent.innerHTML = htmlContent;
                blogPreview.style.display = 'block';
            } else {
                alert('Error generating blog: ' + result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error generating blog. Please try again.');
        } finally {
            loading.style.display = 'none';
        }
    });
    
    // Copy to clipboard
    // Replace the copy functionality with this corrected version
    copyBtn.addEventListener('click', function() {
        if (!currentBlogData) {
            console.error('No blog data available to copy.');
            return;
        }
        
        // Get the current HTML content from the editable div
        const contentElement = document.getElementById('blogContent');
        const htmlToCopy = contentElement.innerHTML;
        //const textToCopy = contentElement.innerText || contentElement.textContent;

        console.log('HTML content to copy:', htmlToCopy);

        
        // Debug output to verify we're getting content
        //console.log('Content to copy:', textToCopy);
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(htmlToCopy)
            .then(() => {
                    alert('Blog HTML copied to clipboard!');
                })
                .catch(err => {
                    console.error('Error copying to clipboard:', err);
                    alert('Failed to copy to clipboard');
                });
        } else {
            const textarea = document.createElement('textarea');
            textarea.value = htmlToCopy;
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                alert('Blog HTML copied to clipboard!');
            } catch (err) {
                console.error('Error copying to clipboard:', err);
                alert('Failed to copy to clipboard');
            }
            document.body.removeChild(textarea);
        }
    });
    
    // Save blog
    saveBtn.addEventListener('click', async function() {
        if (!currentBlogData) return;

        // Update current blog data with HTML content
        currentBlogData.raw_content = document.getElementById('blogContent').innerHTML;
        
        try {
            const response = await fetch('/api/blogs/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    blog_data: currentBlogData,
                    user_id: 'default_user' // In a real app, get from auth
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                alert('Blog saved successfully!');
            } else {
                alert('Error saving blog: ' + result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error saving blog. Please try again.');
        }
    });
    // Email campaign handler
    emailBtn.addEventListener('click', async () => {
        if (!currentBlogData) return;
        
        try {
            const campaign_title = document.getElementById('topic').value;
            const response = await fetch('/api/blogs/create-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: document.getElementById('blogContent').innerHTML,
                    title: currentBlogData.title || campaign_title
                }),
            });
            
            const result = await response.json();
            alert('Email campaign created successfully!');
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create email campaign');
        }
    });
});