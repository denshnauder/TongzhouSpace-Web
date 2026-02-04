// Serverless function for getting directory tree from GitHub
import { Octokit } from '@octokit/rest';

export default async (req, res) => {
  // Validate request method
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    // Get GitHub token from environment variables
    const githubToken = process.env.GITHUB_TOKEN;
    if (!githubToken) {
      return res.status(500).json({ error: 'GitHub Token not configured' });
    }

    // Initialize Octokit
    const octokit = new Octokit({
      auth: githubToken,
    });

    // GitHub repository details
    const owner = 'denshnauder'; // Replace with actual owner
    const repo = 'TongzhouSpace'; // Replace with actual repo
    const branch = 'main'; // Default branch

    // Get repository tree
    const { data: tree } = await octokit.rest.git.getTree({
      owner,
      repo,
      tree_sha: branch,
      recursive: 1
    });

    // Filter out folders and exclude system directories
    const excludedDirs = ['.github', '.vercel', 'public', 'node_modules', '.git'];
    const folderPaths = new Set();

    tree.tree.forEach(item => {
      if (item.type === 'tree') {
        // Get relative path from content directory
        const pathParts = item.path.split('/');
        
        // Skip if path is in excluded directories
        const isExcluded = pathParts.some(part => excludedDirs.includes(part));
        if (isExcluded) {
          return;
        }

        // Add folder path to set
        folderPaths.add(item.path);
      }
    });

    // Convert set to array and sort
    const sortedFolders = Array.from(folderPaths).sort();

    // Return JSON response
    return res.status(200).json(sortedFolders);
  } catch (error) {
    console.error('Error getting directory tree:', error);
    return res.status(500).json({ error: 'Failed to get directory tree' });
  }
};