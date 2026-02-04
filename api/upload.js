// Serverless function for file upload to GitHub
import { Octokit } from '@octokit/rest';

export default async (req, res) => {
  // Validate request method
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    // Get GitHub token from environment variables
    const githubToken = process.env.GITHUB_TOKEN;
    if (!githubToken) {
      return res.status(500).json({ error: 'GitHub Token not configured' });
    }

    // Parse request body
    const { path, file } = req.body;
    if (!path || !file) {
      return res.status(400).json({ error: 'Missing required fields: path and file' });
    }

    // Extract filename from file object
    const filename = file.name;
    const content = file.content;

    // Initialize Octokit
    const octokit = new Octokit({
      auth: githubToken,
    });

    // GitHub repository details
    const owner = 'denshnauder'; // Replace with actual owner
    const repo = 'TongzhouSpace'; // Replace with actual repo

    // Construct full path in content directory
    const fullPath = `content/${path}/${filename}`;

    // Commit message
    const commitMessage = `User Upload: ${filename} via WebUI`;

    // Create or update file in GitHub
    const response = await octokit.rest.repos.createOrUpdateFileContents({
      owner,
      repo,
      path: fullPath,
      message: commitMessage,
      content: content, // Base64 encoded content
      committer: {
        name: 'Web Uploader',
        email: 'web-uploader@tongzhou.space'
      }
    });

    // Return success response
    return res.status(200).json({
      success: true,
      message: 'File uploaded successfully',
      data: response.data
    });
  } catch (error) {
    console.error('Upload error:', error);
    return res.status(500).json({
      error: 'Upload failed',
      details: error.message
    });
  }
};