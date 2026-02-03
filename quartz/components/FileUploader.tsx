import { useState, useEffect } from 'preact/hooks'
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from './types'

interface FileWithContent {
  name: string;
  content: string;
}

export default (() => {
  const FileUploader: QuartzComponent = () => {
    const [selectedPath, setSelectedPath] = useState<string>('大二上/汽车理论');
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [uploadStatus, setUploadStatus] = useState<{
      status: 'idle' | 'uploading' | 'success' | 'error';
      message: string;
    }>({ status: 'idle', message: '' });
    const [folders, setFolders] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [showSuggestions, setShowSuggestions] = useState<boolean>(false);
    const [filteredFolders, setFilteredFolders] = useState<string[]>([]);
    const [inputValue, setInputValue] = useState<string>('大二上/汽车理论');

    // Fetch folder list on component mount
    useEffect(() => {
      const fetchFolders = async () => {
        try {
          const response = await fetch('/api/tree');
          if (response.ok) {
            const data = await response.json();
            setFolders(data);
          } else {
            console.error('Failed to fetch folders:', response.status);
          }
        } catch (error) {
          console.error('Error fetching folders:', error);
        } finally {
          setIsLoading(false);
        }
      };

      fetchFolders();
    }, []);

    // Handle input change and filter folders
    const handleInputChange = (e: any) => {
      const value = e.target.value;
      setInputValue(value);
      setSelectedPath(value);

      if (value) {
        // Filter folders based on input value
        const filtered = folders.filter(folder => 
          folder.toLowerCase().includes(value.toLowerCase())
        );
        setFilteredFolders(filtered);
        setShowSuggestions(true);
      } else {
        setShowSuggestions(false);
      }
    };

    // Handle folder selection from suggestions
    const handleFolderSelect = (folder: string) => {
      setInputValue(folder);
      setSelectedPath(folder);
      setShowSuggestions(false);
    };

    // Check if path exists
    const pathExists = (path: string) => {
      return folders.includes(path);
    };

    // File size limit (20MB)
    const MAX_FILE_SIZE = 20 * 1024 * 1024;

    // Handle file selection
    const handleFileChange = (e: any) => {
      const file = e.target.files?.[0];
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

      if (!selectedPath) {
        setUploadStatus({
          status: 'error',
          message: '请选择目标文件夹'
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

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
          setUploadStatus({
            status: 'success',
            message: '上传成功！'
          });
          // Reset form
          setSelectedFile(null);
          setInputValue('');
          setSelectedPath('');
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
        border: '5px solid red',
        borderRadius: '8px',
        backgroundColor: '#faf8f8'
      }}>
        <h3>文件上传</h3>
        
        {/* Path selection */}
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>目标文件夹:</label>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              onFocus={() => {
                if (inputValue) {
                  const filtered = folders.filter(folder => 
                    folder.toLowerCase().includes(inputValue.toLowerCase())
                  );
                  setFilteredFolders(filtered);
                  setShowSuggestions(true);
                }
              }}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #ddd',
                boxSizing: 'border-box'
              }}
              placeholder="例如：大二上/汽车理论"
            />
            
            {/* Suggestions dropdown */}
            {showSuggestions && filteredFolders.length > 0 && (
              <div style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                backgroundColor: 'white',
                border: '1px solid #ddd',
                borderRadius: '0 0 4px 4px',
                maxHeight: '200px',
                overflowY: 'auto',
                zIndex: 1000,
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}>
                {filteredFolders.map((folder, index) => (
                  <div
                    key={index}
                    onClick={() => handleFolderSelect(folder)}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      fontSize: '14px'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#f0f0f0';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'white';
                    }}
                  >
                    {folder}
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Path existence status */}
          {inputValue && (
            <div style={{ marginTop: '5px', fontSize: '12px' }}>
              {pathExists(inputValue) ? (
                <span style={{ color: '#28a745' }}>✓ 路径存在</span>
              ) : (
                <span style={{ color: '#ffc107' }}>⚠️ 将创建新文件夹</span>
              )}
            </div>
          )}
          
          {/* Loading status */}
          {isLoading && (
            <div style={{ marginTop: '5px', fontSize: '12px', color: '#6c757d' }}>
              加载目录结构中...
            </div>
          )}
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

  return FileUploader;
}) as QuartzComponentConstructor;