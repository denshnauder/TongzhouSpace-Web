import { useState } from 'preact/hooks'
import { QuartzComponent } from './types'

interface FileWithContent {
  name: string;
  content: string;
}

const FileUploader: QuartzComponent = () => {
  const [selectedPath, setSelectedPath] = useState<string>('大二上/汽车理论');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<{
    status: 'idle' | 'uploading' | 'success' | 'error';
    message: string;
  }>({ status: 'idle', message: '' });

  // File size limit (20MB)
  const MAX_FILE_SIZE = 20 * 1024 * 1024;

  // Handle file selection
  const handleFileChange = (e: Event) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) {
      if (file.size > MAX_FILE_SIZE) {
        setUploadStatus({
          status: 'error',
          message: '文件大小超过限制 (20MB)'
        });
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setUploadStatus({ status: 'idle', message: '' });
    }
  };

  // Convert file to Base64
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        // Extract Base64 content without data URL prefix
        const result = reader.result as string;
        const base64Content = result.split(',')[1];
        resolve(base64Content);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  // Handle upload
  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus({
        status: 'error',
        message: '请先选择文件'
      });
      return;
    }

    setUploadStatus({ status: 'uploading', message: '上传中...' });

    try {
      // Convert file to Base64
      const base64Content = await fileToBase64(selectedFile);

      // Prepare file data
      const fileData: FileWithContent = {
        name: selectedFile.name,
        content: base64Content
      };

      // Call API
      const response = await fetch('/api/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          path: selectedPath,
          file: fileData
        })
      });

      const result = await response.json();

      if (result.success) {
        setUploadStatus({
          status: 'success',
          message: '上传成功！'
        });
        // Reset form
        setSelectedFile(null);
        // Clear file input
        const fileInput = document.getElementById('file-input') as HTMLInputElement;
        if (fileInput) {
          fileInput.value = '';
        }
      } else {
        setUploadStatus({
          status: 'error',
          message: `上传失败: ${result.error || '未知错误'}`
        });
      }
    } catch (error) {
      setUploadStatus({
        status: 'error',
        message: `上传失败: ${(error as Error).message}`
      });
    }
  };

  return (
    <div style={{
      padding: '20px',
      border: '1px solid #e5e5e5',
      borderRadius: '8px',
      backgroundColor: '#faf8f8'
    }}>
      <h3>文件上传</h3>
      
      {/* Path selection */}
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>目标文件夹:</label>
        <select
          value={selectedPath}
          onChange={(e) => setSelectedPath((e.target as HTMLSelectElement).value)}
          style={{
            width: '100%',
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid #ddd'
          }}
        >
          <option value="大二上/汽车理论">大二上/汽车理论</option>
          <option value="大二上/材料力学">大二上/材料力学</option>
          <option value="公共课/毛概">公共课/毛概</option>
        </select>
      </div>

      {/* File input */}
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>选择文件:</label>
        <input
          id="file-input"
          type="file"
          accept=".pdf,.md,.markdown"
          onChange={handleFileChange}
          style={{
            width: '100%',
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid #ddd'
          }}
        />
      </div>

      {/* Upload button */}
      <button
        onClick={handleUpload}
        disabled={!selectedFile || uploadStatus.status === 'uploading'}
        style={{
          width: '100%',
          padding: '10px',
          backgroundColor: '#005bac',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: (!selectedFile || uploadStatus.status === 'uploading') ? 'not-allowed' : 'pointer',
          opacity: (!selectedFile || uploadStatus.status === 'uploading') ? 0.6 : 1
        }}
      >
        上传
      </button>

      {/* Status display */}
      <div style={{ marginTop: '15px' }}>
        {uploadStatus.status === 'uploading' && (
          <div style={{ color: '#005bac', fontSize: '14px' }}>
            {uploadStatus.message}
          </div>
        )}
        {uploadStatus.status === 'success' && (
          <div style={{ color: '#28a745', fontSize: '14px' }}>
            {uploadStatus.message}
          </div>
        )}
        {uploadStatus.status === 'error' && (
          <div style={{ color: '#dc3545', fontSize: '14px' }}>
            {uploadStatus.message}
          </div>
        )}
      </div>
    </div>
  );
};

const FileUploaderConstructor = () => FileUploader
export default FileUploaderConstructor