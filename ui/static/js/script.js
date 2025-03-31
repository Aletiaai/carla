document.addEventListener('DOMContentLoaded', function() {
    const blogForm = document.getElementById('blogForm');
    const generateBtn = document.getElementById('generateBtn');
    const blogPreview = document.getElementById('blogPreview');
    const blogContent = document.getElementById('blogContent');
    const copyBtn = document.getElementById('copyBtn');
    const saveBtn = document.getElementById('saveBtn');
    const loading = document.getElementById('loading');
    const emailBtn = document.getElementById('createEmailBtn');
    const publishToWPBtn = document.getElementById('publishToWPBtn');

    let currentBlogData = null;
    
    // Generate blog
    blogForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const topic = document.getElementById('topic').value;
        const audience = document.getElementById('audience').value;
        const length = document.getElementById('length').value;
        const personalStory = document.getElementById('personalStory').value;
        
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
                    personal_story: personalStory,
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
    copyBtn.addEventListener('click', function() {
        if (!currentBlogData) {
            console.error('No blog data available to copy.');
            return;
        }
        
        // Get the current HTML content from the editable div
        const contentElement = document.getElementById('blogContent');
        const htmlToCopy = contentElement.innerHTML;

        console.log('HTML content to copy:', htmlToCopy);
        
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
    
saveBtn.addEventListener('click', async function() {
    if (!currentBlogData || !currentBlogData.id) {
        alert('No blog data available to save.');
        console.error('❌ Error: currentBlogData is missing or has no ID.', currentBlogData);
        return;
    }

    // Get the edited content as plain text
    const blogContentElement = document.getElementById('blogContent');
    const finalContent = blogContentElement.textContent || blogContentElement.innerText;


    // Debugging logs
    console.log('🔵 Sending Save Request with:');
    console.log('   - blog_id:', currentBlogData.id);
    console.log('   - final_content length:', finalContent.length);

    try {
        const response = await fetch('/api/blogs/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                blog_id: currentBlogData.id,
                final_content: finalContent,
                user_id: 'default_user' // Optional, if needed
            })
        });

        console.log('📡 Server response status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Server error:', errorText);
            throw new Error(`Server error: ${response.status} - ${errorText}`);
        }

        const result = await response.json();
        console.log('✅ Save result:', result);

        if (result.status === 'success') {
            alert('Blog saved successfully!');
        } else {
            throw new Error(result.message || 'Unknown error');
        }
    } catch (error) {
        console.error('🔥 Error saving blog:', error);
        alert('Error saving blog: ' + error.message);
    }
});


    // Email campaign handler
    emailBtn.addEventListener('click', async () => {
        if (!currentBlogData) return;
        
        try {
            const campaign_title = document.getElementById('topic').value;
            const response = await fetch('/api/blogs/email-campaign', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: document.getElementById('blogContent').innerHTML,
                    title: currentBlogData.title || campaign_title,
                    blog_id: currentBlogData.id,
                }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error:', errorText);
                alert('Failed to create email campaign. Server error.');
                return;
            }
            const contentType = response.headers.get("content-type");
            if(contentType && contentType.includes("application/json")) {
                const result = await response.json();
                alert('Email campaign created successfully!');
            } else {
                console.error("Response was not JSON");
                alert('Failed to create email campaign. Server error.');
            }
            
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create email campaign. Client side error.');
        }
    });

    // Publish to WP buton handler
    publishToWPBtn.addEventListener('click', async () => {
        if (!currentBlogData) return;
    
        try {
            const campaign_title = document.getElementById('topic').value;
            const blogContent = document.getElementById('blogContent');
            
            // Get the raw HTML content
            const htmlContent = blogContent.innerHTML;
            
            console.log("Sending to WordPress:", {
                title: currentBlogData.title || campaign_title,
                contentLength: htmlContent.length,
                blog_id: currentBlogData.id, 
            });
            
            const response = await fetch('/api/blogs/draft-to-wp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: htmlContent,
                    title: currentBlogData.title || campaign_title,
                    blog_id: currentBlogData.id,
                }),
            });
        
            // Add more debugging
            console.log("Response status:", response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error:', errorText);
                throw new Error(`Server error: ${response.status}`);
            }

            const result = await response.json();
            console.log("WordPress result:", result);
            
            if (result.status === 'success') {
                alert('Blog post created as draft in WordPress!');
            } else {
                throw new Error(result.message || 'Unknown error');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to publish to WordPress: ' + error.message);
        }
    });
});